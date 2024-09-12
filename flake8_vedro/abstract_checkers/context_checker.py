from abc import ABC, abstractmethod
from typing import List

from flake8_plugin_utils import Error

from .scenario_helper import ScenarioHelper


class ContextChecker(ScenarioHelper, ABC):

    @abstractmethod
    def check_context(self, context, config) -> List[Error]:
        pass
