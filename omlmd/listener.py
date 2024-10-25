from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass

import requests

from .model_metadata import ModelMetadata


class Listener(ABC):
    """
    TODO: not yet settled for multi-method or current single update method.
    """

    @abstractmethod
    def update(self, source: t.Any, event: Event) -> None:
        """
        Receive update event.
        """
        pass


class Event(ABC):
    pass


@dataclass
class PushEvent(Event):
    response: requests.Response
    target: str
    metadata: ModelMetadata

    @property
    def ok(self) -> bool:
        return self.response.status_code == 200

    def get_digest(self) -> str:
        return self.response.headers["Docker-Content-Digest"] if self.ok else ""
