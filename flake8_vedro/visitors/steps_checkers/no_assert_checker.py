import ast
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import StepHasAssert
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class NoAssertChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []
        for step in context.steps:
            if (
                step.name.startswith('given')
                or step.name.startswith('when')
                or step.name == '__init__'
            ):
                for line in step.body:
                    if isinstance(line, ast.Assert):
                        errors.append(StepHasAssert(line.lineno, line.col_offset, step_name=step.name))
        return errors
