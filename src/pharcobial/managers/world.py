from pygame.event import Event
from pygame.math import Vector2
from pygame.sprite import Group
from pygame.surface import Surface

from pharcobial.logging import game_logger
from pharcobial.managers.base import BaseManager, ViewController
from pharcobial.sprites.base import BaseSprite


class CameraGroup(Group):
    def __init__(self, surface: Surface) -> None:
        super().__init__()
        self.surface = surface

    def draw_in_view(self, offset: Vector2):
        pending = []
        for sprite in sorted(self.sprites(), key=lambda s: s.rect is not None and s.rect.centery):
            assert isinstance(sprite, BaseSprite)  # for Mypy
            if not sprite.visible:
                continue

            # Mypy doesn't realize this is valid.
            offset_pos: Vector2 = sprite.rect.topleft - offset  # type: ignore[operator]

            # Draw bottom layer first
            if (
                sprite.sprite_id == "player"
                or "adversary-" in sprite.sprite_id
                or "-bubble" in sprite.sprite_id
            ):
                pending.append((sprite.image, offset_pos))
            else:
                self.surface.blit(sprite.image, offset_pos)

        for img, offset in pending:
            self.surface.blit(img, offset)


class Camera(BaseManager):
    def __init__(self) -> None:
        super().__init__()
        self.offset = Vector2()
        self.followee: BaseSprite | None = None

    def update(self):
        if self.followee is not None:
            self.offset.x = self.followee.rect.centerx - self.display.half_width
            self.offset.y = self.followee.rect.centery - self.display.half_height


class WorldManager(ViewController):
    def __init__(self) -> None:
        super().__init__(CameraGroup(self.display.active.screen))
        self.camera = Camera()
        self.group: CameraGroup = self.group

    def validate(self):
        assert self.group is not None
        assert self.camera is not None
        game_logger.debug("World ready.")

    def handle_event(self, event: Event):
        self.sprites.player.handle_event(event)

    def update(self):
        self.camera.update()
        self.group.update()

    def draw(self):
        self.group.draw_in_view(self.camera.offset)

    def follow(self, sprite: BaseSprite):
        self.camera.followee = sprite


world_manager = WorldManager()