from typing import List, Optional


class Config:
    def __init__(self,
                 max_params_count: int,
                 allowed_to_redefine_list: Optional[List]):
        self.max_params_count = max_params_count
        self.allowed_to_redefine_list = allowed_to_redefine_list if allowed_to_redefine_list else []


class DefaultConfig(Config):
    def __init__(self,
                 max_params_count: int = 1,
                 allowed_to_redefine_list: Optional[List] = None
                 ):
        super().__init__(
            max_params_count=max_params_count,
            allowed_to_redefine_list=allowed_to_redefine_list
        )
