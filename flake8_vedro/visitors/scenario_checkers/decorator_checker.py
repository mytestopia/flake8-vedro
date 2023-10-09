import ast
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ScenarioChecker
from flake8_vedro.errors import DecoratorVedroOnly
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_scenario_checker
class VedroOnlyChecker(ScenarioChecker):

    def check_scenario(self, context: Context, *args) -> List[Error]:
        for decorator in context.scenario_node.decorator_list:
            if (
                    isinstance(decorator, ast.Attribute)
                    and decorator.value.id == 'vedro'
                    and decorator.attr == 'only'
            ):
                return [DecoratorVedroOnly(decorator.lineno, decorator.col_offset)]

            elif (
                isinstance(decorator, ast.Name)
                and decorator.id == 'only'
            ):
                for import_from in context.import_from_nodes:
                    if import_from.module == 'vedro':
                        for name in import_from.names:
                            if name.name == 'only':
                                return [DecoratorVedroOnly(decorator.lineno, decorator.col_offset)]

        return []
