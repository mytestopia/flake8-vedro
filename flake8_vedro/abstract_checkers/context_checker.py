from abc import ABC, abstractmethod
from typing import List

from flake8_plugin_utils import Error


class ContextChecker(ABC):

    @abstractmethod
    def check_context(self, context, config) -> List[Error]:
        pass
