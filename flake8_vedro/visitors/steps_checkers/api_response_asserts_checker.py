import ast
from typing import List, Optional, Tuple

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import ApiResponseStatusNotAsserted
from flake8_vedro.helpers import (
    get_ast_name_node_name,
    get_imported_from_dir_functions,
    unwrap_name_from_ast_node,
)
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor

HELPER_PREFIXES = ('assert', 'check', 'verify', 'validate', 'ensure')


@ScenarioVisitor.register_steps_checker
class ApiResponseAssertsChecker(StepsChecker):

    @staticmethod
    def _walk(nodes):
        # nested functions and lambdas are not executed in the step itself
        pending = list(nodes)
        while pending:
            node = pending.pop()
            yield node
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                pending.extend(ast.iter_child_nodes(node))

    @staticmethod
    def _get_variable_name(node: ast.expr) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'self':
            return f'self.{node.attr}'
        return None

    def _is_api_call(self, value: Optional[ast.expr], interfaces: List[ast.alias]) -> bool:
        if not isinstance(value, ast.Call):
            return False

        # Api().get().json() saves a value derived from the response, not the response itself
        if isinstance(value.func, ast.Attribute) and value.func.attr == 'json':
            return False

        for node in self._walk([value]):
            if isinstance(node, ast.Call) and (name_node := unwrap_name_from_ast_node(node)):
                name = get_ast_name_node_name(name_node)
                if any(name in (interface.name, interface.asname) for interface in interfaces):
                    return True
        return False

    def _get_api_responses(self, step, interfaces: List[ast.alias]) -> List[Tuple[str, ast.AST]]:
        responses = []
        for node in self._walk(step.body):
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)):
                targets = [node.target]
            else:
                continue

            value = node.value.value if isinstance(node.value, ast.Await) else node.value
            if not self._is_api_call(value, interfaces):
                continue

            for target in targets:
                if name := self._get_variable_name(target):
                    responses.append((name, node))
        return responses

    def _is_status_checked(self, steps: List, response_name: str) -> bool:
        for step in steps:
            for node in self._walk(step.body):
                if isinstance(node, ast.Assert):
                    expression = node.test
                # comparison without assert is reported by VDR309
                elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Compare):
                    expression = node.value
                else:
                    continue

                for sub_node in ast.walk(expression):
                    if (
                        isinstance(sub_node, ast.Attribute)
                        and sub_node.attr == 'status_code'
                        and self._get_variable_name(sub_node.value) == response_name
                    ):
                        return True
        return False

    def _is_checked_by_helper(self, steps: List, response_name: str) -> bool:
        for step in steps:
            for node in self._walk(step.body):
                if not isinstance(node, ast.Call):
                    continue

                if isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                elif isinstance(node.func, ast.Name):
                    func_name = node.func.id
                else:
                    func_name = ''
                if func_name.lower().startswith(HELPER_PREFIXES):
                    return True

                arguments = [*node.args, *(keyword.value for keyword in node.keywords)]
                if any(self._get_variable_name(argument) == response_name for argument in arguments):
                    return True
        return False

    def check_steps(self, context: Context, config) -> List[Error]:
        if not config.api_interfaces_list:
            return []

        api_interfaces = [
            interface
            for interface in get_imported_from_dir_functions(context.import_from_nodes, 'interfaces')
            if interface.name in config.api_interfaces_list
        ]
        if not api_interfaces:
            return []

        assert_steps = [
            step for step in context.steps
            if step.name.startswith(('then', 'and', 'but'))
        ]
        # steps without asserts are reported by VDR307
        if not any(isinstance(node, ast.Assert) for step in assert_steps for node in self._walk(step.body)):
            return []

        errors = []
        reported = set()
        for step in self.get_when_steps(context.steps):
            for response_name, node in self._get_api_responses(step, api_interfaces):
                if (
                    response_name in reported
                    or self._is_status_checked(assert_steps, response_name)
                    or self._is_checked_by_helper(assert_steps, response_name)
                ):
                    continue

                reported.add(response_name)
                errors.append(ApiResponseStatusNotAsserted(node.lineno, node.col_offset, name=response_name))
        return errors
