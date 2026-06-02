import os
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from data_manager import DataManager
from fatigue_calculator import FatigueCalculator
from help_texts import HELP_TEXTS, STANDARD_GUIDE
from standards import calculate_exercise_load, format_standard_summary, get_personal_standards


FONT = "Microsoft YaHei UI"
BG = "#eef3f8"
CARD = "#ffffff"
CARD_SOFT = "#f7f9fc"
TEXT = "#172033"
MUTED = "#64748b"
PRIMARY = "#2563eb"
PRIMARY_HOVER = "#1d4ed8"
BORDER = "#d9e2ec"
GOOD = "#16a34a"
MILD = "#0ea5e9"
MEDIUM = "#f97316"
DANGER = "#dc2626"

os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.getcwd(), ".matplotlib-cache"))
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class ModernFatigueApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("个人疲劳度分析")
        self.geometry("1240x780")
        self.minsize(1060, 680)
        self.configure(fg_color=BG)

        self.users = []
        self.selected_user = tk.StringVar()
        self.profile_vars = {}
        self.entry_vars = {}
        self.current_user = None
        self.record_checks = {}

        self.result_value_label = None
        self.status_label = None
        self.exercise_load_label = None
        self.suggestion_frame = None
        self.history_frame = None
        self.chart_frame = None
        self.chart_canvas = None

        self._show_login()

    def _clear(self):
        for child in self.winfo_children():
            child.destroy()

    def _card(self, parent, **kwargs):
        return ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER, **kwargs)

    def _soft_card(self, parent, **kwargs):
        return ctk.CTkFrame(parent, fg_color=CARD_SOFT, corner_radius=14, **kwargs)

    def _label(self, parent, text, size=13, weight="normal", color=TEXT, **kwargs):
        return ctk.CTkLabel(parent, text=text, text_color=color, font=(FONT, size, weight), **kwargs)

    def _button(self, parent, text, command=None, primary=False, **kwargs):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=38,
            corner_radius=12,
            fg_color=PRIMARY if primary else "#e8eef7",
            hover_color=PRIMARY_HOVER if primary else "#dce7f5",
            text_color="#ffffff" if primary else TEXT,
            font=(FONT, 13, "bold" if primary else "normal"),
            **kwargs,
        )

    def _show_login(self):
        self._clear()
        self.users = DataManager.load_users()
        names = [self._format_user_name(user) for user in self.users]
        self.selected_user.set(names[0] if names else "暂无用户")

        shell = ctk.CTkFrame(self, fg_color=BG)
        shell.pack(fill=tk.BOTH, expand=True, padx=42, pady=34)

        self._label(shell, "个人疲劳度分析", size=34, weight="bold").pack(anchor=tk.W)
        self._label(shell, "选择用户进入系统；如果还没有用户，请先创建个人档案。", size=14, color=MUTED).pack(anchor=tk.W, pady=(8, 0))

        card = self._card(shell)
        card.pack(fill=tk.X, padx=130, pady=(38, 0))
        card.grid_columnconfigure(0, weight=1)

        self._label(card, "登录", size=24, weight="bold").grid(row=0, column=0, sticky="w", padx=28, pady=(28, 0))
        self._label(card, "每个用户的疲劳记录会单独保存，切换用户后只显示该用户自己的记录。", size=13, color=MUTED).grid(
            row=1, column=0, sticky="w", padx=28, pady=(8, 22)
        )

        form = ctk.CTkFrame(card, fg_color=CARD)
        form.grid(row=2, column=0, sticky="ew", padx=28)
        form.grid_columnconfigure(1, weight=1)
        self._label(form, "用户", size=14).grid(row=0, column=0, sticky="w", padx=(0, 12))
        user_select = ctk.CTkOptionMenu(
            form,
            variable=self.selected_user,
            values=names if names else ["暂无用户"],
            height=38,
            corner_radius=12,
            fg_color=CARD_SOFT,
            button_color="#dbeafe",
            button_hover_color="#bfdbfe",
            text_color=TEXT,
            font=(FONT, 13),
            dropdown_font=(FONT, 13),
        )
        user_select.grid(row=0, column=1, sticky="ew")
        if not names:
            user_select.configure(state="disabled")

        helper = "当前没有用户，请点击“新建用户”。" if not names else "选择用户后点击“进入系统”。"
        self._label(card, helper, size=13, color=MUTED).grid(row=3, column=0, sticky="w", padx=28, pady=(14, 0))

        actions = ctk.CTkFrame(card, fg_color=CARD)
        actions.grid(row=4, column=0, sticky="ew", padx=28, pady=(22, 28))
        actions.grid_columnconfigure(0, weight=1)
        self._button(actions, "新建用户", command=self._show_create_user, width=130).grid(row=0, column=0, sticky="w")
        enter_button = self._button(actions, "进入系统", command=self._enter_app, primary=True, width=140)
        enter_button.grid(row=0, column=1, sticky="e")
        if not names:
            enter_button.configure(state="disabled")

    def _show_create_user(self):
        self._clear()
        self.profile_vars = {
            "name": tk.StringVar(),
            "gender": tk.StringVar(value="男"),
            "age": tk.StringVar(value="18"),
            "height_cm": tk.StringVar(value="170"),
            "weight_kg": tk.StringVar(value="60"),
            "activity_level": tk.StringVar(value="普通"),
            "role": tk.StringVar(value="学生"),
        }

        shell = ctk.CTkFrame(self, fg_color=BG)
        shell.pack(fill=tk.BOTH, expand=True, padx=42, pady=34)

        self._label(shell, "新建用户档案", size=32, weight="bold").pack(anchor=tk.W)
        self._label(shell, "填写基础信息后，系统会按年龄、体重和活动水平生成个人疲劳评估标准。", size=14, color=MUTED).pack(anchor=tk.W, pady=(8, 0))

        card = self._card(shell)
        card.pack(fill=tk.X, padx=120, pady=(30, 0))
        card.grid_columnconfigure(1, weight=1)

        self._profile_entry(card, 0, "昵称", "name", "例如：小明")
        self._profile_option(card, 1, "性别", "gender", ["男", "女", "其他"], "gender")
        self._profile_entry(card, 2, "年龄", "age", "12-100", "age")
        self._profile_entry(card, 3, "身高(cm)", "height_cm", "例如：170")
        self._profile_entry(card, 4, "体重(kg)", "weight_kg", "例如：60", "weight")
        self._profile_option(card, 5, "活动水平", "activity_level", ["久坐", "普通", "活跃"], "personal_standard")
        self._profile_option(card, 6, "身份类型", "role", ["学生", "上班族", "其他"])

        actions = ctk.CTkFrame(card, fg_color=CARD)
        actions.grid(row=7, column=0, columnspan=3, sticky="ew", padx=28, pady=(22, 28))
        actions.grid_columnconfigure(0, weight=1)
        self._button(actions, "返回登录", command=self._show_login, width=130).grid(row=0, column=0, sticky="w")
        self._button(actions, "保存用户", command=self._save_new_user, primary=True, width=130).grid(row=0, column=1, sticky="e")

    def _show_main_shell(self):
        self._clear()
        self._init_entry_vars()
        self.record_checks = {}

        shell = ctk.CTkFrame(self, fg_color=BG)
        shell.pack(fill=tk.BOTH, expand=True, padx=24, pady=22)
        shell.grid_columnconfigure(1, weight=1)
        shell.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(shell, fg_color=BG)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        header.grid_columnconfigure(0, weight=1)
        self._label(header, "个人疲劳度分析", size=28, weight="bold").grid(row=0, column=0, sticky="w")
        self._label(header, self._format_current_user_summary(), size=13, color=MUTED).grid(row=1, column=0, sticky="w", pady=(4, 0))
        self._button(header, "标准说明", command=self._show_standard_guide, width=110).grid(row=0, column=1, rowspan=2, padx=(0, 10))
        self._button(header, "切换用户", command=self._show_login, width=110).grid(row=0, column=2, rowspan=2)

        left = self._card(shell)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        left.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(shell, fg_color=BG)
        right.grid(row=1, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=1)
        right.grid_rowconfigure(3, weight=1)

        self._build_input_panel(left)
        self._build_standard_card(right)
        self._build_result_card(right)
        self._build_chart_card(right)
        self._build_history_card(right)
        self._bind_entry_updates()
        self._update_preview()

    def _build_input_panel(self, parent):
        title = ctk.CTkFrame(parent, fg_color=CARD)
        title.grid(row=0, column=0, sticky="ew", padx=22, pady=(22, 12))
        self._label(title, "今日录入", size=21, weight="bold").pack(side=tk.LEFT)
        self._help_button(title, "suggestions").pack(side=tk.LEFT, padx=(8, 0))
        self._label(parent, "录入今日睡眠、工作、运动和身体状态，结果会实时刷新。", size=12, color=MUTED).grid(
            row=1, column=0, sticky="w", padx=22, pady=(0, 14)
        )

        rows = ctk.CTkFrame(parent, fg_color=CARD)
        rows.grid(row=2, column=0, sticky="ew", padx=22)
        rows.grid_columnconfigure(1, weight=1)

        self._data_entry(rows, 0, "睡眠时间", "sleep_hours", "小时", "sleep_hours")
        self._data_option(rows, 1, "睡眠质量", "sleep_quality", ["差", "一般", "好"], "sleep_quality")
        self._data_entry(rows, 2, "工作/学习", "work_hours", "小时", "work_hours")
        self._data_entry(rows, 3, "屏幕娱乐", "screen_hours", "小时", "screen_hours")
        self._data_entry(rows, 4, "饮水量", "water_ml", "ml", "water_ml")
        self._data_entry(rows, 5, "运动时间", "exercise_minutes", "分钟", "exercise_minutes")
        self._data_option(rows, 6, "运动强度", "exercise_intensity", ["低强度", "中等强度", "高强度"], "exercise_intensity")
        self._data_entry(rows, 7, "心情评分", "mood_score", "1-10", "mood_score")
        self._data_option(rows, 8, "身体不适", "body_status", ["无", "轻微不适", "明显不适"], "body_status")
        self._data_option(rows, 9, "特殊状态", "special_status", ["无", "生理期", "熬夜后", "感冒恢复期"], "special_status")

        actions = ctk.CTkFrame(parent, fg_color=CARD)
        actions.grid(row=3, column=0, sticky="ew", padx=22, pady=(18, 22))
        actions.grid_columnconfigure(0, weight=1)
        self._button(actions, "检查输入", command=self._check_entry_form, width=110).grid(row=0, column=0, sticky="w")
        self._button(actions, "保存今日记录", command=self._save_today_record, primary=True, width=140).grid(row=0, column=1, sticky="e")

    def _build_standard_card(self, parent):
        standards = get_personal_standards(self.current_user or {})
        panel = self._card(parent)
        panel.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        panel.grid_columnconfigure((0, 1, 2), weight=1)

        header = ctk.CTkFrame(panel, fg_color=CARD)
        header.grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(18, 10))
        self._label(header, "个人标准", size=19, weight="bold").pack(side=tk.LEFT)
        self._help_button(header, "personal_standard").pack(side=tk.LEFT, padx=(8, 0))

        items = [
            ("年龄分组", standards["age_group"]),
            ("建议睡眠", f"{standards['sleep_min']}-{standards['sleep_max']} 小时"),
            ("建议饮水", f"{standards['water_min']}-{standards['water_max']} ml"),
            ("运动量目标", str(standards["exercise_load_target"])),
            ("工作/学习上限", f"{standards['work_hours_max']} 小时"),
            ("屏幕娱乐上限", f"{standards['screen_hours_max']} 小时"),
        ]
        for index, (label, value) in enumerate(items):
            item = self._soft_card(panel)
            item.grid(row=1 + index // 3, column=index % 3, sticky="ew", padx=(20 if index % 3 == 0 else 8, 20 if index % 3 == 2 else 0), pady=(0, 16))
            self._label(item, label, size=12, color=MUTED).pack(anchor=tk.W, padx=12, pady=(10, 0))
            self._label(item, value, size=16, weight="bold").pack(anchor=tk.W, padx=12, pady=(3, 10))

    def _build_result_card(self, parent):
        panel = self._card(parent)
        panel.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        panel.grid_columnconfigure(1, weight=1)

        header = ctk.CTkFrame(panel, fg_color=CARD)
        header.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(18, 10))
        self._label(header, "疲劳评估", size=19, weight="bold").pack(side=tk.LEFT)
        self._help_button(header, "fatigue_score").pack(side=tk.LEFT, padx=(8, 0))

        self.result_value_label = self._label(panel, "--", size=42, weight="bold")
        self.result_value_label.grid(row=1, column=0, rowspan=2, sticky="w", padx=(20, 18), pady=(0, 14))
        self.status_label = self._label(panel, "等待录入", size=17, weight="bold")
        self.status_label.grid(row=1, column=1, sticky="sw")
        self.exercise_load_label = self._label(panel, "运动量：--", size=13, color=MUTED)
        self.exercise_load_label.grid(row=2, column=1, sticky="nw", pady=(4, 14))

        suggestion_header = ctk.CTkFrame(panel, fg_color=CARD)
        suggestion_header.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(2, 8))
        self._label(suggestion_header, "恢复建议", size=15, weight="bold").pack(side=tk.LEFT)
        self._help_button(suggestion_header, "suggestions").pack(side=tk.LEFT, padx=(8, 0))
        self.suggestion_frame = ctk.CTkFrame(panel, fg_color=CARD)
        self.suggestion_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 16))

    def _build_chart_card(self, parent):
        panel = self._card(parent)
        panel.grid(row=2, column=0, sticky="nsew", pady=(0, 14))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        self._label(panel, "趋势图", size=19, weight="bold").grid(row=0, column=0, sticky="w", padx=20, pady=(18, 10))
        self.chart_frame = self._soft_card(panel)
        self.chart_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 18))
        self._refresh_chart()

    def _build_history_card(self, parent):
        panel = self._card(parent)
        panel.grid(row=3, column=0, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(panel, fg_color=CARD)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        header.grid_columnconfigure(0, weight=1)
        self._label(header, "历史记录", size=19, weight="bold").grid(row=0, column=0, sticky="w")
        self._button(header, "删除选中", command=self._delete_selected_records, width=100).grid(row=0, column=1, padx=(8, 0))
        self._button(header, "清空当前用户", command=self._clear_current_user_records, width=120).grid(row=0, column=2, padx=(8, 0))

        self.history_frame = ctk.CTkScrollableFrame(panel, fg_color=CARD_SOFT, corner_radius=14)
        self.history_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 18))
        self._refresh_history()

    def _profile_entry(self, parent, row, label, key, placeholder, help_key=None):
        self._field_label(parent, row, label, help_key)
        entry = ctk.CTkEntry(parent, textvariable=self.profile_vars[key], height=38, corner_radius=12, fg_color=CARD_SOFT, text_color=TEXT, border_color=BORDER)
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 12), pady=8)
        self._label(parent, placeholder, size=12, color=MUTED).grid(row=row, column=2, sticky="w", padx=(0, 28))

    def _profile_option(self, parent, row, label, key, values, help_key=None):
        self._field_label(parent, row, label, help_key)
        menu = ctk.CTkOptionMenu(parent, variable=self.profile_vars[key], values=values, height=38, corner_radius=12, fg_color=CARD_SOFT, button_color="#dbeafe", button_hover_color="#bfdbfe", text_color=TEXT)
        menu.grid(row=row, column=1, sticky="ew", padx=(0, 12), pady=8)

    def _field_label(self, parent, row, label, help_key=None):
        frame = ctk.CTkFrame(parent, fg_color=CARD)
        frame.grid(row=row, column=0, sticky="w", padx=(28, 14), pady=8)
        self._label(frame, label, size=13).pack(side=tk.LEFT)
        if help_key:
            self._help_button(frame, help_key).pack(side=tk.LEFT, padx=(7, 0))

    def _data_entry(self, parent, row, label, key, unit, help_key=None):
        self._field_label(parent, row, label, help_key)
        entry = ctk.CTkEntry(parent, textvariable=self.entry_vars[key], height=34, corner_radius=11, fg_color=CARD_SOFT, text_color=TEXT, border_color=BORDER)
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 8), pady=5)
        self._label(parent, unit, size=12, color=MUTED).grid(row=row, column=2, sticky="w", pady=5)

    def _data_option(self, parent, row, label, key, values, help_key=None):
        self._field_label(parent, row, label, help_key)
        menu = ctk.CTkOptionMenu(parent, variable=self.entry_vars[key], values=values, height=34, corner_radius=11, fg_color=CARD_SOFT, button_color="#dbeafe", button_hover_color="#bfdbfe", text_color=TEXT)
        menu.grid(row=row, column=1, columnspan=2, sticky="ew", pady=5)

    def _help_button(self, parent, help_key):
        return ctk.CTkButton(
            parent,
            text="?",
            width=24,
            height=24,
            corner_radius=12,
            fg_color="#dbeafe",
            hover_color="#bfdbfe",
            text_color=PRIMARY,
            font=(FONT, 12, "bold"),
            command=lambda: self._show_help(help_key),
        )

    def _show_help(self, help_key):
        help_item = HELP_TEXTS.get(help_key)
        if not help_item:
            messagebox.showinfo("说明", "暂无说明内容。")
            return

        window = ctk.CTkToplevel(self)
        window.title(help_item["title"])
        window.geometry("480x300")
        window.transient(self)
        window.grab_set()
        window.configure(fg_color=BG)

        panel = self._card(window)
        panel.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
        self._label(panel, help_item["title"], size=20, weight="bold").pack(anchor=tk.W, padx=20, pady=(20, 10))
        self._label(panel, help_item["content"], size=14, color=MUTED, wraplength=410, justify=tk.LEFT).pack(anchor=tk.W, fill=tk.X, padx=20)
        self._button(panel, "我知道了", command=window.destroy, primary=True, width=110).pack(anchor=tk.E, padx=20, pady=(18, 20))

    def _show_standard_guide(self):
        window = ctk.CTkToplevel(self)
        window.title("标准说明")
        window.geometry("680x560")
        window.transient(self)
        window.grab_set()
        window.configure(fg_color=BG)

        panel = self._card(window)
        panel.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
        self._label(panel, "标准说明", size=22, weight="bold").pack(anchor=tk.W, padx=20, pady=(20, 6))
        self._label(panel, "集中说明疲劳等级、年龄分组、睡眠、饮水、运动和建议规则。", size=13, color=MUTED).pack(anchor=tk.W, padx=20, pady=(0, 14))

        textbox = ctk.CTkTextbox(panel, fg_color=CARD_SOFT, text_color=TEXT, corner_radius=14, font=(FONT, 13), wrap=tk.WORD)
        textbox.pack(fill=tk.BOTH, expand=True, padx=20)
        for title, body in STANDARD_GUIDE:
            textbox.insert(tk.END, f"{title}\n{body}\n\n")
        textbox.configure(state="disabled")
        self._button(panel, "关闭", command=window.destroy, primary=True, width=100).pack(anchor=tk.E, padx=20, pady=16)

    def _init_entry_vars(self):
        self.entry_vars = {
            "sleep_hours": tk.StringVar(value="7.5"),
            "sleep_quality": tk.StringVar(value="一般"),
            "work_hours": tk.StringVar(value="8"),
            "screen_hours": tk.StringVar(value="2"),
            "water_ml": tk.StringVar(value="2000"),
            "exercise_minutes": tk.StringVar(value="30"),
            "exercise_intensity": tk.StringVar(value="中等强度"),
            "mood_score": tk.StringVar(value="8"),
            "body_status": tk.StringVar(value="无"),
            "special_status": tk.StringVar(value="无"),
        }

    def _bind_entry_updates(self):
        for var in self.entry_vars.values():
            var.trace_add("write", lambda *_args: self._update_preview())

    def _check_entry_form(self):
        try:
            self._read_entry_form()
        except ValueError as error:
            messagebox.showwarning("输入有误", str(error))
            return
        messagebox.showinfo("输入有效", "今日录入数据格式正确。")

    def _read_entry_form(self):
        return {
            "sleep_hours": self._read_entry_number("sleep_hours", "睡眠时间", 0, 14),
            "sleep_quality": self.entry_vars["sleep_quality"].get(),
            "work_hours": self._read_entry_number("work_hours", "工作/学习时间", 0, 18),
            "screen_hours": self._read_entry_number("screen_hours", "屏幕娱乐时间", 0, 16),
            "water_ml": self._read_entry_number("water_ml", "饮水量", 0, 6000, integer=True),
            "exercise_minutes": self._read_entry_number("exercise_minutes", "运动时间", 0, 240, integer=True),
            "exercise_intensity": self.entry_vars["exercise_intensity"].get(),
            "mood_score": self._read_entry_number("mood_score", "心情评分", 1, 10, integer=True),
            "body_status": self.entry_vars["body_status"].get(),
            "special_status": self.entry_vars["special_status"].get(),
        }

    def _read_entry_number(self, key, label, min_value, max_value, integer=False):
        raw = self.entry_vars[key].get().strip()
        try:
            value = int(raw) if integer else float(raw)
        except ValueError as exc:
            raise ValueError(f"{label}必须是数字。") from exc
        if value < min_value or value > max_value:
            raise ValueError(f"{label}需要在 {min_value} 到 {max_value} 之间。")
        return value

    def _read_profile_form(self):
        name = self.profile_vars["name"].get().strip()
        if not name:
            raise ValueError("请输入昵称。")
        return {
            "name": name,
            "gender": self.profile_vars["gender"].get(),
            "age": self._read_profile_number("age", "年龄", 12, 100, integer=True),
            "height_cm": self._read_profile_number("height_cm", "身高", 80, 230),
            "weight_kg": self._read_profile_number("weight_kg", "体重", 25, 250),
            "activity_level": self.profile_vars["activity_level"].get(),
            "role": self.profile_vars["role"].get(),
        }

    def _read_profile_number(self, key, label, min_value, max_value, integer=False):
        raw = self.profile_vars[key].get().strip()
        try:
            value = int(raw) if integer else float(raw)
        except ValueError as exc:
            raise ValueError(f"{label}必须是数字。") from exc
        if value < min_value or value > max_value:
            raise ValueError(f"{label}需要在 {min_value} 到 {max_value} 之间。")
        return value

    def _update_preview(self):
        if self.result_value_label is None:
            return
        try:
            data = self._read_entry_form()
        except ValueError:
            self.result_value_label.configure(text="--", text_color=TEXT)
            self.status_label.configure(text="等待有效输入", text_color=MUTED)
            self.exercise_load_label.configure(text="运动量：--")
            self._render_suggestions([("输入待完善", "请检查左侧表单，所有数值需要在合理范围内。")])
            return

        standards = get_personal_standards(self.current_user or {})
        fatigue = FatigueCalculator.calculate_fatigue(data, profile=self.current_user, standards=standards)
        status = FatigueCalculator.get_status(fatigue)
        color = self._get_status_color(fatigue)
        exercise_load = calculate_exercise_load(data["exercise_minutes"], data["exercise_intensity"])

        self.result_value_label.configure(text=f"{fatigue:g}", text_color=color)
        self.status_label.configure(text=status, text_color=color)
        self.exercise_load_label.configure(text=f"运动量：{exercise_load:g} / 目标 {standards['exercise_load_target']}")
        self._render_suggestions(FatigueCalculator.build_suggestions(data, fatigue, standards))

    def _render_suggestions(self, suggestions):
        if self.suggestion_frame is None:
            return
        for child in self.suggestion_frame.winfo_children():
            child.destroy()
        for title, detail in suggestions:
            item = self._soft_card(self.suggestion_frame)
            item.pack(fill=tk.X, pady=(0, 8))
            self._label(item, title, size=13, weight="bold").pack(anchor=tk.W, padx=12, pady=(10, 0))
            self._label(item, detail, size=12, color=MUTED, wraplength=660, justify=tk.LEFT).pack(anchor=tk.W, padx=12, pady=(2, 10))

    def _save_today_record(self):
        try:
            data = self._read_entry_form()
        except ValueError as error:
            messagebox.showwarning("输入有误", str(error))
            return

        standards = get_personal_standards(self.current_user or {})
        fatigue = FatigueCalculator.calculate_fatigue(data, profile=self.current_user, standards=standards)
        status = FatigueCalculator.get_status(fatigue)
        exercise_load = calculate_exercise_load(data["exercise_minutes"], data["exercise_intensity"])
        DataManager.save_data(
            {
                "user_id": self.current_user["user_id"],
                **data,
                "exercise_load": exercise_load,
                "fatigue": fatigue,
                "status": status,
                "standard_summary": format_standard_summary(standards),
            }
        )
        self._update_preview()
        self._refresh_history()
        self._refresh_chart()
        messagebox.showinfo("保存成功", "今日疲劳记录已保存。")

    def _refresh_history(self):
        if self.history_frame is None or not self.current_user:
            return
        for child in self.history_frame.winfo_children():
            child.destroy()
        self.record_checks = {}

        records = DataManager.load_records(self.current_user["user_id"])
        if not records:
            self._label(self.history_frame, "暂无历史记录，保存今日记录后会显示在这里。", size=13, color=MUTED).pack(anchor=tk.CENTER, pady=28)
            return

        for record in reversed(records):
            selected = tk.BooleanVar(value=False)
            self.record_checks[record["record_id"]] = selected
            item = ctk.CTkFrame(self.history_frame, fg_color=CARD, corner_radius=12, border_width=1, border_color=BORDER)
            item.pack(fill=tk.X, pady=(0, 8), padx=2)
            ctk.CTkCheckBox(item, text="", variable=selected, width=24, checkbox_width=18, checkbox_height=18).grid(row=0, column=0, rowspan=2, padx=(12, 4), pady=12)
            self._label(item, f"{record['date']}    疲劳值 {record['fatigue']}    {record['status']}", size=13, weight="bold").grid(row=0, column=1, sticky="w", pady=(10, 0))
            detail = (
                f"睡眠 {record['sleep_hours']:g}h/{record['sleep_quality']} | 工作 {record['work_hours']:g}h | "
                f"屏幕 {record['screen_hours']:g}h | 饮水 {record['water_ml']}ml | 运动量 {record['exercise_load']:g} | 心情 {record['mood_score']}"
            )
            self._label(item, detail, size=12, color=MUTED).grid(row=1, column=1, sticky="w", pady=(2, 10))

    def _delete_selected_records(self):
        selected_ids = [record_id for record_id, var in self.record_checks.items() if var.get()]
        if not selected_ids:
            messagebox.showwarning("未选择记录", "请先选择要删除的历史记录。")
            return
        if not messagebox.askyesno("确认删除", f"确定删除选中的 {len(selected_ids)} 条记录吗？"):
            return
        DataManager.delete_records(selected_ids)
        self._refresh_history()
        self._refresh_chart()

    def _clear_current_user_records(self):
        if not self.current_user:
            return
        records = DataManager.load_records(self.current_user["user_id"])
        if not records:
            messagebox.showinfo("暂无数据", "当前用户没有可清空的历史记录。")
            return
        if not messagebox.askyesno("确认清空", "确定清空当前用户的全部历史记录吗？此操作无法撤销。"):
            return
        DataManager.clear_data(self.current_user["user_id"])
        self._refresh_history()
        self._refresh_chart()

    def _refresh_chart(self):
        if self.chart_frame is None or not self.current_user:
            return
        for child in self.chart_frame.winfo_children():
            child.destroy()

        records = DataManager.load_records(self.current_user["user_id"])
        if not records:
            self._label(self.chart_frame, "暂无趋势数据，保存记录后会显示折线图。", size=13, color=MUTED).pack(anchor=tk.CENTER, expand=True)
            return

        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
        except ImportError:
            self._label(self.chart_frame, "未安装 matplotlib，无法显示趋势图。", size=13, color=MUTED).pack(anchor=tk.CENTER, expand=True)
            return

        recent = records[-14:]
        dates = [record["date"][5:10] for record in recent]
        fatigue_values = [float(record["fatigue"]) for record in recent]
        figure = Figure(figsize=(6.6, 2.3), dpi=100, facecolor=CARD_SOFT)
        axis = figure.add_subplot(111)
        axis.set_facecolor(CARD_SOFT)
        axis.plot(dates, fatigue_values, marker="o", color=PRIMARY, linewidth=2.2)
        axis.fill_between(dates, fatigue_values, color="#bfdbfe", alpha=0.35)
        axis.set_ylim(0, 100)
        axis.set_ylabel("疲劳值", color=MUTED)
        axis.grid(True, linestyle="--", alpha=0.28)
        axis.tick_params(axis="x", labelsize=8, colors=MUTED)
        axis.tick_params(axis="y", labelsize=8, colors=MUTED)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_color(BORDER)
        axis.spines["bottom"].set_color(BORDER)
        figure.tight_layout()

        self.chart_canvas = FigureCanvasTkAgg(figure, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _save_new_user(self):
        try:
            profile = self._read_profile_form()
        except ValueError as error:
            messagebox.showwarning("信息有误", str(error))
            return
        DataManager.create_user(profile)
        messagebox.showinfo("保存成功", "用户档案已创建。")
        self._show_login()

    def _enter_app(self):
        user = self._find_selected_user()
        if user is None:
            messagebox.showwarning("未选择用户", "请先选择一个用户。")
            return
        self.current_user = user
        self._show_main_shell()

    def _find_selected_user(self):
        selected = self.selected_user.get()
        for user in self.users:
            if self._format_user_name(user) == selected:
                return user
        return None

    def _format_user_name(self, user):
        return f"{user['name']}（{user['age']}岁，{user['gender']}）"

    def _format_current_user_summary(self):
        user = self.current_user or {}
        return (
            f"当前用户：{user.get('name', '--')} | {user.get('gender', '--')} | "
            f"{user.get('age', '--')} 岁 | {user.get('activity_level', '--')} | {user.get('role', '--')}"
        )

    def _get_status_color(self, fatigue):
        if fatigue <= 30:
            return GOOD
        if fatigue <= 60:
            return MILD
        if fatigue <= 80:
            return MEDIUM
        return DANGER


if __name__ == "__main__":
    app = ModernFatigueApp()
    app.mainloop()
