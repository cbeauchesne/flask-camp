from .exceptions import ConfigurationError


class Event:
    def __init__(self) -> None:
        self._callbacks = []

    def fire(self, **kwargs):
        for callback in self._callbacks:
            callback(**kwargs)

    def __call__(self, callack: callable) -> None:

        if not callable(callack):
            raise ConfigurationError(f"{callack} is not callable")

        self._callbacks.append(callack)

        return callack
