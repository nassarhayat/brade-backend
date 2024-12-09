from collections import defaultdict

class SessionContext:
    def __init__(self):
        self.steps = []
        self.variables = defaultdict(str)
        self.context_document_ids = []

    def add_step(self, step):
        self.steps.append(step)

    def get_last_step_output(self):
        if self.steps:
            return self.steps[-1]["output"]
        return None

    def set_context_document_ids(self, document_ids):
        self.context_document_ids = document_ids