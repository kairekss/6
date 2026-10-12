"""
ОКФРС. Практика 6. Задание 1.
4 случайных байта (32 бита) + 32 физических переключателя.
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
        self.bits = [random.randint(0, 1) for _ in range(32)]
        self.pulse_t = 0.0

    def randomize(self):
        self.bits = [random.randint(0, 1) for _ in range(32)]

    def toggle(self, idx):
        if 0 <= idx < 32:
            self.bits[idx] = 1 - self.bits[idx]

    def get_bytes(self):
        result = []
        for b in range(4):
            val = 0
            for i in range(8):
                val = (val << 1) | self.bits[b * 8 + i]
            result.append(val)
        return result

    def byte_bits(self, byte_idx):
        return self.bits[byte_idx * 8: byte_idx * 8 + 8]

    def tick(self, dt):
        self.pulse_t += dt

    def total_ones(self):
        return sum(self.bits)


# ============================================================
# ТУМБЛЕР
# ============================================================
def draw_switch(canvas, x, y, w, h, state, color=NEON_GREEN):
    pad = 3
    if state == 1:
        for i in range(3, 0, -1):
            round_rect(canvas, x - i, y - i, x + w + i, y + h + i,
                       h // 2 + i,
                       fill="", outline=lerp(color, BG_DEEP, i / 4),
                       width=1)
        round_rect(canvas, x, y, x + w, y + h, h // 2,
                   fill=lerp(color, BG_DEEP, 0.4),
                   outline=color, width=2)
        r = (h - 2 * pad) // 2
        cx = x + w - pad - r
        cy = y + h // 2
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill="#ffffff", outline=color, width=1)
    else:
        round_rect(canvas, x, y, x + w, y + h, h // 2,
                   fill="#0f141c",
                   outline="#2a3040", width=2)
        r = (h - 2 * pad) // 2
        cx = x + pad + r
        cy = y + h // 2
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill="#3a4050", outline="#5a6070", width=1)


# ============================================================
# КАРТОЧКА БАЙТА
# ============================================================
def draw_byte_card(canvas, x, y, w, h, byte_idx, bits, value, color):
    """Карточка байта — компактная, с одним рядом тумблеров."""
    round_rect(canvas, x, y, x + w, y + h, 14,
               fill=BG_GLASS,
               outline=lerp(color, BG_DEEP, 0.5), width=2)

    # заголовок
    canvas.create_text(x + 18, y + 20, anchor="w",
                       text=f"БАЙТ {byte_idx+1}",
                       fill=TEXT_DIM, font=FONT_LABEL_S)
    # hex справа
    canvas.create_text(x + w - 18, y + 20, anchor="e",
                       text=f"0x{value:02X}",
                       fill=color, font=FONT_MONO_S)

    # двоичное значение
    bin_str = "".join(str(b) for b in bits)
    canvas.create_text(x + w / 2, y + 50,
                       text=bin_str,
                       fill=color,
                       font=("Consolas", 20, "bold"))
    canvas.create_text(x + w / 2, y + 68,
                       text="BIN",
                       fill=TEXT_DIM, font=("Consolas", 8))

    # разделитель
    canvas.create_line(x + 15, y + 80,
                       x + w - 15, y + 80,
                       fill=BORDER)

    # 8 тумблеров в один ряд
    gap = 5
    total_w = w - 36
    sw_w = (total_w - 7 * gap) / 8
    sw_h = 24
    sw_y = y + 105

    switch_zones = {}

    for i in range(8):
        sx = x + 18 + i * (sw_w + gap)
        bit_val = bits[i]

        # НОМЕР БИТА НАД тумблером
        canvas.create_text(sx + sw_w / 2, sw_y - 10,
                           text=str(7 - i),
                           fill=TEXT_GLOW,
                           font=("Consolas", 9, "bold"))

        draw_switch(canvas, sx, sw_y, sw_w, sw_h, bit_val, color)

        # значение бита под тумблером
        canvas.create_text(sx + sw_w / 2, sw_y + sw_h + 12,
                           text=str(bit_val),
                           fill=color if bit_val == 1 else TEXT_DIM,
                           font=("Consolas", 10, "bold"))

        switch_zones[byte_idx * 8 + i] = (sx, sw_y, sx + sw_w, sy + sw_h) \
            if False else (sx, sw_y, sx + sw_w, sw_y + sw_h)

    # DEC и HEX крупно
    canvas.create_text(x + w / 2, y + h - 22,
                       text=f"DEC = {value}",
                       fill=color, font=FONT_MONO)

    return switch_zones


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Bit Generator · 4 байта · 32 бита")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.state = BitsState()
        self.switch_zones = {}
        self.btn_zones = {}

        self.W, self.H = 1500, 950

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
        self.canvas.create_text(100, 40, text="BIT GENERATOR",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(340, 44, text="· 4 БАЙТА · 32 БИТА",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

    # ---------- СВОДКА ----------
    def _draw_summary(self, w, y):
        byte_vals = self.state.get_bytes()
        total = self.state.total_ones()

        card_h = 90
        round_rect(self.canvas, 50, y, w - 50, y + card_h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(80, y + 25, anchor="w",
                                text="ВСЕГО БИТ",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        self.canvas.create_text(80, y + 60, anchor="w",
                                text="32",
                                fill=NEON_CYAN, font=FONT_BIG)

        self.canvas.create_text(230, y + 25, anchor="w",
                                text="ВКЛ (1)",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        self.canvas.create_text(230, y + 60, anchor="w",
                                text=f"{total}",
                                fill=NEON_GREEN, font=FONT_BIG)

        self.canvas.create_text(360, y + 25, anchor="w",
                                text="ВЫКЛ (0)",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        self.canvas.create_text(360, y + 60, anchor="w",
                                text=f"{32 - total}",
                                fill=NEON_RED, font=FONT_BIG)

        self.canvas.create_text(500, y + 25, anchor="w",
                                text="32-БИТ HEX",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        hex32 = f"0x{byte_vals[0]:02X}{byte_vals[1]:02X}{byte_vals[2]:02X}{byte_vals[3]:02X}"
        self.canvas.create_text(500, y + 60, anchor="w",
                                text=hex32,
                                fill=NEON_AMBER, font=FONT_BIG)

    # ---------- КНОПКИ (внизу, отдельно) ----------
    def _draw_buttons_row(self, w, y):
        btn_w = 200
        btn_h = 50
        gap = 20
        total = 3 * btn_w + 2 * gap
        start_x = (w - total) / 2

        self._draw_btn(start_x, y, btn_w, btn_h,
                       "🎲  СЛУЧАЙНО", NEON_PURP, "random")
        self._draw_btn(start_x + btn_w + gap, y, btn_w, btn_h,
                       "✕  ОЧИСТИТЬ", NEON_RED, "clear")
        self._draw_btn(start_x + 2 * (btn_w + gap), y, btn_w, btn_h,
                       "✓  ВСЕ 1", NEON_GREEN, "all_ones")

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

    # ---------- ГРАФИК СИГНАЛА ----------
    def _draw_wave(self, w, y, h):
        round_rect(self.canvas, 50, y, w - 50, y + h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(70, y + 22, anchor="w",
                                text="▸ БИТОВЫЙ СИГНАЛ NRZ",
                                fill=NEON_CYAN, font=FONT_LABEL)
        self.canvas.create_text(w - 70, y + 22, anchor="e",
                                text="уровень 1 = высокий · 0 = низкий",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        gx0 = 80
        gx1 = w - 80
        gy0 = y + 50
        gy1 = y + h - 50

        high_y = gy0 + 15
        low_y = gy1 - 15

        # уровни
        self.canvas.create_line(gx0, high_y, gx1, high_y,
                                fill="#1a2540", dash=(4, 4))
        self.canvas.create_line(gx0, low_y, gx1, low_y,
                                fill="#1a2540", dash=(4, 4))
        self.canvas.create_text(gx0 - 12, high_y, anchor="e", text="1",
                                fill=NEON_GREEN, font=FONT_MONO_S)
        self.canvas.create_text(gx0 - 12, low_y, anchor="e", text="0",
                                fill=NEON_RED, font=FONT_MONO_S)

        bit_w = (gx1 - gx0) / 32

        pts = []
        for i in range(32):
            bit = self.state.bits[i]
            y_level = high_y if bit == 1 else low_y
            x0 = gx0 + i * bit_w
            x1 = gx0 + (i + 1) * bit_w
            pts.extend([x0, y_level, x1, y_level])
            if i < 31:
                y_next = high_y if self.state.bits[i + 1] == 1 else low_y
                pts.extend([x1, y_level, x1, y_next])

        if len(pts) >= 4:
            self.canvas.create_line(*pts,
                                    fill=lerp(NEON_GREEN, BG_DEEP, 0.7),
                                    width=6, joinstyle="miter")
            self.canvas.create_line(*pts, fill=NEON_GREEN,
                                    width=2, joinstyle="miter")

        # разделители между байтами
        for b in range(1, 4):
            xx = gx0 + b * 8 * bit_w
            self.canvas.create_line(xx, gy0, xx, gy1,
                                    fill="#2a3040", dash=(2, 2))

        # номера битов
        for i in range(0, 32, 4):
            xx = gx0 + (i + 2) * bit_w
            self.canvas.create_text(xx, gy1 + 18,
                                    text=str(i),
                                    fill=TEXT_DIM,
                                    font=("Consolas", 9))

    # ---------- ПЕРЕРИСОВКА ----------
    def _redraw_all(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = self.W, self.H
        self.W, self.H = w, h

        self.switch_zones = {}
        self.btn_zones = {}

        self._draw_bg(w, h)
        self._draw_header(w)

        # карточки байтов
        card_w = (w - 100 - 3 * 20) / 4
        card_h = 175
        card_y = 95
        byte_vals = self.state.get_bytes()
        byte_colors = [NEON_CYAN, NEON_GREEN, NEON_PINK, NEON_PURP]

        for b in range(4):
            x = 50 + b * (card_w + 20)
            zones = draw_byte_card(self.canvas, x, card_y, card_w, card_h,
                                    b, self.state.byte_bits(b), byte_vals[b],
                                    byte_colors[b])
            self.switch_zones.update(zones)

        # сводка
        summary_y = card_y + card_h + 20
        self._draw_summary(w, summary_y)

        # кнопки — ОТДЕЛЬНЫЙ РЯД под сводкой
        btn_y = summary_y + 90 + 15
        self._draw_buttons_row(w, btn_y)

        # график сигнала
        wave_y = btn_y + 50 + 20
        wave_h = h - wave_y - 20
        if wave_h > 100:
            self._draw_wave(w, wave_y, wave_h)

    # ---------- КЛИКИ ----------
    def _on_click(self, event):
        x, y = event.x, event.y

        for idx, (x0, y0, x1, y1) in self.switch_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                self.state.toggle(idx)
                return

        for key, (x0, y0, x1, y1) in self.btn_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                self._do_action(key)
                return

    def _do_action(self, key):
        if key == "random":
            self.state.randomize()
        elif key == "clear":
            self.state.bits = [0] * 32
        elif key == "all_ones":
            self.state.bits = [1] * 32

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