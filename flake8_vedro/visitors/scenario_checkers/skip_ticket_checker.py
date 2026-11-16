import ast
from typing import List, Optional

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ScenarioChecker
from flake8_vedro.errors import SkipReasonTicketMissing
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_scenario_checker
class SkipTicketChecker(ScenarioChecker):

    @staticmethod
    def _is_skip_decorator(decorator: ast.expr, context: Context) -> bool:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == 'vedro'
            and target.attr == 'skip'
        ):
            return True

        if not isinstance(target, ast.Name):
            return False

        return any(
            import_from.module == 'vedro'
            and any(
                alias.name == 'skip'
                and (alias.asname or alias.name) == target.id
                for alias in import_from.names
            )
            for import_from in context.import_from_nodes
        )

    @staticmethod
    def _get_reason(decorator: ast.expr) -> Optional[str]:
        if not isinstance(decorator, ast.Call):
            return ''

        reason = decorator.args[0] if decorator.args else None
        if reason is None:
            reason = next(
                (keyword.value for keyword in decorator.keywords if keyword.arg == 'reason'),
                None,
            )
        if reason is None or (isinstance(reason, ast.Constant) and reason.value is None):
            return ''
        if isinstance(reason, ast.Constant) and isinstance(reason.value, str):
            return reason.value

        # dynamic reason cannot be checked statically
        return None

    def check_scenario(self, context: Context, config) -> List[Error]:
        if not config.require_skip_ticket:
            return []

        errors = []
        for decorator in context.scenario_node.decorator_list:
            if not self._is_skip_decorator(decorator, context):
                continue

            reason = self._get_reason(decorator)
            if reason is None or config.skip_ticket_pattern.search(reason):
                continue

            errors.append(SkipReasonTicketMissing(decorator.lineno, decorator.col_offset))
        return errors
