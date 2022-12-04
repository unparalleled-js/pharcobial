from collections import namedtuple
from enum import Enum
from typing import Tuple

from pygame.sprite import Sprite

from pharcobial.constants import DEFAULT_BLOCK_SIZE

Color = Tuple[int, int, int]
Coordinates = namedtuple("Coordinates", ("x", "y"))


class BaseSprite(Sprite):
    x: int = 0
    y: int = 0
    height: int = DEFAULT_BLOCK_SIZE
    width: int = DEFAULT_BLOCK_SIZE

    @property
    def coordinates(self) -> Coordinates:
        return Coordinates(self.x, self.y)


class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
