from textual.message import Message


class ReportProgress(Message):
    def __init__(self, sender, *, completion: int) -> None:
        super().__init__(sender)
        self.completion = completion
