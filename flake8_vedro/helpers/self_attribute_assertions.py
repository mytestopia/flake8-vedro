import ast
from typing import List


def is_self_attribute(node: ast.expr) -> bool:
    """Checks if node is a 'self' attribute (e.g., self.offers_mock)."""
    if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == 'self'
    ):
        return True
    return False


def is_self_attribute_asserted(assert_statements: List[ast.Assert], self_attribute: ast.Attribute) -> bool:
    """Checks if provided self_attribute is asserted in any of given assert statements."""
    if not is_self_attribute(self_attribute):
        raise ValueError('Parameter "self_attribute" expects a "self" attribute (e.g., self.attribute_name)')

    for assert_statement in assert_statements:
        for condition_node in ast.walk(assert_statement.test):
            if (
                    isinstance(condition_node, ast.Attribute)
                    and isinstance(condition_node.value, ast.Name)
                    and condition_node.value.id == self_attribute.value.id
                    and condition_node.attr == self_attribute.attr
            ):
                return True
    return False
