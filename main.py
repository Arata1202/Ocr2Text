import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import os
from PIL import ImageGrab
import pytesseract
import threading
from config import PROMPT

class ScreenshotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ocr2Gpt")
        self.root.geometry("300x80")

        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

        pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

        self.is_processing = False

        self.screenshot_button = tk.Button(
            self.root,
            text="Take Screenshot",
            command=self.take_screenshot,
            font=("Arial", 14),
            relief="raised",
            padx=20,
            pady=10
        )
        self.screenshot_button.pack(pady=20)

        self._create_result_window()

    def _create_result_window(self):
        self.result_window = tk.Toplevel(self.root)
        self.result_window.title("Ocr2Text")
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

        button_frame = tk.Frame(self.result_window)
        button_frame.pack(pady=(0, 10))

        copy_button = tk.Button(
            button_frame,
            text="Copy All Text",
            command=self._copy_all_text,
            font=("Arial", 12),
            relief="raised",
            padx=10,
            pady=5
        )
        copy_button.pack(side=tk.LEFT, padx=(0, 5))

        clear_button = tk.Button(
            button_frame,
            text="Clear",
            command=self._clear_text,
            font=("Arial", 12),
            relief="raised",
            padx=10,
            pady=5
        )
        clear_button.pack(side=tk.LEFT, padx=(5, 0))

        self._add_result("OCR results will be displayed here.\n")

    def _on_result_window_close(self):
        self.result_window.withdraw()

    def _add_result(self, text):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, text)
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)

    def _copy_all_text(self):
        try:
            all_text = self.text_widget.get("1.0", tk.END).strip()
            text_with_append = all_text + PROMPT
            self.root.clipboard_clear()
            self.root.clipboard_append(text_with_append)
            self.root.update()
            self._show_copy_feedback()
        except Exception as e:
            print(f"Copy error: {e}")

    def _show_copy_feedback(self):
        feedback_label = tk.Label(
            self.result_window,
            text="✓ Text copied to clipboard.",
            font=("Arial", 10),
            fg="green",
            bg=self.result_window.cget("bg")
        )
        feedback_label.pack(pady=(0, 5))

        self.root.after(2000, feedback_label.destroy)

    def _clear_text(self):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.config(state=tk.DISABLED)
        self._add_result("OCR results will be displayed here.\n")

    def take_screenshot(self):
        if self.is_processing:
            return

        self.result_window.deiconify()
        self.root.withdraw()
        self.root.after(500, self._capture_screen)

    def _capture_screen(self):
        try:
            self._set_processing_state(True)

            screenshot = ImageGrab.grab()
            filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
            filepath = os.path.join(self.screenshot_dir, filename)
            screenshot.save(filepath)

            timestamp = datetime.now().strftime("%H:%M:%S")
            self._add_result(f"\n{'='*65}\n[{timestamp}] Screenshot saved: {filename}\n")
            self._add_result("Running OCR...\n" + "="*65 + "\n\n")

            threading.Thread(target=self._process_with_ocr, args=(filepath,), daemon=True).start()

        except Exception as e:
            self._add_result(f"Error: Failed to take screenshot: {str(e)}\n")
            self._set_processing_state(False)
        finally:
            self.root.deiconify()

    def _process_with_ocr(self, image_path):
        try:
            from PIL import Image
            image = Image.open(image_path)
            ocr_text = pytesseract.image_to_string(image, lang='eng+jpn')

            cleaned_text = '\n'.join(line.strip() for line in ocr_text.split('\n') if line.strip())

            timestamp = datetime.now().strftime("%H:%M:%S")
            if cleaned_text:
                self.root.after(0, self._add_result, f"[{timestamp}] OCR Result:\n{cleaned_text}\n")
            else:
                self.root.after(0, self._add_result, f"[{timestamp}] OCR Result: No text detected.\n")

            self.root.after(0, self._add_result, "-" * 50 + "\n")

        except Exception as e:
            self.root.after(0, self._add_result, f"Error: OCR processing failed: {str(e)}\n")
        finally:
            self.root.after(0, self._set_processing_state, False)

    def _set_processing_state(self, is_processing):
        self.is_processing = is_processing
        if is_processing:
            self.screenshot_button.config(
                text="Processing OCR...",
                state="disabled"
            )
        else:
            self.screenshot_button.config(
                text="Take Screenshot",
                state="normal"
            )

if __name__ == "__main__":
    ScreenshotApp().root.mainloop()
