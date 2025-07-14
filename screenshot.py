import tkinter as tk
from datetime import datetime
import os
from PIL import ImageGrab

class ScreenshotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screenshot")
        self.root.geometry("300x50")

        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

        tk.Button(
            self.root,
            text="Take Screenshot",
            command=self.take_screenshot,
            font=("Arial", 14),
            relief="raised",
            padx=20,
            pady=10
        ).pack(pady=20)

    def take_screenshot(self):
        self.root.withdraw()
        self.root.after(500, self._capture_screen)

    def _capture_screen(self):
        screenshot = ImageGrab.grab()
        filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
        filepath = os.path.join(self.screenshot_dir, filename)
        screenshot.save(filepath)
        self.root.deiconify()
        print(f"Screenshot saved: {filepath}")

if __name__ == "__main__":
    ScreenshotApp().root.mainloop()
