import ast
from typing import Union, List
from flake8_plugin_utils import Error
from flake8_vedro.errors import ContextWithoutAssert
from flake8_vedro.config import Config
from flake8_vedro.visitors._visitor_with_filename import VisitorWithFilename


class ContextAssertVisitor(VisitorWithFilename):

    @property
    def config(self):
        return self._config

    def check_assert_in_contexts(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], config: Config) -> List[
            Error]:
        if config.is_context_assert_optional:
            return []
        else:
            for decorator in node.decorator_list:
                if (isinstance(decorator, ast.Attribute)
                        and decorator.value.id == 'vedro'
                        and decorator.attr == 'context'):
                    has_assert = False

                    for line in node.body:
                        if isinstance(line, ast.Assert):
                            has_assert = True
                            break

                        elif isinstance(line, ast.With):
                            for line_body in line.body:
                                if isinstance(line_body, ast.Assert):
                                    has_assert = True
                                    break

                    if not has_assert:
                        self.error_from_node(ContextWithoutAssert, node,
                                             func_name=node.name)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.check_assert_in_contexts(node, self.config)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.check_assert_in_contexts(node, self.config)
