from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.errors import (
    StepAssertHasComparisonWithoutAssert,
    StepAssertHasUselessAssert
)
from flake8_vedro.visitors import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import UselessAssertChecker


def test_useless_assert_constant():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UselessAssertChecker)
    code = """
    class Scenario:
        def when(): pass
        def then():
            assert True
    """
    assert_error(ScenarioVisitor, code, StepAssertHasUselessAssert, step_name='then')


def test_useless_assert_var():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UselessAssertChecker)
    code = """
    class Scenario:
        def when(): pass
        def then():
            assert foo
    """
    assert_error(ScenarioVisitor, code, StepAssertHasUselessAssert, step_name='then')


def test_assert_constant_not_in_scenario():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UselessAssertChecker)
    code = """
    def any_helper(): assert True
    """
    assert_not_error(ScenarioVisitor, code)


def test_compation_without_assert():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UselessAssertChecker)
    code = """
    class Scenario:
        def when(): pass
        def then():
            foo == var
    """
    assert_error(ScenarioVisitor, code, StepAssertHasComparisonWithoutAssert, step_name='then')
