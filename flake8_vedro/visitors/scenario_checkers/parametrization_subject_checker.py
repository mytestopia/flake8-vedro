import re
from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ScenarioChecker
from flake8_vedro.errors import SubjectIsNotParametrized
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_scenario_checker
class ParametrizationSubjectChecker(ScenarioChecker):

    def check_scenario(self, context: Context, *args) -> List[Error]:
        init_node = self.get_init_step(context.scenario_node)

        if init_node and init_node.decorator_list:
            params_decorator = self.get_params_decorators(init_node)

            if len(params_decorator) > 1:
                subject_node = self.get_subject(context.scenario_node)
                pattern = re.compile('^.*\{.+\}.*$')  # noqa: W605
                if not pattern.match(subject_node.value.value):
                    return [SubjectIsNotParametrized(subject_node.lineno, subject_node.col_offset)]
        return []
