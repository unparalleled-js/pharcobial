from functools import cached_property
from typing import List

from pygame.event import Event
from pyparsing import Iterator

from pharcobial.managers.base import ViewController
from pharcobial.types import MenuItem, UserInput
from pharcobial.utils import quit


class Menu(ViewController):
    def __init__(self, menu_id: str, choices: List[MenuItem]):
        self.choices = choices
        self.selected = 0
        super().__init__(f"{menu_id}-menu")

    def __iter__(self) -> Iterator[MenuItem]:
        yield from self.choices

    def __getitem__(self, index: int | slice) -> MenuItem | List[MenuItem]:
        return self.choices[index]

    def __len__(self) -> int:
        return len(self.choices)

    def draw(self):
        start_x = self.display.half_width // 2
        start_y = self.display.half_height // 2

        for item in self.choices:
            if item.index == self.selected:
                font_size = 36
                color = "green"
                x_offset = -8
            else:
                font_size = 34
                color = "white"
                x_offset = 0

            y_offset = start_y + (item.index * font_size) + 10
            self.display.show_text(
                item.title, font_size, (start_x + x_offset, start_y + y_offset), color
            )

    def handle_event(self, event: Event):
        if event.type != UserInput.KEY_DOWN:
            return

        if event.key == self.options.key_bindings.escape:
            self.pop()

        elif event.key == self.options.key_bindings.down:
            self.selected = (self.selected + 1) % len(self)

        elif event.key == self.options.key_bindings.up:
            self.selected = (self.selected - 1) % len(self)

        elif event.key == self.options.key_bindings.enter:
            item = self.choices[self.selected]
            item.action()

    def pop(self):
        self.views.pop()


class OptionsMenu(Menu):
    def __init__(self):
        titles = ["Back"]

        music_suffix = "disabled" if self.options.disable_music else "enabled"
        titles.append(f"Music ({music_suffix})")

        sfx_suffix = "disabled" if self.options.disable_sfx else "enabled"
        titles.append(f"Sfx ({sfx_suffix})")

        choices: List[MenuItem] = []
        for index, title in enumerate(titles):
            choices.append(MenuItem(title=title, index=index, action=lambda: None))

        super().__init__("options", choices)


class MainMenu(Menu):
    def __init__(self):
        choices = []
        actions = {
            "Quit": quit,
            "Options": self.go_to_options_menu,
        }

        for index, title in enumerate(("Continue", "Options", "Quit")):
            fn = actions.get(title, self.pop)
            item = MenuItem(title=title, index=index, action=fn)
            choices.append(item)

        super().__init__("main", choices)
        self.options_menu = OptionsMenu()

    def pop(self):
        self.views.pop()
        self.clock.paused = False

    def go_to_options_menu(self):
        self.views.push(self.options_menu)


class MenuManager(ViewController):
    @cached_property
    def main(self) -> Menu:
        return MainMenu()

    def draw(self):
        self.main.draw()

    def handle_event(self, event: Event):
        self.main.handle_event(event)


menu_manager = MenuManager("menu")
