from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.errors import StepsWrongOrder
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import OrderChecker


def test_scenario_no_given():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(OrderChecker)
    code = """
    class Scenario:
        def when(): pass
        def then(): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_no_given_with_init():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(OrderChecker)
    code = """
    class Scenario:
        def __init__(self): pass
        def when(): pass
        def then(): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_no_init():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(OrderChecker)
    code = """
    class Scenario:
        def given(): pass
        def when(): pass
        def then(): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_several_given():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(OrderChecker)
    code = """
    class Scenario:
        def given(): pass
        def given_another(): pass
        def when(): pass
        def then(): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_then_before_when():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(OrderChecker)
    code = """
    class Scenario:
        def then(): pass
        def when(): pass
    """
    assert_error(ScenarioVisitor, code, StepsWrongOrder,
                 previous_step='then', current_step='when')


def test_scenario_given_after_when():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(OrderChecker)
    code = """
    class Scenario:
        def when(): pass
        def given(): pass
        def then(): pass
    """
    assert_error(ScenarioVisitor, code, StepsWrongOrder,
                 previous_step='when', current_step='given')


def test_scenario_and_before_then():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(OrderChecker)
    code = """
    class Scenario:
        def when(): pass
        def and_(): pass
        def then(): pass
    """
    assert_error(ScenarioVisitor, code, StepsWrongOrder,
                 previous_step='and_', current_step='then')


def test_scenario_several_and():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(OrderChecker)
    code = """
    class Scenario:
        def when(): pass
        def then_(): pass
        def and_(): pass
        def and_another(): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_but_after_and():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(OrderChecker)
    code = """
    class Scenario:
        def when(): pass
        def then_(): pass
        def and_(): pass
        def but(): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_but_before_and():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(OrderChecker)
    code = """
    class Scenario:
        def when(): pass
        def then_(): pass
        def and_(): pass
        def but(): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_invalid_step_name():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(OrderChecker)
    code = """
    class Scenario:
        def no_events(): pass
        def when(): pass
        def no_events_again(): pass
        def then(): pass
    """
    assert_not_error(ScenarioVisitor, code)
