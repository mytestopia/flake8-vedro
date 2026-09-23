import os
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ScenarioChecker
from flake8_vedro.errors import SubjectDuplicatedAcrossScenarios
from flake8_vedro.helpers.subject_scanner import SubjectsMap
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_scenario_checker
class DuplicateSubjectChecker(ScenarioChecker):
    """
    Unlike VDR106 (several subjects within one scenario), this rule compares
    subjects across the whole scenarios/ tree.

    Under flake8 --jobs each worker builds the subject map of the tree once and
    reports only the occurrences in the files it owns. The first occurrence by
    sorted path is the original and is never reported, so every duplicate is
    reported exactly once whatever the file-to-worker distribution is.
    """

    def check_scenario(self, context: Context, *args) -> List[Error]:
        # scenarios outside scenarios/ are VDR103's business
        if context.scenarios_root is None:
            return []

        subject = self.get_subject(context.scenario_node)
        if subject is None:
            return []

        original = SubjectsMap.for_root(context.scenarios_root).find_original(context.filename, subject)
        if original is None:
            return []

        return [SubjectDuplicatedAcrossScenarios(
            subject.lineno, subject.col_offset,
            first_file=self._display_path(original.path),
            first_lineno=original.lineno,
        )]

    def _display_path(self, path: str) -> str:
        """Show the path the way flake8 does (relative to cwd) when possible."""
        try:
            relative = os.path.relpath(path)
        except ValueError:  # different drive on windows
            return path
        return path if relative.startswith('..') else relative
