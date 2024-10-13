import ast
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import StepWithMockedRequestCheckNotFound
from flake8_vedro.helpers import unwrap_name_from_ast_node, get_ast_name_node_name
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


def _check_mocked_context_manager_in_line(line) -> bool:
    if isinstance(line, ast.With) or isinstance(line, ast.AsyncWith):
        for item in line.items:
            context_manager_name_node = unwrap_name_from_ast_node(item.context_expr)
            context_manager_name = get_ast_name_node_name(context_manager_name_node)
            if context_manager_name.startswith('mocked'):
                return True

    return False


@ScenarioVisitor.register_steps_checker
class MockedRequestsChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []
        when_steps = self.get_when_steps(context.steps)

        lineno = context.scenario_node.lineno
        col_offset = context.scenario_node.col_offset

        is_mock_in_when_step = False
        for step in when_steps:
            for line in step.body:
                if _check_mocked_context_manager_in_line(line):
                    is_mock_in_when_step = True
                    break

        if is_mock_in_when_step:
            print('\nMock was found in when step')

            found_request_check_step = False
            for step in context.steps:
                if (
                    step.name.startswith('then')
                    or step.name.startswith('and')
                    or step.name.startswith('but')
                ):
                    if 'request' in step.name and 'sent' in step.name:
                        print('\nStep with "request ... sent" was found')
                        found_request_check_step = True

            if not found_request_check_step:
                errors.append(StepWithMockedRequestCheckNotFound(lineno, col_offset))

        return errors
