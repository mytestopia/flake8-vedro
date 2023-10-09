from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import StepThenDuplicated, StepThenNotFound
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class SingleThenChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        then_steps = self.get_then_steps(context.steps)

        lineno = context.scenario_node.lineno
        col_offset = context.scenario_node.col_offset

        if not then_steps:
            return [StepThenNotFound(lineno, col_offset)]

        if len(then_steps) > 1:
            return [StepThenDuplicated(lineno, col_offset)]
        return []
