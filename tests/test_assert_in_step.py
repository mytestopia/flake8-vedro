from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.errors import StepAssertWithoutAssert
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import AssertChecker


def test_init_without_assert():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(AssertChecker)
    code = """
     class Scenario:
        def __init__(self): pass
        def given(): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_given_without_assert():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(AssertChecker)
    code = """
     class Scenario:
        def given(): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_when_without_assert():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(AssertChecker)
    code = """
     class Scenario:
        def when(): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_then_without_assert():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(AssertChecker)
    code = """
     class Scenario:
        def then(): pass
    """
    assert_error(ScenarioVisitor, code, StepAssertWithoutAssert, step_name='then')


def test_scenario_and_without_assert():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(AssertChecker)
    code = """
     class Scenario:
        def when(): pass
        def then(): assert foo == var
        def and_(): pass
    """
    assert_error(ScenarioVisitor, code, StepAssertWithoutAssert, step_name='and_')


def test_scenario_but_without_assert():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(AssertChecker)
    code = """
     class Scenario:
        def when(): pass
        def then(): assert foo == var
        def but(): pass
    """
    assert_error(ScenarioVisitor, code, StepAssertWithoutAssert, step_name='but')


def test_scenario_assert_in_for():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(AssertChecker)
    code = """
     class Scenario:
        def when(): pass
        def then():
            for i in [1, 2]:
                assert True
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_assert_in_while():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(AssertChecker)
    code = """
     class Scenario:
        def when(): pass
        def then():
            while foo:
                assert True
    """
    assert_not_error(ScenarioVisitor, code)
