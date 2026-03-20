import argparse
import ast
import re
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
    version = '1.1.1'
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
            help='If contexts should have specific assertions (rule VDR400)',
        )
        option_manager.add_option(
            '--scenario-params-max-count',
            default=Defaults.MAX_PARAMS_COUNT,
            type=int,
            parse_from_config=True,
            help='Maximum allowed parameters in vedro parametrized scenario. '
                 '(Default: %(default)s) (rule VDR109)',
        )
        option_manager.add_option(
            '--allowed-to-redefine-list',
            comma_separated_list=True,
            parse_from_config=True,
            help='List of scope variables allowed to redefine (rule VDR311)',
        )
        option_manager.add_option(
            '--allowed-interfaces-list',
            comma_separated_list=True,
            parse_from_config=True,
            help='List of interfaces allowed to use in any steps (rule VDR302)',
        )
        option_manager.add_option(
            '--allow-partial-redefinitions-in-one-step',
            default='false',
            type=str,
            parse_from_config=True,
            help='Allow partial redefinitions in one step (rule VDR312)',
        )
        option_manager.add_option(
            '--allow-unused-with-block-attributes',
            default='true',
            type=str,
            parse_from_config=True,
            help='Allow unused with block attributes (rule VDR313)',
        )
        option_manager.add_option(
            '--ignore-variables-pattern',
            default=None,
            type=str,
            parse_from_config=True,
            help='Regex pattern for variable names to ignore (rule VDR313)',
        )

    @classmethod
    def parse_options_to_config(
        cls, option_manager: OptionManager, options: argparse.Namespace, args: List[str]
    ) -> Config:
        cls._validate_ignore_variables_pattern(options.ignore_variables_pattern)
        return Config(
            is_context_assert_optional=str_to_bool(options.is_context_assert_optional),
            max_params_count=options.scenario_params_max_count,
            allowed_to_redefine_list=options.allowed_to_redefine_list,
            allowed_interfaces_list=options.allowed_interfaces_list,
            allow_partial_redefinitions_in_one_step=str_to_bool(options.allow_partial_redefinitions_in_one_step),
            allow_unused_with_block_attributes=str_to_bool(options.allow_unused_with_block_attributes),
            ignore_variables_pattern=options.ignore_variables_pattern
        )

    @classmethod
    def _validate_ignore_variables_pattern(cls, ignore_variables_pattern: str | None) -> None:
        if ignore_variables_pattern is None:
            return

        try:
            re.compile(ignore_variables_pattern)
        except re.error as e:
            raise ValueError(
                f"Invalid regex pattern for --ignore-variables-pattern: "
                f"'{ignore_variables_pattern}' ({e})"
            )
