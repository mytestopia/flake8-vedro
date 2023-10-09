import ast
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import StepAssertWithoutAssert
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class AssertChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []
        for step in context.steps:
            if (
                step.name.startswith('then')
                or step.name.startswith('and')
                or step.name.startswith('but')
            ):
                has_assert = False

                for line in step.body:
                    if isinstance(line, ast.Assert):
                        has_assert = True
                        break

                    elif isinstance(line, ast.For) or isinstance(line, ast.While):
                        for line_body in line.body:
                            if isinstance(line_body, ast.Assert):
                                has_assert = True
                                break

                if not has_assert:
                    errors.append(StepAssertWithoutAssert(step.lineno, step.col_offset, step_name=step.name))
        return errors
