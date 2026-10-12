"""
ОКФРС. Практика 6. Задание 3.
Вывод 4 байт в двоичном виде + контрольная сумма.
Проверка: изменение любого бита → меняется контрольная сумма.
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
        # история контрольной суммы
        self.prev_checksum = None
        self.last_changed_idx = None
        self.change_flash_until = 0.0

    def randomize(self):
        self.prev_checksum = self.checksum()
        self.bits = [random.randint(0, 1) for _ in range(32)]
        self.last_changed_idx = None

    def toggle(self, idx):
        if 0 <= idx < 32:
            self.prev_checksum = self.checksum()
            self.bits[idx] = 1 - self.bits[idx]
            self.last_changed_idx = idx
            self.change_flash_until = time.time() + 1.0

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

    def checksum(self):
        """
        Контрольная сумма — XOR всех байтов + инверсия + маска 0xFF.
        Меняется при любом изменении любого бита.
        """
        bytes_vals = self.get_bytes()
        s = 0
        for v in bytes_vals:
            s ^= v
        return (~s) & 0xFF

    def checksum_bin(self):
        return f"{self.checksum():08b}"

    def total_ones(self):
        return sum(self.bits)


# ============================================================
# ТУМБЛЕР
# ============================================================
def draw_switch(canvas, x, y, w, h, state, color=NEON_GREEN, flash=False):
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
                   outline=NEON_AMBER if flash else "#2a3040",
                   width=2)
        r = (h - 2 * pad) // 2
        cx = x + pad + r
        cy = y + h // 2
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill="#3a4050", outline="#5a6070", width=1)

    # если был изменён недавно — подсветить
    if flash:
        canvas.create_oval(x - 4, y - 4, x + w + 4, y + h + 4,
                           fill="", outline=NEON_AMBER, width=2,
                           dash=(4, 3))


# ============================================================
# КАРТОЧКА БАЙТА
# ============================================================
def draw_byte_card(canvas, x, y, w, h, byte_idx, bits, value, color,
                   changed_idx=None):
    round_rect(canvas, x, y, x + w, y + h, 14,
               fill=BG_GLASS,
               outline=lerp(color, BG_DEEP, 0.5), width=2)

    canvas.create_text(x + 18, y + 20, anchor="w",
                       text=f"БАЙТ {byte_idx+1}",
                       fill=TEXT_DIM, font=FONT_LABEL_S)
    canvas.create_text(x + w - 18, y + 20, anchor="e",
                       text=f"0x{value:02X}",
                       fill=color, font=FONT_MONO_S)

    bin_str = "".join(str(b) for b in bits)
    canvas.create_text(x + w / 2, y + 50,
                       text=bin_str,
                       fill=color,
                       font=("Consolas", 20, "bold"))
    canvas.create_text(x + w / 2, y + 68,
                       text="BIN",
                       fill=TEXT_DIM, font=("Consolas", 8))

    canvas.create_line(x + 15, y + 80,
                       x + w - 15, y + 80,
                       fill=BORDER)

    gap = 5
    total_w = w - 36
    sw_w = (total_w - 7 * gap) / 8
    sw_h = 24
    sw_y = y + 105

    zones = {}

    for i in range(8):
        sx = x + 18 + i * (sw_w + gap)
        bit_val = bits[i]
        global_idx = byte_idx * 8 + i

        flash = (changed_idx == global_idx)

        # номер бита над тумблером
        canvas.create_text(sx + sw_w / 2, sw_y - 10,
                           text=str(7 - i),
                           fill=NEON_AMBER if flash else TEXT_GLOW,
                           font=("Consolas", 9, "bold"))

        draw_switch(canvas, sx, sw_y, sw_w, sw_h, bit_val, color, flash)

        # значение бита под тумблером
        canvas.create_text(sx + sw_w / 2, sw_y + sw_h + 12,
                           text=str(bit_val),
                           fill=color if bit_val == 1 else TEXT_DIM,
                           font=("Consolas", 10, "bold"))

        zones[global_idx] = (sx, sw_y, sx + sw_w, sw_y + sw_h)

    canvas.create_text(x + w / 2, y + h - 22,
                       text=f"DEC = {value}",
                       fill=color, font=FONT_MONO)

    return zones


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Checksum · Контрольная сумма")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

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
        self.canvas.create_text(100, 40, text="CHECKSUM",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(280, 44,
                                text="· КОНТРОЛЬНАЯ СУММА · 32 БИТА",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

    # ---------- БОЛЬШАЯ КОНТРОЛЬНАЯ СУММА ----------
    def _draw_checksum_big(self, w, y):
        card_h = 140
        round_rect(self.canvas, 50, y, w - 50, y + card_h, 14,
                   fill=BG_GLASS, outline=NEON_AMBER, width=2)

        self.canvas.create_text(w / 2, y + 25,
                                text="▸ КОНТРОЛЬНАЯ СУММА",
                                fill=TEXT_DIM, font=FONT_LABEL)

        cs = self.state.checksum()
        cs_bin = self.state.checksum_bin()

        # DEC / HEX / BIN
        col_w = (w - 140) / 3

        # DEC
        x1 = 70 + col_w / 2
        self.canvas.create_text(x1, y + 55,
                                text="DEC",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        self.canvas.create_text(x1, y + 95,
                                text=f"{cs}",
                                fill=NEON_AMBER, font=("Consolas", 34, "bold"))

        # HEX
        x2 = 70 + col_w + col_w / 2
        self.canvas.create_text(x2, y + 55,
                                text="HEX",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        self.canvas.create_text(x2, y + 95,
                                text=f"0x{cs:02X}",
                                fill=NEON_PINK, font=("Consolas", 34, "bold"))

        # BIN
        x3 = 70 + col_w * 2 + col_w / 2
        self.canvas.create_text(x3, y + 55,
                                text="BIN",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        self.canvas.create_text(x3, y + 95,
                                text=cs_bin,
                                fill=NEON_GREEN, font=("Consolas", 26, "bold"))

        # разделители
        for i in range(1, 3):
            xx = 70 + i * col_w
            self.canvas.create_line(xx, y + 45, xx, y + card_h - 15,
                                    fill=BORDER, dash=(3, 3))

    # ---------- ИНДИКАТОР ИЗМЕНЕНИЯ ----------
    def _draw_change_indicator(self, w, y):
        card_h = 65
        prev = self.state.prev_checksum
        cur = self.state.checksum()

        if prev is None:
            bg = "#0e1218"
            outline = BORDER
            text = "Измените любой бит — контрольная сумма пересчитается"
            text_color = TEXT_DIM
        elif prev != cur:
            bg = lerp(NEON_GREEN, BG_DEEP, 0.75)
            outline = NEON_GREEN
            text = f"✓ БИТ ИЗМЕНЁН: контрольная сумма изменилась  {prev} → {cur}"
            text_color = NEON_GREEN
        else:
            bg = lerp(NEON_AMBER, BG_DEEP, 0.75)
            outline = NEON_AMBER
            text = "— Значение не изменилось"
            text_color = NEON_AMBER

        round_rect(self.canvas, 50, y, w - 50, y + card_h, 12,
                   fill=bg, outline=outline, width=2)

        # если недавно меняли — мигаем
        if time.time() < self.state.change_flash_until:
            self.canvas.create_text(w / 2, y + card_h / 2,
                                    text=text, fill=text_color,
                                    font=("Segoe UI", 14, "bold"))
        else:
            self.canvas.create_text(w / 2, y + card_h / 2,
                                    text=text, fill=text_color,
                                    font=("Segoe UI", 12, "bold"))

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
                       "✕  ВСЕ 0", NEON_RED, "clear")
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

        # определяем какой бит недавно менялся
        flash_idx = None
        if time.time() < self.state.change_flash_until:
            flash_idx = self.state.last_changed_idx

        for b in range(4):
            x = 50 + b * (card_w + 20)
            zones = draw_byte_card(self.canvas, x, card_y, card_w, card_h,
                                    b, self.state.byte_bits(b), byte_vals[b],
                                    byte_colors[b], flash_idx)
            self.switch_zones.update(zones)

        # большая контрольная сумма
        self._draw_checksum_big(w, 290)

        # индикатор изменения
        self._draw_change_indicator(w, 450)

        # кнопки
        self._draw_buttons(w, 540)

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
            self.state.prev_checksum = self.state.checksum()
            self.state.bits = [0] * 32
            self.state.last_changed_idx = None
        elif key == "all_ones":
            self.state.prev_checksum = self.state.checksum()
            self.state.bits = [1] * 32
            self.state.last_changed_idx = None

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