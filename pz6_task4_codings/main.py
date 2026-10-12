"""
ОКФРС. Практика 6. Задание 4.
Кодировки битового сигнала: NRZ · NRZI · Манчестер · MLT-3 · AMI · Pulse.
Интерфейс уровня лабораторного ПО.
Премиум-стиль 2026.
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import sys, os, math, random, time, csv, datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# ПАЛИТРА
# ============================================================
BG_DEEP    = "#08090f"
BG_GLASS   = "#131823"
BG_CARD    = "#0f141c"
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
def encode_nrz(bits):
    return [1 if b == 1 else -1 for b in bits]


def encode_nrzi(bits):
    levels = []
    cur = -1
    for b in bits:
        if b == 1:
            cur = -cur
        levels.append(cur)
    return levels


def encode_manchester(bits):
    levels = []
    for b in bits:
        if b == 1:
            levels.extend([-1, 1])
        else:
            levels.extend([1, -1])
    return levels


def encode_mlt3(bits):
    cycle = [-1, 0, 1, 0]
    idx = 0
    levels = []
    for b in bits:
        if b == 1:
            idx = (idx + 1) % 4
        levels.append(cycle[idx])
    return levels


def encode_ami(bits):
    levels = []
    sign = 1
    for b in bits:
        if b == 1:
            levels.append(sign)
            sign = -sign
        else:
            levels.append(0)
    return levels


def encode_pulse(bits):
    levels = []
    for b in bits:
        if b == 1:
            levels.extend([1, 0])
        else:
            levels.extend([0, 0])
    return levels


CODINGS = [
    ("NRZ",        "1 = высокий, 0 = низкий",           encode_nrz,        NEON_CYAN,  1),
    ("NRZI",       "1 = смена, 0 = без смены",          encode_nrzi,       NEON_BLUE,  1),
    ("MANCHESTER", "0 = В→Н, 1 = Н→В",                  encode_manchester, NEON_GREEN, 2),
    ("MLT-3",      "1 = смена (-1→0→+1→0), 0 = без",     encode_mlt3,       NEON_AMBER, 1),
    ("AMI",        "0 = 0, 1 = чередование +1 / -1",     encode_ami,        NEON_PINK,  1),
    ("PULSE (RZ)", "1 = импульс в первой половине",      encode_pulse,      NEON_PURP,  2),
]


# ============================================================
# СОСТОЯНИЕ
# ============================================================
class AppState:
    def __init__(self):
        self.bits = [random.randint(0, 1) for _ in range(32)]
        self.hover_bit = None
        self.hover_coding = None

    def randomize(self):
        self.bits = [random.randint(0, 1) for _ in range(32)]

    def clear(self):
        self.bits = [0] * 32

    def all_ones(self):
        self.bits = [1] * 32

    def set_bits(self, s):
        s = "".join(c for c in s if c in "01")
        self.bits = [int(c) for c in s] if s else []

    def to_string(self):
        return "".join(str(b) for b in self.bits)


def checksum_byte(bits):
    cs = 0
    for b in bits:
        cs = ((cs << 1) | b) & 0xFF
    return cs


# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Bit Encoding Analyzer")
        root.geometry("1600x1000")
        root.minsize(1400, 900)
        root.configure(bg=BG_DEEP)

        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.state = AppState()
        self.btn_zones = {}
        self.entry_widget = None

        self.W, self.H = 1600, 1000

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

    # ---------- ЗАГОЛОВОК ----------
    def _draw_header(self, w):
        self.canvas.create_text(60, 35, text="⚡",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 22))
        self.canvas.create_text(95, 35, text="BIT ENCODER",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 17, "bold"))
        self.canvas.create_text(260, 38,
                                text="· NRZ · MANCHESTER · MLT-3 · AMI",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 10, "bold"))

        # FPS + CHK — в правом верхнем углу, с запасом
        self.canvas.create_text(w - 120, 25,
                                text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, anchor="e",
                                font=("Consolas", 10, "bold"))
        self.canvas.create_text(w - 120, 45,
                                text=f"CHK 0x{checksum_byte(self.state.bits):02X}",
                                fill=NEON_AMBER, anchor="e",
                                font=("Consolas", 11, "bold"))

        self.canvas.create_line(40, 60, w - 40, 60, fill=BORDER)

    # ---------- ПАНЕЛЬ ВВОДА ----------
    def _draw_input_panel(self, w, y):
        card_h = 130
        inner_pad = 20
        round_rect(self.canvas, 40, y, w - 40, y + card_h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(40 + inner_pad, y + 22, anchor="w",
                                text="▸ ПОСЛЕДОВАТЕЛЬНОСТЬ БИТ",
                                fill=NEON_CYAN,
                                font=("Segoe UI", 10, "bold"))

        cs = checksum_byte(self.state.bits)
        self.canvas.create_text(40 + inner_pad, y + 42, anchor="w",
                                text=f"{len(self.state.bits)} бит · контрольная сумма 0x{cs:02X}",
                                fill=TEXT_DIM,
                                font=("Segoe UI", 9))

        # === КНОПКИ СЧИТАЕМ ПЕРВЫМИ, чтобы знать их ширину ===
        btn_w = 128
        btn_h = 26
        gap_x = 6
        gap_y = 6
        cols = 4
        rows = 2

        block_w = cols * btn_w + (cols - 1) * gap_x

        block_x1 = w - 40 - inner_pad
        block_x = block_x1 - block_w
        block_y = y + 14

        buttons = [
            ("🎲 СЛУЧАЙНО", NEON_PURP, "random"),
            ("✕ ВСЕ 0",     NEON_RED,   "clear"),
            ("✓ ВСЕ 1",     NEON_GREEN, "all_ones"),
            ("💾 PNG",      NEON_CYAN,  "export_png"),
            ("⇄ ИНВЕРТ",    NEON_AMBER, "invert"),
            ("↔ БАЙТЫ",     NEON_BLUE,  "swap_bytes"),
            ("📄 CSV",      NEON_GREEN, "export_csv"),
            ("⏱ ДЛИНА",     NEON_PINK,  "resize"),
        ]

        for i, (text, color, key) in enumerate(buttons):
            row = i // cols
            col = i % cols
            bx = block_x + col * (btn_w + gap_x)
            by = block_y + row * (btn_h + gap_y)

            round_rect(self.canvas, bx, by,
                       bx + btn_w, by + btn_h, 6,
                       fill=lerp(color, BG_DEEP, 0.8),
                       outline=color, width=1)
            self.canvas.create_text(bx + btn_w / 2, by + btn_h / 2,
                                    text=text, fill=color,
                                    font=("Segoe UI", 8, "bold"))
            self.btn_zones[key] = (bx, by, bx + btn_w, by + btn_h)

        # === ПОЛЕ ВВОДА — от левого края до блока кнопок ===
        entry_x = 40 + inner_pad
        entry_y = y + 62
        entry_w = block_x - entry_x - 20       # 20px зазор
        entry_h = 32

        if entry_w < 100:
            entry_w = 100

        round_rect(self.canvas, entry_x, entry_y,
                   entry_x + entry_w, entry_y + entry_h, 6,
                   fill="#0a0d14", outline=BORDER_HL, width=1)

        if self.entry_widget is None or not self.entry_widget.winfo_exists():
            self.entry_widget = tk.Entry(
                self.root,
                bg="#0a0d14", fg=NEON_GREEN,
                insertbackground=NEON_CYAN,
                font=("Consolas", 12, "bold"),
                bd=0, highlightthickness=0)
            self.entry_widget.insert(0, self.state.to_string())
            self.entry_widget.bind("<KeyRelease>", self._on_entry_change)
        else:
            if self.root.focus_get() != self.entry_widget:
                self.entry_widget.delete(0, tk.END)
                self.entry_widget.insert(0, self.state.to_string())

        self.entry_widget.place(x=entry_x + 10, y=entry_y + 6,
                                 width=entry_w - 20, height=entry_h - 12)

    # ---------- ГРАФИКИ ----------
    def _draw_waveforms(self, w, y_start, y_end):
        n_codings = len(CODINGS)
        gap_between = 10
        available_h = y_end - y_start
        block_h = (available_h - (n_codings - 1) * gap_between) / n_codings

        self._block_h = block_h
        self._gap_between = gap_between
        self._y_start = y_start

        for i, (name, desc, func, color, scale) in enumerate(CODINGS):
            yy = y_start + i * (block_h + gap_between)
            self._draw_one_waveform(w, yy, block_h, name, desc,
                                     func, color, scale)

    def _draw_one_waveform(self, w, y, h, name, desc, func, color, scale):
        round_rect(self.canvas, 40, y, w - 40, y + h, 10,
                   fill=BG_GLASS,
                   outline=lerp(color, BG_DEEP, 0.6), width=1)

        hover = (self.state.hover_coding == name)
        if hover:
            round_rect(self.canvas, 40, y, w - 40, y + h, 10,
                       outline=color, width=2)

        # подпись слева
        name_x = 40 + 20
        name_y = y + h / 2
        self.canvas.create_text(name_x, name_y - 10,
                                text=name, fill=color, anchor="w",
                                font=("Segoe UI", 11, "bold"))
        self.canvas.create_text(name_x, name_y + 10,
                                text=desc, fill=TEXT_DIM, anchor="w",
                                font=("Segoe UI", 8))

        # область графика
        gx0 = 260
        gx1 = w - 60
        gy0 = y + 12
        gy1 = y + h - 22

        mid_y = (gy0 + gy1) / 2

        round_rect(self.canvas, gx0, gy0, gx1, gy1, 4,
                   fill="#050810", outline="")

        if name in ("MANCHESTER", "PULSE (RZ)"):
            high_y = gy0 + 6
            low_y = gy1 - 6
        else:
            high_y = gy0 + 8
            low_y = gy1 - 8

        self.canvas.create_line(gx0, mid_y, gx1, mid_y,
                                fill="#1a2540", dash=(2, 4))

        bits = self.state.bits
        n = len(bits)
        if n == 0:
            self.canvas.create_text((gx0 + gx1) / 2, mid_y,
                                    text="нет данных",
                                    fill=TEXT_DIM,
                                    font=("Segoe UI", 10, "bold"))
            return

        levels = func(bits)
        n_levels = len(levels)

        step = (gx1 - gx0) / n_levels

        def level_to_y(lvl):
            if lvl > 0:
                return high_y
            elif lvl < 0:
                return low_y
            else:
                return mid_y

        # === сначала подсветка (под линией) ===
        if self.state.hover_bit is not None and 0 <= self.state.hover_bit < n:
            hb = self.state.hover_bit
            hx0 = gx0 + hb * step * scale
            hx1 = hx0 + step * scale

            # лёгкая заливка фона
            self.canvas.create_rectangle(hx0, gy0, hx1, gy1,
                                          fill=lerp(color, BG_DEEP, 0.85),
                                          outline="")
            # вертикальные пунктиры
            self.canvas.create_line(hx0, gy0, hx0, gy1,
                                    fill=color, dash=(3, 3), width=1)
            self.canvas.create_line(hx1, gy0, hx1, gy1,
                                    fill=color, dash=(3, 3), width=1)

        # === теперь линия сигнала (ПОВЕРХ подсветки) ===
        pts = []
        for i, lvl in enumerate(levels):
            x0 = gx0 + i * step
            x1 = gx0 + (i + 1) * step
            y_lvl = level_to_y(lvl)
            pts.extend([x0, y_lvl, x1, y_lvl])
            if i < n_levels - 1:
                y_next = level_to_y(levels[i + 1])
                pts.extend([x1, y_lvl, x1, y_next])

        if len(pts) >= 4:
            self.canvas.create_line(*pts,
                                    fill=lerp(color, BG_DEEP, 0.7),
                                    width=5, joinstyle="miter")
            self.canvas.create_line(*pts, fill=color,
                                    width=2, joinstyle="miter")

        # разделители битов
        for i in range(n + 1):
            xx = gx0 + i * step * scale
            if xx > gx1:
                break
            is_byte = (i % 8 == 0)
            col = "#3a4560" if is_byte else "#1a2540"
            dash = (2, 3) if is_byte else (1, 5)
            self.canvas.create_line(xx, gy0, xx, gy1,
                                    fill=col, dash=dash, width=1)

        # если hover — значение бита сверху и снизу от графика
        if self.state.hover_bit is not None and 0 <= self.state.hover_bit < n:
            hb = self.state.hover_bit
            hx0 = gx0 + hb * step * scale
            hx1 = hx0 + step * scale
            cx = (hx0 + hx1) / 2

            # значение бита — над графиком
            self.canvas.create_rectangle(cx - 14, gy0 - 18,
                                          cx + 14, gy0 - 2,
                                          fill=color, outline="")
            self.canvas.create_text(cx, gy0 - 10,
                                    text=str(bits[hb]),
                                    fill=BG_DEEP,
                                    font=("Consolas", 10, "bold"))

        # номера битов внизу
        for i in range(0, n, 8):
            xx = gx0 + i * step * scale + (step * scale) / 2
            self.canvas.create_text(xx, gy1 + 12,
                                    text=f"{i}",
                                    fill=TEXT_DIM,
                                    font=("Consolas", 8))

    # ---------- СТАТУС-БАР ----------
    def _draw_status_bar(self, w, h):
        y = h - 22
        self.canvas.create_line(40, y - 8, w - 40, y - 8, fill=BORDER)
        self.canvas.create_text(60, y + 3, anchor="w",
                                text=f"БИТ: {len(self.state.bits)}",
                                fill=TEXT_DIM,
                                font=("Consolas", 9, "bold"))
        self.canvas.create_text(200, y + 3, anchor="w",
                                text="Кликни в поле ввода — редактирование · Наведи на бит — увидишь значение",
                                fill=TEXT_DIM,
                                font=("Segoe UI", 9))

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
        self._draw_input_panel(w, 75)

        y_start = 220
        y_end = h - 35
        self._draw_waveforms(w, y_start, y_end)

        self._draw_status_bar(w, h)

    # ---------- СОБЫТИЯ ----------
    def _on_entry_change(self, event):
        try:
            text = self.entry_widget.get()
            filtered = "".join(c for c in text if c in "01")
            self.state.bits = [int(c) for c in filtered] if filtered else []
        except Exception:
            pass

    def _on_click(self, event):
        for key, (x0, y0, x1, y1) in self.btn_zones.items():
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                self._do_action(key)
                return

    def _on_motion(self, event):
        w = self.W
        h = self.H
        y_start = getattr(self, "_y_start", 220)
        block_h = getattr(self, "_block_h", 100)
        gap_between = getattr(self, "_gap_between", 10)

        self.state.hover_bit = None
        self.state.hover_coding = None

        y_cursor = event.y
        for i, (name, desc, func, color, scale) in enumerate(CODINGS):
            by = y_start + i * (block_h + gap_between)
            if by <= y_cursor <= by + block_h:
                self.state.hover_coding = name
                gx0 = 260
                gx1 = w - 60
                n = len(self.state.bits)
                if n > 0 and gx0 <= event.x <= gx1:
                    total_w = gx1 - gx0
                    bit_w = total_w / n
                    bit_i = int((event.x - gx0) / bit_w)
                    if 0 <= bit_i < n:
                        self.state.hover_bit = bit_i
                break

    def _on_leave(self, event):
        self.state.hover_bit = None
        self.state.hover_coding = None

    def _do_action(self, key):
        if key == "random":
            self.state.randomize()
            self._update_entry()
        elif key == "clear":
            self.state.clear()
            self._update_entry()
        elif key == "all_ones":
            self.state.all_ones()
            self._update_entry()
        elif key == "invert":
            self.state.bits = [1 - b for b in self.state.bits]
            self._update_entry()
        elif key == "swap_bytes":
            b = self.state.bits
            if len(b) == 32:
                chunks = [b[i * 8:(i + 1) * 8] for i in range(4)]
                chunks.reverse()
                self.state.bits = [x for c in chunks for x in c]
                self._update_entry()
        elif key == "resize":
            cur = len(self.state.bits)
            if cur < 16:
                n = 16
            elif cur < 32:
                n = 32
            elif cur < 64:
                n = 64
            else:
                n = 8
            self.state.bits = [random.randint(0, 1) for _ in range(n)]
            self._update_entry()
        elif key == "export_png":
            self._export_png()
        elif key == "export_csv":
            self._export_csv()

    def _update_entry(self):
        if self.entry_widget and self.entry_widget.winfo_exists():
            self.entry_widget.delete(0, tk.END)
            self.entry_widget.insert(0, self.state.to_string())

    def _export_png(self):
        try:
            from PIL import ImageGrab
            path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG image", "*.png")],
                initialfile=f"codings_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            if not path:
                return
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()
            ImageGrab.grab().crop((x, y, x1, y1)).save(path)
            messagebox.showinfo("Экспорт", f"Сохранено:\n{path}")
        except ImportError:
            messagebox.showerror("Ошибка",
                "Установите Pillow: pip install pillow")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"codings_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["BIT"] + [c[0] for c in CODINGS])
                for i, b in enumerate(self.state.bits):
                    row = [b]
                    for name, desc, func, color, scale in CODINGS:
                        levels = func(self.state.bits)
                        idx = int(i * scale + scale / 2)
                        if 0 <= idx < len(levels):
                            row.append(levels[idx])
                        else:
                            row.append("")
                    writer.writerow(row)
            messagebox.showinfo("Экспорт", f"Сохранено:\n{path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        self._redraw_all()
        self.root.after(80, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()