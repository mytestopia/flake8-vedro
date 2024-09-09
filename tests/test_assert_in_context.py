from flake8_plugin_utils import assert_error, assert_not_error
from flake8_vedro.visitors.context_assert_visitor import ContextAssertVisitor
from flake8_vedro.errors.errors import ContextWithoutAssert
from flake8_vedro.config import DefaultConfig


def test_function_def_without_assert():
    code = """
    @vedro.context
    def f(): pass
    """
    assert_error(ContextAssertVisitor, code, ContextWithoutAssert,
                 config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_without_assert_when_optional():
    code = """
    @vedro.context
    def f(): pass
    """
    assert_not_error(ContextAssertVisitor, code,
                     config=DefaultConfig(is_context_assert_optional=True))


def test_function_def_without_assert_in_with():
    code = """
    @vedro.context
    def f():
        with ():
            pass
    """
    assert_error(ContextAssertVisitor, code, ContextWithoutAssert,
                 config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_assert():
    code = """
    @vedro.context
    def f(): assert page.is_visible()
    """
    assert_not_error(ContextAssertVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_assert_in_with():
    code = """
    @vedro.context
    def f():
        with ():
            assert page.is_visible()
    """
    assert_not_error(ContextAssertVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_without_assert():
    code = """
    @vedro.context
    async def f(): pass
    """
    assert_error(ContextAssertVisitor, code, ContextWithoutAssert,
                 config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_without_assert_in_with():
    code = """
    @vedro.context
    async def f():
        with ():
            pass
    """
    assert_error(ContextAssertVisitor, code, ContextWithoutAssert,
                 config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_assert():
    code = """
    @vedro.context
    async def f(): assert page.is_visible()
    """
    assert_not_error(ContextAssertVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_assert_in_with():
    code = """
    @vedro.context
    async def f():
        with ():
            assert page.is_visible()
    """
    assert_not_error(ContextAssertVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_without_assert_when_optional():
    code = """
    @vedro.context
    async def f(): pass
    """
    assert_not_error(ContextAssertVisitor, code, config=DefaultConfig(is_context_assert_optional=True))
