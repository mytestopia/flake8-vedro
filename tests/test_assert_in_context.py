from flake8_plugin_utils import assert_error, assert_not_error
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import ContextAssertChecker


def test_context_without_assert():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ContextAssertChecker)
    code = """
    @vedro.context:
    async def(): pass
    """
    assert_error(ScenarioVisitor, code, ContextAssertChecker)


def test_context_without_assert_in_with():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ContextAssertChecker)
    code = """
    @vedro.context:
    async def():
        with foo:
            pass
    """
    assert_error(ScenarioVisitor, code, ContextAssertChecker)


def test_context_assert():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ContextAssertChecker)
    code = """
    @vedro.context:
    async def(): assert await page.is_visible()
    """
    assert_not_error(ScenarioVisitor, code)


def test_context_assert_in_with():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ContextAssertChecker)
    code = """
    @vedro.context:
    async def():
        with foo:
            assert await page.is_visible()
    """
    assert_not_error(ScenarioVisitor, code)
