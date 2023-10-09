from typing import List

from flake8_plugin_utils import Error

from flake8_vedro.abstract_checkers import ScenarioChecker
from flake8_vedro.errors import ExceedMaxParamsCount
from flake8_vedro.visitors.scenario_visitor import Context, ScenarioVisitor


@ScenarioVisitor.register_scenario_checker
class ParametrizationLimitChecker(ScenarioChecker):

    def check_scenario(self, context: Context, config) -> List[Error]:
        errors = []

        init_node = self.get_init_step(context.scenario_node)

        if init_node is None or not init_node.decorator_list:
            return errors

        for decorator in self.get_params_decorators(init_node):
            if len(decorator.args) > config.max_params_count:
                errors.append(ExceedMaxParamsCount(decorator.lineno, decorator.col_offset,
                                                   current=len(decorator.args),
                                                   max=config.max_params_count))
        return errors
