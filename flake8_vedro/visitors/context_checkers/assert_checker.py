import ast
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ContextChecker
from flake8_vedro.errors import ContextWithoutAssert
from flake8_vedro.visitors.context_visitor import Context, ContextVisitor


@ContextVisitor.register_context_checker
class ContextAssertChecker(ContextChecker):

    def check_context(self, context: Context, config) -> List[Error]:
        errors = []
        has_assert = self._has_assert_in_block(context.node.body)

        if not has_assert:
            errors.append(ContextWithoutAssert(context.node.lineno, context.node.col_offset,
                                               context_name=context.node.name))

        return errors

    def _has_assert_in_block(self, block: List[ast.stmt]) -> bool:
        for line in block:
            if isinstance(line, ast.Assert):
                return True
            elif isinstance(line, (ast.With, ast.AsyncWith)):
                if self._has_assert_in_block(line.body):
                    return True
        return False
