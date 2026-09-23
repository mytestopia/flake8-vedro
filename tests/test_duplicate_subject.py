import ast
import textwrap

import pytest

from flake8_vedro.config import DefaultConfig
from flake8_vedro.errors import SubjectDuplicatedAcrossScenarios
from flake8_vedro.helpers.subject_scanner import SubjectsMap
from flake8_vedro.visitors import ScenarioVisitor
from flake8_vedro.visitors.scenario_checkers import DuplicateSubjectChecker

# VDR110 compares a scenario with the other files in its scenarios/ folder, so
# these tests write scenarios to disk into a per-test cwd. assert_error and
# assert_not_error cannot be used: they run the visitor on an in-memory snippet
# without a filename, and the checker needs a filename to find its folder and
# to recognise its own occurrence. _assert_error and _assert_not_error below
# mirror their contract (single error, type check, exact message) on a path.

CONFIG = DefaultConfig()


@pytest.fixture(autouse=True)
def scenarios_tree(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(DuplicateSubjectChecker)
    SubjectsMap.clear_cache()
    yield tmp_path
    SubjectsMap.clear_cache()


def write(path, code):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(code))
    return path


def _create_scenario(scenarios_tree, path, subject):
    return write(scenarios_tree / path, f'''
    class Scenario:
        subject = {subject!r}
    ''')


def _errors(path, config):
    visitor = ScenarioVisitor(config=config, filename=str(path))
    visitor.visit(ast.parse(path.read_text()))
    return visitor.errors


def _assert_error(path, config, **message_kwargs):
    errors = _errors(path, config)
    assert len(errors) == 1, f'expected one error in {path}, got {[e.message for e in errors]}'
    error = errors[0]
    assert isinstance(error, SubjectDuplicatedAcrossScenarios)
    expected = SubjectDuplicatedAcrossScenarios.formatted_message(**message_kwargs)
    assert error.message == expected, f'Expected "{expected}", got "{error.message}"'


def _assert_not_error(path, config):
    errors = _errors(path, config)
    assert not errors, f'unexpected error in {path}: {[e.message for e in errors]}'


def test_unique_subjects(scenarios_tree):
    a = _create_scenario(scenarios_tree, 'scenarios/a.py', 'register user')
    b = _create_scenario(scenarios_tree, 'scenarios/b.py', 'login user')
    _assert_not_error(a, CONFIG)
    _assert_not_error(b, CONFIG)


def test_duplicated_subject(scenarios_tree):
    a = _create_scenario(scenarios_tree, 'scenarios/a.py', 'register user')
    b = _create_scenario(scenarios_tree, 'scenarios/b.py', 'register user')
    _assert_not_error(a, CONFIG)
    _assert_error(b, CONFIG, first_file='scenarios/a.py', first_lineno=3)


def test_first_subject_by_sorted_path_is_not_reported(scenarios_tree):
    # written in reverse order: the report should not depend on it
    b = _create_scenario(scenarios_tree, 'scenarios/b.py', 'register user')
    a = _create_scenario(scenarios_tree, 'scenarios/a.py', 'register user')
    _assert_not_error(a, CONFIG)
    _assert_error(b, CONFIG, first_file='scenarios/a.py', first_lineno=3)


def test_every_duplicated_subject_is_reported(scenarios_tree):
    paths = [_create_scenario(scenarios_tree, f'scenarios/{name}.py', 'register user') for name in ('a', 'b', 'c')]

    _assert_not_error(paths[0], CONFIG)
    for path in paths[1:]:
        _assert_error(path, CONFIG, first_file='scenarios/a.py', first_lineno=3)


