class NoLogs():
    def __init__(self):
        self.opened = False

    def open(self):
        self.opened = True

    def isOpen(self):
        return self.opened

    def close(self):
        self.opened = False

    def post(self, start, end, tests, results):
        pass