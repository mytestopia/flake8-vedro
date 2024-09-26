from typing import List, Optional


class Config:
    def __init__(self, is_context_assert_optional: bool,
                 max_params_count: int,
                 allowed_to_redefine_list: Optional[List]):
        self.is_context_assert_optional = is_context_assert_optional
        self.max_params_count = max_params_count
        self.allowed_to_redefine_list = allowed_to_redefine_list if allowed_to_redefine_list else []


class DefaultConfig(Config):
    def __init__(self,
                 is_context_assert_optional: bool = True,
                 max_params_count: int = 1,
                 allowed_to_redefine_list: Optional[List] = None
                 ):
        super().__init__(
            is_context_assert_optional=is_context_assert_optional,
            max_params_count=max_params_count,
            allowed_to_redefine_list=allowed_to_redefine_list
        )
