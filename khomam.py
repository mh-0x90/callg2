from __future__ import annotations

import os


DEFAULT_TEXT = "haha"
ENV_VAR_NAME = "SOMESARA_TEXT"


def read_env_text(env_var_name: str = ENV_VAR_NAME) -> str:
    return os.getenv(env_var_name, DEFAULT_TEXT)