"""The refusal the real package raises: `problems` is every problem, one line each."""


class Failure(Exception):
    def __init__(self, problems):
        if isinstance(problems, str):
            problems = [problems]
        self.problems = list(problems)
        super().__init__("\n".join(self.problems))
