from typing import List, Optional


class Config:
    def __init__(self, is_context_assert_optional: bool,
                 is_mock_assert_optional: bool,
                 mock_name_pattern: str,
                 max_params_count: int,
                 allowed_to_redefine_list: Optional[List]):
        self.is_context_assert_optional = is_context_assert_optional
        self.is_mock_assert_optional = is_mock_assert_optional
        self.mock_name_pattern = mock_name_pattern
        self.max_params_count = max_params_count
        self.allowed_to_redefine_list = allowed_to_redefine_list if allowed_to_redefine_list else []


class DefaultConfig(Config):
    def __init__(self,
                 is_context_assert_optional: bool = True,
                 is_mock_assert_optional: bool = True,
                 mock_name_pattern: str = r"(?=.*mock)(?!.*grpc)",
                 max_params_count: int = 1,
                 allowed_to_redefine_list: Optional[List] = None
                 ):
        super().__init__(
            is_context_assert_optional=is_context_assert_optional,
            is_mock_assert_optional=is_mock_assert_optional,
            mock_name_pattern=mock_name_pattern,
            max_params_count=max_params_count,
            allowed_to_redefine_list=allowed_to_redefine_list
        )
