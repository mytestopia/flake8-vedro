import ast
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ScenarioChecker
from flake8_vedro.errors import ScenarioNotInherited
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_scenario_checker
class ParentChecker(ScenarioChecker):

    def check_scenario(self, context: Context, *args) -> List[Error]:
        has_parent = False
        for base in context.scenario_node.bases:
            if isinstance(base, ast.Attribute):
                base: ast.Attribute
                if base.attr == 'Scenario' and base.value.id == 'vedro':
                    has_parent = True
        if not has_parent:
            return [ScenarioNotInherited(context.scenario_node.lineno, context.scenario_node.col_offset)]
        return []
