from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.errors import StepInvalidName
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import NameChecker


def test_scenario_init_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(NameChecker)
    code = """
    class Scenario(vedro.Scenario):
        def __init__(self): pass
        def when(): pass
        def then(): assert foo == var
    """
    assert_not_error(ScenarioVisitor, code)


def test_several_given_steps():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(NameChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(): pass
        def given_another(self): pass
        def when(): pass
        def then(): assert foo == var
        def and_(self): assert foo == var
    """
    assert_not_error(ScenarioVisitor, code)


def test_invalid_step_name():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(NameChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(): pass
        def when(): pass
        def then(): assert foo == var
        def it_should_be(): pass
    """
    assert_error(ScenarioVisitor, code, StepInvalidName, step_name="it_should_be")
