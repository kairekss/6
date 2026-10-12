"""
ОКФРС. Практика 6. Задание 9.
Амплитудная модуляция (AM):
несущая + модулирующая → AM-сигнал.
Управление: несущая частота, амплитуда, глубина модуляции.
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
# СОСТОЯНИЕ
# ============================================================
class AppState:
    def __init__(self):
        # AM: s(t) = A_c · [1 + m · cos(2π·f_m·t)] · cos(2π·f_c·t)
        self.carrier_freq = 8.0        # f_c — несущая, Гц
        self.carrier_amp = 1.0         # A_c — амплитуда несущей
        self.mod_freq = 1.0            # f_m — модулирующая, Гц
        self.mod_depth = 0.5           # m — глубина модуляции 0..1

        self.t_max = 2.0

        self.paused = False
        self.anim_time = 0.0

        # показ
        self.show_carrier = True
        self.show_modulating = True
        self.show_envelope = True
        self.show_am = True

    def tick(self, dt):
        if not self.paused:
            self.anim_time += dt
            if self.anim_time > self.t_max:
                self.anim_time = 0.0

    def reset(self):
        self.carrier_freq = 8.0
        self.carrier_amp = 1.0
        self.mod_freq = 1.0
        self.mod_depth = 0.5
        self.paused = False
        self.anim_time = 0.0

    def randomize(self):
        self.carrier_freq = random.uniform(4.0, 20.0)
        self.carrier_amp = random.uniform(0.5, 1.5)
        self.mod_freq = random.uniform(0.5, 3.0)
        self.mod_depth = random.uniform(0.2, 1.0)

    # --- формулы ---
    def carrier(self, t):
        return self.carrier_amp * math.cos(2 * math.pi * self.carrier_freq * t)

    def modulating(self, t):
        return math.cos(2 * math.pi * self.mod_freq * t)

    def am_signal(self, t):
        """AM-сигнал: A_c · [1 + m·cos]·cos."""
        return (self.carrier_amp
                * (1 + self.mod_depth * math.cos(2 * math.pi * self.mod_freq * t))
                * math.cos(2 * math.pi * self.carrier_freq * t))

    def envelope_top(self, t):
        return self.carrier_amp * (1 + self.mod_depth * math.cos(2 * math.pi * self.mod_freq * t))

    def envelope_bottom(self, t):
        return -self.envelope_top(t)


# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Amplitude Modulation · Амплитудная модуляция")
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
        self.canvas.create_text(100, 40, text="AM MODULATION",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(340, 44,
                                text="· АМПЛИТУДНАЯ МОДУЛЯЦИЯ",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 11, "bold"))

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

    # ---------- ГРАФИК ----------
    def _draw_graph(self, w, y, h):
        """Один большой график со всеми кривыми."""
        panel_w = 420
        card_x = 50
        card_w = w - 100 - panel_w - 20

        round_rect(self.canvas, card_x, y, card_x + card_w, y + h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(card_x + 20, y + 25, anchor="w",
                                text="▸ s(t) = A_c · [1 + m · cos(2π·f_m·t)] · cos(2π·f_c·t)",
                                fill=NEON_CYAN, font=FONT_LABEL)

        if self.state.paused:
            self.canvas.create_text(card_x + card_w - 20, y + 25, anchor="e",
                                    text="⏸ ПАУЗА",
                                    fill=NEON_AMBER, font=FONT_LABEL)

        # область графика
        gx0 = card_x + 70
        gx1 = card_x + card_w - 40
        gy0 = y + 55
        gy1 = y + h - 70

        mid_y = (gy0 + gy1) / 2
        half_h = (gy1 - gy0) / 2

        round_rect(self.canvas, gx0, gy0, gx1, gy1, 4,
                   fill=BG_GRAPH, outline="")

        # сетка
        n_vert = 20
        for i in range(n_vert + 1):
            k = i / n_vert
            xx = gx0 + (gx1 - gx0) * k
            is_sec = (i % 5 == 0)
            col = "#1a2540" if is_sec else "#0f1420"
            dash = () if is_sec else (2, 3)
            self.canvas.create_line(xx, gy0, xx, gy1,
                                    fill=col, dash=dash, width=1)

        n_hor = 8
        for i in range(n_hor + 1):
            k = i / n_hor
            yy = gy0 + (gy1 - gy0) * k
            is_mid = (i == n_hor // 2)
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

        # подписи времени
        for i in range(0, 5):
            t_label = i * (self.state.t_max / 4)
            xx = gx0 + (t_label / self.state.t_max) * (gx1 - gx0)
            self.canvas.create_line(xx, mid_y - 4, xx, mid_y + 4,
                                    fill=NEON_AMBER, width=2)
            self.canvas.create_text(xx, mid_y + 18,
                                    text=f"{t_label:.2f}",
                                    fill=NEON_AMBER,
                                    font=("Consolas", 9, "bold"))

        # подписи Y (от -2 до +2 условно)
        y_max = 2.0
        for v in [-y_max, -y_max/2, y_max/2, y_max]:
            y_ = mid_y - (v / y_max) * half_h * 0.9
            self.canvas.create_line(gx0 - 4, y_, gx0 + 4, y_,
                                    fill=NEON_AMBER, width=2)
            self.canvas.create_text(gx0 - 10, y_, anchor="e",
                                    text=f"{v:+.1f}",
                                    fill=NEON_AMBER,
                                    font=("Consolas", 9, "bold"))

        n_pts = 1500

        def to_screen(t, val):
            """Преобразование: значение val в пиксели."""
            x = gx0 + (t / self.state.t_max) * (gx1 - gx0)
            y_ = mid_y - (val / y_max) * half_h * 0.9
            y_ = max(gy0 + 4, min(gy1 - 4, y_))
            return x, y_

        # === ОГИБАЮЩАЯ (пунктир) ===
        if self.state.show_envelope:
            for sign in (+1, -1):
                pts = []
                for j in range(n_pts):
                    t = j / (n_pts - 1) * self.state.t_max
                    env = sign * self.state.envelope_top(t)
                    px, py = to_screen(t, env)
                    pts.extend([px, py])
                self.canvas.create_line(*pts,
                                        fill=lerp(NEON_PINK, BG_DEEP, 0.4),
                                        dash=(4, 4), width=2)

        # === МОДУЛИРУЮЩАЯ ===
        if self.state.show_modulating:
            pts = []
            for j in range(n_pts):
                t = j / (n_pts - 1) * self.state.t_max
                v = self.state.modulating(t) * self.state.carrier_amp
                px, py = to_screen(t, v)
                pts.extend([px, py])
            self.canvas.create_line(*pts,
                                    fill=lerp(NEON_AMBER, BG_DEEP, 0.3),
                                    width=2)

        # === НЕСУЩАЯ ===
        if self.state.show_carrier:
            pts = []
            for j in range(n_pts):
                t = j / (n_pts - 1) * self.state.t_max
                v = self.state.carrier(t)
                px, py = to_screen(t, v)
                pts.extend([px, py])
            self.canvas.create_line(*pts,
                                    fill=lerp(NEON_GREEN, BG_DEEP, 0.4),
                                    width=1)

        # === AM-СИГНАЛ ===
        if self.state.show_am:
            pts = []
            for j in range(n_pts):
                t = j / (n_pts - 1) * self.state.t_max
                v = self.state.am_signal(t)
                px, py = to_screen(t, v)
                pts.extend([px, py])
            # свечение
            self.canvas.create_line(*pts,
                                    fill=lerp(NEON_CYAN, BG_DEEP, 0.75),
                                    width=6)
            self.canvas.create_line(*pts,
                                    fill=NEON_CYAN, width=2)

        # === АНИМАЦИОННЫЙ МАРКЕР ===
        if not self.state.paused:
            t_m = self.state.anim_time
            v = self.state.am_signal(t_m)
            px, py = to_screen(t_m, v)

            for r in range(12, 0, -3):
                col = lerp(NEON_AMBER, BG_DEEP, r / 14)
                self.canvas.create_oval(px - r, py - r,
                                        px + r, py + r,
                                        fill="", outline=col, width=1)
            self.canvas.create_oval(px - 6, py - 6, px + 6, py + 6,
                                    fill=NEON_AMBER, outline="#ffffff", width=2)

    # ---------- ПАНЕЛЬ УПРАВЛЕНИЯ ----------
    def _draw_panel(self, w, y, h):
        panel_w = 420
        panel_x = w - 50 - panel_w

        round_rect(self.canvas, panel_x, y, panel_x + panel_w, y + h, 14,
                   fill=BG_GLASS, outline=lerp(NEON_PURP, BG_DEEP, 0.5),
                   width=2)

        self.canvas.create_text(panel_x + 20, y + 25, anchor="w",
                                text="▸ ПАРАМЕТРЫ МОДУЛЯЦИИ",
                                fill=NEON_PURP, font=FONT_LABEL)

        sliders = [
            ("НЕСУЩАЯ · f_c",  "carrier_freq", 2.0, 25.0,
             self.state.carrier_freq, NEON_GREEN, "Гц"),
            ("НЕСУЩАЯ · A_c",  "carrier_amp",  0.2, 2.0,
             self.state.carrier_amp, NEON_GREEN, "В"),
            ("МОДУЛЯЦИЯ · f_m", "mod_freq",    0.2, 5.0,
             self.state.mod_freq, NEON_AMBER, "Гц"),
            ("ГЛУБИНА · m",     "mod_depth",   0.0, 1.0,
             self.state.mod_depth, NEON_PINK, "0..1"),
        ]

        slider_h = 90
        start_y = y + 65
        self.slider_zones = {}

        for i, (label, key, vmin, vmax, val, color, unit) in enumerate(sliders):
            sy = start_y + i * slider_h

            self.canvas.create_text(panel_x + 20, sy, anchor="w",
                                    text=label,
                                    fill=TEXT_DIM, font=FONT_LABEL)

            if key == "mod_depth":
                val_text = f"{val:.3f}"
            else:
                val_text = f"{val:.2f} {unit}"
            self.canvas.create_text(panel_x + panel_w - 20, sy, anchor="e",
                                    text=val_text,
                                    fill=color, font=FONT_MONO_S)

            # полоса
            bar_x0 = panel_x + 20
            bar_x1 = panel_x + panel_w - 20
            bar_y = sy + 30
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

            # деления
            for j in range(5):
                kk = j / 4
                xx = bar_x0 + (bar_x1 - bar_x0) * kk
                self.canvas.create_line(xx, bar_y + 14, xx, bar_y + 18,
                                        fill=TEXT_DIM, width=1)

            self.canvas.create_text(panel_x + panel_w / 2, bar_y + 30,
                                    text=unit, fill=TEXT_DIM,
                                    font=("Consolas", 9, "italic"))

            self.slider_zones[key] = (bar_x0 - 10, bar_y - 14,
                                       bar_x1 + 10, bar_y + 14,
                                       vmin, vmax)

        # === информационный блок ===
        info_y = start_y + 4 * slider_h + 10

        round_rect(self.canvas, panel_x + 20, info_y,
                   panel_x + panel_w - 20, info_y + 115, 10,
                   fill=BG_PANEL, outline=NEON_CYAN, width=1)

        self.canvas.create_text(panel_x + panel_w / 2, info_y + 20,
                                text="s(t) = A_c · [1 + m·cos(2π·f_m·t)]·cos(2π·f_c·t)",
                                fill=NEON_CYAN,
                                font=("Consolas", 10, "bold"))

        # коэффициенты
        self.canvas.create_text(panel_x + 35, info_y + 50, anchor="w",
                                text=f"f_c = {self.state.carrier_freq:.2f} Гц",
                                fill=NEON_GREEN, font=FONT_MONO_S)
        self.canvas.create_text(panel_x + 35, info_y + 72, anchor="w",
                                text=f"A_c = {self.state.carrier_amp:.2f}",
                                fill=NEON_GREEN, font=FONT_MONO_S)
        self.canvas.create_text(panel_x + 35, info_y + 94, anchor="w",
                                text=f"f_m = {self.state.mod_freq:.2f} Гц",
                                fill=NEON_AMBER, font=FONT_MONO_S)

        self.canvas.create_text(panel_x + panel_w - 35, info_y + 50, anchor="e",
                                text=f"m = {self.state.mod_depth:.3f}",
                                fill=NEON_PINK, font=FONT_MONO_S)
        # коэф. модуляции в процентах
        self.canvas.create_text(panel_x + panel_w - 35, info_y + 72, anchor="e",
                                text=f"{self.state.mod_depth*100:.0f} %",
                                fill=NEON_PINK, font=FONT_MONO_S)
        # ширина полосы
        bw = 2 * self.state.mod_freq
        self.canvas.create_text(panel_x + panel_w - 35, info_y + 94, anchor="e",
                                text=f"BW = {bw:.2f} Гц",
                                fill=NEON_CYAN, font=FONT_MONO_S)

        # === кнопки ===
        btn_y = info_y + 125
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

        self._draw_btn(panel_x + 15, btn_y + b_h + b_gap, b_w, b_h,
                       "∿ НЕСУЩАЯ", NEON_GREEN, "toggle_carrier",
                       active=self.state.show_carrier)
        self._draw_btn(panel_x + 15 + b_w + b_gap, btn_y + b_h + b_gap,
                       b_w, b_h,
                       "∿ МОДУЛ.", NEON_AMBER, "toggle_modulating",
                       active=self.state.show_modulating)
        self._draw_btn(panel_x + 15 + 2 * (b_w + b_gap),
                       btn_y + b_h + b_gap, b_w, b_h,
                       "⌐ ОГИБАЮЩАЯ", NEON_PINK, "toggle_envelope",
                       active=self.state.show_envelope)

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
        elif key == "carrier_amp":  self.state.carrier_amp = val
        elif key == "mod_freq":     self.state.mod_freq = val
        elif key == "mod_depth":    self.state.mod_depth = val

    def _do_action(self, key):
        if key == "pause":
            self.state.paused = not self.state.paused
        elif key == "reset":
            self.state.reset()
        elif key == "random":
            self.state.randomize()
        elif key == "toggle_carrier":
            self.state.show_carrier = not self.state.show_carrier
        elif key == "toggle_modulating":
            self.state.show_modulating = not self.state.show_modulating
        elif key == "toggle_envelope":
            self.state.show_envelope = not self.state.show_envelope

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