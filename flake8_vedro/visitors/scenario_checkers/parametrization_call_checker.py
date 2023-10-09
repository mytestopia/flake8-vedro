import ast
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ScenarioChecker
from flake8_vedro.errors import ContextCallInParams
from flake8_vedro.helpers import (
    get_ast_name_node_name,
    get_imported_from_dir_functions,
    unwrap_name_from_ast_node
)
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_scenario_checker
class ParametrizationCallChecker(ScenarioChecker):

    def check_scenario(self, context: Context, config) -> List[Error]:
        errors = []

        init_node = self.get_init_step(context.scenario_node)

        if init_node is None or not init_node.decorator_list:
            return []

        imported_contexts = get_imported_from_dir_functions(
            context.import_from_nodes, 'contexts')
        if not imported_contexts:
            return []

        for decorator in self.get_params_decorators(init_node):
            for arg in decorator.args:
                if isinstance(arg, ast.Call):
                    name_node = unwrap_name_from_ast_node(arg)
                    if name_node is not None:
                        name = get_ast_name_node_name(name_node)

                        for func_name in imported_contexts:
                            if name == func_name.name or name == func_name.asname:
                                errors.append(ContextCallInParams(decorator.lineno, decorator.col_offset))
                                break
        return errors
