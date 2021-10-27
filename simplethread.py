
from threading import Thread


class SimpleThread:

    def __init__(self):
        self._running = False
        self._thread = Thread(target=self.thread_loop)

    def __del__(self):
        if hasattr(self, "_thread"):
            self.stop()

    def start(self):
        if not hasattr(self, "_thread"):
            self._thread = Thread(target=self.thread_loop)

        self._running = True
        self._thread.start()

    def stop(self):
        if self._running:
            self._running = False
            self._thread.join()
            del self._thread

    def thread_loop(self):
        pass
