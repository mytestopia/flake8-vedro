from typing import List, Optional


class Config:
    def __init__(self, is_context_assert_optional: bool,
                 max_params_count: int,
                 allowed_to_redefine_list: Optional[List],
                 allowed_interfaces_list: Optional[List],
                 allow_partial_redefinitions_in_one_step: bool,
                 allow_unused_with_block_attributes: bool):
        self.is_context_assert_optional = is_context_assert_optional
        self.max_params_count = max_params_count
        self.allowed_to_redefine_list = allowed_to_redefine_list or []
        self.allowed_interfaces_list = allowed_interfaces_list or []
        self.allow_partial_redefinitions_in_one_step = allow_partial_redefinitions_in_one_step
        self.allow_unused_with_block_attributes = allow_unused_with_block_attributes


class DefaultConfig(Config):
    def __init__(self,
                 is_context_assert_optional: bool = True,
                 max_params_count: int = 1,
                 allowed_to_redefine_list: Optional[List] = None,
                 allowed_interfaces_list: Optional[List[str]] = None,
                 allow_partial_redefinitions_in_one_step: bool = False,
                 allow_unused_with_block_attributes: bool = True):
        super().__init__(
            is_context_assert_optional=is_context_assert_optional,
            max_params_count=max_params_count,
            allowed_to_redefine_list=allowed_to_redefine_list,
            allowed_interfaces_list=allowed_interfaces_list,
            allow_partial_redefinitions_in_one_step=allow_partial_redefinitions_in_one_step,
            allow_unused_with_block_attributes=allow_unused_with_block_attributes
        )
