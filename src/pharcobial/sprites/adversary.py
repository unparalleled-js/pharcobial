from abc import abstractmethod
from functools import cached_property

from pharcobial._types import DrawInfo
from pharcobial.constants import BLOCK_SIZE

from .base import BaseSprite


class Adversary(BaseSprite):
    @abstractmethod
    def get_gfx_id(self) -> str:
        """
        Determines the graphic used for the adversary.
        """

    def get_draw_info(self) -> DrawInfo:
        return DrawInfo(gfx_id=self.get_gfx_id(), rect=self.rect)


class BushMonster(Adversary):
    def __init__(self, monster_id: int):
        super().__init__()
        self.monster_id = monster_id
        self.speed = 0.2

    @cached_property
    def movement_length(self) -> int:
        return round(BLOCK_SIZE * self.speed)

    def get_gfx_id(self) -> str:
        return "bush-monster"

    def get_sprite_id(self) -> str:
        return str(self.monster_id)

    def update(self, *args, **kwargs):
        """
        The monster is always moving towards the player.
        """

        player = kwargs["player"]

        new_left = self.rect.left
        new_top = self.rect.top

        # Handle x
        if player.rect.left > self.rect.left:
            new_left = self.rect.left + min(self.movement_length, player.rect.left - self.rect.left)
        elif player.rect.left < self.rect.left:
            new_left = self.rect.left - min(self.movement_length, self.rect.left - player.rect.left)

        # Handle y
        if player.rect.top > self.rect.top:
            new_top = self.rect.top + min(self.movement_length, player.rect.top - self.rect.top)
        elif player.rect.top < self.rect.top:
            new_top = self.rect.top - min(self.movement_length, self.rect.top - player.rect.top)

        self.move(new_left, new_top)
