import ast
import os
import re
import string
from typing import Dict, Iterator, List, NamedTuple, Optional

from flake8_vedro.abstract_checkers.scenario_helper import (
    SCENARIO_CLASS_NAME,
    ScenarioHelper,
    Subject,
)

# Directories that never contain scenarios and only slow the walk down
# (dot-directories are pruned separately).
PRUNED_DIRS = {'__pycache__', 'node_modules'}


def is_comparable(value: str) -> bool:
    """Tell whether a subject template can be compared with other ones.

    A `{subject}` placeholder means the scenario takes (a part of) its subject
    from params, so equal templates like 'delete {subject} photo' or '{subject}'
    in different scenarios do not mean equal subjects.
    """
    try:
        fields = [field for _, field, _, _ in string.Formatter().parse(value) if field]
    except ValueError:  # malformed template, e.g. an unbalanced brace
        return True
    # {subject.name} and {subject[0]} are still the subject param
    return not any(re.match(r'subject\b', field) for field in fields)


class Occurrence(NamedTuple):
    path: str  # absolute
    lineno: int


class SubjectsMap:
    """Literal subjects of every scenario under a scenarios root.

    Occurrences of a subject are sorted, so the first one is a deterministic
    "original" regardless of which process builds the map. Maps are cached per
    process per root, use `for_root` to get one.
    """

    _cache: Dict[str, 'SubjectsMap'] = {}

    def __init__(self, root: str) -> None:
        self._occurrences = _scan(root)

    @classmethod
    def for_root(cls, root: str) -> 'SubjectsMap':
        key = os.path.abspath(root)
        if key not in cls._cache:
            cls._cache[key] = cls(key)
        return cls._cache[key]

    @classmethod
    def clear_cache(cls) -> None:
        """Drop the cached maps (used by tests)."""
        cls._cache.clear()

    def find_original(self, filename: str, subject: Subject) -> Optional[Occurrence]:
        """Return the original occurrence if `subject` in `filename` duplicates it."""
        if subject.value is None or not is_comparable(subject.value):
            return None

        occurrences = self._occurrences.get(subject.value, [])
        current = os.path.abspath(filename)

        # A file is one scenario: vedro collects scenarios from the module
        # namespace, so of several `Scenario` classes only the last one runs.
        # Not in the map means the file on disk differs from the tree flake8
        # parsed (stdin, or an unsaved editor buffer) - nothing to compare with.
        if all(occurrence.path != current for occurrence in occurrences):
            return None
        if occurrences[0].path == current:
            return None
        return occurrences[0]


def _scan(root: str) -> Dict[str, List[Occurrence]]:
    result: Dict[str, List[Occurrence]] = {}

    for dirpath, dirnames, filenames in os.walk(root):
        # prune in place so os.walk does not descend into them
        dirnames[:] = [d for d in dirnames if d not in PRUNED_DIRS and not d.startswith('.')]
        for name in filenames:
            if not name.endswith('.py'):
                continue
            path = os.path.join(dirpath, name)
            for subject in _subjects_in_file(path):
                result.setdefault(subject.value, []).append(Occurrence(path, subject.lineno))

    for occurrences in result.values():
        occurrences.sort()
    return result


def _subjects_in_file(path: str) -> List[Subject]:
    try:
        with open(path, encoding='utf-8') as handle:
            tree = ast.parse(handle.read(), filename=path)
    except (OSError, ValueError, SyntaxError):
        return []

    found = []
    for class_node in _find_scenario_nodes(tree):
        # only the first subject counts, the rest are VDR106's business
        subject = ScenarioHelper().get_subject(class_node)
        if subject is not None and subject.value is not None and is_comparable(subject.value):
            found.append(subject)
    return found


def _find_scenario_nodes(node: ast.AST) -> Iterator[ast.ClassDef]:
    """Yield the same Scenario classes that ScenarioVisitor visits.

    ScenarioVisitor.visit_ClassDef does not call generic_visit, so traversal
    stops at every class: a Scenario nested in another class is never checked
    and must not end up in the map either, or it would become an original that
    can never be reported.
    """
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.ClassDef):
            if child.name == SCENARIO_CLASS_NAME:
                yield child
        else:
            yield from _find_scenario_nodes(child)
