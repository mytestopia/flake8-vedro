from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.errors import StepHasAssert
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import NoAssertChecker


def test_assert_in_init_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(NoAssertChecker)
    code = """
    class Scenario:
        def __init__(self): assert True
        def when(): pass
    """
    assert_error(ScenarioVisitor, code, StepHasAssert, step_name='__init__')


def test_assert_in_when_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(NoAssertChecker)
    code = """
    class Scenario:
        def __init__(self): pass
        def when(): assert True
    """
    assert_error(ScenarioVisitor, code, StepHasAssert, step_name='when')


def test_assert_in_then_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(NoAssertChecker)
    code = """
    class Scenario:
        def __init__(self): pass
        def given(): pass
        def when(): pass
        def then(): assert foo == var
    """
    assert_not_error(ScenarioVisitor, code)


def test_assert_in_given_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(NoAssertChecker)
    code = """
    class Scenario:
        def given(): assert True
        def when(): pass
    """
    assert_error(ScenarioVisitor, code, StepHasAssert, step_name='given')
