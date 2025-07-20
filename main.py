import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import os
import base64
from PIL import ImageGrab
from openai import OpenAI
from dotenv import load_dotenv
import threading

load_dotenv()

class ScreenshotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ocr2Gpt")
        self.root.geometry("300x80")

        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        tk.Button(
            self.root,
            text="Take screenshot",
            command=self.take_screenshot,
            font=("Arial", 14),
            relief="raised",
            padx=20,
            pady=10
        ).pack(pady=20)

        self._create_result_window()

    def _create_result_window(self):
        self.result_window = tk.Toplevel(self.root)
        self.result_window.title("Ocr2Gpt")
        self.result_window.geometry("600x500")
        self.result_window.protocol("WM_DELETE_WINDOW", self._on_result_window_close)
        self.text_widget = scrolledtext.ScrolledText(
            self.result_window,
            wrap=tk.WORD,
            font=("Arial", 14),
            padx=10,
            pady=10
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

    def _on_result_window_close(self):
        self.result_window.withdraw()

    def _add_result(self, text):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, text)
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)

    def take_screenshot(self):
        self.result_window.deiconify()
        self.root.withdraw()
        self.root.after(500, self._capture_screen)

    def _capture_screen(self):
        try:
            screenshot = ImageGrab.grab()
            filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
            filepath = os.path.join(self.screenshot_dir, filename)
            screenshot.save(filepath)

            timestamp = datetime.now().strftime("%H:%M:%S")
            self._add_result(f"\n=================================================================\n[{timestamp}] Screenshot saved: {filename}\n")
            self._add_result("Processing OCR...\n=================================================================\n\n")

            threading.Thread(target=self._process_with_chatgpt, args=(filepath,), daemon=True).start()

        except Exception as e:
            error_msg = f"Failed to take screenshot: {str(e)}"
            self._add_result(f"Error: {error_msg}\n")
        finally:
            self.root.deiconify()

    def _process_with_chatgpt(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{os.getenv('PROMPT')}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )

            result_text = response.choices[0].message.content
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.root.after(0, self._add_result, f"[{timestamp}] OCR Result:\n{result_text}\n")
            self.root.after(0, self._add_result, "-" * 50 + "\n")

        except Exception as e:
            error_msg = f"Error processing ChatGPT API: {str(e)}"
            self.root.after(0, self._add_result, f"Error: {error_msg}\n")

if __name__ == "__main__":
    ScreenshotApp().root.mainloop()
