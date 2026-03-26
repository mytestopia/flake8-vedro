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

    @staticmethod
    def _get_ast_calls_in_body(body):
        return [
            (line, node)
            for line in body
            for node in ast.walk(line)
            if isinstance(node, ast.Call)
        ]

    def _get_called_names_in_step(self, step: FuncType) -> List[Tuple[str, int, int]]:
        """
        Return list of names and their positions (line and column offset) in file for classes/functions,
        which are called in step from argument
        """
        classes_or_functions_in_step: List[Tuple[str, int, int]] = []

        ast_calls = self._get_ast_calls_in_body(step.body)
        for line, ast_call in ast_calls:
            name_node = unwrap_name_from_ast_node(ast_call)
            if name_node and (name := get_ast_name_node_name(name_node)):
                call = (name, line.lineno, line.col_offset)

                # Chain calls like API().get() produce multiple ast.Call nodes with
                # identical (name, lineno, col_offset), causing duplicate linter warnings.
                # It reduces linter output's readability, so we deduplicate same calls here.
                if call not in classes_or_functions_in_step:
                    classes_or_functions_in_step.append(call)

        return classes_or_functions_in_step

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
                for func, lineno, col_offset in self._get_called_names_in_step(step):
                    for func_name in imported_interfaces:
                        if func == func_name.name or func == func_name.asname:
                            errors.append(ImportedInterfaceInWrongStep(
                                lineno=lineno, col_offset=col_offset, func_name=func))
        return errors
