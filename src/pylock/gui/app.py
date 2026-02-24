import os
import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from ..config import load_password, load_config
from ..locker import lock_file, unlock_file
from .history import HistoryWindow


class DropZone(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.file_path = None
        self.callback = None

        self.label = ctk.CTkLabel(
            self,
            text="点击选择文件",
            font=ctk.CTkFont(size=16),
            text_color="gray",
        )
        self.label.pack(expand=True, fill="both", padx=20, pady=40)

        self.label.bind("<Button-1>", self.on_click)
        self.bind("<Button-1>", self.on_click)

    def on_click(self, event=None):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.set_file(file_path)

    def set_file(self, file_path):
        self.file_path = file_path
        file_name = os.path.basename(file_path)
        self.label.configure(text=file_name, text_color=("gray10", "gray90"))
        if self.callback:
            self.callback(file_path)

    def clear(self):
        self.file_path = None
        self.label.configure(text="点击选择文件", text_color="gray")


class PylockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pylock - 文件加密工具")
        self.geometry("700x600")
        self.resizable(False, False)

        self.selected_file = None
        self.config = None

        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            main_frame,
            text="Pylock 文件加密工具",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=0, pady=(0, 20))

        self.drop_zone = DropZone(
            main_frame, height=120, corner_radius=10, fg_color=("gray93", "gray17")
        )
        self.drop_zone.grid(row=1, column=0, pady=(0, 20), sticky="ew", padx=40)
        self.drop_zone.callback = self.on_file_selected

        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.grid(row=2, column=0, pady=(0, 20), sticky="ew", padx=40)
        input_frame.grid_columnconfigure(0, weight=1)

        password_label = ctk.CTkLabel(input_frame, text="密码:")
        password_label.grid(row=0, column=0, sticky="w")

        self.password_entry = ctk.CTkEntry(
            input_frame, placeholder_text="请输入密码", show="*"
        )
        self.password_entry.grid(row=1, column=0, pady=(5, 0), sticky="ew")

        self.show_password_var = ctk.BooleanVar(value=False)
        show_password_checkbox = ctk.CTkCheckBox(
            input_frame,
            text="显示密码",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
        )
        show_password_checkbox.grid(row=2, column=0, sticky="w", pady=(5, 0))

        mode_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        mode_frame.grid(row=3, column=0, pady=(0, 20))

        self.mode_var = ctk.StringVar(value="lock")

        encrypt_radio = ctk.CTkRadioButton(
            mode_frame,
            text="加密",
            variable=self.mode_var,
            value="lock",
            command=self.on_mode_changed,
        )
        encrypt_radio.grid(row=0, column=0, padx=10)

        decrypt_radio = ctk.CTkRadioButton(
            mode_frame,
            text="解密",
            variable=self.mode_var,
            value="unlock",
            command=self.on_mode_changed,
        )
        decrypt_radio.grid(row=0, column=1, padx=10)

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, pady=(0, 20))

        self.execute_button = ctk.CTkButton(
            button_frame,
            text="开始执行",
            command=self.execute,
            width=200,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.execute_button.grid(row=0, column=0, padx=5)

        history_button = ctk.CTkButton(
            button_frame,
            text="历史记录",
            command=self.open_history,
            width=100,
            height=40,
        )
        history_button.grid(row=0, column=1, padx=5)

        self.progress = ctk.CTkProgressBar(main_frame, width=400)
        self.progress.grid(row=5, column=0, pady=(0, 10))
        self.progress.set(0)

        self.result_text = ctk.CTkTextbox(main_frame, height=120, width=500)
        self.result_text.grid(row=6, column=0, pady=(0, 10))
        self.result_text.configure(state="disabled")

    def load_config(self):
        try:
            self.config = load_config("config.json")
            if self.config.get("password"):
                self.password_entry.insert(0, self.config["password"])
        except Exception:
            pass

    def on_file_selected(self, file_path):
        self.selected_file = file_path
        self.clear_result()

    def on_mode_changed(self):
        self.clear_result()
        self.drop_zone.clear()
        self.selected_file = None

    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def execute(self):
        password = self.password_entry.get()

        if not password:
            self.show_error("请输入密码")
            return

        if self.mode_var.get() == "lock":
            self.execute_lock(password)
        else:
            self.execute_unlock(password)

    def execute_lock(self, password):
        if not self.selected_file:
            self.show_error("请选择要加密的文件")
            return

        self.set_progress(0.1)
        self.execute_button.configure(state="disabled", text="加密中...")
        self.clear_result()

        thread = threading.Thread(target=self._lock_thread, args=(password,))
        thread.start()

    def _lock_thread(self, password):
        try:
            self.after(0, lambda: self.set_progress(0.3))
            result = lock_file(self.selected_file, password)

            self.after(0, lambda: self.set_progress(0.9))
            self.after(
                0,
                lambda: self.show_result(
                    f"加密成功！\n\n"
                    f"原始文件名: {result['original_name']}\n"
                    f"加密后文件名: {result['encrypted_name']}\n"
                    f"输出文件: {result['tar_path']}\n\n"
                    f"提示: {result['tar_path']} 已生成"
                ),
            )
            self.after(0, lambda: self.set_progress(1.0))
        except Exception as e:
            self.after(0, lambda: self.show_error(f"加密失败: {str(e)}"))
        finally:
            self.after(
                0,
                lambda: self.execute_button.configure(state="normal", text="开始执行"),
            )

    def execute_unlock(self, password):
        if not self.selected_file:
            self.show_error("请选择要解密的文件")
            return

        if not self.selected_file.endswith(".tar"):
            self.show_error("请选择 .tar 文件进行解密")
            return

        self.set_progress(0.1)
        self.execute_button.configure(state="disabled", text="解密中...")
        self.clear_result()

        thread = threading.Thread(target=self._unlock_thread, args=(password,))
        thread.start()

    def _unlock_thread(self, password):
        try:
            self.after(0, lambda: self.set_progress(0.3))
            result = unlock_file(self.selected_file, password)

            self.after(0, lambda: self.set_progress(0.9))
            self.after(
                0,
                lambda: self.show_result(
                    f"解密成功！\n\n"
                    f"原始文件名: {result['original_name']}\n"
                    f"解密后文件名: {result['decrypted_name']}\n"
                    f"输出文件: {result['decrypted_path']}\n\n"
                    f"提示: {result['decrypted_path']} 已生成"
                ),
            )
            self.after(0, lambda: self.set_progress(1.0))
        except Exception as e:
            self.after(0, lambda: self.show_error(f"解密失败: {str(e)}"))
        finally:
            self.after(
                0,
                lambda: self.execute_button.configure(state="normal", text="开始执行"),
            )

    def open_history(self):
        history_window = HistoryWindow(self)
        history_window.focus()

    def set_progress(self, value):
        self.progress.set(value)

    def show_result(self, message):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", message)
        self.result_text.configure(state="disabled")

    def show_error(self, message):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", f"错误: {message}")
        self.result_text.configure(state="disabled", text_color="red")

    def clear_result(self):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.configure(state="disabled")


def main():
    app = PylockApp()
    app.mainloop()


if __name__ == "__main__":
    main()
