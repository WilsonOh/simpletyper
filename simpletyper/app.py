import os
import string
import random
from typing import Type
import argparse
from pathlib import Path

from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from textual.app import App
from textual.driver import Driver
from textual.events import Key
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Footer


WORD_LIST_PATH = Path(__file__).parent.resolve() / "words"


counter = 0
stop = False


def load_words(file: str, limit: int) -> str:
    with open(WORD_LIST_PATH / file) as f:
        words = random.choices(f.read().split("\n"), k=limit)
        return (" ".join(words)).strip()


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

    def check_count_down(self) -> None:
        if counter <= 0:
            self.end()

    def on_mount(self) -> None:
        if self.count_down:
            self.set_interval(1, self.check_count_down)

    def update_text(self, c: str) -> None:
        curr_idx = len(self.user_input) + 1
        if curr_idx >= len(self.text):
            self.end()
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

    def end(self) -> None:
        global stop
        global counter
        stop = True
        self.display_text = self.get_WPM()

    def init_text(self) -> None:
        self.display_text = Text.assemble(
            Text(self.text[0], style="black on white"),
            self.text[1:],
            style="#909090",
            justify="center",
        )

    def reset(self) -> None:
        global counter
        global stop
        stop = False
        if self.count_down:
            counter = self.count_down
        else:
            counter = 0
        self.text = load_words(file=self.file, limit=self.num_words)
        self.init_text()
        self.user_input = ""

    def get_WPM(self) -> Text:
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
        return Text.from_markup(
            f"""
    Typed [green]{len(self.user_input.split())}[/] words and {len(self.user_input)} characters in {timing}s
    Words Per Minute: [green underline bold]{wpm:.2f}[/]
    Characters Per Minute: [purple bold]{(len(self.user_input)/timing) * 60}[/]
    Accuracy: [blue]{accuracy:.2f}%[/]
    Press [magenta]r[/] to restart or Escape to quit
            """,
            justify="center",
        )

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


class StopWatchTimer(Widget):

    display_text = Reactive("0s")
    start = False

    def update(self) -> None:
        global counter
        if self.start and not stop:
            counter += 1
            self.display_text = str(counter) + "s"
            self.refresh()

    def on_mount(self) -> None:
        self.set_interval(1, self.update)

    def render(self) -> RenderableType:
        return Panel(Align.center(self.display_text, vertical="middle"), title="Timer")


class CountDownTimer(StopWatchTimer):
    def update(self) -> None:
        global counter
        if self.start and not stop:
            counter -= 1
            self.display_text = str(counter) + "s"
            self.refresh()


class PyType(App):
    def __init__(
        self,
        screen: bool = True,
        driver_class: Type[Driver] | None = None,
        log: str = "",
        log_verbosity: int = 1,
        title: str = "Textual Application",
        *,
        file: str,
        num_words: int,
        count_down: int = 0,
    ):
        super().__init__(screen, driver_class, log, log_verbosity, title)
        self.text_box = TextBox(file=file, num_words=num_words, count_down=count_down)
        if count_down:
            self.timer = CountDownTimer()
            self.timer.display_text = f"{count_down}s"
        else:
            self.timer = StopWatchTimer()
        self.count_down = count_down
        global counter
        counter = count_down

    async def on_load(self) -> None:
        await self.bind("escape", "quit", "Quit the app")
        self.text_box.init_text()

    async def on_mount(self) -> None:
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(self.timer, edge="top", size=5)
        await self.view.dock(self.text_box, edge="top")

    def on_key(self, event: Key) -> None:
        global stop
        if stop:
            global counter
            self.timer.display_text = "GAME OVER"
            if event.key == "r":
                self.text_box.reset()
                self.timer.start = False
                if self.count_down:
                    self.timer.display_text = f"{self.count_down}s"
                else:
                    self.timer.display_text = "0s"
            return
        self.timer.start = True
        if event.key in string.printable:
            self.text_box.update_text(event.key)
        if event.key == "ctrl+h":
            self.text_box.delete_text()


def main():
    word_files = [file.stem for file in WORD_LIST_PATH.iterdir()]
    parser = argparse.ArgumentParser(description="Typing Speed Test Powered by Textual")
    parser.add_argument(
        "-f",
        "--file",
        dest="file",
        help="The word list file",
        choices=word_files,
        type=str,
        default="top2500",
    )
    parser.add_argument(
        "-n",
        "--num_words",
        dest="num_words",
        help="number of words to show on screen",
        type=int,
        default=20,
    )
    parser.add_argument(
        "-t",
        "--timer",
        dest="count_down",
        help="Set a timer to countdown for <n>s",
        type=int,
        default=0,
    )
    args = parser.parse_args()
    PyType.run(file=args.file, num_words=args.num_words, count_down=args.count_down)


if __name__ == "__main__":
    main()
