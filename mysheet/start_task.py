from .task import Task


class StartTask(Task):
    def __init__(self) -> None:
        super().__init__()

    def execute(self) -> None:
        pass
