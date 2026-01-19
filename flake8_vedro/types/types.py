import ast
from typing import Union

FuncType = Union[ast.FunctionDef, ast.AsyncFunctionDef]
WithType = Union[ast.With, ast.AsyncWith]
