from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.errors import ScopeVarIsPartiallyRedefined
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import (
    ScopePartialRedefinitionChecker
)


def test_full_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopePartialRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = 1
        def when(self):
            self.var_1 = "woo"
    """
    assert_not_error(ScenarioVisitor, code)


def test_dict_no_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopePartialRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = {"key": "value"}
        async def when(self):
            pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_dict_partial_redefinition():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopePartialRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = {"key": "value"}
        async def when(self):
            self.var_1["new_key"] = "new_value"
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsPartiallyRedefined, name="var_1")


def test_dict_partial_redefinition_2():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopePartialRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = {"key": {"internal_key": "value"}}
        async def when(self):
            self.var_1["key"]["internal_key"] = "new_value"
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsPartiallyRedefined, name="var_1")


def test_dict_partial_redefinition_no_scope():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopePartialRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        async def when(self):
            var_1 = {"key": "value"}
            var_1["new_key"] = "new_value"
    """
    assert_not_error(ScenarioVisitor, code)
