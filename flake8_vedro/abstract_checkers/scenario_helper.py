import ast
import pathlib
from typing import List, Optional

SCENARIOS_FOLDER = 'scenarios'


class ScenarioHelper:

    def get_all_steps(self, class_node: ast.ClassDef) -> List:
        return [
            element for element in class_node.body if (
                isinstance(element, ast.FunctionDef)
                or isinstance(element, ast.AsyncFunctionDef)
            )
        ]

    def get_init_step(self, node: ast.ClassDef) -> Optional[ast.FunctionDef]:
        for element in node.body:
            if isinstance(element, ast.FunctionDef) and element.name == '__init__':
                return element

    def get_subjects(self, node: ast.ClassDef) -> List[ast.Assign]:
        subjects = []
        for element in node.body:
            if isinstance(element, ast.Assign) and element.targets[0].id == 'subject':
                subjects.append(element)
        return subjects

    def get_subject(self, node: ast.ClassDef) -> Optional[ast.Assign]:
        subjects = self.get_subjects(node)
        return subjects[0] if subjects else None

    def get_params_decorators(self, init_node: ast.FunctionDef) -> List[ast.Call]:
        params_decorator = []
        for decorator in init_node.decorator_list:
            if isinstance(decorator, ast.Call):

                # @vedro.params
                if (
                        isinstance(decorator.func, ast.Attribute)
                        and decorator.func.value.id == 'vedro'
                        and decorator.func.attr == 'params'
                ):
                    params_decorator.append(decorator)

                # @params
                elif isinstance(decorator.func, ast.Name) and decorator.func.id == 'params':
                    params_decorator.append(decorator)
        return params_decorator

    def get_when_steps(self, steps: List) -> List:
        return [
            step for step in steps if step.name.startswith('when')
        ]

    def get_then_steps(self, steps: List) -> List:
        return [
            step for step in steps if step.name.startswith('then')
        ]

    def is_file_in_folder(self, filename: str,
                          folder: str = SCENARIOS_FOLDER) -> bool:
        path = pathlib.Path(filename)

        for parent in path.parents:
            if parent.name == folder:
                return True
        return False
