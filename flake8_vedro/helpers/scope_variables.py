import ast
from typing import Optional, Union

from flake8_vedro.types import FuncType
from flake8_vedro.types.types import WithType


def get_self_attribute_name(atr: ast.Attribute) -> Optional[str]:
    if isinstance(atr.value, ast.Name) and atr.value.id == 'self':
        return atr.attr


def extract_self_attributes(target) -> list[str]:
    if target is None:
        return []

    # with ... as self.var
    if isinstance(target, ast.Attribute):
        if get_self_attribute_name(target) is not None:
            return [target.attr]

    # with ... as (self.var1, self.var2)
    elif isinstance(target, ast.Tuple):
        result = []
        for elt in target.elts:
            result.extend(extract_self_attributes(elt))
        return result

    return []


def get_all_scope_variables(node: Union[FuncType, WithType],
                            skip_context_manager_attributes: bool = False) -> list[tuple]:
    defined_attributes = []

    context_manager_vars = set()
    for child in ast.walk(node):
        if isinstance(child, (ast.With, ast.AsyncWith)):
            for item in child.items:
                context_manager_vars.update(
                    extract_self_attributes(item.optional_vars)
                )

    class AttributeDefVisitor(ast.NodeVisitor):
        def visit_Attribute(self, node: ast.Attribute):
            if not isinstance(node.ctx, ast.Store):
                return

            if name := get_self_attribute_name(node):
                if skip_context_manager_attributes and name in context_manager_vars:
                    return

                defined_attributes.append((name, node.lineno, node.col_offset))

            self.generic_visit(node)

    visitor = AttributeDefVisitor()
    visitor.visit(node)

    return defined_attributes


def get_all_used_scope_variables(node: FuncType) -> set:
    variables = set()

    class AttributeVisitor(ast.NodeVisitor):
        def visit_Attribute(self, node: ast.Attribute):
            if not isinstance(node.ctx, ast.Load):
                return

            if name := get_self_attribute_name(node):
                variables.add(name)

            self.generic_visit(node)

    visitor = AttributeVisitor()
    visitor.visit(node)

    return variables
