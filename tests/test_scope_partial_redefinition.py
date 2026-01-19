from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.config import DefaultConfig
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
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


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
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


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
    assert_error(ScenarioVisitor, code, ScopeVarIsPartiallyRedefined,
                 config=DefaultConfig(),
                 name="var_1")


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
    assert_error(ScenarioVisitor, code, ScopeVarIsPartiallyRedefined,
                 config=DefaultConfig(),
                 name="var_1")


def test_dict_partial_redefinition_no_scope():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopePartialRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        async def when(self):
            var_1 = {"key": "value"}
            var_1["new_key"] = "new_value"
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


def test_dict_allowed_partial_redefinition_in_one_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopePartialRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = {"key": "value"}
            self.var_1["new_key"] = "new_value"
    """
    assert_not_error(ScenarioVisitor, code,
                     config=DefaultConfig(allow_partial_redefinitions_in_one_step=True))


def test_dict_not_allowed_partial_redefinition_in_one_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopePartialRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = {"key": "value"}
            self.var_1["new_key"] = "new_value"
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsPartiallyRedefined,
                 config=DefaultConfig(allow_partial_redefinitions_in_one_step=False),
                 name="var_1")


def test_dict_allowed_partial_redefinition_in_different_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopePartialRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1 = {"key": "value"}

        def another_given(self):
            self.var_1["new_key"] = "new_value"
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsPartiallyRedefined,
                 config=DefaultConfig(allow_partial_redefinitions_in_one_step=True),
                 name="var_1")


def test_dict_allowed_partial_redefinition_in_one_step_tuple():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopePartialRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.var_1, self.var_2 = {"key1": "value1"}, {"key2": "value2"}
            self.var_2["key_2"] = "new_value"
    """
    assert_not_error(ScenarioVisitor, code,
                     config=DefaultConfig(allow_partial_redefinitions_in_one_step=True))


def test_saving_partial_dict_to_self():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScopePartialRedefinitionChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given1(self):
            self.message = {'payload': {'id': '12345'}}
            self.message['payload'] = {'id': '1'}

        def given2(self):
            id = self.message['payload']['id']
    """
    assert_not_error(ScenarioVisitor, code,
                     config=DefaultConfig(allow_partial_redefinitions_in_one_step=True))
