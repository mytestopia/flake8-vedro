import ast
from typing import List, Tuple

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import MockCallResultNotSavedAsSelfAttribute, MockCallResultNotAsserted
from flake8_vedro.types import FuncType
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class MockAssertChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        if config.is_mock_assert_optional:
            return []

        errors = []
        when_steps = self.get_when_steps(context.steps)
        then_and_but_steps = self.get_then_and_but_steps(context.steps)
        if not when_steps or not then_and_but_steps:
            return []

        mock_context_managers = _get_mock_context_managers_from_step(when_steps[0])
        for context_manager, lineno, col_offset in mock_context_managers:
            mock_func_name = context_manager.context_expr.func.id
            mock_var = context_manager.optional_vars
            if not _is_self_attribute(mock_var):
                errors.append(MockCallResultNotSavedAsSelfAttribute(lineno, col_offset, mock_func_name=mock_func_name))
                continue

            if not _is_self_attribute_assert_found_in_steps(then_and_but_steps, mock_var):
                mock_var_name = '{}.{}'.format(mock_var.value.id, mock_var.attr)
                errors.append(MockCallResultNotAsserted(lineno, col_offset, mock_var_name=mock_var_name))

        return errors


def _get_mock_context_managers_from_step(step: FuncType) -> List[Tuple[ast.withitem, int, int]]:
    """Returns list of context managers that start with 'mock' and their positions (line and column offset)."""
    mock_context_managers: List[Tuple[ast.withitem, int, int]] = []

    for statement in step.body:
        if isinstance(statement, (ast.With, ast.AsyncWith)):
            for item in statement.items:
                if (
                    isinstance(item.context_expr, ast.Call) and
                    isinstance(item.context_expr.func, ast.Name) and
                    item.context_expr.func.id.startswith("mock")
                ):
                    mock_context_managers.append((item, statement.lineno, statement.col_offset))

    return mock_context_managers


def _is_self_attribute(node: ast.expr) -> bool:
    """Checks if node is a 'self' attribute (e.g., self.offers_mock) and returns result as bool"""
    if (
            isinstance(node, ast.Attribute) and
            isinstance(node.value, ast.Name) and
            node.value.id == 'self'
    ):
        return True
    return False


def _is_self_attribute_assert_found_in_steps(steps: List[FuncType], self_attribute: ast.Attribute) -> bool:
    """Searches for self_attribute (e.g., self.offers_mock) assert in steps and returns result as bool."""
    if not _is_self_attribute(self_attribute):
        raise ValueError('Parameter "self_attribute" expects a "self" attribute (e.g., self.attribute_name)')

    for step in steps:
        for statement in step.body:
            for statement_node in ast.walk(statement):
                if isinstance(statement_node, ast.Assert):
                    for assert_node in ast.walk(statement_node.test):
                        if (
                                isinstance(assert_node, ast.Attribute) and
                                isinstance(assert_node.value, ast.Name) and
                                assert_node.value.id == self_attribute.value.id and
                                assert_node.attr == self_attribute.attr
                        ):
                            return True
    return False
