from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.config import DefaultConfig
from flake8_vedro.errors import ExceedMaxParamsCount
from flake8_vedro.visitors import ScenarioVisitor
from flake8_vedro.visitors.scenario_checkers import ParametrizationLimitChecker


def test_exceeded_parameters_count():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationLimitChecker)
    code = """
    class Scenario:
        subject = 'any subject'
        @params(1, 2)
        def __init__(foo, bar): pass
    """
    assert_error(ScenarioVisitor, code, ExceedMaxParamsCount,
                 config=DefaultConfig(max_params_count=1),
                 max=1,
                 current=2)


def test_not_exceeded_parameters_count():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationLimitChecker)
    code = """
    class Scenario:
        subject = 'any subject'
        @params(1)
        def __init__(foo): pass
    """
    assert_not_error(ScenarioVisitor, code, DefaultConfig(max_params_count=1))
