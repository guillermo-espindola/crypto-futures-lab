import time

from threading import Thread

from app.heartbeat_event import HeartbeatEvent

class Heartbeat:
    def __init__(self, interval_seconds: int):
        self._interval_seconds = interval_seconds
        self._is_running = False
        self._thread: Thread = None

        self.beat_event = HeartbeatEvent()

    def start(self):
        self._is_running = True
        self._thread = Thread(target=self._run_beat_loop, daemon=True)
        self._thread.start()

    def _run_beat_loop(self):
        while self._is_running:
            time.sleep(self._interval_seconds)
            if self._is_running:
                current_timestamp = int(time.time() * 1000)
                self.beat_event.trigger(current_timestamp)

    def stop(self):
        self._is_running = False