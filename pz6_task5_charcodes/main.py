"""
ОКФРС. Практика 6. Задание 5.
Код символа при нажатии клавиши в разных кодировках:
ASCII · Unicode · CP1251 · CP866 · KOI8-R · UTF-8 · Base64.
Премиум-стиль 2026.
"""
import tkinter as tk
import sys, os, math, time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# ПАЛИТРА
# ============================================================
BG_DEEP    = "#08090f"
BG_GLASS   = "#131823"
BG_CARD    = "#0f141c"
BORDER     = "#232a3d"

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
FONT_VAL   = ("Consolas", 16, "bold")
FONT_BIG   = ("Consolas", 22, "bold")
FONT_HUGE  = ("Consolas", 38, "bold")


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
def get_ascii_code(ch):
    """ASCII — только 0..127. Если символ русский — None."""
    code = ord(ch)
    if code < 128:
        return code
    return None


def get_unicode_code(ch):
    """Unicode — номер кодпойнта."""
    return ord(ch)


def get_cp1251_code(ch):
    """Windows-1251 (кириллица)."""
    try:
        return ch.encode("cp1251")[0]
    except Exception:
        return None


def get_cp866_code(ch):
    """CP866 (DOS кириллица)."""
    try:
        return ch.encode("cp866")[0]
    except Exception:
        return None


def get_koi8r_code(ch):
    """KOI8-R."""
    try:
        return ch.encode("koi8-r")[0]
    except Exception:
        return None


def get_utf8_bytes(ch):
    """UTF-8 — байты в hex."""
    try:
        b = ch.encode("utf-8")
        return b.hex().upper()
    except Exception:
        return None


def get_utf8_bytes_count(ch):
    """Сколько байт занимает в UTF-8."""
    try:
        return len(ch.encode("utf-8"))
    except Exception:
        return 0


def get_base64(ch):
    """Base64 символа."""
    import base64
    try:
        b = ch.encode("utf-8")
        return base64.b64encode(b).decode("ascii")
    except Exception:
        return None


# ============================================================
# СОСТОЯНИЕ
# ============================================================
class AppState:
    def __init__(self):
        self.char = "A"           # текущий символ
        self.history = []         # история нажатий (последние 10)
        self.t = 0.0

    def set_char(self, ch):
        if ch:
            self.char = ch
            self.history.insert(0, ch)
            if len(self.history) > 10:
                self.history.pop()

    def tick(self, dt):
        self.t += dt


# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Character Code · ASCII · Unicode · CP1251 · CP866")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.state = AppState()
        self.btn_zones = {}
        self.entry_widget = None

        self.W, self.H = 1500, 950

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

        # ГЛАВНОЕ — перехват нажатия клавиш по всему окну
        root.bind("<Key>", self._on_key)

        # фокус на окне
        root.focus_set()

        self.root.update_idletasks()
        self._redraw_all()
        self._animate()

    def _on_resize(self, event):
        self._redraw_all()

    # ---------- ПЕРЕХВАТ КЛАВИШ ----------
    def _on_key(self, event):
        """Ловим нажатие клавиш и меняем символ."""
        ch = event.char
        if not ch:
            return
        # если фокус в поле ввода — не перехватываем
        if self.entry_widget and self.root.focus_get() == self.entry_widget:
            return
        # печатаемый символ
        if len(ch) == 1:
            self.state.set_char(ch)

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
        self.canvas.create_text(100, 40, text="CHARACTER CODE",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(340, 44,
                                text="· ASCII · UNICODE · CP1251 · CP866 · UTF-8",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 11, "bold"))

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

    # ---------- ГЛАВНАЯ КАРТОЧКА СИМВОЛА ----------
    def _draw_char_card(self, w, y):
        card_h = 220
        round_rect(self.canvas, 50, y, w - 50, y + card_h, 16,
                   fill=BG_GLASS,
                   outline=lerp(NEON_CYAN, BG_DEEP, 0.5), width=2)

        # подпись
        self.canvas.create_text(w / 2, y + 25,
                                text="▸ ТЕКУЩИЙ СИМВОЛ",
                                fill=TEXT_DIM, font=FONT_LABEL)

        # большой символ
        ch = self.state.char
        self.canvas.create_text(w / 2, y + 115,
                                text=ch,
                                fill=NEON_CYAN,
                                font=("Consolas", 90, "bold"))

        # подсказка
        self.canvas.create_text(w / 2, y + 195,
                                text="нажми любую клавишу",
                                fill=TEXT_DIM,
                                font=("Segoe UI", 10, "italic"))

        # Unicode name
        try:
            import unicodedata
            uname = unicodedata.name(ch, "—")
        except Exception:
            uname = "—"
        self.canvas.create_text(w / 2, y + 60,
                                text=uname,
                                fill=NEON_AMBER,
                                font=("Consolas", 11, "bold"))

    # ---------- ТАБЛИЦА КОДИРОВОК ----------
    def _draw_codes_table(self, w, y):
        card_h = 380
        round_rect(self.canvas, 50, y, w - 50, y + card_h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(w / 2, y + 25,
                                text="▸ КОДЫ СИМВОЛА В РАЗНЫХ КОДИРОВКАХ",
                                fill=NEON_CYAN, font=FONT_LABEL)

        # разделитель
        self.canvas.create_line(70, y + 45, w - 70, y + 45, fill=BORDER)

        ch = self.state.char

        # столбцы: [код | hex | bin | dec | описание]
        rows = [
            ("ASCII",          get_ascii_code(ch), NEON_GREEN,
             "0..127 — базовая таблица"),
            ("Unicode",        get_unicode_code(ch), NEON_PURP,
             "кодпойнт U+XXXX"),
            ("Windows-1251",   get_cp1251_code(ch), NEON_CYAN,
             "CP1251 — русская Windows"),
            ("CP866 (DOS)",    get_cp866_code(ch), NEON_AMBER,
             "IBM866 — DOS-кириллица"),
            ("KOI8-R",         get_koi8r_code(ch), NEON_PINK,
             "советская кодировка"),
        ]

        col_xs = [w * 0.10, w * 0.32, w * 0.47, w * 0.60, w * 0.78]
        headers = ["КОДИРОВКА", "DEC", "HEX", "BIN", "ОПИСАНИЕ"]
        for h_text, x in zip(headers, col_xs):
            self.canvas.create_text(x, y + 70, text=h_text,
                                    fill=TEXT_DIM, font=FONT_LABEL_S)

        row_h = 45
        row_start = y + 100

        for i, (name, code, color, desc) in enumerate(rows):
            ry = row_start + i * row_h
            # зебра
            if i % 2 == 0:
                round_rect(self.canvas, 70, ry - 16,
                           w - 70, ry + row_h - 25, 6,
                           fill="#0e1218")

            # название
            self.canvas.create_text(col_xs[0], ry,
                                    text=name, fill=color,
                                    font=("Segoe UI", 11, "bold"), anchor="w")

            if code is None:
                # не поддерживается
                for x in col_xs[1:4]:
                    self.canvas.create_text(x, ry,
                                            text="—",
                                            fill=NEON_RED,
                                            font=("Consolas", 13, "bold"))
            else:
                self.canvas.create_text(col_xs[1], ry,
                                        text=str(code),
                                        fill=color,
                                        font=("Consolas", 15, "bold"))
                self.canvas.create_text(col_xs[2], ry,
                                        text=f"0x{code:02X}" if code < 256 else f"0x{code:04X}",
                                        fill=color,
                                        font=("Consolas", 15, "bold"))
                self.canvas.create_text(col_xs[3], ry,
                                        text=f"{code:08b}" if code < 256 else f"{code:016b}",
                                        fill=color,
                                        font=("Consolas", 10, "bold"))

            self.canvas.create_text(col_xs[4], ry,
                                    text=desc,
                                    fill=TEXT_DIM,
                                    font=("Segoe UI", 9),
                                    anchor="w")

    # ---------- UTF-8 / BASE64 ----------
    def _draw_extra(self, w, y):
        card_h = 130
        round_rect(self.canvas, 50, y, w - 50, y + card_h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(w / 2, y + 25,
                                text="▸ UTF-8 · BASE64",
                                fill=NEON_CYAN, font=FONT_LABEL)

        ch = self.state.char
        utf8 = get_utf8_bytes(ch) or "—"
        n_bytes = get_utf8_bytes_count(ch)
        b64 = get_base64(ch) or "—"

        col_w = (w - 100) / 3
        col_xs = [50 + col_w / 2, 50 + col_w * 1.5, 50 + col_w * 2.5]

        # UTF-8
        self.canvas.create_text(col_xs[0], y + 55,
                                text="UTF-8 (HEX)",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        self.canvas.create_text(col_xs[0], y + 90,
                                text=utf8,
                                fill=NEON_GREEN,
                                font=("Consolas", 22, "bold"))

        # Байт
        self.canvas.create_text(col_xs[1], y + 55,
                                text="БАЙТ В UTF-8",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        self.canvas.create_text(col_xs[1], y + 90,
                                text=f"{n_bytes} байт",
                                fill=NEON_AMBER,
                                font=("Consolas", 22, "bold"))

        # Base64
        self.canvas.create_text(col_xs[2], y + 55,
                                text="BASE64",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        self.canvas.create_text(col_xs[2], y + 90,
                                text=b64,
                                fill=NEON_PINK,
                                font=("Consolas", 22, "bold"))

        # разделители
        for i in range(1, 3):
            xx = 50 + i * col_w
            self.canvas.create_line(xx, y + 45, xx, y + card_h - 15,
                                    fill=BORDER, dash=(3, 3))

    # ---------- ИСТОРИЯ ----------
    def _draw_history(self, w, y):
        card_h = 80
        round_rect(self.canvas, 50, y, w - 50, y + card_h, 12,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(70, y + 22, anchor="w",
                                text="▸ ИСТОРИЯ НАЖАТИЙ",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        # символы справа налево
        history = self.state.history
        if not history:
            self.canvas.create_text(w / 2, y + 50,
                                    text="Нажми любую клавишу — символ появится здесь",
                                    fill=TEXT_DIM,
                                    font=("Segoe UI", 11, "italic"))
            return

        n = min(len(history), 10)
        start_x = 90
        step = 55

        for i in range(n):
            ch = history[i]
            cx = start_x + i * step
            cy = y + 52

            # яркость убывает с возрастом
            t = i / max(1, n)
            col = lerp(NEON_CYAN, BG_DEEP, t * 0.75)

            # тумблер
            round_rect(self.canvas, cx - 18, cy - 18,
                       cx + 18, cy + 18, 6,
                       fill=lerp(col, BG_DEEP, 0.7),
                       outline=col, width=1)

            self.canvas.create_text(cx, cy,
                                    text=ch if ch.strip() else "·",
                                    fill=col,
                                    font=("Consolas", 16, "bold"))

    # ---------- ПОДСКАЗКА ----------
    def _draw_hint(self, w, h):
        self.canvas.create_text(w / 2, h - 25,
                                text="Нажми любую клавишу — код символа отобразится выше",
                                fill=TEXT_DIM,
                                font=("Segoe UI", 10, "italic"))

    # ---------- ПЕРЕРИСОВКА ----------
    def _redraw_all(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = self.W, self.H
        self.W, self.H = w, h

        self._draw_bg(w, h)
        self._draw_header(w)
        self._draw_char_card(w, 90)
        self._draw_codes_table(w, 330)
        self._draw_extra(w, 730)
        self._draw_history(w, 880)

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
        self.root.after(60, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()