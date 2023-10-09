import ast
from typing import List


def get_imported_from_dir_functions(
        import_from_nodes: List[ast.ImportFrom],
        dir_name: str,
) -> List[ast.alias]:
    """
    Return list of function names which was imported from directory with dir_name
    """
    function_names: List[ast.alias] = []
    for import_node in import_from_nodes:
        import_node: ast.ImportFrom
        if import_node.module == dir_name or f'{dir_name}.' in import_node.module:
            for name in import_node.names:
                function_names.append(name)
    return function_names
