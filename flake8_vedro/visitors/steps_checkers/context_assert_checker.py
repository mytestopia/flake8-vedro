import ast
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import ContextWithoutAssert
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class ContextAssertChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []
        for decorator in context.scenario_node.decorator_list:
            for step in context.steps:
                if (
                        isinstance(decorator, ast.Attribute)
                        and decorator.value.id == 'vedro'
                        and decorator.attr == 'context'
                ):
                    has_assert = False

                    for line in step.body:
                        if isinstance(line, ast.Assert):
                            has_assert = True
                            break

                        elif isinstance(line, ast.With):
                            for line_body in line.body:
                                if isinstance(line_body, ast.Assert):
                                    has_assert = True
                                    break

                    if not has_assert:
                        errors.append(ContextWithoutAssert(step.lineno, step.col_offset))

            return errors
