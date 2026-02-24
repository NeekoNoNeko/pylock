import json
import os
import sys
from pathlib import Path

import customtkinter as ctk


def get_program_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent.parent


class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("加密历史记录")
        self.geometry("600x500")
        self.resizable(True, True)

        self.history_file = get_program_dir() / "cipertext.json"

        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self, text="加密历史记录", font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)

        search_label = ctk.CTkLabel(search_frame, text="搜索:")
        search_label.grid(row=0, column=0, padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="输入文件名搜索..."
        )
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        refresh_button = ctk.CTkButton(
            button_frame, text="刷新", command=self.load_history, width=100
        )
        refresh_button.grid(row=0, column=0, padx=(0, 10))

        close_button = ctk.CTkButton(
            button_frame, text="关闭", command=self.destroy, width=100
        )
        close_button.grid(row=0, column=1, sticky="e")

        self.table_frame = ctk.CTkScrollableFrame(
            self, label_text="记录列表", label_font=ctk.CTkFont(size=14, weight="bold")
        )
        self.table_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_frame, text="原始文件名", font=ctk.CTkFont(weight="bold"), anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            header_frame, text="加密文件名", font=ctk.CTkFont(weight="bold"), anchor="w"
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.content_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)

        self.all_data = []

    def load_history(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if not os.path.exists(self.history_file):
            ctk.CTkLabel(
                self.content_frame, text="暂无历史记录", text_color="gray"
            ).grid(row=0, column=0, columnspan=2, pady=20)
            return

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                self.all_data = json.load(f)
        except Exception:
            self.all_data = []

        if not self.all_data:
            ctk.CTkLabel(
                self.content_frame, text="暂无历史记录", text_color="gray"
            ).grid(row=0, column=0, columnspan=2, pady=20)
            return

        self.display_data(self.all_data)

    def display_data(self, data):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        for i, item in enumerate(data):
            original = item.get("original_name", "")
            encrypted = item.get("encrypted_name", "")

            bg_color = ("gray85", "gray17") if i % 2 == 0 else ("gray90", "gray14")

            row_frame = ctk.CTkFrame(self.content_frame, fg_color=bg_color)
            row_frame.grid(row=i, column=0, columnspan=2, sticky="ew", pady=1)
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row_frame, text=original, anchor="w").grid(
                row=0, column=0, sticky="ew", padx=10, pady=5
            )

            ctk.CTkLabel(row_frame, text=encrypted, anchor="w").grid(
                row=0, column=1, sticky="ew", padx=10, pady=5
            )

        if not data:
            ctk.CTkLabel(
                self.content_frame, text="没有匹配的记录", text_color="gray"
            ).grid(row=0, column=0, columnspan=2, pady=20)

    def on_search(self, event):
        search_text = self.search_entry.get().strip().lower()

        if not search_text:
            self.display_data(self.all_data)
            return

        filtered = [
            item
            for item in self.all_data
            if search_text in item.get("original_name", "").lower()
            or search_text in item.get("encrypted_name", "").lower()
        ]

        self.display_data(filtered)
