import argparse
import string
from typing import Type

from textual.app import App
from textual.driver import Driver
from textual.events import Key
from textual.widgets import Footer

from simpletyper.events.gamedone import GameDone
from simpletyper.utils.load_words import WORD_LIST_PATH
from simpletyper.widgets.text_box import TextBox
from simpletyper.widgets.timer import CountDownTimer, StopWatchTimer


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
            self.timer = CountDownTimer(count_down)
            self.timer.display_text = f"{count_down}s"
        else:
            self.timer = StopWatchTimer()
        self.count_down = count_down

    async def on_load(self) -> None:
        await self.bind("escape", "quit", "Quit the app")
        self.text_box.init_text()

    async def on_mount(self) -> None:
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(self.timer, edge="top", size=5)
        await self.view.dock(self.text_box, edge="top")

    def on_key(self, event: Key) -> None:
        if self.text_box.stop:
            if event.key == "r":
                self.text_box.reset()
                self.timer.start = False
                if self.count_down:
                    self.timer.counter = self.count_down
                else:
                    self.timer.counter = 0
                self.timer.display_text = str(self.timer.counter) + "s"
            return
        self.timer.start = True
        if event.key in string.printable:
            self.text_box.update_text(event.key)
        if event.key == "ctrl+h":
            self.text_box.delete_text()

    def handle_game_done(self, _: GameDone) -> None:
        self.timer.start = False
        self.text_box.set_end_screen(self.timer.counter)
        self.timer.display_text = "GAME OVER"
        self.text_box.stop = True


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


#
#
# if __name__ == "__main__":
#     main()
