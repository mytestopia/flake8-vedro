from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import ScopeVarIsRedefined
from flake8_vedro.helpers.scope_variables import get_all_scope_variables
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class ScopeRedefinitionChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []
        scope_variables = set()
        for step in context.steps:
            for var_name, lineno, col_offset in get_all_scope_variables(step):
                if var_name in scope_variables:
                    if var_name not in config.allowed_to_redefine_list:
                        errors.append(ScopeVarIsRedefined(lineno, col_offset, name=var_name))
                else:
                    scope_variables.add(var_name)
        return errors
