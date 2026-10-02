import ast
import os
import re
import string
from typing import Dict, Iterator, List, NamedTuple, Optional

from flake8_vedro.abstract_checkers.scenario_helper import (
    SCENARIO_CLASS_NAME,
    SCENARIOS_FOLDER,
    ScenarioHelper,
    Subject,
)

PRUNED_DIRS = {'__pycache__', 'node_modules'}


def is_comparable_subject(value: str) -> bool:
    """
    Subject with {subject} placeholder takes its value from params, so it can't be compared
    """
    try:
        fields = [field for _, field, _, _ in string.Formatter().parse(value) if field]
    except ValueError:  # malformed template, e.g. an unbalanced brace
        return True
    # also {subject.name} and {subject[0]}
    return not any(re.match(r'subject\b', field) for field in fields)


class Occurrence(NamedTuple):
    path: str
    lineno: int


class SubjectsMap:
    """
    Subjects of all scenarios in ./scenarios, built once per process
    """

    _cache: Optional['SubjectsMap'] = None

    def __init__(self) -> None:
        self._occurrences = _scan(SCENARIOS_FOLDER)

    @classmethod
    def get(cls) -> 'SubjectsMap':
        if cls._cache is None:
            cls._cache = cls()
        return cls._cache

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache = None

    def find_duplicate_original(self, filename: str, subject: Subject) -> Optional[Occurrence]:
        """
        Return the first occurrence of subject if the scenario in filename is not the first one
        """
        if subject.value is None:
            return None

        occurrences = self._occurrences.get(subject.value, [])
        current = os.path.relpath(filename)

        # vedro runs only the last Scenario of a module, so a file is one scenario.
        # Not found: file is outside ./scenarios or differs from the one on disk
        if all(occurrence.path != current for occurrence in occurrences):
            return None
        if occurrences[0].path == current:
            return None
        return occurrences[0]


def _scan(root: str) -> Dict[str, List[Occurrence]]:
    result: Dict[str, List[Occurrence]] = {}

    for dirpath, dirnames, filenames in os.walk(root):
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
        subject = ScenarioHelper().get_subject(class_node)
        if subject is not None and subject.value is not None and is_comparable_subject(subject.value):
            found.append(subject)
    return found


def _find_scenario_nodes(node: ast.AST) -> Iterator[ast.ClassDef]:
    """
    Return the same Scenario classes that ScenarioVisitor visits (it doesn't go inside classes)
    """
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.ClassDef):
            if child.name == SCENARIO_CLASS_NAME:
                yield child
        else:
            yield from _find_scenario_nodes(child)
