from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget
from simpletyper.events.gamedone import GameDone


class StopWatchTimer(Widget):

    display_text = Reactive("0s")
    start = False
    counter = 0

    def update(self) -> None:
        if self.start:
            self.counter += 1
            self.display_text = str(self.counter) + "s"
            self.refresh()

    def on_mount(self) -> None:
        self.set_interval(1, self.update)

    def render(self) -> RenderableType:
        return Panel(Align.center(self.display_text, vertical="middle"), title="Timer")


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
            self.counter -= 1
            self.display_text = str(self.counter) + "s"
            self.refresh()
