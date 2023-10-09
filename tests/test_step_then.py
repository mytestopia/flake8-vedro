from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.errors import StepThenDuplicated, StepThenNotFound
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import SingleThenChecker


def test_scenario_without_then():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(SingleThenChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(): pass
        def when(): pass
    """
    assert_error(ScenarioVisitor, code, StepThenNotFound)


def test_scenario_with_then_long_name():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(SingleThenChecker)
    code = """
    class Scenario(vedro.Scenario):
        def then_it_should_return(): assert foo == var
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_with_duplicated_then():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(SingleThenChecker)
    code = """
    class Scenario(vedro.Scenario):
        def then(): assert foo == var
        def then_another(): assert foo == var
    """
    assert_error(ScenarioVisitor, code, StepThenDuplicated)
