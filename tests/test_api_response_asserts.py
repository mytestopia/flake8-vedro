from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.config import DefaultConfig
from flake8_vedro.errors import ApiResponseStatusNotAsserted
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import ApiResponseAssertsChecker


def test_status_code_asserted():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.response = ChatApi().get_user()

        def then_it_should_return_success_status_code(self):
            assert self.response.status_code == 200

        def and_it_should_return_user(self):
            assert self.response.json() == {"id": 123}
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_status_code_not_asserted():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.response = ChatApi().get_user()

        def then_it_should_return_user(self):
            assert self.response.json() == {"id": 123}
    """
    assert_error(ScenarioVisitor, code, ApiResponseStatusNotAsserted, name="self.response",
                 config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_status_code_not_asserted_for_local_variable():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            response = ChatApi().get_user()

        def then_it_should_return_user(self):
            assert response.json() == {"id": 123}
    """
    assert_error(ScenarioVisitor, code, ApiResponseStatusNotAsserted, name="response",
                 config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_status_code_not_asserted_for_annotated_assignment():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.response: Response = ChatApi().get_user()

        def then_it_should_return_user(self):
            assert self.response.json() == {"id": 123}
    """
    assert_error(ScenarioVisitor, code, ApiResponseStatusNotAsserted, name="self.response",
                 config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_status_code_not_asserted_for_named_expression():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            log(response := ChatApi().get_user())

        def then_it_should_return_user(self):
            assert response.json() == {"id": 123}
    """
    assert_error(ScenarioVisitor, code, ApiResponseStatusNotAsserted, name="response",
                 config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_status_code_not_asserted_for_awaited_response():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        async def when_user_requests(self):
            self.response = await ChatApi().get_user()

        def then_it_should_return_user(self):
            assert self.response.json() == {"id": 123}
    """
    assert_error(ScenarioVisitor, code, ApiResponseStatusNotAsserted, name="self.response",
                 config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_status_code_not_asserted_for_aliased_interface():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi as Api

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.response = Api().get_user()

        def then_it_should_return_user(self):
            assert self.response.json() == {"id": 123}
    """
    assert_error(ScenarioVisitor, code, ApiResponseStatusNotAsserted, name="self.response",
                 config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_status_code_not_asserted_for_one_of_responses():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.first_response = ChatApi().get_user()
            self.second_response = ChatApi().get_user()

        def then_it_should_return_success_status_code(self):
            assert self.first_response.status_code == 200
    """
    assert_error(ScenarioVisitor, code, ApiResponseStatusNotAsserted, name="self.second_response",
                 config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_status_code_wrapped_in_call():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.response = ChatApi().get_user()

        def then_it_should_return_success_status_code(self):
            assert str(self.response.status_code) == "200"
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_status_code_compared_without_assert():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.response = ChatApi().get_user()

        def then_it_should_return_success_status_code(self):
            self.response.status_code == 200

        def and_it_should_return_user(self):
            assert self.response.json() == {"id": 123}
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_response_checked_by_helper():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.response = ChatApi().get_user()

        def then_it_should_return_user(self):
            assert self.response.json() == {"id": 123}
            self.check_response()
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_response_passed_to_function():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.response = ChatApi().get_user()

        def then_it_should_return_user(self):
            assert self.response.json() == {"id": 123}
            response_is_valid(self.response)
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_response_derived_value():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.user = ChatApi().get_user().json()

        def then_it_should_return_user(self):
            assert self.user == {"id": 123}
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_response_not_saved():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            ChatApi().get_user()

        def then_it_should_return_user(self):
            assert self.user == {"id": 123}
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_response_in_lambda():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.request = lambda: ChatApi().get_user()

        def then_it_should_return_user(self):
            assert self.request is not None
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_steps_without_asserts():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.response = ChatApi().get_user()

        def then_it_should_return_user(self):
            pass
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_interface_not_in_api_interfaces_list():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.kafka_api import KafkaApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.response = KafkaApi().get_user()

        def then_it_should_return_user(self):
            assert self.response.json() == {"id": 123}
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(api_interfaces_list=['ChatApi']))


def test_rule_is_disabled_by_default():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ApiResponseAssertsChecker)
    code = """
    from interfaces.chat_api import ChatApi

    class Scenario(vedro.Scenario):
        def when_user_requests(self):
            self.response = ChatApi().get_user()

        def then_it_should_return_user(self):
            assert self.response.json() == {"id": 123}
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())
