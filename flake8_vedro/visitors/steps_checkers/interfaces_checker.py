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
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class InterfacesUsageChecker(StepsChecker):

    def _get_func_names_in_step(self, step: ast.FunctionDef or ast.AsyncFunctionDef) -> List[Tuple[str, int, int]]:
        """
        Return list of names and their positions (line and column offset) in file for functions,
        which are called in step from argument
        """
        functions_in_step: List[Tuple[str, int, int]] = []
        body = step.body
        for line in body:
            ast_call = None
            if isinstance(line, ast.Assign):  # foo = ...
                if isinstance(line.value, ast.Subscript):  # ... = func()[0]
                    if isinstance(line.value.value, ast.Call):
                        ast_call = line.value.value
                elif isinstance(line.value, ast.Call):  # ... = func()
                    ast_call = line.value

            elif isinstance(line, ast.Expr):
                if isinstance(line.value, ast.Call):  # func()
                    ast_call = line.value

                elif isinstance(line.value, ast.Await) and \
                        isinstance(line.value.value, ast.Call):
                    ast_call = line.value.value

            if ast_call:
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
        imported_interfaces = get_imported_from_dir_functions(context.import_from_nodes, 'interfaces')
        if not imported_interfaces:
            return []

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
