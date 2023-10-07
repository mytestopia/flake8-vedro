from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.errors import StepWhenDuplicated, StepWhenNotFound
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import SingleWhenChecker


def test_scenario_without_when():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(SingleWhenChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(): pass
        def then(): assert foo == var
    """
    assert_error(ScenarioVisitor, code, StepWhenNotFound)


def test_scenario_with_when():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(SingleWhenChecker)
    code = """
    class Scenario(vedro.Scenario):
        def when(): pass
        def then(): assert foo == var
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_with_when_long_name():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(SingleWhenChecker)
    code = """
    class Scenario(vedro.Scenario):
        def when_user_get(): pass
        def then(): assert foo == var
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_with_duplicated_when():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(SingleWhenChecker)
    code = """
    class Scenario(vedro.Scenario):
        def when(): pass
        def when_another(): pass
        def then(): assert foo == var
    """
    assert_error(ScenarioVisitor, code, StepWhenDuplicated)
