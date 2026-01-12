from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.config import DefaultConfig
from flake8_vedro.errors import ImportedInterfaceInWrongStep
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor
from flake8_vedro.visitors.steps_checkers import InterfacesUsageChecker


def test_interface_imported_from_submodule():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.api import API
    class Scenario:
        def given(): API().get()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='API')


def test_interface_imported_from_module():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces import API

    class Scenario:
        def given(): API().get()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='API')


def test_interface_imported_from_module_no_init():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces import API

    class Scenario:
        def given(): API.get()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='API')


def test_interface_called_as_assign():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces import API

    class Scenario:
        def given(): response = API()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='API')


def test_interface_as_function():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces import get

    class Scenario:
        def given(): get()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='get')


def test_interface_method_in_when():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.api import API
    from contexts import added

    class Scenario:
        def given(): added()
        def when(): API().get()
    """
    assert_not_error(ScenarioVisitor, code,
                     config=DefaultConfig())


def test_interface_method_in_then():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.api import API
    from contexts import added

    class Scenario:
        subject = 'string'
        def given(): added()
        def when(): pass
        def then():
            assert foo == var
            API()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='API')


def test_interface_method_in_and():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.api import API

    class Scenario:
        def when(): pass
        def then(): assert foo == var
        def and_():
            assert foo == var
            API()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='API')


def test_interface_method_in_but():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.api import API

    class Scenario:
        def when(): pass
        def then(): assert foo == var
        def and_(): assert foo == var
        def but():
            assert foo == var
            API()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='API')


def test_call_self_method():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.api import API

    class Scenario:
        def given(): self.photo = self.photo_method()
        def when(): pass
        def then(): assert foo == var
    """
    assert_not_error(ScenarioVisitor, code,
                     config=DefaultConfig())


def test_call_async_method():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces import get

    class Scenario:
        def given(): await get()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='get')


def test_call_async_class_method():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.api import API

    class Scenario:
        def given(): await API.get()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='API')


def test_schema():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    class Scenario:
        def given(): pass
        def when(): pass
        def then(): assert foo == schema.array.len(1)
    """
    assert_not_error(ScenarioVisitor, code,
                     config=DefaultConfig())


def test_call_interface_inside_nested_with():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.api import API

    class Scenario:
        def given():
            with mock_1():
                with mock_2():
                    API()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='API')


def test_call_interface_inside_with_async():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.api import API

    class Scenario:
        def given():
            async with mock_1():
                with mock_2():
                    API()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='API')


def test_call_interface_inside_with():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.api import API

    class Scenario:
        def given():
            with (mock_1(), mock_2()):
                API()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(),
                 func_name='API')


def test_interface_imported_allowed():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.kafka import KafkaApi
    class Scenario:
        def given(): KafkaApi().count()
    """
    assert_not_error(ScenarioVisitor, code,
                     config=DefaultConfig(allowed_interfaces_list=['KafkaApi']))


def test_interface_imported_allowed_and_not_allowed():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(InterfacesUsageChecker)
    code = """
    from interfaces.kafka import KafkaApi
    from interfaces.app import AppApi
    class Scenario:
        def given():
            KafkaApi.get()
            AppApi().get()
    """
    assert_error(ScenarioVisitor, code, ImportedInterfaceInWrongStep,
                 config=DefaultConfig(allowed_interfaces_list=['KafkaApi']),
                 func_name='AppApi')
