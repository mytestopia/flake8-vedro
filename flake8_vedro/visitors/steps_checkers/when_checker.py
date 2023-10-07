from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import StepWhenDuplicated, StepWhenNotFound
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class SingleWhenChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        when_steps = self.get_when_steps(context.steps)

        lineno = context.scenario_node.lineno
        col_offset = context.scenario_node.col_offset

        if not when_steps:
            return [StepWhenNotFound(lineno, col_offset)]

        if len(when_steps) > 1:
            return [StepWhenDuplicated(lineno, col_offset)]
        return []
