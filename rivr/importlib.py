from typing import Callable

from rivr.http import Response


def import_module(name: str) -> Callable[..., Response]:
    if callable(name):
        return name

    module = __import__(name)
    for i in name.split('.')[1:]:
        module = getattr(module, i)

    if not callable(module):
        raise ImportError(
            'rivr.import.import_module cannot import %s because it is not a callable.'
            % name
        )

    return module
