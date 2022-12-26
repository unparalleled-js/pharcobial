import pygame

from pharcobial.managers.base import BaseManager
from pharcobial.types import GameEvent, GameOptions
from pharcobial.utils import quit


class Game(BaseManager):
    def __init__(self, game_options: GameOptions):
        super().__init__()
        pygame.init()
        self.running = False
        self.options.load(game_options)

    def start(self):
        """
        Start the game.
        Does game setup and then runs the game
        """
        self.setup()
        self.run()
        quit()

    def setup(self):
        """
        All initial game setup happens here.
        If starting from beginning of the game, load initial setup.
        Else, load from a saved state.
        """

        # Process a map CSV file so it can be used for sprite-generation.
        self.map.load(self.options.map_id)

        # Validate is used to ensure the creation of a dependency
        # before other logic. This is to help the dependency injection
        # have some ordering, as needed.
        for manager in (
            self.options,
            self.display,
            self.map,
            self.world,
            self.collision,
        ):
            manager.validate()

        # Load all sprites in this level.
        self.sprites.init_level(self.options.map_id)
        self.sprites.validate()

        # Have camera follow player initially.
        self.world.follow(self.sprites.player)

        # Start off in normal, world mode.
        self.views.push(self.world)

    def run(self):
        """
        Runs the game. Controls the game loop.
        """
        self.running = True
        while self.running:
            self.react()

    def react(self):
        """
        React to game events.
        """

        for event in self.events.queue:
            match event:
                case GameEvent.QUIT:
                    self.running = False
                    quit()

                case GameEvent.MENU:
                    self.clock.paused = True
                    self.menu.visible = True
                    self.views.push(self.menu)
                    self.views.active.run()

                case GameEvent.CONTINUE:
                    self.views.active.run()
