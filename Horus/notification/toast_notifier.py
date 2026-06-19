import winsound

from winotify import Notification, audio

from notification.notifier_interface import INotifier
from utils.logger_interface import ILogger

class ToastNotifier(INotifier):
    def __init__(self, logger: ILogger):
        self._logger = logger

    def notify(self, message: str) -> None:

        self._toast = Notification(app_id="Horus", 
                            title="Horus message", 
                            msg=message,
                            duration="long")
        self._toast.set_audio(audio.Default, loop=False)
        self._toast.show()
        winsound.Beep(5000, 100)
        winsound.Beep(5000, 100)
        self._logger.info({message})