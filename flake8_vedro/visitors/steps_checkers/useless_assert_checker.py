import ast
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import (
    StepAssertHasComparisonWithoutAssert,
    StepAssertHasUselessAssert
)
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class UselessAssertChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []
        for step in context.steps:
            for line in step.body:
                if isinstance(line, ast.Assert):

                    if isinstance(line.test, ast.Constant) or isinstance(line.test, ast.Name):
                        errors.append(StepAssertHasUselessAssert(
                            line.lineno, line.col_offset, step_name=step.name))

                if isinstance(line, ast.Expr):
                    if isinstance(line.value, ast.Compare):
                        errors.append(StepAssertHasComparisonWithoutAssert(
                            line.lineno, line.col_offset, step_name=step.name))
        return errors
