"""
ОКФРС. Практика 6. Задание 10.
Цифровые модуляции: ASK · FSK · PSK (+ QPSK).
Управление основными параметрами.
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
BG_GRAPH   = "#050810"
BG_PANEL   = "#0f141c"
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
# МОДУЛЯЦИИ
# ============================================================
def ask_signal(bits, t, f_c, bit_duration):
    """
    ASK (Amplitude Shift Keying):
    1 → несущая есть, 0 → нет.
    """
    bit_idx = int(t / bit_duration)
    if bit_idx >= len(bits):
        bit_idx = len(bits) - 1
    b = bits[bit_idx]
    return math.cos(2 * math.pi * f_c * t) if b == 1 else 0.0


def fsk_signal(bits, t, f_0, f_1, bit_duration):
    """
    FSK (Frequency Shift Keying):
    0 → f_0, 1 → f_1.
    """
    bit_idx = int(t / bit_duration)
    if bit_idx >= len(bits):
        bit_idx = len(bits) - 1
    b = bits[bit_idx]
    f = f_1 if b == 1 else f_0
    return math.cos(2 * math.pi * f * t)


def psk_signal(bits, t, f_c, bit_duration):
    """
    BPSK (Binary Phase Shift Keying):
    0 → фаза 0, 1 → фаза π.
    """
    bit_idx = int(t / bit_duration)
    if bit_idx >= len(bits):
        bit_idx = len(bits) - 1
    b = bits[bit_idx]
    phase = math.pi if b == 1 else 0.0
    return math.cos(2 * math.pi * f_c * t + phase)


def qpsk_signal(bits, t, f_c, bit_duration):
    """
    QPSK — использует пары бит:
    00 → +45°,  01 → +135°,  10 → -45°,  11 → -135°.
    """
    pair_idx = int(t / bit_duration)
    if pair_idx * 2 >= len(bits):
        pair_idx = (len(bits) - 1) // 2
    # берём пару
    i1 = pair_idx * 2
    i2 = i1 + 1
    b1 = bits[i1] if i1 < len(bits) else 0
    b2 = bits[i2] if i2 < len(bits) else 0

    phase_map = {
        (0, 0): math.pi / 4,
        (0, 1): 3 * math.pi / 4,
        (1, 0): -math.pi / 4,
        (1, 1): -3 * math.pi / 4,
    }
    phase = phase_map.get((b1, b2), 0.0)
    return math.cos(2 * math.pi * f_c * t + phase)


# ============================================================
# СОСТОЯНИЕ
# ============================================================
class AppState:
    def __init__(self):
        # биты — 8 штук
        self.bits = [1, 0, 1, 1, 0, 0, 1, 0]
        self.bits_per_symbol = 8

        # параметры
        self.carrier_freq = 10.0        # f_c — несущая
        self.f_0 = 5.0                  # для FSK
        self.f_1 = 15.0                 # для FSK
        self.bit_duration = 0.1         # длительность одного бита, сек
        self.amplitude = 1.0

        self.t_max = 8 * 0.1  # 8 бит × 0.1 = 0.8 сек

        self.paused = False
        self.anim_time = 0.0

        # тип модуляции
        self.modulation = "ASK"   # ASK | FSK | PSK | QPSK

    def tick(self, dt):
        if not self.paused:
            self.anim_time += dt
            if self.anim_time > self.t_max:
                self.anim_time = 0.0

    def reset(self):
        self.bits = [1, 0, 1, 1, 0, 0, 1, 0]
        self.carrier_freq = 10.0
        self.f_0 = 5.0
        self.f_1 = 15.0
        self.bit_duration = 0.1
        self.amplitude = 1.0
        self.paused = False
        self.anim_time = 0.0
        self.t_max = 8 * 0.1
        self.modulation = "ASK"

    def randomize(self):
        self.bits = [random.randint(0, 1) for _ in range(8)]

    def get_signal(self, t):
        """Возвращает значение сигнала в момент t согласно текущей модуляции."""
        if self.modulation == "ASK":
            return self.amplitude * ask_signal(self.bits, t, self.carrier_freq,
                                                 self.bit_duration)
        elif self.modulation == "FSK":
            return self.amplitude * fsk_signal(self.bits, t,
                                                 self.f_0, self.f_1,
                                                 self.bit_duration)
        elif self.modulation == "PSK":
            return self.amplitude * psk_signal(self.bits, t, self.carrier_freq,
                                                 self.bit_duration)
        elif self.modulation == "QPSK":
            return self.amplitude * qpsk_signal(self.bits, t, self.carrier_freq,
                                                  self.bit_duration)
        return 0.0


# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Digital Modulation · ASK · FSK · PSK")
        root.geometry("1600x1000")
        root.minsize(1400, 900)
        root.configure(bg=BG_DEEP)

        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.state = AppState()
        self.btn_zones = {}
        self.slider_zones = {}
        self.drag_slider = None

        self.W, self.H = 1600, 1000

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

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
        self.canvas.create_text(60, 40, text="∿",
                                fill=NEON_CYAN,
                                font=("Segoe UI", 30, "bold"))
        self.canvas.create_text(100, 40, text="DIGITAL MODULATION",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(400, 44,
                                text="· ASK · FSK · PSK · QPSK",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 11, "bold"))

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

    # ---------- ГРАФИК ----------
    def _draw_graph(self, w, y, h):
        panel_w = 420
        card_x = 50
        card_w = w - 100 - panel_w - 20

        round_rect(self.canvas, card_x, y, card_x + card_w, y + h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        # заголовок
        info = {
            "ASK":  "1 → несущая есть,   0 → нет",
            "FSK":  "0 → низкая частота,  1 → высокая",
            "PSK":  "0 → фаза 0°,   1 → фаза 180°",
            "QPSK": "пары бит: 00 / 01 / 10 / 11 → 4 фазы",
        }
        self.canvas.create_text(card_x + 20, y + 25, anchor="w",
                                text=f"▸ {self.state.modulation}",
                                fill=NEON_CYAN, font=FONT_LABEL)
        self.canvas.create_text(card_x + 120, y + 25, anchor="w",
                                text=info.get(self.state.modulation, ""),
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        if self.state.paused:
            self.canvas.create_text(card_x + card_w - 20, y + 25, anchor="e",
                                    text="⏸ ПАУЗА",
                                    fill=NEON_AMBER, font=FONT_LABEL)

        # область графика
        gx0 = card_x + 70
        gx1 = card_x + card_w - 40
        gy0 = y + 60
        gy1 = y + h - 100

        mid_y = (gy0 + gy1) / 2
        half_h = (gy1 - gy0) / 2

        round_rect(self.canvas, gx0, gy0, gx1, gy1, 4,
                   fill=BG_GRAPH, outline="")

        # сетка по битам
        n_bits = len(self.state.bits)
        for i in range(n_bits + 1):
            t_bit = i * self.state.bit_duration
            xx = gx0 + (t_bit / self.state.t_max) * (gx1 - gx0)
            is_major = (i % 2 == 0)
            col = "#2a3040" if is_major else "#1a2540"
            dash = () if is_major else (2, 3)
            self.canvas.create_line(xx, gy0, xx, gy1,
                                    fill=col, dash=dash, width=1)

        # горизонтальная сетка
        for i in range(5):
            k = i / 4
            yy = gy0 + (gy1 - gy0) * k
            is_mid = (i == 2)
            col = "#2a3040" if is_mid else "#0f1420"
            dash = () if is_mid else (2, 3)
            self.canvas.create_line(gx0, yy, gx1, yy,
                                    fill=col, dash=dash, width=1)

        # оси
        self.canvas.create_line(gx0, mid_y, gx1, mid_y,
                                fill=NEON_AMBER, width=2)
        self.canvas.create_line(gx0, gy0, gx0, gy1,
                                fill=NEON_AMBER, width=2)

        self.canvas.create_text(gx1 - 15, mid_y - 12, anchor="e",
                                text="t, с", fill=NEON_AMBER,
                                font=("Consolas", 11, "italic"))
        self.canvas.create_text(gx0 + 15, gy0 + 12, anchor="w",
                                text="s", fill=NEON_AMBER,
                                font=("Consolas", 11, "italic"))

        # === сигнал ===
        n_pts = 2000
        pts = []
        for j in range(n_pts):
            t = j / (n_pts - 1) * self.state.t_max
            v = self.state.get_signal(t)
            y_norm = v / max(0.1, self.state.amplitude)
            y_norm = max(-1.0, min(1.0, y_norm))
            px = gx0 + (j / (n_pts - 1)) * (gx1 - gx0)
            py = mid_y - y_norm * half_h * 0.85
            pts.extend([px, py])

        if len(pts) >= 4:
            self.canvas.create_line(*pts,
                                    fill=lerp(NEON_CYAN, BG_DEEP, 0.75),
                                    width=6, joinstyle="miter")
            self.canvas.create_line(*pts, fill=NEON_CYAN,
                                    width=2, joinstyle="miter")

        # === анимационный маркер ===
        if not self.state.paused:
            t_m = self.state.anim_time
            v = self.state.get_signal(t_m)
            y_norm = v / max(0.1, self.state.amplitude)
            y_norm = max(-1.0, min(1.0, y_norm))
            px = gx0 + (t_m / self.state.t_max) * (gx1 - gx0)
            py = mid_y - y_norm * half_h * 0.85

            for r in range(12, 0, -3):
                col = lerp(NEON_AMBER, BG_DEEP, r / 14)
                self.canvas.create_oval(px - r, py - r,
                                        px + r, py + r,
                                        fill="", outline=col, width=1)
            self.canvas.create_oval(px - 6, py - 6, px + 6, py + 6,
                                    fill=NEON_AMBER, outline="#ffffff", width=2)

        # === биты снизу графика ===
        bit_y = gy1 + 20
        for i, b in enumerate(self.state.bits):
            t_c = (i + 0.5) * self.state.bit_duration
            xx = gx0 + (t_c / self.state.t_max) * (gx1 - gx0)
            col = NEON_GREEN if b == 1 else NEON_RED
            # маленький индикатор
            round_rect(self.canvas, xx - 12, bit_y - 2,
                       xx + 12, bit_y + 18, 4,
                       fill=lerp(col, BG_DEEP, 0.7),
                       outline=col, width=1)
            self.canvas.create_text(xx, bit_y + 8,
                                    text=str(b), fill=col,
                                    font=("Consolas", 11, "bold"))

        self.canvas.create_text(gx0 - 20, bit_y + 8, anchor="e",
                                text="БИТЫ:",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        # === подписи времени под графиком ===
        for i in range(n_bits + 1):
            t = i * self.state.bit_duration
            xx = gx0 + (t / self.state.t_max) * (gx1 - gx0)
            self.canvas.create_text(xx, gy1 + 40,
                                    text=f"{t:.2f}",
                                    fill=TEXT_DIM,
                                    font=("Consolas", 8))

        # === легенда типов модуляции ===
        leg_y = gy1 + 60
        descriptions = [
            ("ASK",  "Amplitude Shift Keying", NEON_GREEN),
            ("FSK",  "Frequency Shift Keying", NEON_AMBER),
            ("PSK",  "Phase Shift Keying",     NEON_PINK),
            ("QPSK", "Quadrature PSK",         NEON_PURP),
        ]
        x_start = gx0
        for i, (name, desc, col) in enumerate(descriptions):
            is_active = (self.state.modulation == name)
            x = x_start + i * 200
            marker_col = col if is_active else TEXT_DIM
            self.canvas.create_text(x, leg_y, anchor="w",
                                    text=f"{'▶' if is_active else ' '} {name}",
                                    fill=marker_col,
                                    font=("Consolas", 10, "bold"))
            self.canvas.create_text(x + 60, leg_y, anchor="w",
                                    text=desc, fill=TEXT_DIM,
                                    font=("Segoe UI", 9))

    # ---------- ПАНЕЛЬ ----------
    def _draw_panel(self, w, y, h):
        panel_w = 420
        panel_x = w - 50 - panel_w

        round_rect(self.canvas, panel_x, y, panel_x + panel_w, y + h, 14,
                   fill=BG_GLASS, outline=lerp(NEON_PURP, BG_DEEP, 0.5),
                   width=2)

        self.canvas.create_text(panel_x + 20, y + 25, anchor="w",
                                text="▸ ТИП МОДУЛЯЦИИ",
                                fill=NEON_PURP, font=FONT_LABEL)

        # === 4 кнопки выбора модуляции ===
        self.btn_zones = {}
        btn_w = 90
        btn_h = 50
        gap = 10
        total_w = 4 * btn_w + 3 * gap
        start_x = panel_x + (panel_w - total_w) / 2
        sel_y = y + 50

        modulations = [
            ("ASK",  NEON_GREEN),
            ("FSK",  NEON_AMBER),
            ("PSK",  NEON_PINK),
            ("QPSK", NEON_PURP),
        ]
        for i, (name, col) in enumerate(modulations):
            bx = start_x + i * (btn_w + gap)
            active = (self.state.modulation == name)
            self._draw_mod_btn(bx, sel_y, btn_w, btn_h,
                                name, col, active)

        # === ползунки параметров ===
        self.canvas.create_text(panel_x + 20, y + 120, anchor="w",
                                text="▸ ПАРАМЕТРЫ",
                                fill=NEON_PURP, font=FONT_LABEL)

        sliders = []
        if self.state.modulation in ("ASK", "PSK", "QPSK"):
            sliders.append(("НЕСУЩАЯ · f_c", "carrier_freq", 4.0, 30.0,
                            self.state.carrier_freq, NEON_CYAN, "Гц"))
        if self.state.modulation == "FSK":
            sliders.append(("ЧАСТОТА · f_0 (бит 0)", "f_0", 2.0, 15.0,
                            self.state.f_0, NEON_RED, "Гц"))
            sliders.append(("ЧАСТОТА · f_1 (бит 1)", "f_1", 5.0, 30.0,
                            self.state.f_1, NEON_GREEN, "Гц"))
        sliders.append(("ДЛИТЕЛЬНОСТЬ БИТА", "bit_duration", 0.02, 0.3,
                        self.state.bit_duration, NEON_AMBER, "сек"))
        sliders.append(("АМПЛИТУДА", "amplitude", 0.2, 2.0,
                        self.state.amplitude, NEON_PINK, "В"))

        slider_h = 80
        start_y = y + 145
        self.slider_zones = {}

        for i, (label, key, vmin, vmax, val, color, unit) in enumerate(sliders):
            sy = start_y + i * slider_h

            self.canvas.create_text(panel_x + 20, sy, anchor="w",
                                    text=label,
                                    fill=TEXT_DIM, font=FONT_LABEL)

            if key == "bit_duration":
                val_text = f"{val:.3f} {unit}"
            else:
                val_text = f"{val:.2f} {unit}"
            self.canvas.create_text(panel_x + panel_w - 20, sy, anchor="e",
                                    text=val_text,
                                    fill=color, font=FONT_MONO_S)

            bar_x0 = panel_x + 20
            bar_x1 = panel_x + panel_w - 20
            bar_y = sy + 28
            bar_h = 8

            round_rect(self.canvas, bar_x0, bar_y - bar_h/2,
                       bar_x1, bar_y + bar_h/2, 4,
                       fill="#0f141c", outline="")

            k = (val - vmin) / (vmax - vmin) if vmax > vmin else 0
            k = max(0.0, min(1.0, k))
            if k > 0.005:
                round_rect(self.canvas, bar_x0, bar_y - bar_h/2,
                           bar_x0 + (bar_x1 - bar_x0) * k, bar_y + bar_h/2,
                           4, fill=color, outline="")

            cx_ = bar_x0 + (bar_x1 - bar_x0) * k
            self.canvas.create_oval(cx_ - 9, bar_y - 9,
                                    cx_ + 9, bar_y + 9,
                                    fill="#ffffff", outline=color, width=2)

            for j in range(5):
                kk = j / 4
                xx = bar_x0 + (bar_x1 - bar_x0) * kk
                self.canvas.create_line(xx, bar_y + 12, xx, bar_y + 16,
                                        fill=TEXT_DIM, width=1)

            self.slider_zones[key] = (bar_x0 - 10, bar_y - 14,
                                       bar_x1 + 10, bar_y + 14,
                                       vmin, vmax)

        # === информационный блок ===
        info_y = start_y + len(sliders) * slider_h + 5

        round_rect(self.canvas, panel_x + 20, info_y,
                   panel_x + panel_w - 20, info_y + 110, 10,
                   fill=BG_PANEL, outline=NEON_CYAN, width=1)

        self.canvas.create_text(panel_x + panel_w / 2, info_y + 20,
                                text="ПАРАМЕТРЫ СИГНАЛА",
                                fill=NEON_CYAN,
                                font=FONT_LABEL_S)

        # левый столбец
        self.canvas.create_text(panel_x + 35, info_y + 45, anchor="w",
                                text=f"f_c = {self.state.carrier_freq:.2f} Гц",
                                fill=NEON_CYAN, font=FONT_MONO_S)
        self.canvas.create_text(panel_x + 35, info_y + 68, anchor="w",
                                text=f"Бит = {self.state.bit_duration*1000:.0f} мс",
                                fill=NEON_AMBER, font=FONT_MONO_S)
        self.canvas.create_text(panel_x + 35, info_y + 91, anchor="w",
                                text=f"Ампл = {self.state.amplitude:.2f} В",
                                fill=NEON_PINK, font=FONT_MONO_S)

        # правый столбец
        bit_rate = 1.0 / self.state.bit_duration
        self.canvas.create_text(panel_x + panel_w - 35, info_y + 45, anchor="e",
                                text=f"Скорость = {bit_rate:.0f} бит/с",
                                fill=NEON_GREEN, font=FONT_MONO_S)
        self.canvas.create_text(panel_x + panel_w - 35, info_y + 68, anchor="e",
                                text=f"Битов = {len(self.state.bits)}",
                                fill=NEON_GREEN, font=FONT_MONO_S)
        self.canvas.create_text(panel_x + panel_w - 35, info_y + 91, anchor="e",
                                text=f"Длина = {self.state.t_max:.2f} с",
                                fill=NEON_CYAN, font=FONT_MONO_S)

        # === кнопки действий ===
        btn_y = info_y + 120
        b_w = 130
        b_h = 40
        b_gap = 8

        self._draw_btn(panel_x + 15, btn_y, b_w, b_h,
                       "⏸ ПАУЗА", NEON_AMBER, "pause",
                       active=self.state.paused)
        self._draw_btn(panel_x + 15 + b_w + b_gap, btn_y, b_w, b_h,
                       "↺ СБРОС", NEON_RED, "reset")
        self._draw_btn(panel_x + 15 + 2 * (b_w + b_gap), btn_y, b_w, b_h,
                       "🎲 СЛУЧАЙНО", NEON_PURP, "random")

        # === биты — ряд переключателей ===
        bit_y = btn_y + b_h + 20
        self.canvas.create_text(panel_x + 20, bit_y, anchor="w",
                                text="▸ БИТЫ (клик для переключения):",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        for i, b in enumerate(self.state.bits):
            bx = panel_x + 20 + i * 45
            by = bit_y + 20
            col = NEON_GREEN if b == 1 else NEON_RED
            round_rect(self.canvas, bx, by, bx + 38, by + 40, 6,
                       fill=lerp(col, BG_DEEP, 0.7),
                       outline=col, width=2)
            self.canvas.create_text(bx + 19, by + 20,
                                    text=str(b), fill=col,
                                    font=("Consolas", 16, "bold"))
            self.btn_zones[f"bit_{i}"] = (bx, by, bx + 38, by + 40)

    def _draw_mod_btn(self, x, y, w, h, text, color, active):
        if active:
            for i in range(4, 0, -1):
                round_rect(self.canvas, x - i, y - i,
                           x + w + i, y + h + i, 10 + i,
                           outline=lerp(color, BG_DEEP, i / 5), width=1)
            round_rect(self.canvas, x, y, x + w, y + h, 10,
                       fill=lerp(color, BG_DEEP, 0.5),
                       outline=color, width=3)
            self.canvas.create_text(x + w / 2, y + h / 2,
                                    text=text, fill=color,
                                    font=("Consolas", 16, "bold"))
        else:
            round_rect(self.canvas, x, y, x + w, y + h, 10,
                       fill="#0f141c",
                       outline="#2a3040", width=1)
            self.canvas.create_text(x + w / 2, y + h / 2,
                                    text=text, fill=TEXT_DIM,
                                    font=("Consolas", 16, "bold"))
        self.btn_zones[f"mod_{text}"] = (x, y, x + w, y + h)

    def _draw_btn(self, x, y, w, h, text, color, key, active=False):
        if active:
            for i in range(3, 0, -1):
                round_rect(self.canvas, x - i, y - i,
                           x + w + i, y + h + i, 10 + i,
                           outline=lerp(color, BG_DEEP, i / 4), width=1)
            round_rect(self.canvas, x, y, x + w, y + h, 10,
                       fill=lerp(color, BG_DEEP, 0.6),
                       outline=color, width=2)
            self.canvas.create_text(x + w / 2, y + h / 2,
                                    text=text, fill=color,
                                    font=("Segoe UI", 10, "bold"))
        else:
            round_rect(self.canvas, x, y, x + w, y + h, 10,
                       fill="#0f141c",
                       outline="#2a3040", width=1)
            self.canvas.create_text(x + w / 2, y + h / 2,
                                    text=text, fill=TEXT_DIM,
                                    font=("Segoe UI", 10, "bold"))
        self.btn_zones[key] = (x, y, x + w, y + h)

    # ---------- ПЕРЕРИСОВКА ----------
    def _redraw_all(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = self.W, self.H
        self.W, self.H = w, h

        # пересчёт t_max при изменении длительности бита
        self.state.t_max = len(self.state.bits) * self.state.bit_duration

        self.btn_zones = {}
        self.slider_zones = {}

        self._draw_bg(w, h)
        self._draw_header(w)

        graph_y = 90
        graph_h = h - 120
        self._draw_graph(w, graph_y, graph_h)
        self._draw_panel(w, graph_y, graph_h)

    # ---------- СОБЫТИЯ ----------
    def _on_click(self, event):
        x, y = event.x, event.y

        # ползунки
        for key, (x0, y0, x1, y1, vmin, vmax) in self.slider_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                self.drag_slider = key
                self._set_slider_from_mouse(key, x)
                return

        # кнопки
        for key, (x0, y0, x1, y1) in self.btn_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                self._do_action(key)
                return

    def _on_drag(self, event):
        if self.drag_slider:
            self._set_slider_from_mouse(self.drag_slider, event.x)

    def _on_release(self, event):
        self.drag_slider = None

    def _set_slider_from_mouse(self, key, mouse_x):
        if key not in self.slider_zones:
            return
        x0, y0, x1, y1, vmin, vmax = self.slider_zones[key]
        bar_x0 = x0 + 10
        bar_x1 = x1 - 10
        if bar_x1 <= bar_x0:
            return
        k = (mouse_x - bar_x0) / (bar_x1 - bar_x0)
        k = max(0.0, min(1.0, k))
        val = vmin + k * (vmax - vmin)

        if key == "carrier_freq":   self.state.carrier_freq = val
        elif key == "f_0":          self.state.f_0 = val
        elif key == "f_1":          self.state.f_1 = val
        elif key == "bit_duration": self.state.bit_duration = val
        elif key == "amplitude":    self.state.amplitude = val

    def _do_action(self, key):
        if key == "pause":
            self.state.paused = not self.state.paused
        elif key == "reset":
            self.state.reset()
        elif key == "random":
            self.state.randomize()
        elif key.startswith("mod_"):
            mod = key[4:]
            self.state.modulation = mod
            # пересчёт t_max
            self.state.t_max = len(self.state.bits) * self.state.bit_duration
            self.state.anim_time = 0.0
        elif key.startswith("bit_"):
            idx = int(key[4:])
            if 0 <= idx < len(self.state.bits):
                self.state.bits[idx] = 1 - self.state.bits[idx]

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