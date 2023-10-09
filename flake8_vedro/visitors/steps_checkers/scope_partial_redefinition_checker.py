import ast
from typing import Any, List, Optional

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import ScopeVarIsPartiallyRedefined
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class ScopePartialRedefinitionChecker(StepsChecker):

    def _get_self_attribute_name(self, atr: ast.Attribute) -> Optional[str]:
        if isinstance(atr.value, ast.Name) and atr.value.id == 'self':
            return atr.attr

    def _get_self_dict_name(self, target: Any) -> Optional[str]:
        """
        self.foo["key"] = ... -> "foo"
        self.foo["key1"]["key2"] = ... -> "foo"
        self.foo = ... -> None]
        foo["key"] = ... -> None
        """
        if not isinstance(target, ast.Subscript):
            return None
        if isinstance(target.value, ast.Subscript):
            return self._get_self_dict_name(target.value)
        elif isinstance(target.value, ast.Attribute):
            return self._get_self_attribute_name(target.value)

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []
        for step in context.steps:
            for line in step.body:

                if not isinstance(line, ast.Assign):
                    continue

                for target in line.targets:
                    name = self._get_self_dict_name(target)
                    if name:
                        errors.append(ScopeVarIsPartiallyRedefined(line.lineno, line.col_offset, name=name))
        return errors
