import pytest
from flake8_plugin_utils import assert_error, assert_not_error

from flake8_vedro.config import DefaultConfig
from flake8_vedro.errors import SkipReasonTicketMissing
from flake8_vedro.plugins import VedroScenarioStylePlugin
from flake8_vedro.visitors.scenario_checkers import SkipTicketChecker
from flake8_vedro.visitors.scenario_visitor import ScenarioVisitor


def test_bare_vedro_skip():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    @vedro.skip
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_error(ScenarioVisitor, code, SkipReasonTicketMissing,
                 config=DefaultConfig(require_skip_ticket=True))


def test_bare_skip_imported_from_vedro():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    from vedro import skip

    @skip
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_error(ScenarioVisitor, code, SkipReasonTicketMissing,
                 config=DefaultConfig(require_skip_ticket=True))


def test_vedro_skip_without_reason():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    @vedro.skip()
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_error(ScenarioVisitor, code, SkipReasonTicketMissing,
                 config=DefaultConfig(require_skip_ticket=True))


def test_vedro_skip_with_none_reason():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    @vedro.skip(reason=None)
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_error(ScenarioVisitor, code, SkipReasonTicketMissing,
                 config=DefaultConfig(require_skip_ticket=True))


def test_vedro_skip_with_empty_reason():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    @vedro.skip("")
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_error(ScenarioVisitor, code, SkipReasonTicketMissing,
                 config=DefaultConfig(require_skip_ticket=True))


def test_aliased_skip_with_reason_without_ticket():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    from vedro import skip as skip_scenario

    @skip_scenario(reason="temporarily disabled")
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_error(ScenarioVisitor, code, SkipReasonTicketMissing,
                 config=DefaultConfig(require_skip_ticket=True))


def test_reason_with_ticket_prefix_only():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    @vedro.skip("CHAT-")
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_error(ScenarioVisitor, code, SkipReasonTicketMissing,
                 config=DefaultConfig(require_skip_ticket=True))


def test_ticket_in_positional_reason():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    @vedro.skip("temporarily disabled: CHAT-123")
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(require_skip_ticket=True))


def test_ticket_in_keyword_reason():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    from vedro import skip

    @skip(reason="CHAT-123: waiting for fix")
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(require_skip_ticket=True))


def test_dynamic_reason():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    @vedro.skip(reason=SKIP_REASON)
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(require_skip_ticket=True))


def test_skip_not_from_vedro():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    from other import skip

    @skip
    @pytest.skip("no ticket")
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig(require_skip_ticket=True))


def test_custom_ticket_pattern():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    @vedro.skip("#123")
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_not_error(
        ScenarioVisitor, code,
        config=DefaultConfig(
            require_skip_ticket=True,
            skip_ticket_pattern=VedroScenarioStylePlugin.parse_skip_ticket_pattern(r'#\d+')
        )
    )


def test_custom_ticket_pattern_does_not_match():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    @vedro.skip("CHAT-123")
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_error(
        ScenarioVisitor, code, SkipReasonTicketMissing,
        config=DefaultConfig(
            require_skip_ticket=True,
            skip_ticket_pattern=VedroScenarioStylePlugin.parse_skip_ticket_pattern(r'#\d+')
        )
    )


def test_rule_is_disabled_by_default():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(SkipTicketChecker)
    code = """
    @vedro.skip
    class Scenario(vedro.Scenario):
        subject = "subject"
    """
    assert_not_error(ScenarioVisitor, code, config=DefaultConfig())


def test_invalid_ticket_pattern():
    with pytest.raises(ValueError, match='--skip-ticket-pattern'):
        VedroScenarioStylePlugin.parse_skip_ticket_pattern('[')
