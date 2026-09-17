import ast
import textwrap

import pytest

from flake8_vedro.config import DefaultConfig
from flake8_vedro.errors import SubjectDuplicatedAcrossScenarios
from flake8_vedro.helpers.subject_scanner import clear_cache
from flake8_vedro.visitors import ScenarioVisitor
from flake8_vedro.visitors.scenario_checkers import DuplicateSubjectChecker

# VDR110 compares a scenario with the other files in its scenarios/ folder, so
# these tests write scenarios to disk into a per-test cwd. assert_error and
# assert_not_error cannot be used: they run the visitor on an in-memory snippet
# without a filename, and the checker needs a filename to find its folder and
# to recognise its own occurrence. _assert_error and _assert_not_error below
# mirror their contract (single error, type check, exact message) on a path.

CONFIG_ON = DefaultConfig(check_duplicate_subjects=True)
CONFIG_OFF = DefaultConfig()


@pytest.fixture(autouse=True)
def scenarios_tree(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(DuplicateSubjectChecker)
    clear_cache()
    yield tmp_path
    clear_cache()


def write(path, code):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(code))
    return path


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


def test_check_is_disabled_by_default(scenarios_tree):
    a = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    b = write(scenarios_tree / 'scenarios/b.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    _assert_not_error(a, CONFIG_OFF)
    _assert_not_error(b, CONFIG_OFF)


def test_unique_subjects(scenarios_tree):
    a = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    b = write(scenarios_tree / 'scenarios/b.py', '''
    class Scenario:
        subject = 'login user'
    ''')
    _assert_not_error(a, CONFIG_ON)
    _assert_not_error(b, CONFIG_ON)


def test_duplicated_subject(scenarios_tree):
    a = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    b = write(scenarios_tree / 'scenarios/b.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    _assert_not_error(a, CONFIG_ON)
    _assert_error(b, CONFIG_ON, first_file='scenarios/a.py', first_lineno=3)


def test_first_subject_by_sorted_path_is_not_reported(scenarios_tree):
    # written in reverse order: the report should not depend on it
    b = write(scenarios_tree / 'scenarios/b.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    a = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    _assert_not_error(a, CONFIG_ON)
    _assert_error(b, CONFIG_ON, first_file='scenarios/a.py', first_lineno=3)


def test_every_duplicated_subject_is_reported(scenarios_tree):
    paths = [write(scenarios_tree / f'scenarios/{name}.py', '''
    class Scenario:
        subject = 'register user'
    ''') for name in ('a', 'b', 'c')]

    _assert_not_error(paths[0], CONFIG_ON)
    for path in paths[1:]:
        _assert_error(path, CONFIG_ON, first_file='scenarios/a.py', first_lineno=3)


def test_duplicated_subject_in_one_file(scenarios_tree):
    path = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'


    class Scenario:
        subject = 'register user'
    ''')
    _assert_error(path, CONFIG_ON, first_file='scenarios/a.py', first_lineno=3)


def test_different_parametrization_placeholders(scenarios_tree):
    error = write(scenarios_tree / 'scenarios/get_names_by_error.py', '''
    class Scenario:
        subject = 'get names with {error}'
    ''')
    locale = write(scenarios_tree / 'scenarios/get_names_by_locale.py', '''
    class Scenario:
        subject = 'get names with {locale}'
    ''')
    _assert_not_error(error, CONFIG_ON)
    _assert_not_error(locale, CONFIG_ON)


def test_same_parametrization_template(scenarios_tree):
    a = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'get names with {error}'
    ''')
    b = write(scenarios_tree / 'scenarios/b.py', '''
    class Scenario:
        subject = 'get names with {error}'
    ''')
    _assert_not_error(a, CONFIG_ON)
    _assert_error(b, CONFIG_ON, first_file='scenarios/a.py', first_lineno=3)


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
    b = write(scenarios_tree / 'scenarios/b.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    _assert_not_error(a, CONFIG_ON)
    _assert_not_error(b, CONFIG_ON)


def test_scenario_outside_scenarios_folder(scenarios_tree):
    inside = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    outside = write(scenarios_tree / 'not_scenarios/b.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    _assert_not_error(inside, CONFIG_ON)
    _assert_not_error(outside, CONFIG_ON)


def test_another_scenarios_folder_is_another_namespace(scenarios_tree):
    first = write(scenarios_tree / 'service_a/scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    second = write(scenarios_tree / 'service_b/scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    _assert_not_error(first, CONFIG_ON)
    _assert_not_error(second, CONFIG_ON)


def test_scenario_nested_in_class_is_not_the_first_subject(scenarios_tree):
    # ScenarioVisitor never checks a Scenario nested in another class, so such a
    # scenario must not become the first occurrence: it could never be reported
    write(scenarios_tree / 'scenarios/A_nested.py', '''
    class Outer:
        class Scenario:
            subject = 'register user'
    ''')
    a = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    b = write(scenarios_tree / 'scenarios/b.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    _assert_not_error(a, CONFIG_ON)
    _assert_error(b, CONFIG_ON, first_file='scenarios/a.py', first_lineno=3)


def test_scenario_nested_in_function_is_the_first_subject(scenarios_tree):
    # ScenarioVisitor does check it, so it must be in the map
    nested = write(scenarios_tree / 'scenarios/A_nested.py', '''
    def make_scenario():
        class Scenario:
            subject = 'register user'
        return Scenario
    ''')
    a = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    _assert_not_error(nested, CONFIG_ON)
    _assert_error(a, CONFIG_ON, first_file='scenarios/A_nested.py', first_lineno=4)


def test_unparsable_class_body_does_not_break_the_check(scenarios_tree):
    write(scenarios_tree / 'scenarios/A_unparsable.py', '''
    class Scenario:
        FIRST, SECOND = 1, 2
        subject = 'get names'
    ''')
    a = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    b = write(scenarios_tree / 'scenarios/b.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    _assert_not_error(a, CONFIG_ON)
    _assert_error(b, CONFIG_ON, first_file='scenarios/a.py', first_lineno=3)


def test_file_with_syntax_error_is_skipped(scenarios_tree):
    write(scenarios_tree / 'scenarios/A_broken.py', '''
    class Scenario
        subject = 'register user'
    ''')
    a = write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    b = write(scenarios_tree / 'scenarios/b.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    _assert_not_error(a, CONFIG_ON)
    _assert_error(b, CONFIG_ON, first_file='scenarios/a.py', first_lineno=3)


def test_subject_moved_in_an_unsaved_file_is_skipped(scenarios_tree):
    # flake8 can be given a tree that differs from the file on disk (stdin, an
    # unsaved editor buffer): there is nothing reliable to compare, so be quiet
    write(scenarios_tree / 'scenarios/a.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    b = write(scenarios_tree / 'scenarios/b.py', '''
    class Scenario:
        subject = 'register user'
    ''')
    moved = ast.parse("\n\n\nclass Scenario:\n    subject = 'register user'\n")

    visitor = ScenarioVisitor(config=CONFIG_ON, filename=str(b))
    visitor.visit(moved)
    assert not visitor.errors
