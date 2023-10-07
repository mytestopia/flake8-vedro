import ast
from typing import List, Optional, Tuple, Union

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import ScopeVarIsRedefined
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class ScopeRedefinitionChecker(StepsChecker):

    def _get_self_attribute_name(self, atr: ast.Attribute) -> Optional[str]:
        if isinstance(atr.value, ast.Name) and atr.value.id == 'self':
            return atr.attr

    def _get_all_scope_variables(self,
                                 node: Union[
                                     ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.With, ast.AsyncWith
                                 ]) -> List[Tuple]:
        scope_variables = []
        body = node.body
        for line in body:
            new_variables = []

            def extend_if_attribute(ast_node: ast.expr):
                if isinstance(ast_node, ast.Attribute):
                    name = self._get_self_attribute_name(ast_node)
                    if name:
                        new_variables.append((name, line.lineno, line.col_offset))

            if isinstance(line, ast.Assign):
                for target in line.targets:
                    # self.foo = ...
                    extend_if_attribute(target)

                    # self.foo, self.buzz = ...
                    if isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            extend_if_attribute(elt)

            # with ... as self.foo:
            elif isinstance(line, ast.With) or isinstance(line, ast.AsyncWith):
                for item in line.items:
                    extend_if_attribute(item.optional_vars)

                # in with body could be the same assigns, tuples or with
                new_variables.extend(self._get_all_scope_variables(line))

            scope_variables.extend(new_variables)
        return scope_variables

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []
        scope_variables = set()
        for step in context.steps:
            step_variables = self._get_all_scope_variables(step)
            for var_name, lineno, col_offset in step_variables:
                if var_name in scope_variables:
                    if var_name not in config.allowed_to_redefine_list:
                        errors.append(ScopeVarIsRedefined(lineno, col_offset, name=var_name))
                else:
                    scope_variables.add(var_name)
        return errors
