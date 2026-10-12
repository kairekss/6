"""
ОКФРС. Практика 6. Задание 2.
Вывод 4 байт в DEC / BIN / HEX формате.
Премиум-стиль 2026.
"""
import tkinter as tk
import sys, os, math, random, time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# ПАЛИТРА
# ============================================================
BG_DEEP    = "#08090f"
BG_GLASS   = "#131823"
BORDER     = "#232a3d"

NEON_CYAN  = "#00f0ff"
NEON_GREEN = "#39ff88"
NEON_PINK  = "#ff3ea5"
NEON_PURP  = "#a066ff"
NEON_AMBER = "#ffb830"
NEON_RED   = "#ff4d5e"

TEXT_MAIN  = "#e8f0ff"
TEXT_DIM   = "#5a6780"
TEXT_GLOW  = "#8fa4c4"

FONT_MONO  = ("Consolas", 13, "bold")
FONT_MONO_S= ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_LABEL_S = ("Segoe UI", 9)
FONT_BIG   = ("Consolas", 22, "bold")
FONT_HUGE  = ("Consolas", 32, "bold")


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
    steps = 6
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
# СОСТОЯНИЕ
# ============================================================
class BitsState:
    def __init__(self):
        self.bytes = [random.randint(0, 255) for _ in range(4)]

    def randomize(self):
        self.bytes = [random.randint(0, 255) for _ in range(4)]

    def clear(self):
        self.bytes = [0, 0, 0, 0]

    def set_all_ff(self):
        self.bytes = [255, 255, 255, 255]


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Hex Output · DEC · BIN · HEX")
        root.geometry("1500x900")
        root.minsize(1300, 800)
        root.configure(bg=BG_DEEP)

        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.state = BitsState()
        self.btn_zones = {}

        self.W, self.H = 1500, 900

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)

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
        self.canvas.create_text(60, 40, text="⚡",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="HEX OUTPUT",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(300, 44,
                                text="· DEC · BIN · HEX · 4 БАЙТА",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

    # ---------- БОЛЬШОЙ HEX ----------
    def _draw_big_hex(self, w, y):
        """Большая карточка с 32-битным HEX."""
        card_h = 130
        round_rect(self.canvas, 50, y, w - 50, y + card_h, 14,
                   fill=BG_GLASS, outline=NEON_AMBER, width=2)

        self.canvas.create_text(w / 2, y + 30,
                                text="32-БИТНОЕ ЗНАЧЕНИЕ В HEX",
                                fill=TEXT_DIM, font=FONT_LABEL)

        hex_str = "".join(f"{b:02X}" for b in self.state.bytes)
        self.canvas.create_text(w / 2, y + 80,
                                text=f"0x {hex_str[0:2]}  {hex_str[2:4]}  {hex_str[4:6]}  {hex_str[6:8]}",
                                fill=NEON_AMBER, font=("Consolas", 42, "bold"))

    # ---------- БАЙТЫ ----------
    def _draw_bytes_table(self, w, y):
        """Таблица: 4 байта × (BIN / DEC / HEX)."""
        card_h = 340
        round_rect(self.canvas, 50, y, w - 50, y + card_h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        # заголовок таблицы
        self.canvas.create_text(w / 2, y + 25,
                                text="▸ ПРЕДСТАВЛЕНИЕ КАЖДОГО БАЙТА",
                                fill=NEON_CYAN, font=FONT_LABEL)

        # разделитель
        self.canvas.create_line(70, y + 45, w - 70, y + 45, fill=BORDER)

        # колонки
        col_names = ["БАЙТ", "ДВОИЧНЫЙ (BIN)", "ДЕСЯТИЧНЫЙ (DEC)", "16-РИЧНЫЙ (HEX)"]
        col_xs = [110, w * 0.35, w * 0.58, w * 0.80]
        col_colors = [TEXT_GLOW, NEON_GREEN, NEON_CYAN, NEON_AMBER]

        for name, x, col in zip(col_names, col_xs, col_colors):
            self.canvas.create_text(x, y + 70,
                                    text=name,
                                    fill=col, font=FONT_LABEL)

        # строки
        row_h = 55
        row_y_start = y + 100

        for i, val in enumerate(self.state.bytes):
            ry = row_y_start + i * row_h
            bin_str = f"{val:08b}"

            # зебра
            if i % 2 == 0:
                round_rect(self.canvas, 70, ry - 20,
                           w - 70, ry + row_h - 25, 8,
                           fill="#0e1218")

            # номер байта
            self.canvas.create_text(col_xs[0], ry,
                                    text=f"#{i+1}",
                                    fill=NEON_PINK, font=FONT_MONO)

            # BIN — с разделением по 4
            bin_pretty = f"{bin_str[:4]} {bin_str[4:]}"
            self.canvas.create_text(col_xs[1], ry,
                                    text=bin_pretty,
                                    fill=NEON_GREEN, font=("Consolas", 16, "bold"))

            # DEC
            self.canvas.create_text(col_xs[2], ry,
                                    text=f"{val:>3}",
                                    fill=NEON_CYAN, font=("Consolas", 18, "bold"))

            # HEX
            self.canvas.create_text(col_xs[3], ry,
                                    text=f"0x{val:02X}",
                                    fill=NEON_AMBER, font=("Consolas", 18, "bold"))

    # ---------- ОБЩИЙ DEC / BIN ----------
    def _draw_total(self, w, y):
        card_h = 100
        round_rect(self.canvas, 50, y, w - 50, y + card_h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        # DEC
        self.canvas.create_text(w * 0.25, y + 25,
                                text="ОБЩЕЕ DEC (32-бит)",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        total_dec = 0
        for b in self.state.bytes:
            total_dec = (total_dec << 8) | b
        self.canvas.create_text(w * 0.25, y + 60,
                                text=f"{total_dec}",
                                fill=NEON_CYAN, font=FONT_BIG)

        # BIN
        self.canvas.create_text(w * 0.75, y + 25,
                                text="ОБЩЕЕ BIN (32-бит)",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        total_bin = "".join(f"{b:08b}" for b in self.state.bytes)
        # разбиваем по 4 для читаемости
        pretty = " ".join(total_bin[i:i+4] for i in range(0, 32, 4))
        self.canvas.create_text(w * 0.75, y + 60,
                                text=pretty,
                                fill=NEON_GREEN, font=("Consolas", 15, "bold"))

    # ---------- КНОПКИ ----------
    def _draw_buttons(self, w, y):
        btn_w = 220
        btn_h = 50
        gap = 20
        total = 3 * btn_w + 2 * gap
        start_x = (w - total) / 2

        self._draw_btn(start_x, y, btn_w, btn_h,
                       "🎲  СЛУЧАЙНО", NEON_PURP, "random")
        self._draw_btn(start_x + btn_w + gap, y, btn_w, btn_h,
                       "✕  ОЧИСТИТЬ", NEON_RED, "clear")
        self._draw_btn(start_x + 2 * (btn_w + gap), y, btn_w, btn_h,
                       "✓  ВСЕ 0xFF", NEON_GREEN, "ff")

    def _draw_btn(self, x, y, w, h, text, color, key):
        round_rect(self.canvas, x + 2, y + 3, x + w + 2, y + h + 3, 12,
                   fill="#000000", outline="")
        round_rect(self.canvas, x, y, x + w, y + h, 12,
                   fill=lerp(color, BG_DEEP, 0.7),
                   outline=color, width=2)
        self.canvas.create_text(x + w / 2, y + h / 2,
                                text=text, fill=color,
                                font=("Segoe UI", 12, "bold"))
        self.btn_zones[key] = (x, y, x + w, y + h)

    # ---------- ПЕРЕРИСОВКА ----------
    def _redraw_all(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = self.W, self.H
        self.W, self.H = w, h

        self.btn_zones = {}

        self._draw_bg(w, h)
        self._draw_header(w)
        self._draw_big_hex(w, 90)
        self._draw_bytes_table(w, 240)
        self._draw_total(w, 600)
        self._draw_buttons(w, 720)

    # ---------- КЛИКИ ----------
    def _on_click(self, event):
        x, y = event.x, event.y
        for key, (x0, y0, x1, y1) in self.btn_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                self._do_action(key)
                return

    def _do_action(self, key):
        if key == "random":
            self.state.randomize()
        elif key == "clear":
            self.state.clear()
        elif key == "ff":
            self.state.set_all_ff()

    # ---------- АНИМАЦИЯ ----------
    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        self._redraw_all()
        self.root.after(60, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()