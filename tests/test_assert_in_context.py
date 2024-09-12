from flake8_plugin_utils import assert_error, assert_not_error
from flake8_vedro.visitors.context_assert_visitor import ContextAssertVisitor
from flake8_vedro.errors.errors import ContextWithoutAssert
from flake8_vedro.config import DefaultConfig
from flake8_vedro.visitors.context_checkers import ContextAssertChecker


def test_function_def_without_assert():
    ContextAssertVisitor.deregister_all()
    ContextAssertVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f(): pass
    """
    assert_error(ContextAssertVisitor, code, ContextWithoutAssert,
                 config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_without_assert_when_optional():
    ContextAssertVisitor.deregister_all()
    ContextAssertVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f(): pass
    """
    assert_not_error(ContextAssertVisitor, code,
                     config=DefaultConfig(is_context_assert_optional=True))


def test_function_def_without_assert_in_with():
    ContextAssertVisitor.deregister_all()
    ContextAssertVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f():
        with ():
            pass
    """
    assert_error(ContextAssertVisitor, code, ContextWithoutAssert,
                 config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_assert():
    ContextAssertVisitor.deregister_all()
    ContextAssertVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f(): assert page.is_visible()
    """
    assert_not_error(ContextAssertVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_assert_in_with():
    ContextAssertVisitor.deregister_all()
    ContextAssertVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f():
        with ():
            assert page.is_visible()
    """
    assert_not_error(ContextAssertVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_without_assert():
    ContextAssertVisitor.deregister_all()
    ContextAssertVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    async def f(): pass
    """
    assert_error(ContextAssertVisitor, code, ContextWithoutAssert,
                 config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_without_assert_in_with():
    ContextAssertVisitor.deregister_all()
    ContextAssertVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    async def f():
        with ():
            pass
    """
    assert_error(ContextAssertVisitor, code, ContextWithoutAssert,
                 config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_assert():
    ContextAssertVisitor.deregister_all()
    ContextAssertVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    async def f(): assert page.is_visible()
    """
    assert_not_error(ContextAssertVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_assert_in_with():
    ContextAssertVisitor.deregister_all()
    ContextAssertVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    async def f():
        with ():
            assert page.is_visible()
    """
    assert_not_error(ContextAssertVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_without_assert_when_optional():
    ContextAssertVisitor.deregister_all()
    ContextAssertVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    async def f(): pass
    """
    assert_not_error(ContextAssertVisitor, code, config=DefaultConfig(is_context_assert_optional=True))
