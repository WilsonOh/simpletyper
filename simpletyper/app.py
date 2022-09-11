import argparse
import string
from time import gmtime, strftime

from textual.app import App
from textual.driver import Driver
from textual.events import Key
from textual.widgets import Footer

from simpletyper.events.gamedone import GameDone
from simpletyper.events.progress import ReportProgress
from simpletyper.utils.load_words import WORD_LIST_PATH
from simpletyper.widgets.text_box import TextBox
from simpletyper.widgets.hud import CountDownTimer, StopWatchTimer, Progress


class PyType(App):
    def __init__(
        self,
        screen: bool = True,
        driver_class: type[Driver] | None = None,
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
        else:
            self.timer = StopWatchTimer()
        self.timer.timer_display = strftime(
            "%M minutes and %S seconds", gmtime(count_down)
        )
        self.progress_bar = Progress(num_words=len(self.text_box.text))
        self.count_down = count_down

    async def on_load(self) -> None:
        await self.bind("escape", "quit", "Quit the app")
        await self.bind("ctrl+r", "reset", "Reset")
        self.text_box.init_text()

    async def on_mount(self) -> None:
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(self.timer, size=5)
        await self.view.dock(self.progress_bar, size=5)
        await self.view.dock(self.text_box)

    def action_reset(self) -> None:
        self.timer.start = False
        self.text_box.reset()
        if self.count_down:
            self.timer.counter = self.count_down
        else:
            self.timer.counter = 0
        self.progress_bar.completion = 0
        self.timer.timer_display = strftime(
            "%M minutes and %S seconds", gmtime(self.count_down)
        )

    def on_key(self, event: Key) -> None:
        if self.text_box.stop:
            self.timer.start = False
            if event.key == "r":
                self.action_reset()
        else:
            self.timer.start = True
            if event.key in string.printable:
                self.text_box.update_text(event.key)
            if event.key == "ctrl+h":
                self.text_box.delete_text()

    def handle_game_done(self, _: GameDone) -> None:
        self.timer.start = False
        self.text_box.set_end_screen(self.timer.counter)
        self.timer.timer_display = "GAME OVER"
        self.text_box.stop = True

    def handle_report_progress(self, event: ReportProgress) -> None:
        self.progress_bar.completion = event.completion


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
        default="top250",
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
    PyType.run(
        file=args.file,
        num_words=args.num_words,
        count_down=args.count_down,
        log="textual.log",
    )


if __name__ == "__main__":
    main()
