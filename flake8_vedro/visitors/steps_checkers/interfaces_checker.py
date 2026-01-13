import ast
from typing import List, Tuple

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import ImportedInterfaceInWrongStep
from flake8_vedro.helpers import (
    get_ast_name_node_name,
    get_imported_from_dir_functions,
    unwrap_name_from_ast_node
)
from flake8_vedro.types import FuncType
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class InterfacesUsageChecker(StepsChecker):

    def get_ast_call_in_body(self, body):
        ast_calls = []
        for line in body:
            if isinstance(line, ast.With) or isinstance(line, ast.AsyncWith):
                ast_calls.extend(self.get_ast_call_in_body(line.body))

            elif isinstance(line, ast.Assign):  # foo = ...

                if isinstance(line.value, ast.Subscript):  # ... = func()[0]
                    if isinstance(line.value.value, ast.Call):
                        ast_calls.append((line, line.value.value))
                elif isinstance(line.value, ast.Call):  # ... = func()
                    ast_calls.append((line, line.value))

            elif isinstance(line, ast.Expr):
                if isinstance(line.value, ast.Call):  # func()
                    ast_calls.append((line, line.value))

                elif isinstance(line.value, ast.Await) and \
                        isinstance(line.value.value, ast.Call):
                    ast_calls.append((line, line.value.value))
        return ast_calls

    def _get_func_names_in_step(
            self, step: FuncType) -> List[Tuple[str, int, int]]:
        """
        Return list of names and their positions (line and column offset) in file for functions,
        which are called in step from argument
        """
        functions_in_step: List[Tuple[str, int, int]] = []
        ast_calls = self.get_ast_call_in_body(step.body)

        for line, ast_call in ast_calls:
            name_node = unwrap_name_from_ast_node(ast_call.func)
            name = get_ast_name_node_name(name_node) if name_node else None
            if name:
                functions_in_step.append((
                    name,
                    line.lineno,
                    line.col_offset  # TODO fix
                ))
        return functions_in_step

    def check_steps(self, context: Context, config) -> List[Error]:
        imported_interfaces = get_imported_from_dir_functions(
            context.import_from_nodes,
            'interfaces',
        )
        if not imported_interfaces:
            return []

        if config.allowed_interfaces_list:
            imported_interfaces = list(filter(
                lambda x: x.name not in config.allowed_interfaces_list,
                imported_interfaces)
            )

        errors = []
        for step in context.steps:
            if (
                step.name.startswith('given')
                or step.name.startswith('then')
                or step.name.startswith('and')
                or step.name.startswith('but')
            ):
                for func, lineno, col_offset in self._get_func_names_in_step(step):
                    for func_name in imported_interfaces:
                        if func == func_name.name or func == func_name.asname:
                            errors.append(ImportedInterfaceInWrongStep(
                                lineno=lineno, col_offset=col_offset, func_name=func))
        return errors
