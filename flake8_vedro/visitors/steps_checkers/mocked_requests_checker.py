import ast
from typing import List, Tuple

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import MockCallResultNotSavedAsVariable, MockHistoryNotAsserted
from flake8_vedro.types import StepType
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


def get_mock_context_managers(step: StepType) -> List[Tuple[ast.withitem, int, int]]:
    """Returns list of context managers that start with 'mock' and their positions (line and column offset)"""
    mock_context_managers: List[Tuple[ast.withitem, int, int]] = []
    for line in step.body:
        if isinstance(line, ast.With) or isinstance(line, ast.AsyncWith):
            for item in line.items:
                if isinstance(item.context_expr, ast.Call) and item.context_expr.func.id.startswith('mock'):
                    mock_context_managers.append((item, line.lineno, line.col_offset))

    return mock_context_managers


@ScenarioVisitor.register_steps_checker
class MockedRequestsChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []
        when_steps = self.get_when_steps(context.steps)

        mock_context_managers = []
        for step in when_steps:
            mock_context_managers = get_mock_context_managers(step)
            for context_manager, lineno, col_offset in mock_context_managers:
                if context_manager.optional_vars is None:
                    errors.append(MockCallResultNotSavedAsVariable(lineno, col_offset,
                                                                   mock_name=context_manager.context_expr.func.id))

        for context_manager, lineno, col_offset in mock_context_managers:
            if isinstance(context_manager.optional_vars, ast.Attribute):
                print(f'Context manager {context_manager.context_expr.func.id} has '
                      f'{context_manager.optional_vars.value.id}.{context_manager.optional_vars.attr} var')
                mock_assert_found = False
                for step in context.steps:
                    if step.name.startswith('then') or step.name.startswith('and') or step.name.startswith('but'):
                        for line in step.body:
                            if isinstance(line, ast.Assert) and isinstance(line.test, ast.Compare):
                                if isinstance(line.test.left, ast.Attribute) and \
                                        isinstance(line.test.left.value, ast.Attribute):
                                    if line.test.left.value.value.id == context_manager.optional_vars.value.id and \
                                            line.test.left.value.attr == context_manager.optional_vars.attr and \
                                            line.test.left.attr == 'history':
                                        mock_assert_found = True
                if not mock_assert_found:
                    errors.append(MockHistoryNotAsserted(
                        lineno,
                        col_offset,
                        mock_var=f'{context_manager.optional_vars.value.id}.{context_manager.optional_vars.attr}'))

        return errors
