from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.errors import ContextCallInParams
from flake8_vedro.visitors import ScenarioVisitor
from flake8_vedro.visitors.scenario_checkers import ParametrizationCallChecker


def test_call_func_in_params():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationCallChecker)
    code = """
    class Scenario:
        subject = 'any subject'
        @params(foo())
        def __init__(foo): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_context_call_func_in_params():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationCallChecker)
    code = """
    from contexts import foo
    class Scenario:
        subject = 'any subject'
        @params(foo())
        def __init__(foo): pass
    """
    assert_error(ScenarioVisitor, code, ContextCallInParams)


def test_context_call_lambda_in_params():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationCallChecker)
    code = """
    from contexts import foo
    class Scenario:
        subject = 'any subject'
        @params(lambda: foo)
        def __init__(foo): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_constant_in_params():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationCallChecker)
    code = """
    class Scenario:
        subject = 'any subject'
        @params(1)
        def __init__(foo): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_schema_attribute_in_params():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationCallChecker)
    code = """
    class Scenario:
        subject = 'any subject'
        @params(schema.str)
        def __init__(foo): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_schema_call_in_params():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(ParametrizationCallChecker)
    code = """
    from d42 import schema
    class Scenario:
        subject = 'any subject'
        @params(schema.int.min(1))
        def __init__(foo): pass
    """
    assert_not_error(ScenarioVisitor, code)
