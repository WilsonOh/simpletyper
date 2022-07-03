import os
import math

from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from textual.reactive import Reactive
from textual.widget import Widget

from simpletyper.events.gamedone import GameDone
from simpletyper.events.progress import ReportProgress
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
        self.keypresses = 0
        self.mispresses = 0

    def update_text(self, c: str) -> None:
        if self.stop:
            return
        prev_idx = len(self.user_input)
        curr_idx = prev_idx + 1
        if curr_idx >= len(self.text):
            self.emit_no_wait(GameDone(self))
            return
        self.user_input += c
        self.keypresses += 1
        curr_char = self.text[curr_idx]
        previous_part = self.display_text[:prev_idx]
        correct = self.text[prev_idx] == self.user_input[prev_idx]
        if not correct:
            self.mispresses += 1
        previous_word = Text(
            self.text[prev_idx],
            style=("green bold" if correct else "red underline"),
        )
        after: Text = self.display_text[curr_idx + 1 :]
        new_char: Text = Text(curr_char, style="black on white")
        self.display_text = Text.assemble(
            previous_part, previous_word, new_char, after, justify="center"
        )
        self.emit_no_wait(ReportProgress(sender=self, completion=len(self.user_input)))

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
        if counter <= 0 and not self.count_down:
            counter = 1
        elif self.count_down and counter < 0:
            counter = 0
        else:
            counter = math.floor(counter)
        timing = abs(self.count_down - counter) if self.count_down else counter
        if timing == 0:
            timing = 1
        uncorrected_mistakes = sum(
            [c1 != c2 for c1, c2 in zip(self.user_input, self.text)]
        )
        raw_wpm = ((len(self.user_input) / 5) / timing) * 60
        net_wpm = (
            ((len(self.user_input) / 5) - uncorrected_mistakes / 5) / timing
        ) * 60
        if net_wpm < 0:
            net_wpm = 0
        accuracy = ((self.keypresses - self.mispresses) / self.keypresses) * 100
        screen = Text.from_markup(
            f"""
    Typed [green]{len(self.user_input.split())}[/] words and [green]{len(self.user_input)}[/] characters in [blue]{timing}s[/]
    Uncorrected Mistakes: {uncorrected_mistakes}
    Gross Words Per Minute: [green underline bold]{raw_wpm:.2f}[/]
    Net Words Per Minute: [green underline bold]{net_wpm:.2f}[/]
    Characters Per Minute: [purple bold]{(len(self.user_input)/timing) * 60:.2f}[/]
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
        self.display_text = Text.assemble(before, new_char, after, justify="center")
        self.emit_no_wait(ReportProgress(sender=self, completion=len(self.user_input)))

    def render(self) -> RenderableType:
        return Panel(
            Align.center(
                self.display_text,
                vertical="middle",
                width=os.get_terminal_size()[0] // 2,
            ),
            title=Text.from_markup("[yellow]SimpleTyper[/]"),
        )
