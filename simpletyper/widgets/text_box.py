import os

from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from textual.reactive import Reactive
from textual.widget import Widget

from simpletyper.events.gamedone import GameDone
from simpletyper.utils.load_words import load_words


class TextBox(Widget):
    user_input = ""
    display_text = Reactive(Text())

    def __init__(
        self,
        name: str | None = None,
        *,
        file: str,
        num_words: int,
        count_down: int = 0,
    ) -> None:
        super().__init__(name)
        self.file = file
        self.num_words = num_words
        self.text = load_words(file, num_words)
        self.count_down = count_down
        self.stop = False

    def update_text(self, c: str) -> None:
        if self.stop:
            return
        curr_idx = len(self.user_input) + 1
        if curr_idx >= len(self.text):
            self.emit_no_wait(GameDone(self))
            return
        self.user_input += c
        curr_char = self.text[curr_idx]
        before = Text()

        for char1, char2 in zip(str(self.user_input[:curr_idx]), self.text):
            before.append(
                Text(char2, style=("green bold" if char1 == char2 else "red underline"))
            )

        after: Text = self.display_text[curr_idx + 1 :]
        new_char: Text = Text(curr_char, style="black on white")
        self.display_text = Text.assemble(before + new_char + after, justify="center")

    def init_text(self) -> None:
        self.display_text = Text.assemble(
            Text(self.text[0], style="black on white"),
            self.text[1:],
            style="#909090",
            justify="center",
        )

    def reset(self) -> None:
        self.stop = False
        self.text = load_words(file=self.file, limit=self.num_words)
        self.init_text()
        self.user_input = ""

    def set_end_screen(self, counter: int) -> None:
        if counter == 0 and not self.count_down:
            counter = 1
        elif self.count_down and counter == -1:
            counter = 0
        timing = abs(self.count_down - counter) if self.count_down else counter
        if self.count_down:
            wpm = (len(self.user_input.split()) / timing) * 60
        else:
            wpm = (len(self.user_input.split()) / counter) * 60
        accuracy = (
            sum([c1 == c2 for c1, c2 in zip(self.text, self.user_input)])
            / len(self.user_input)
            * 100
        )
        screen = Text.from_markup(
            f"""
    Typed [green]{len(self.user_input.split())}[/] words and {len(self.user_input)} characters in {timing}s
    Words Per Minute: [green underline bold]{wpm:.2f}[/]
    Characters Per Minute: [purple bold]{(len(self.user_input)/timing) * 60}[/]
    Accuracy: [blue]{accuracy:.2f}%[/]
    Press [magenta]r[/] to restart or Escape to quit
            """,
            justify="center",
        )
        self.display_text = screen

    def delete_text(self) -> None:
        if len(self.user_input) == 0:
            return
        curr_idx = len(self.user_input) - 1
        self.user_input = self.user_input[:-1]
        curr_char = self.text[curr_idx]
        before: Text = self.display_text[:curr_idx]
        after: Text = Text(self.text[curr_idx + 1 :], style="#909090")
        new_char: Text = Text(curr_char, style="black on white")
        self.display_text = before + new_char + after

    def render(self) -> RenderableType:
        return Panel(
            Align.center(
                self.display_text,
                vertical="middle",
                width=os.get_terminal_size()[0] // 2,
            ),
            title="PyType",
        )
