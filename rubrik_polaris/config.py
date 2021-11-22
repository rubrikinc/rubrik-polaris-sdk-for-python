from os import environ
from typing import Optional

ENV_VAR_PREFIX = 'rubrik_'
_rubrik_env = {k: environ[k] for k in environ if k.startswith(ENV_VAR_PREFIX)}
ENV_VAR_PREFIX_DEPRECATED = 'rubrik_polaris_'


def get_conf_val(
        name: str,
        override: Optional[str] = None,
        default: Optional[str] = None,
        raise_if_none: Optional[bool] = True) -> Optional[str]:
    """Looks up a configuration value, in this order:
       1. if `override` given, return that.
       2. if not defined, look up the env variable 'rubrik_'+name
       3. if not defined, look up the deprecated env variable
          'rubrik_polaris_'+name
       4. if not defined, use `default`
       5. if not defined, raise if `raise_if_none` or return None.
    """
    val = override if override is not None else \
        _rubrik_env.get(
            ENV_VAR_PREFIX + name,
            _rubrik_env.get(ENV_VAR_PREFIX_DEPRECATED + name, default))

    if raise_if_none and val is None:
        raise Exception(f'Missing configuration: {ENV_VAR_PREFIX}{name} '
                        f'not defined in the environment.')
    return val
