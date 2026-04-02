from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.errors import StepHasBranching
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
