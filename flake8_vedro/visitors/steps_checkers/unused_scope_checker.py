import ast
import re
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.config import Config
from flake8_vedro.errors import ScopeVarIsNotUsed
from flake8_vedro.helpers.scope_variables import (
    get_all_scope_variables,
    get_all_used_scope_variables
)
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_steps_checker
class UnusedScopeVariablesChecker(StepsChecker):

    def _get_scope_variables_used_in_subject(self, context: Context) -> set:
        subject = self.get_subject(context.scenario_node)

        # It treats as a mistake in VDR104, VDR105
        if not (subject and isinstance(subject.value, ast.Constant)):
            return set()

        matches = re.findall(r'{(\w+)(?:\.\w+)*}', subject.value.value)
        return set(matches)

    def check_steps(self, context: Context, config: Config) -> List[Error]:
        definitions = []
        usages = self._get_scope_variables_used_in_subject(context)

        for step in context.steps:
            usages |= get_all_used_scope_variables(step)
            definitions.extend(
                get_all_scope_variables(
                    step, skip_context_manager_attributes=config.allow_unused_with_block_attributes)
            )

        errors = []
        for var_name, lineno, col_offset in definitions:
            if not var_name.startswith('_') and var_name not in usages:
                errors.append(ScopeVarIsNotUsed(lineno, col_offset, name=var_name))

        return errors
