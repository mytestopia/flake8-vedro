import ast
import os
import pathlib
from typing import Dict, Iterator, List, Optional, Tuple

SCENARIOS_FOLDER = 'scenarios'

# Directories that never contain scenarios and only slow the walk down
# (dot-directories are pruned separately).
PRUNED_DIRS = {'__pycache__', 'node_modules'}

# subject value -> [(absolute file path, lineno)], sorted
SubjectMap = Dict[str, List[Tuple[str, int]]]

# scenarios root -> subject map, built once per process per root
_cache: Dict[str, SubjectMap] = {}


def get_scenarios_root(filename: str) -> Optional[str]:
    """Return the outermost "scenarios" directory containing `filename`.

    The scan is scoped to this directory, not to the current working directory,
    so that the subject namespace matches the vedro project the file belongs to:
    a vendored or excluded copy of a scenarios tree, or a sibling service in a
    monorepo, is a different root and never collides with this one.
    """
    path = pathlib.Path(os.path.abspath(filename))
    roots = [str(parent) for parent in path.parents if parent.name == SCENARIOS_FOLDER]
    return roots[-1] if roots else None


def get_literal_subject(class_node: ast.ClassDef) -> Optional[Tuple[str, int, int]]:
    """Return (value, lineno, col_offset) of the first literal string subject.

    Returns None if the scenario has no subject, or if its first subject is not
    a string literal. Only the first `subject` assignment counts, the rest are
    VDR106's business.

    Deliberately does not reuse ScenarioHelper.get_subjects: the scanner reads
    every file in the tree, so it must not raise on a class body it does not
    understand (e.g. `A, B = 1, 2`).
    """
    for element in class_node.body:
        if not isinstance(element, ast.Assign):
            continue
        target = element.targets[0]
        if not isinstance(target, ast.Name) or target.id != 'subject':
            continue

        value = element.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value, element.lineno, element.col_offset
        return None
    return None


def collect_subjects(root: str) -> SubjectMap:
    """Return {subject: [(file, lineno)]} for every scenario under `root`.

    Occurrences are sorted, so the first one is a deterministic "primary"
    regardless of which process builds the map. Results are cached per process
    per root; call `clear_cache` to reset (used by tests).
    """
    key = os.path.abspath(root)
    cached = _cache.get(key)
    if cached is None:
        cached = _scan(key)
        _cache[key] = cached
    return cached


def clear_cache() -> None:
    """Drop the cached subject maps (used by tests)."""
    _cache.clear()


def _scan(root: str) -> SubjectMap:
    result: SubjectMap = {}

    for dirpath, dirnames, filenames in os.walk(root):
        # prune in place so os.walk does not descend into them
        dirnames[:] = [d for d in dirnames if d not in PRUNED_DIRS and not d.startswith('.')]
        for name in filenames:
            if not name.endswith('.py'):
                continue
            path = os.path.join(dirpath, name)
            for value, lineno, _ in _subjects_in_file(path):
                result.setdefault(value, []).append((path, lineno))

    for occurrences in result.values():
        occurrences.sort()
    return result


def _subjects_in_file(path: str) -> List[Tuple[str, int, int]]:
    try:
        with open(path, encoding='utf-8') as handle:
            tree = ast.parse(handle.read(), filename=path)
    except (OSError, ValueError, SyntaxError):
        return []

    found = []
    for class_node in _find_scenario_nodes(tree):
        subject = get_literal_subject(class_node)
        if subject is not None:
            found.append(subject)
    return found


def _find_scenario_nodes(node: ast.AST) -> Iterator[ast.ClassDef]:
    """Yield the same Scenario classes that ScenarioVisitor visits.

    ScenarioVisitor.visit_ClassDef does not call generic_visit, so traversal
    stops at every class: a Scenario nested in another class is never checked
    and must not end up in the map either, or it would become a primary that
    can never be reported.
    """
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.ClassDef):
            if child.name == 'Scenario':
                yield child
        else:
            yield from _find_scenario_nodes(child)
