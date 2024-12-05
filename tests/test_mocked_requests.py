from flake8_plugin_utils import assert_not_error

from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import MockAssertChecker


def test_mocked_request_check():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(MockAssertChecker)
    code = """
        class Scenario(vedro.Scenario):
            def given(self):
                self.var_1 = 1
            def when(self):
                async with x as self.x, b() as t, mocked_hotel() as self.f, mocked_city:
                    self.page.button.tap()
            def then_booking_request_was_sent_with_correct_params(self):
                pass
            def and_booking_request_was_sent_with_correct_params(self):
                for i in range(2):
                    assert len(self.f)
            def but_booking_request_was_sent_with_correct_params(self):
                pass
        """
    assert_not_error(ScenarioVisitor, code)
