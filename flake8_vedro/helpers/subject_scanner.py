import ast
import os
import pathlib
import re
import string
from typing import Dict, Iterator, List, NamedTuple, Optional

from flake8_vedro.abstract_checkers.scenario_helper import (
    SCENARIO_CLASS_NAME,
    SCENARIOS_FOLDER,
    ScenarioHelper,
    Subject,
)


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
    Subjects of all scenarios in a scenarios folder, built once per process
    """

    _cache: Optional['SubjectsMap'] = None

    def __init__(self, root: str) -> None:
        self._occurrences = _scan(root)

    @classmethod
    def for_root(cls, root: str) -> 'SubjectsMap':
        if cls._cache is None:
            cls._cache = cls(root)
        return cls._cache

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache = None

    def find_duplicate_original(self, filename: str, subject: Subject) -> Optional[Occurrence]:
        """
        Return the first occurrence of subject if the scenario in filename is not the first one
        """
        occurrences = self._occurrences.get(subject.value)
        # vedro runs only the last Scenario of a module, so a file is one scenario
        if not occurrences or occurrences[0].path == os.path.relpath(filename):
            return None
        return occurrences[0]


def find_scenarios_root(filename: str) -> Optional[str]:
    """
    Return the outermost scenarios folder containing filename, relative to cwd
    """
    path = pathlib.Path(os.path.abspath(filename))
    roots = [parent for parent in path.parents if parent.name == SCENARIOS_FOLDER]
    return os.path.relpath(roots[-1]) if roots else None


def _scan(root: str) -> Dict[str, List[Occurrence]]:
    result: Dict[str, List[Occurrence]] = {}

    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if not name.endswith('.py'):
                continue
            path = os.path.relpath(os.path.join(dirpath, name))
            for subject in _subjects_in_file(path):
                result.setdefault(subject.value, []).append(Occurrence(path, subject.lineno))

    for occurrences in result.values():
        occurrences.sort(key=lambda occurrence: (os.path.abspath(occurrence.path), occurrence.lineno))
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
