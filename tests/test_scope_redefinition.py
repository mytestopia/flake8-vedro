from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.config import DefaultConfig
from flake8_vedro.errors import ScopeVarIsRedefined
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import ScopeRedefinitionChecker


def test_without_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            var_1 = 1
            self.var_2 = 2
        def when(self):
            self.var_1 = "woo"
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


def test_assign_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = 1
            self.var_2 = 2
        def when(self):
            self.var_1 = "woo"
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsRedefined, name="var_1",
                 config=DefaultConfig())


def test_assign_redefinition_in_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def when(self):
            self.var_1 = 1
            self.var_1 = 2
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsRedefined, name="var_1",
                 config=DefaultConfig())


def test_assign_redefinition_with_func():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = 1
        def when(self):
            self.var_1 = func()
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsRedefined, name="var_1",
                 config=DefaultConfig())


def test_assign_redefinition_tuple_1():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = 1
        def when(self):
            self.var_1, self.var_2 = func()
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsRedefined, name="var_1",
                 config=DefaultConfig())


def test_assign_redefinition_tuple_2():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = 1
        def when(self):
            self.var_2, self.var_1 = func()
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsRedefined, name="var_1",
                 config=DefaultConfig())


def test_assign_redefinition_underscore():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = 1
        def when(self):
            _, self.var_1 = func()
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsRedefined, name="var_1",
                 config=DefaultConfig())


def test_with_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = 1
        def when(self):
            with mock() as self.var_1:
              pass
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsRedefined, name="var_1",
                 config=DefaultConfig())


def test_async_with_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = 1
        async def when(self):
            async with mock() as self.var_1:
              pass
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsRedefined, name="var_1",
                 config=DefaultConfig())


def test_double_with_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = 1
        async def when(self):
            with mock_1():
                with mock_2() as self.var_1:
                    pass
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsRedefined, name="var_1",
                 config=DefaultConfig())


def test_with_body_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = 1
        async def when(self):
            with mock_1():
                self.var_1 = 2
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsRedefined, name="var_1",
                 config=DefaultConfig())


def test_dict_partial_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = {"key": "value"}
        async def when(self):
            self.var_1["new_key"] = "new_value"
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


def test_dict_update_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = {"key": "value"}
        async def when(self):
            self.var_2.update({"key": "value"})
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


def test_allowed_assign_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.page = page()
        def when(self):
            self.page = change_page()
    """
    assert_not_error(ScenarioVisitor, code,
                     config=DefaultConfig(allowed_to_redefine_list=['page']))


def test_allowed_multiple_assign_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.page = page()
            self.var = 1
        def when(self):
            self.page = change_page()
            self.var = 2
    """
    assert_not_error(ScenarioVisitor, code,
                     config=DefaultConfig(allowed_to_redefine_list=['var', 'page']))


def test_not_allowed_assign_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopeRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var = func()
        def when(self):
            self.var = func()
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsRedefined, name='var',
                 config=DefaultConfig(allowed_to_redefine_list=['page']))
