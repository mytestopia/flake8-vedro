import ast
from typing import Union, Optional, List, Type
from flake8_vedro.abstract_checkers import (
    ContextChecker
)
from flake8_plugin_utils import Error
from flake8_vedro.errors import ContextWithoutAssert
from flake8_vedro.config import Config
from flake8_vedro.visitors._visitor_with_filename import VisitorWithFilename


class Context:
    def __init__(self, scenario_node: Union[ast.FunctionDef, ast.AsyncFunctionDef], filename: str):
        self.scenario_node = scenario_node
        self.filename = filename


class ContextAssertVisitor(VisitorWithFilename):
    context_checkers: List[ContextChecker] = []

    def __init__(self, config: Optional[Config] = None,
                 filename: Optional[str] = None) -> None:
        super().__init__(config, filename)

    @property
    def config(self):
        return self._config

    @classmethod
    def register_context_checker(cls, checker: Type[ContextChecker]):
        cls.context_checkers.append(checker())
        return checker

    @classmethod
    def deregister_all(cls):
        cls.context_checkers = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> List[Error]:
        for decorator in node.decorator_list:
            if (isinstance(decorator, ast.Attribute)
                    and decorator.value.id == 'vedro'
                    and decorator.attr == 'context'):
                context = Context(scenario_node=node,
                                  filename=self.filename)
                try:
                    for checker in self.context_checkers:
                        self.errors.extend(checker.check_context(context, self.config))
                except Exception as e:
                    print(f'Linter failed: checking {context.filename} with {checker.__class__}.\n'
                          f'Exception: {e}')

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> List[Error]:
        for decorator in node.decorator_list:
            if (isinstance(decorator, ast.Attribute)
                    and decorator.value.id == 'vedro'
                    and decorator.attr == 'context'):
                context = Context(scenario_node=node,
                                  filename=self.filename)
                try:
                    for checker in self.context_checkers:
                        self.errors.extend(checker.check_context(context, self.config))
                except Exception as e:
                    print(f'Linter failed: checking {context.filename} with {checker.__class__}.\n'
                          f'Exception: {e}')
