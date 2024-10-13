from flake8_plugin_utils import assert_not_error

from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import MockedRequestsChecker


def test_mocked_request_check():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(MockedRequestsChecker)
    code = """
        class Scenario(vedro.Scenario):
            def given(self):
                self.var_1 = 1
            def when(self):
                async with mocked_hotel(), x, b(), mocked_offers_error(), mocked_destinations, mocked_favorites() as a:
                    self.page.button.tap()
            def then_booking_request_was_sent_with_correct_params(self):
                pass
        """
    assert_not_error(ScenarioVisitor, code)
