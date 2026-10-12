"""
ОКФРС. Практика 6. Задание 11.
Перевод текста в код и обратно: UTF-8 · CP1251 · KOI8-R · ISO-8859-1 · ASCII · Base64.
Премиум-стиль 2026.
"""
import tkinter as tk
import sys, os, math, time, base64

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# ПАЛИТРА
# ============================================================
BG_DEEP    = "#08090f"
BG_GLASS   = "#131823"
BG_GRAPH   = "#050810"
BG_PANEL   = "#0f141c"
BG_CELL    = "#0e1218"
BORDER     = "#232a3d"
BORDER_HL  = "#2f3648"

NEON_CYAN  = "#00f0ff"
NEON_GREEN = "#39ff88"
NEON_PINK  = "#ff3ea5"
NEON_PURP  = "#a066ff"
NEON_AMBER = "#ffb830"
NEON_RED   = "#ff4d5e"
NEON_BLUE  = "#4d8dff"

TEXT_MAIN  = "#e8f0ff"
TEXT_DIM   = "#5a6780"
TEXT_GLOW  = "#8fa4c4"

FONT_MONO  = ("Consolas", 13, "bold")
FONT_MONO_S= ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_LABEL_S = ("Segoe UI", 9)


def lerp(c1, c2, t):
    t = max(0.0, min(1.0, float(t)))
    try:
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    except Exception:
        return c1
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(r1 + (r2 - r1) * t))),
        max(0, min(255, int(g1 + (g2 - g1) * t))),
        max(0, min(255, int(b1 + (b2 - b1) * t))))


def round_rect(canvas, x1, y1, x2, y2, r,
               fill=None, outline=None, width=1, tags=""):
    pts = []
    steps = 8
    for i in range(steps + 1):
        a = math.pi + (math.pi / 2) * (i / steps)
        pts.extend([x1 + r + r * math.cos(a), y1 + r + r * math.sin(a)])
    for i in range(steps + 1):
        a = -math.pi/2 + (math.pi / 2) * (i / steps)
        pts.extend([x2 - r + r * math.cos(a), y1 + r + r * math.sin(a)])
    for i in range(steps + 1):
        a = 0 + (math.pi / 2) * (i / steps)
        pts.extend([x2 - r + r * math.cos(a), y2 - r + r * math.sin(a)])
    for i in range(steps + 1):
        a = math.pi/2 + (math.pi / 2) * (i / steps)
        pts.extend([x1 + r + r * math.cos(a), y2 - r + r * math.sin(a)])
    return canvas.create_polygon(pts, fill=fill or "", outline=outline or "",
                                 width=width, smooth=False, tags=tags)


# ============================================================
# КОДИРОВКИ
# ============================================================
def to_utf8(ch):
    try:
        return ch.encode("utf-8").hex().upper()
    except Exception:
        return "—"

def to_cp1251(ch):
    try:
        return ch.encode("cp1251").hex().upper()
    except Exception:
        return "—"

def to_koi8r(ch):
    try:
        return ch.encode("koi8-r").hex().upper()
    except Exception:
        return "—"

def to_iso(ch):
    try:
        return ch.encode("iso-8859-1").hex().upper()
    except Exception:
        return "—"

def to_ascii(ch):
    try:
        code = ord(ch)
        if code < 128:
            return f"{code:02X}"
        return "—"
    except Exception:
        return "—"

def to_base64(ch):
    try:
        return base64.b64encode(ch.encode("utf-8")).decode("ascii")
    except Exception:
        return "—"


# ============================================================
# СОСТОЯНИЕ
# ============================================================
class AppState:
    def __init__(self):
        self.text = "Привет"
        self.pulse_t = 0.0
        self.hover_cell = None      # (row, col)
        self.click_flash = None     # (row, col) — подсветка после клика
        self.click_time = 0.0

    def tick(self, dt):
        self.pulse_t += dt

    def reset(self):
        self.text = "Привет"

    def clear(self):
        self.text = ""


# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Text Codes · Кодировки текста")
        root.geometry("1600x950")
        root.minsize(1400, 850)
        root.configure(bg=BG_DEEP)

        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.state = AppState()
        self.btn_zones = {}
        self.cell_zones = {}        # кликабельные ячейки (для копирования)
        self.entry_widget = None
        self.copy_message = ""
        self.copy_message_time = 0.0

        self.W, self.H = 1600, 950

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", self._on_leave)

        self.root.update_idletasks()
        self._redraw_all()
        self._animate()

    def _on_resize(self, event):
        self._redraw_all()

    # ---------- ФОН ----------
    def _draw_bg(self, w, h):
        for i in range(40):
            y0 = int(i * h / 40)
            y1 = int((i + 1) * h / 40)
            col = lerp(BG_DEEP, "#0a0e18", i / 40)
            self.canvas.create_rectangle(0, y0, w, y1, fill=col, outline="")
        for x in range(0, w, 60):
            self.canvas.create_line(x, 0, x, h, fill="#0d1220")
        for y in range(0, h, 60):
            self.canvas.create_line(0, y, w, y, fill="#0d1220")

    # ---------- ЗАГОЛОВОК ----------
    def _draw_header(self, w):
        self.canvas.create_text(60, 40, text="⌨",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="TEXT CODES",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(300, 44,
                                text="· UTF-8 · CP1251 · KOI8-R · ISO · ASCII · Base64",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 11, "bold"))

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")

        # сообщение "скопировано"
        if self.copy_message and time.time() - self.copy_message_time < 1.5:
            self.canvas.create_text(w - 250, 37, anchor="e",
                                    text=f"✓ {self.copy_message}",
                                    fill=NEON_GREEN,
                                    font=("Segoe UI", 10, "bold"))

        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

    # ---------- ПАНЕЛЬ ВВОДА ----------
    def _draw_input_panel(self, w, y):
        card_h = 100
        round_rect(self.canvas, 50, y, w - 50, y + card_h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        # заголовок
        self.canvas.create_text(70, y + 22, anchor="w",
                                text="▸ ВВЕДИТЕ ТЕКСТ",
                                fill=NEON_CYAN, font=FONT_LABEL)
        self.canvas.create_text(200, y + 22, anchor="w",
                                text=f"длина: {len(self.state.text)} символов",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        # поле ввода — ОГРАНИЧЕНО, чтобы не заходить на кнопки
        entry_x = 70
        entry_y = y + 45
        # кнопки занимают справа примерно 340 px
        btn_block_w = 340
        entry_w = w - 100 - btn_block_w - 20
        entry_h = 38

        round_rect(self.canvas, entry_x, entry_y,
                   entry_x + entry_w, entry_y + entry_h, 8,
                   fill="#050810", outline=BORDER_HL, width=1)

        if self.entry_widget is None or not self.entry_widget.winfo_exists():
            self.entry_widget = tk.Entry(
                self.root,
                bg="#050810", fg=NEON_GREEN,
                insertbackground=NEON_CYAN,
                font=("Consolas", 14, "bold"),
                bd=0, highlightthickness=0)
            self.entry_widget.insert(0, self.state.text)
            self.entry_widget.bind("<KeyRelease>", self._on_entry_change)
        else:
            if self.root.focus_get() != self.entry_widget:
                self.entry_widget.delete(0, tk.END)
                self.entry_widget.insert(0, self.state.text)

        self.entry_widget.place(x=entry_x + 12, y=entry_y + 6,
                                 width=entry_w - 24, height=entry_h - 12)

        # кнопки — ОТДЕЛЬНО, справа от поля
        btn_y = entry_y
        btn_h = 38
        btn_w = 150
        gap = 12
        btn_x = w - 50 - 20 - 2 * btn_w - gap

        self._draw_btn(btn_x, btn_y, btn_w, btn_h,
                       "↺  СБРОС", NEON_RED, "reset")
        self._draw_btn(btn_x + btn_w + gap, btn_y, btn_w, btn_h,
                       "⌫  ОЧИСТИТЬ", NEON_AMBER, "clear")

    def _draw_btn(self, x, y, w, h, text, color, key):
        round_rect(self.canvas, x, y, x + w, y + h, 8,
                   fill=lerp(color, BG_DEEP, 0.75),
                   outline=color, width=2)
        self.canvas.create_text(x + w / 2, y + h / 2,
                                text=text, fill=color,
                                font=("Segoe UI", 11, "bold"))
        self.btn_zones[key] = (x, y, x + w, y + h)

    # ---------- ТАБЛИЦА ----------
    def _draw_table(self, w, y, h):
        round_rect(self.canvas, 50, y, w - 50, y + h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(70, y + 25, anchor="w",
                                text="▸ ПОСИМВОЛЬНОЕ ПРЕДСТАВЛЕНИЕ",
                                fill=NEON_CYAN, font=FONT_LABEL)
        self.canvas.create_text(w - 70, y + 25, anchor="e",
                                text="клик по ячейке — скопировать код",
                                fill=TEXT_DIM, font=("Segoe UI", 9, "italic"))

        # столбцы
        # СИМВОЛ  |  UTF-8  |  CP1251  |  KOI8-R  |  ISO  |  ASCII  |  Base64
        col_starts = [
            70,               # символ
            w * 0.13,         # UTF-8
            w * 0.28,         # CP1251
            w * 0.42,         # KOI8-R
            w * 0.55,         # ISO
            w * 0.68,         # ASCII
            w * 0.78,         # Base64
        ]
        headers = ["СИМВОЛ", "UTF-8", "CP1251", "KOI8-R", "ISO-8859-1", "ASCII", "Base64"]
        header_colors = [TEXT_GLOW, NEON_CYAN, NEON_GREEN, NEON_AMBER, NEON_PINK, NEON_BLUE, NEON_PURP]

        for x_start, h_text, h_color in zip(col_starts, headers, header_colors):
            self.canvas.create_text(x_start + 8, y + 55, anchor="w",
                                    text=h_text, fill=h_color,
                                    font=FONT_LABEL_S)

        self.canvas.create_line(70, y + 72, w - 70, y + 72, fill=BORDER)

        # строки (максимум 12)
        text = self.state.text[:12]
        row_h = 42
        row_y = y + 82
        self.cell_zones = {}

        for i, ch in enumerate(text):
            ry = row_y + i * row_h
            if ry + row_h > y + h - 10:
                break

            # зебра
            if i % 2 == 0:
                round_rect(self.canvas, 60, ry - 14,
                           w - 60, ry + row_h - 20, 6,
                           fill=BG_CELL)

            # 7 значений: ch + 6 кодировок
            vals = [
                ("", ch,                     NEON_AMBER),
                ("utf8",   to_utf8(ch),      NEON_CYAN),
                ("cp1251", to_cp1251(ch),    NEON_GREEN),
                ("koi8r",  to_koi8r(ch),     NEON_AMBER),
                ("iso",    to_iso(ch),       NEON_PINK),
                ("ascii",  to_ascii(ch),     NEON_BLUE),
                ("b64",    to_base64(ch),    NEON_PURP),
            ]

            for j, (key, val, color) in enumerate(vals):
                col_x = col_starts[j]
                # фон ячейки (подсветка при hover)
                cell_x0 = col_x
                cell_x1 = col_starts[j + 1] - 10 if j + 1 < len(col_starts) else w - 70
                cell_w = cell_x1 - cell_x0

                is_hover = (self.state.hover_cell == (i, j))
                is_click = (self.state.click_flash == (i, j)
                             and time.time() - self.state.click_time < 0.5)

                if is_click:
                    round_rect(self.canvas, cell_x0, ry - 14,
                               cell_x1, ry + row_h - 20, 6,
                               fill=lerp(color, BG_DEEP, 0.7),
                               outline=color, width=1)
                elif is_hover:
                    round_rect(self.canvas, cell_x0, ry - 14,
                               cell_x1, ry + row_h - 20, 6,
                               fill="#1a1f2e", outline=BORDER_HL, width=1)

                # текст
                if j == 0:
                    self.canvas.create_text(col_x + 20, ry - 6,
                                            text=val, fill=color,
                                            font=("Consolas", 18, "bold"))
                else:
                    self.canvas.create_text(col_x + 8, ry - 6, anchor="w",
                                            text=val, fill=color,
                                            font=("Consolas", 12, "bold"))

                # регистрируем зону для клика (кроме символа)
                if j > 0:
                    self.cell_zones[(i, j)] = (cell_x0, ry - 14,
                                                 cell_x1, ry + row_h - 20,
                                                 val)

        if not text:
            self.canvas.create_text(w / 2, y + h / 2,
                                    text="Введите текст в поле выше",
                                    fill=TEXT_DIM, font=FONT_LABEL)

    # ---------- ИТОГИ (ВСЯ СТРОКА) ----------
    def _draw_result(self, w, y, h):
        round_rect(self.canvas, 50, y, w - 50, y + h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(70, y + 25, anchor="w",
                                text="▸ КОД ВСЕЙ СТРОКИ",
                                fill=NEON_CYAN, font=FONT_LABEL)

        text = self.state.text
        if not text:
            return

        # вычисляем
        try:
            utf8 = text.encode("utf-8").hex().upper()
        except Exception:
            utf8 = "—"
        try:
            cp1251 = text.encode("cp1251").hex().upper()
        except Exception:
            cp1251 = "—"
        try:
            b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
        except Exception:
            b64 = "—"

        items = [
            ("UTF-8",  utf8,   NEON_CYAN),
            ("CP1251", cp1251, NEON_GREEN),
            ("Base64", b64,    NEON_PURP),
        ]

        col_w = (w - 100) / 3

        for i, (label, value, color) in enumerate(items):
            cx = 50 + col_w * i + col_w / 2
            cx_left = 50 + col_w * i + 20
            cx_right = 50 + col_w * (i + 1) - 20

            # заголовок столбца
            self.canvas.create_text(cx_left, y + 52, anchor="w",
                                    text=label, fill=color,
                                    font=FONT_LABEL)

            # фон для значения
            round_rect(self.canvas, cx_left, y + 65,
                       cx_right, y + h - 20, 8,
                       fill=BG_CELL, outline=lerp(color, BG_DEEP, 0.6),
                       width=1)

            # значение — с переносом если длинное
            display = value
            if len(display) > 50:
                # разбить на 2 строки
                half = len(display) // 2
                line1 = display[:half]
                line2 = display[half:]
                self.canvas.create_text(cx_left + 15, y + 90, anchor="w",
                                        text=line1, fill=color,
                                        font=("Consolas", 11, "bold"))
                self.canvas.create_text(cx_left + 15, y + 112, anchor="w",
                                        text=line2, fill=color,
                                        font=("Consolas", 11, "bold"))
            else:
                self.canvas.create_text(cx_left + 15,
                                        (y + 65 + y + h - 20) / 2,
                                        anchor="w",
                                        text=display, fill=color,
                                        font=("Consolas", 13, "bold"))

            # разделитель
            if i < 2:
                xx = 50 + col_w * (i + 1)
                self.canvas.create_line(xx, y + 45, xx, y + h - 15,
                                        fill=BORDER, dash=(3, 3))

    # ---------- ПЕРЕРИСОВКА ----------
    def _redraw_all(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = self.W, self.H
        self.W, self.H = w, h

        self.btn_zones = {}
        self.cell_zones = {}

        self._draw_bg(w, h)
        self._draw_header(w)
        self._draw_input_panel(w, 90)

        # таблица посередине
        table_y = 210
        table_h = h - 210 - 200
        if table_h < 200:
            table_h = 200
        self._draw_table(w, table_y, table_h)

        # итоги внизу
        result_y = table_y + table_h + 15
        result_h = h - result_y - 20
        if result_h < 100:
            result_h = 100
        self._draw_result(w, result_y, result_h)

    # ---------- СОБЫТИЯ ----------
    def _on_entry_change(self, event):
        try:
            self.state.text = self.entry_widget.get()
        except Exception:
            pass

    def _on_motion(self, event):
        """Определяет, на какой ячейке мышь."""
        self.state.hover_cell = None
        for key, zone in self.cell_zones.items():
            x0, y0, x1, y1, val = zone
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                self.state.hover_cell = key
                return

    def _on_leave(self, event):
        self.state.hover_cell = None

    def _on_click(self, event):
        # кнопки
        for key, (x0, y0, x1, y1) in self.btn_zones.items():
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                self._do_action(key)
                return

        # ячейки — копирование в буфер
        for key, zone in self.cell_zones.items():
            x0, y0, x1, y1, val = zone
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                if val and val != "—":
                    try:
                        self.root.clipboard_clear()
                        self.root.clipboard_append(val)
                        self.copy_message = f"скопировано: {val}"
                        self.copy_message_time = time.time()
                    except Exception:
                        pass
                    self.state.click_flash = key
                    self.state.click_time = time.time()
                return

    def _do_action(self, key):
        if key == "reset":
            self.state.reset()
            self._update_entry()
        elif key == "clear":
            self.state.clear()
            self._update_entry()

    def _update_entry(self):
        if self.entry_widget and self.entry_widget.winfo_exists():
            self.entry_widget.delete(0, tk.END)
            self.entry_widget.insert(0, self.state.text)

    # ---------- АНИМАЦИЯ ----------
    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        dt = 0.033
        self.state.tick(dt)

        self._redraw_all()
        self.root.after(50, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()