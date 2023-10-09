from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ScenarioChecker
from flake8_vedro.errors import ScenarioLocationInvalid
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_scenario_checker
class LocationChecker(ScenarioChecker):

    def check_scenario(self, context: Context, *args) -> List[Error]:
        if context.filename is not None:
            if not self.is_file_in_folder(context.filename):
                return [ScenarioLocationInvalid(context.scenario_node.lineno, context.scenario_node.col_offset)]
        return []
