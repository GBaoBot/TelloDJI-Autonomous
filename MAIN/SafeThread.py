import threading

class SafeThread (threading.Thread):
    def __init__(self, target) -> None:
        threading.Thread.__init__(self)
        self.daemon = True
        self.target = target
        self.stopEvent = threading.Event()

    def stop(self) -> None:
        self.stopEvent.set()

    def run(self) -> None:
        while not self.stopEvent.is_set():
            self.target()