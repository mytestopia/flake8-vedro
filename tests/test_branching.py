from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.config import DefaultConfig
from flake8_vedro.errors import StepHasBranching
from flake8_vedro.plugins import VedroScenarioStylePlugin
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import BranchingChecker


def test_step_with_if():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def when(self):
            self.response = Api().method()

        def then(self):
            if self.response.status_code == 200:
                assert True
    """
    assert_error(ScenarioVisitor, code, StepHasBranching, step_name="then")


def test_step_with_if_else():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def when(self):
            if something:
                self.response = Api().method1()
            else:
                self.response = Api().method2()
    """
    assert_error(ScenarioVisitor, code, StepHasBranching, step_name="when")


def test_step_with_elif():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            if a:
                self.x = 1
            elif b:
                self.x = 2
    """
    assert_error(ScenarioVisitor, code, StepHasBranching, step_name="given")


def test_step_with_ternary():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.value = 1 if condition else 2
    """
    assert_error(ScenarioVisitor, code, StepHasBranching, step_name="given")


def test_step_with_match_case():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def then(self):
            match self.response.status_code:
                case 200:
                    assert True
                case _:
                    assert False
    """
    assert_error(ScenarioVisitor, code, StepHasBranching, step_name="then")


def test_step_with_list_comprehension():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given_list_comprehension(self):
            self.something = [item for item in something() if item is not None]
    """
    assert_not_error(ScenarioVisitor, code)


def test_step_without_branching():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            self.users = [user() for _ in range(5)]

        def when(self):
            with interface():
                self.response = Api().method(self.users)

        def then(self):
            assert self.response.status_code == 200
    """
    assert_not_error(ScenarioVisitor, code)


def test_nested_if():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def when(self):
            with mock() as self.history:
                if self.history:
                    process(self.history)
    """
    assert_error(ScenarioVisitor, code, StepHasBranching, step_name="when")


def test_async_step_with_branching():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        async def when(self):
            if condition:
                self.response = await Api().method()
    """
    assert_error(ScenarioVisitor, code, StepHasBranching, step_name="when")


def test_async_step_without_branching():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        async def when(self):
            self.response = await Api().method()
    """
    assert_not_error(ScenarioVisitor, code)


def test_with_branching_outside_of_scenario():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    if something:
        do_something()
        
    class Scenario(vedro.Scenario):
        def when(self):
            self.response = await Api().method()
    """
    assert_not_error(ScenarioVisitor, code)


def test_allow_ifs_in_given_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            if condition:
                self.x = 1
    """
    assert_not_error(
        ScenarioVisitor, code, 
        config=DefaultConfig(allow_ifs_in_steps=VedroScenarioStylePlugin.parse_allow_ifs_in_steps('given'))
    )


def test_allow_ifs_in_given_still_errors_in_when():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def when(self):
            if condition:
                self.response = Api().method()
    """
    assert_error(ScenarioVisitor, code, StepHasBranching,
                 config=DefaultConfig(allow_ifs_in_steps=VedroScenarioStylePlugin.parse_allow_ifs_in_steps('given')),
                 step_name="when")


def test_allow_ifs_in_when_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def when(self):
            if condition:
                self.response = Api().method()
    """
    assert_not_error(
        ScenarioVisitor, code, 
        config=DefaultConfig(allow_ifs_in_steps=VedroScenarioStylePlugin.parse_allow_ifs_in_steps('when'))
    )


def test_allow_ifs_in_then_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def then(self):
            if self.response.status_code == 200:
                assert True
    """
    assert_not_error(
        ScenarioVisitor, code,
        config=DefaultConfig(allow_ifs_in_steps=VedroScenarioStylePlugin.parse_allow_ifs_in_steps('then'))
    )


def test_allow_ifs_in_then_also_allows_and_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def and_check(self):
            if condition:
                assert True
    """
    assert_not_error(
        ScenarioVisitor, code,
        config=DefaultConfig(allow_ifs_in_steps=VedroScenarioStylePlugin.parse_allow_ifs_in_steps('then'))
    )


def test_allow_ifs_in_then_also_allows_but_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def but_check(self):
            if condition:
                assert True
    """
    assert_not_error(
        ScenarioVisitor, code,
        config=DefaultConfig(allow_ifs_in_steps=VedroScenarioStylePlugin.parse_allow_ifs_in_steps('then'))
    )


def test_allow_ifs_in_init_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def __init__(self):
            if condition:
                self.x = 1
    """
    assert_not_error(
        ScenarioVisitor, code,
        config=DefaultConfig(allow_ifs_in_steps=VedroScenarioStylePlugin.parse_allow_ifs_in_steps('init'))
    )


def test_allow_ifs_in_multiple_steps():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            if a:
                self.x = 1

        def when(self):
            if b:
                self.response = Api().method()

        def then(self):
            if self.response.status_code == 200:
                assert True
    """
    assert_not_error(
        ScenarioVisitor, code,
        config=DefaultConfig(allow_ifs_in_steps=VedroScenarioStylePlugin.parse_allow_ifs_in_steps('given,when,then'))
    )


def test_allow_ifs_in_multiple_steps_still_errors_in_others():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given(self):
            if a:
                self.x = 1

        def then(self):
            if self.response.status_code == 200:
                assert True
    """
    assert_error(ScenarioVisitor, code, StepHasBranching,
                 config=DefaultConfig(allow_ifs_in_steps=VedroScenarioStylePlugin.parse_allow_ifs_in_steps('then')),
                 step_name="given")


def test_allow_ifs_empty_list_forbids_all():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def when(self):
            if condition:
                self.response = Api().method()
    """
    assert_error(ScenarioVisitor, code, StepHasBranching,
                 config=DefaultConfig(allow_ifs_in_steps=tuple()),
                 step_name="when")


def test_allow_ifs_in_given_with_named_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(BranchingChecker)
    code = """
    class Scenario(vedro.Scenario):
        def given_user(self):
            if condition:
                self.user = User()
    """
    assert_not_error(
        ScenarioVisitor, code,
        config=DefaultConfig(allow_ifs_in_steps=VedroScenarioStylePlugin.parse_allow_ifs_in_steps('given'))
    )
