import pygame  # type: ignore

from .base import BaseManager


class ClockManager(BaseManager):
    def __init__(self):
        super().__init__()
        self._clock = pygame.time.Clock()

    def tick(self):
        self._clock.tick(self.options.fps)


clock_manager = ClockManager()