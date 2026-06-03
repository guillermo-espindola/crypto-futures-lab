import winsound
import tkinter as tk
from tkinter import messagebox
from notification.notifier_interface import INotifier

class AlertNotifier(INotifier):
    def notify(self, message: str) -> None:
        winsound.Beep(5000, 700)
        winsound.Beep(5000, 700)
        winsound.Beep(5000, 700)

        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showinfo("Alert", message)