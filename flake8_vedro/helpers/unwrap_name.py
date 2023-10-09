import ast


def unwrap_name_from_ast_node(element: ast.Attribute or ast.Call or ast.Name) -> ast.Name:
    if isinstance(element, ast.Attribute):
        return unwrap_name_from_ast_node(element.value)

    elif isinstance(element, ast.Call):
        return unwrap_name_from_ast_node(element.func)

    elif isinstance(element, ast.Name):
        return element

    elif isinstance(element, ast.Subscript):
        return unwrap_name_from_ast_node(element.value)


def get_ast_name_node_name(element: ast.Name) -> str:
    return element.id
