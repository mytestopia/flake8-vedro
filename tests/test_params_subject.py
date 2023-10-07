from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.config import DefaultConfig
from flake8_vedro.errors import SubjectIsNotParametrized
from flake8_vedro.visitors import ScenarioVisitor
from flake8_vedro.visitors.scenario_checkers import (
    ParametrizationSubjectChecker
)


def test_params_without_subject_substitution():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationSubjectChecker)
    code = """
    class Scenario:
        subject = 'any subject'
        @params(1)
        @params(2)
        def __init__(foo): pass
    """
    assert_error(ScenarioVisitor, code, SubjectIsNotParametrized,
                 config=DefaultConfig(max_params_count=3))


def test_vedro_params_without_subject_substitution():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationSubjectChecker)
    code = """
    class Scenario:
        subject = 'any subject'
        @vedro.params(1)
        @vedro.params(2)
        def __init__(foo): pass
    """
    assert_error(ScenarioVisitor, code, SubjectIsNotParametrized,
                 config=DefaultConfig(max_params_count=3))


def test_param_without_subject_substitution():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationSubjectChecker)
    code = """
    class Scenario:
        subject = 'any subject'
        @params(1)
        def __init__(foo): pass
    """
    assert_not_error(ScenarioVisitor, code, DefaultConfig(max_params_count=3))


def test_params_with_subject_substitution():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationSubjectChecker)
    code = """
    class Scenario:
        subject = 'any subject {any}'
        @params(1)
        @params(2)
        def __init__(foo): pass
    """
    assert_not_error(ScenarioVisitor, code, DefaultConfig(max_params_count=3))


def test_no_params_no_substitution():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationSubjectChecker)
    code = """
    class Scenario:
        subject = 'any subject'
        def __init__(): pass
    """
    assert_not_error(ScenarioVisitor, code)
