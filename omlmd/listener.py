from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .model_metadata import ModelMetadata


class Listener(ABC):
    """
    TODO: not yet settled for multi-method or current single update method.
    """

    @abstractmethod
    def update(self, source: Any, event: Event) -> None:
        """
        Receive update event.
        """
        pass


class Event:
    pass


class PushEvent(Event):
    def __init__(self, target: str, metadata: ModelMetadata):
        # TODO: cannot just receive yet the push sha, waiting for: https://github.com/oras-project/oras-py/pull/146 in a release.
        self.target = target
        self.metadata = metadata