def test_same_subject_in_one_file_is_not_reported(scenarios_tree):
    # vedro runs only the last `Scenario` class of a module, so it is not a
    # duplicate in the report
    path = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'


    class Scenario:
        subject = 'register user'
    ''')
    _assert_not_error(path, CONFIG)


def test_different_parametrization_placeholders(scenarios_tree):
    error = _create_scenario(scenarios_tree, 'scenarios/get_names_by_error.py', 'get names with {error}')
    locale = _create_scenario(scenarios_tree, 'scenarios/get_names_by_locale.py', 'get names with {locale}')
    _assert_not_error(error, CONFIG)
    _assert_not_error(locale, CONFIG)


def test_same_parametrization_template(scenarios_tree):
    a = _create_scenario(scenarios_tree, 'scenarios/a.py', 'get names with {error}')
    b = _create_scenario(scenarios_tree, 'scenarios/b.py', 'get names with {error}')
    _assert_not_error(a, CONFIG)
    _assert_error(b, CONFIG, first_file='scenarios/a.py', first_lineno=3)


@pytest.mark.parametrize('subject', [
    'delete reaction on {subject} photo by author',
    '{subject}',
    '{subject.name} with {error}',
])
def test_subject_placeholder_is_not_compared(scenarios_tree, subject):
    # {subject} is filled from params, so equal templates give different subjects
    paths = [_create_scenario(scenarios_tree, f'scenarios/{name}.py', subject)
             for name in ('a', 'b', 'c')]

    for path in paths:
        _assert_not_error(path, CONFIG)


def test_placeholder_similar_to_subject_is_compared(scenarios_tree):
    a = _create_scenario(scenarios_tree, 'scenarios/a.py', 'get {subject_id} photo')
    b = _create_scenario(scenarios_tree, 'scenarios/b.py', 'get {subject_id} photo')
    _assert_not_error(a, CONFIG)
    _assert_error(b, CONFIG, first_file='scenarios/a.py', first_lineno=3)


@pytest.mark.parametrize('subject', [
    'some_variable',
    "f'register {user}'",
    "'register' + ' user'",
])
def test_subject_is_not_a_string_literal(scenarios_tree, subject):
    a = write(scenarios_tree / 'scenarios/a.py', f'''
    class Scenario:
        subject = {subject}
    ''')
    b = _create_scenario(scenarios_tree, 'scenarios/b.py', 'register user')
    _assert_not_error(a, CONFIG)
    _assert_not_error(b, CONFIG)


def test_scenario_outside_scenarios_folder(scenarios_tree):
    inside = _create_scenario(scenarios_tree, 'scenarios/a.py', 'register user')
    outside = _create_scenario(scenarios_tree, 'not_scenarios/b.py', 'register user')
    _assert_not_error(inside, CONFIG)
    _assert_not_error(outside, CONFIG)


def test_another_scenarios_folder_is_another_namespace(scenarios_tree):
    first = _create_scenario(scenarios_tree, 'service_a/scenarios/a.py', 'register user')
    second = _create_scenario(scenarios_tree, 'service_b/scenarios/a.py', 'register user')
    _assert_not_error(first, CONFIG)
    _assert_not_error(second, CONFIG)


def test_scenario_nested_in_class_is_not_the_first_subject(scenarios_tree):
    # ScenarioVisitor never checks a Scenario nested in another class, so such a
    # scenario must not become the first occurrence: it could never be reported
    write(scenarios_tree / 'scenarios/A_nested.py', '''
    class Outer:
        class Scenario:
            subject = 'register user'
    ''')
    a = _create_scenario(scenarios_tree, 'scenarios/a.py', 'register user')
    b = _create_scenario(scenarios_tree, 'scenarios/b.py', 'register user')
    _assert_not_error(a, CONFIG)
    _assert_error(b, CONFIG, first_file='scenarios/a.py', first_lineno=3)


def test_scenario_nested_in_function_is_the_first_subject(scenarios_tree):
    # ScenarioVisitor does check it, so it must be in the map
    nested = write(scenarios_tree / 'scenarios/A_nested.py', '''
    def make_scenario():
        class Scenario:
            subject = 'register user'
        return Scenario
    ''')
    a = _create_scenario(scenarios_tree, 'scenarios/a.py', 'register user')
    _assert_not_error(nested, CONFIG)
    _assert_error(a, CONFIG, first_file='scenarios/A_nested.py', first_lineno=4)


def test_unparsable_class_body_does_not_break_the_check(scenarios_tree):
    write(scenarios_tree / 'scenarios/A_unparsable.py', '''
    class Scenario:
        FIRST, SECOND = 1, 2
        subject = 'get names'
    ''')
    a = _create_scenario(scenarios_tree, 'scenarios/a.py', 'register user')
    b = _create_scenario(scenarios_tree, 'scenarios/b.py', 'register user')
    _assert_not_error(a, CONFIG)
    _assert_error(b, CONFIG, first_file='scenarios/a.py', first_lineno=3)


def test_file_with_syntax_error_is_skipped(scenarios_tree):
    write(scenarios_tree / 'scenarios/A_broken.py', '''
    class Scenario
        subject = 'register user'
    ''')
    a = _create_scenario(scenarios_tree, 'scenarios/a.py', 'register user')
    b = _create_scenario(scenarios_tree, 'scenarios/b.py', 'register user')
    _assert_not_error(a, CONFIG)
    _assert_error(b, CONFIG, first_file='scenarios/a.py', first_lineno=3)


def test_subject_changed_in_an_unsaved_file_is_skipped(scenarios_tree):
    # flake8 can be given a tree that differs from the file on disk (stdin, an
    # unsaved editor buffer): there is nothing reliable to compare, so be quiet
    _create_scenario(scenarios_tree, 'scenarios/a.py', 'register user')
    b = _create_scenario(scenarios_tree, 'scenarios/b.py', 'login user')
    changed = ast.parse("class Scenario:\n    subject = 'register user'\n")

    visitor = ScenarioVisitor(config=CONFIG, filename=str(b))
    visitor.visit(changed)
    assert not visitor.errors


def test_subject_moved_in_an_unsaved_file_is_reported_at_its_line(scenarios_tree):
    _create_scenario(scenarios_tree, 'scenarios/a.py', 'register user')
    b = _create_scenario(scenarios_tree, 'scenarios/b.py', 'register user')
    moved = ast.parse("\n\n\nclass Scenario:\n    subject = 'register user'\n")

    visitor = ScenarioVisitor(config=CONFIG, filename=str(b))
    visitor.visit(moved)
    assert [error.lineno for error in visitor.errors] == [5]
