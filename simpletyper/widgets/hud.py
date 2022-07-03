import os
from time import gmtime, strftime

from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.text import Text
from textual.reactive import Reactive
from textual.widget import Widget

from simpletyper.events.gamedone import GameDone


class Progress(Widget):

    completion = Reactive(0)

    def __init__(self, num_words, name: str | None = None) -> None:
        super().__init__(name)
        self.num_words = num_words - 1

    def render(self) -> RenderableType:
        return Panel(
            Align.center(
                ProgressBar(
                    completed=self.completion,
                    total=self.num_words,
                    complete_style="green",
                    width=int(os.get_terminal_size()[0] * 0.7),
                ),
                vertical="middle",
            ),
            title=Text.from_markup(
                f"[bold green]Progress:[/] [blue]{(self.completion/self.num_words) * 100:.2f}%[/]"
            ),
        )


class StopWatchTimer(Widget):

    start = False
    counter = 0
    timer_display = Reactive("")
    interval = 0.1

    def update(self) -> None:
        if self.start:
            self.counter += self.interval
            self.timer_display = strftime(
                "%M minutes and %S seconds", gmtime(self.counter)
            )
            self.refresh()

    def on_mount(self) -> None:
        self.set_interval(0.1, self.update)

    def render(self) -> RenderableType:
        text = f"[bold green]Time:[/] [yellow]{self.timer_display}[/]"
        # [bold green]WPM:[/] [yellow]{50}[/]  [bold green]Accuracy:[/] [yellow]{50}%"
        return Panel(
            Align.center(
                Text.from_markup(text, justify="center"), vertical="middle", width=100
            )
        )


class CountDownTimer(StopWatchTimer):
    def __init__(
        self,
        count_down: int,
        name: str | None = None,
    ) -> None:
        super().__init__(name)
        self.counter = count_down

    def update(self) -> None:
        if self.start:
            if self.counter <= 0:
                self.emit_no_wait(GameDone(self))
                self.start = False
            self.counter -= self.interval
            self.timer_display = strftime(
                "%M minutes and %S seconds", gmtime(self.counter)
            )
            self.refresh()
