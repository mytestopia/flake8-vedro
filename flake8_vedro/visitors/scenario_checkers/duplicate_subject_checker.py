from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ScenarioChecker
from flake8_vedro.errors import SubjectDuplicatedAcrossScenarios
from flake8_vedro.helpers.subject_scanner import SubjectsMap, find_scenarios_root
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_scenario_checker
class DuplicateSubjectChecker(ScenarioChecker):
    """
    Compare subjects of all scenarios in the scenarios folder. The first occurrence by sorted path
    is never reported, so the result doesn't depend on --jobs
    """

    def check_scenario(self, context: Context, *args) -> List[Error]:
        root = find_scenarios_root(context.filename)
        if root is None:
            return []

        subject = self.get_subject(context.scenario_node)
        if subject is None:
            return []

        original = SubjectsMap.for_root(root).find_duplicate_original(context.filename, subject)
        if original is None:
            return []

        return [SubjectDuplicatedAcrossScenarios(
            subject.lineno, subject.col_offset,
            first_file=original.path,
            first_lineno=original.lineno,
        )]
