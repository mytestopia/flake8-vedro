from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.errors import (
    SubjectDuplicated,
    SubjectEmpty,
    SubjectNotFound
)
from flake8_vedro.visitors import ScenarioVisitor
from flake8_vedro.visitors.scenario_checkers import (
    SingleSubjectChecker,
    SubjectEmptyChecker
)


def test_vedro_scenario_correct_subject():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SubjectEmptyChecker)
    ScenarioVisitor.register_scenario_checker(SingleSubjectChecker)
    code = """
    class Scenario:
        subject = 'any string'
        def when(): pass
        def then(): assert True
    """
    assert_not_error(ScenarioVisitor, code)


def test_vedro_scenario_empty_subject():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SubjectEmptyChecker)
    code = """
    class Scenario:
        subject = ''
        def when(): pass
    """
    assert_error(ScenarioVisitor, code, SubjectEmpty)


def test_vedro_scenario_no_subject():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SingleSubjectChecker)
    ScenarioVisitor.register_scenario_checker(SubjectEmptyChecker)
    code = """
        class Scenario:
            def when(): pass
    """
    assert_error(ScenarioVisitor, code, SubjectNotFound)


def test_vedro_scenario_subject_duplicate():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SingleSubjectChecker)
    code = """
    class Scenario:
        subject = 'string'
        subject = 'another string'
        def when(): pass
    """
    assert_error(ScenarioVisitor, code, SubjectDuplicated)
