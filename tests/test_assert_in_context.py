from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.config import DefaultConfig
from flake8_vedro.errors.errors import ContextWithoutAssert
from flake8_vedro.visitors.context_checkers import ContextAssertChecker
from flake8_vedro.visitors.context_visitor import ContextVisitor


def test_function_def_without_assert_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f(): pass
    """
    assert_error(ContextVisitor, code, ContextWithoutAssert, context_name='f',
                 config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_without_decorator_and_assert_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    def f(): pass
    """
    assert_not_error(ContextVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_without_assert_when_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f(): pass
    """
    assert_not_error(ContextVisitor, code, config=DefaultConfig(is_context_assert_optional=True))


def test_function_def_without_assert_in_with_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f():
        with ():
            pass
    """
    assert_error(ContextVisitor, code, ContextWithoutAssert, context_name='f',
                 config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_without_assert_in_async_with_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f():
        async with ():
            pass
    """
    assert_error(ContextVisitor, code, ContextWithoutAssert, context_name='f',
                 config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_without_assert_in_double_nested_with_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f():
        with mock_1():
            with mock_2():
               pass
    """
    assert_error(ContextVisitor, code, ContextWithoutAssert, context_name='f',
                 config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_with_assert_in_double_nested_with_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f():
        with mock_1():
            with mock_2():
               assert True
    """
    assert_not_error(ContextVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_without_assert_in_with_when_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f():
        with ():
            pass
    """
    assert_not_error(ContextVisitor, code, config=DefaultConfig(is_context_assert_optional=True))


def test_function_def_assert_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f(): assert True
    """
    assert_not_error(ContextVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_function_def_assert_in_with_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    def f():
        with ():
            assert True
    """
    assert_not_error(ContextVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_without_assert_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    async def f(): pass
    """
    assert_error(ContextVisitor, code, ContextWithoutAssert, context_name='f',
                 config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_without_assert_in_with_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    async def f():
        with ():
            pass
    """
    assert_error(ContextVisitor, code, ContextWithoutAssert, context_name='f',
                 config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_assert_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    async def f(): assert True
    """
    assert_not_error(ContextVisitor, code, config=DefaultConfig(is_context_assert_optional=False))


def test_async_function_def_assert_in_with_when_not_optional():
    ContextVisitor.deregister_all()
    ContextVisitor.register_context_checker(ContextAssertChecker)
    code = """
    @vedro.context
    async def f():
        with ():
            assert True
    """
    assert_not_error(ContextVisitor, code, config=DefaultConfig(is_context_assert_optional=False))
