import ast
from typing import List, Tuple

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import MockCallResultNotSavedAsVariable, MockHistoryNotAsserted
from flake8_vedro.types import StepType
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


def get_mock_context_managers_from_step(step: StepType) -> List[Tuple[ast.withitem, int, int]]:
    """Returns list of context managers that start with 'mock' and their positions (line and column offset)"""
    mock_context_managers: List[Tuple[ast.withitem, int, int]] = []
    for line in step.body:
        if isinstance(line, ast.With) or isinstance(line, ast.AsyncWith):
            for item in line.items:
                if isinstance(item.context_expr, ast.Call) and item.context_expr.func.id.startswith('mock'):
                    mock_context_managers.append((item, line.lineno, line.col_offset))

    return mock_context_managers


def is_mock_assert_found_in_step(step: StepType, mock_var: ast.Attribute) -> bool:
    """Searches for mock assert in step and returns result as bool"""
    is_mock_assert_found = False
    for line in step.body:
        if isinstance(line, ast.Assert):
            for node in ast.walk(line.test):
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                    if node.value.id == mock_var.value.id and node.attr == mock_var.attr:
                        is_mock_assert_found = True
                        print(ast.dump(node))
    return is_mock_assert_found


@ScenarioVisitor.register_steps_checker
class MockedRequestsChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []
        when_steps = self.get_when_steps(context.steps)
        then_and_but_steps = self.get_then_and_but_steps(context.steps)
        if not when_steps or not then_and_but_steps:
            return []

        mock_context_managers = get_mock_context_managers_from_step(when_steps[0])
        for context_manager, lineno, col_offset in mock_context_managers:
            mock_func_name = context_manager.context_expr.func.id
            mock_var = context_manager.optional_vars
            if not isinstance(mock_var, ast.Attribute):
                errors.append(MockCallResultNotSavedAsVariable(lineno, col_offset, mock_func_name=mock_func_name))
            else:
                is_mock_assert_found = False
                for step in then_and_but_steps:
                    if is_mock_assert_found := is_mock_assert_found_in_step(step, mock_var):
                        break
                if not is_mock_assert_found:
                    mock_var_name = '{}.{}'.format(mock_var.value.id, mock_var.attr)
                    errors.append(MockHistoryNotAsserted(lineno, col_offset, mock_var_name=mock_var_name))

        return errors
