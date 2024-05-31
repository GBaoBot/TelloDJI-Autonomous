import threading

class SafeThread (threading.Thread):
    def __init__(self, target) -> None:
        threading.Thread.__init__(self)
        self.daemon = True
        self.target = target
        self.stop_ev = threading.Event()

    def stop(self) -> None:
        self.stop_ev.set()

    def run(self) -> None:
        while not self.stop_ev.is_set():
            self.target()