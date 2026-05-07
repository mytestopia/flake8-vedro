import ast
from typing import List, Type

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import StepsChecker
from flake8_vedro.errors import StepHasBranching
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


STEP_PREFIX_MAP = {
    'init': ('__init__',),
    'given': ('given',),
    'when': ('when',),
    'then': ('then', 'and', 'but'),
}


@ScenarioVisitor.register_steps_checker
class BranchingChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []

        allow_ifs_in_steps = tuple()
        if config is not None:
            allow_ifs_in_steps = config.allow_ifs_in_steps

        for step in context.steps:
            if step.name.startswith(allow_ifs_in_steps):
                continue

            for if_statement in self._find_if_statements(step):
                errors.append(
                    StepHasBranching(
                        if_statement.lineno,
                        if_statement.col_offset,
                        step_name=step.name
                    )
                )

        return errors

    @staticmethod
    def _find_if_statements(step) -> list[ast.If | ast.Match | ast.IfExp]:
        if_statements = []

        elif_nodes = set()
        for node in ast.walk(step):
            # elif-nodes requires if-nodes, so treating elif as en error is redundant
            if id(node) in elif_nodes:
                continue

            if isinstance(node, ast.If):
                if_statements.append(node)
                elif_nodes |= set(id(item) for item in node.orelse)

            elif isinstance(node, (ast.Match, ast.IfExp)):
                if_statements.append(node)

        return if_statements
