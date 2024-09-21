import ast
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ContextChecker
from flake8_vedro.errors import ContextWithoutAssert
from flake8_vedro.visitors.context_assert_visitor import Context, ContextAssertVisitor


@ContextAssertVisitor.register_context_checker
class ContextAssertChecker(ContextChecker):

    def check_context(self, context: Context, config) -> List[Error]:
        # if config.is_context_assert_optional:
        #     return errors
        errors = []
        # for step in context.steps:

        for step in context.scenario_node:
            for decorator in step.decorator_list:
                if (isinstance(decorator, ast.Attribute)
                        and decorator.value.id == 'vedro'
                        and decorator.attr == 'context'):
                    has_assert = False
                    for line in step.body:
                        if isinstance(line, ast.Assert):
                            has_assert = True
                            break

        # elif isinstance(line, ast.With):
        #     for line_body in line.body:
        #         if isinstance(line_body, ast.Assert):
        #             has_assert = True
        #             break

                    if not has_assert:
                        errors.append(ContextWithoutAssert(step.lineno, step.col_offset))

        return errors
