from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.config import DefaultConfig
from flake8_vedro.errors import ScopeVarIsNotUsed
from flake8_vedro.visitors import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers.unused_scope_checker import UnusedScopeVariablesChecker


def test_not_allowed_unused_variable_in_given_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"

        def given(self):
            self.variable = 1
            self.unused_variable = 2

        def when(self):
            Api().method(self.variable)
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsNotUsed, name="unused_variable", config=DefaultConfig())


def test_not_allowed_unused_variable_in_then_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"

        def given(self):
            self.variable = 1

        def when(self):
            Api().method(self.variable)

        def then(self):
            self.unused_variable = 2
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsNotUsed, name="unused_variable", config=DefaultConfig())


def test_not_allowed_unused_variable_in_when_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"

        def given(self):
            self.variable = 1

        def when(self):
            self.unused_variable = Api().method(self.variable)
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsNotUsed, name="unused_variable", config=DefaultConfig())


def test_allowed_unused_with_attribute_by_default():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"

        def given(self):
            self.variable = 1

        def when(self):
            with context() as self.unused_variable:
                 Api().method(self.variable)
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


def test_not_allowed_unused_with_attribute_setting():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"

        def given(self):
            self.variable = 1

        def when(self):
            with context() as self.unused_variable:
                 Api().method(self.variable)
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsNotUsed, name="unused_variable",
                 config=DefaultConfig(allow_unused_with_block_attributes=False))


def test_not_allowed_unused_packed_with_attribute_setting():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"

        def when(self):
            with context() as (self.variable, self.unused_variable):
                 Api().method(self.variable)
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsNotUsed, name="unused_variable",
                 config=DefaultConfig(allow_unused_with_block_attributes=False))


def test_not_allowed_unused_with_attribute_for_few_contexts_setting():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"

        def when(self):
            with (
                first_context() as self.variable,
                second_context() as self.unused_variable,
            ):
                 Api().method(self.variable)
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsNotUsed, name="unused_variable",
                 config=DefaultConfig(allow_unused_with_block_attributes=False))


def test_allowed_unused_underscored_variable():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"

        def given(self):
            self.variable = 1
            self._unused_variable = 2

        def when(self):
            Api().method(self.variable)
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


def test_allowed_variable_defined_outside():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"

        def given(self):
            context()
            self.variable = self.context_variable + 1

        def when(self):
            Api().method(self.variable)
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


def test_allowed_use_variable_attributes():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"

        def given(self):
            self.variable = context()

        def given_2(self):
            self.variable_2 = self.variable.method()

        def when(self):
            Api().method(self.variable_2)
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


def test_allowed_empty_scenario():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


def test_allowed_used_init_variables():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "{subject}"

        def __init__(self, subject):
            self.subject = subject
            self.variable = 1

        def when(self):
            Api().method(self.variable)
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


def test_not_allowed_unused_init_variables():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "some subject"

        def __init__(self, subject):
            self.unused_subject = subject
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsNotUsed, name="unused_subject",
                 config=DefaultConfig(allow_unused_with_block_attributes=False))


def test_not_allowed_unused_unpacked_variable():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(UnusedScopeVariablesChecker)
    code = """
    class Scenario(vedro.Scenario):
        subject = "subject"

        def given(self):
            self.variable, self.unused_variable = context()

        def when(self):
            Api().method(self.variable)
    """
    assert_error(ScenarioVisitor, code, ScopeVarIsNotUsed, name="unused_variable", config=DefaultConfig())
