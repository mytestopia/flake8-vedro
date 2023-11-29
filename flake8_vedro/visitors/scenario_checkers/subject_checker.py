import ast
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ScenarioChecker
from flake8_vedro.errors import (
    SubjectDuplicated,
    SubjectEmpty,
    SubjectNotFound
)
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_scenario_checker
class SingleSubjectChecker(ScenarioChecker):

    def check_scenario(self, context: Context, *args) -> List[Error]:
        subjects = self.get_subjects(context.scenario_node)

        if not subjects:
            return [SubjectNotFound(context.scenario_node.lineno, context.scenario_node.col_offset)]

        errors = []
        if len(subjects) > 1:
            for subject in subjects[1:]:
                errors.append(SubjectDuplicated(subject.lineno, subject.col_offset))

        return errors


@ScenarioVisitor.register_scenario_checker
class SubjectEmptyChecker(ScenarioChecker):

    def check_scenario(self, context: Context, *args) -> List[Error]:
        subject = self.get_subject(context.scenario_node)
        if subject and isinstance(subject.value, ast.Constant):
            if not subject.value.value:
                return [SubjectEmpty(subject.lineno, subject.col_offset)]
        return []
