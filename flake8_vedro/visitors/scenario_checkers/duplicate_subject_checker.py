import os
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ScenarioChecker
from flake8_vedro.errors import SubjectDuplicatedAcrossScenarios
from flake8_vedro.helpers.subject_scanner import (
    collect_subjects,
    get_literal_subject,
    get_scenarios_root,
)
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_scenario_checker
class DuplicateSubjectChecker(ScenarioChecker):
    """
    Unlike VDR106 (several subjects within one scenario), this rule compares
    subjects across the whole scenarios/ tree, so it is opt-in via
    check_duplicate_subjects.

    Under flake8 --jobs each worker builds the subject map of the tree once and
    reports only the occurrences in the files it owns. The first occurrence by
    sorted path is the primary and is never reported, so every duplicate is
    reported exactly once whatever the file-to-worker distribution is.
    """

    def check_scenario(self, context: Context, config) -> List[Error]:
        if config is None or not config.check_duplicate_subjects:
            return []

        if context.filename is None:
            return []

        # scenarios outside scenarios/ are VDR103's business
        scenarios_root = get_scenarios_root(context.filename)
        if scenarios_root is None:
            return []

        subject = get_literal_subject(context.scenario_node)
        if subject is None:
            return []
        value, lineno, col_offset = subject

        occurrences = collect_subjects(scenarios_root).get(value, [])
        if len(occurrences) <= 1:
            return []

        current = (os.path.abspath(context.filename), lineno)

        # not in the map means the file on disk differs from the tree flake8
        # parsed (stdin, or an unsaved editor buffer) - nothing to compare with
        if current not in occurrences or current == occurrences[0]:
            return []

        first_file, first_lineno = occurrences[0]
        return [SubjectDuplicatedAcrossScenarios(
            lineno, col_offset,
            first_file=self._display_path(first_file),
            first_lineno=first_lineno,
        )]

    def _display_path(self, path: str) -> str:
        """Show the path the way flake8 does (relative to cwd) when possible."""
        try:
            relative = os.path.relpath(path)
        except ValueError:  # different drive on windows
            return path
        return path if relative.startswith('..') else relative
