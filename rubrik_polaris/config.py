from os import environ
from typing import Optional

ENV_VAR_PREFIX = 'rubrik_polaris_'
_rubrik_env = {k: environ[k] for k in environ if k.startswith(ENV_VAR_PREFIX)}


def get_conf_val(
        name: str,
        override: Optional[str] = None,
        default: Optional[str] = None,
        raise_if_none: Optional[bool] = True) -> Optional[str]:
    val = override if override is not None else \
        _rubrik_env.get(ENV_VAR_PREFIX + name, default)

    if raise_if_none and val is None:
        raise Exception(f'Missing configuration: {ENV_VAR_PREFIX}{name} '
                        f'not defined in the environment.')
    return val
