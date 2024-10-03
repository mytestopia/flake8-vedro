import argparse
import ast
from typing import Callable, List, Optional

from flake8.options.manager import OptionManager
from flake8_plugin_utils import Plugin, Visitor

from flake8_vedro.visitors import ContextVisitor, ScenarioVisitor

from .config import Config
from .defaults import Defaults


def str_to_bool(string):
    return string.lower() in ('true', 'yes', 't', '1')


class PluginWithFilename(Plugin):
    def __init__(self, tree: ast.AST, filename: str, *args, **kwargs):
        super().__init__(tree)
        self.filename = filename

    def run(self):
        for visitor_cls in self.visitors:
            visitor = self._create_visitor(visitor_cls, filename=self.filename)
            visitor.visit(self._tree)
            for error in visitor.errors:
                yield self._error(error)

    @classmethod
    def _create_visitor(cls, visitor_cls: Callable, filename: Optional[str] = None) -> Visitor:
        if cls.config is None:
            return visitor_cls(filename=filename)
        return visitor_cls(config=cls.config, filename=filename)


class VedroScenarioStylePlugin(PluginWithFilename):
    name = 'flake8_vedro'
    version = '1.0.2'
    visitors = [
        ScenarioVisitor,
        ContextVisitor
    ]

    def __init__(self, tree: ast.AST, filename: str, *args, **kwargs):
        super().__init__(tree, filename)

    @classmethod
    def add_options(cls, option_manager: OptionManager):
        option_manager.add_option(
            '--is-context-assert-optional',
            default='true',
            type=str,
            parse_from_config=True,
            help='If contexts should have specific assertions',
        )
        option_manager.add_option(
            '--scenario-params-max-count',
            default=Defaults.MAX_PARAMS_COUNT,
            type=int,
            parse_from_config=True,
            help='Maximum allowed parameters in vedro parametrized scenario. '
                 '(Default: %(default)s)',
        )
        option_manager.add_option(
            '--allowed-to-redefine-list',
            comma_separated_list=True,
            parse_from_config=True,
            help='List of scope variables allowed to redefine',
        )

    @classmethod
    def parse_options_to_config(
        cls, option_manager: OptionManager, options: argparse.Namespace, args: List[str]
    ) -> Config:
        return Config(
            is_context_assert_optional=str_to_bool(options.is_context_assert_optional),
            max_params_count=options.scenario_params_max_count,
            allowed_to_redefine_list=options.allowed_to_redefine_list,
        )
