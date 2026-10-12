"""
ОКФРС. Практика 6. Задание 8.
Сложение 5 гармонических колебаний синусоидальной формы.
Задаём амплитуду и частоту каждой, строим графики и результат.
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
NEON_ORANGE= "#ff8c42"

TEXT_MAIN  = "#e8f0ff"
TEXT_DIM   = "#5a6780"
TEXT_GLOW  = "#8fa4c4"

# ШРИФТЫ
FONT_MONO  = ("Consolas", 13, "bold")
FONT_MONO_S= ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_LABEL_S = ("Segoe UI", 9)

# 5 цветов для 5 гармоник
H_COLORS = [NEON_CYAN, NEON_GREEN, NEON_PINK, NEON_PURP, NEON_AMBER]


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
        self.harmonics = [
            {"amp": 1.0, "freq": 1.0},
            {"amp": 0.5, "freq": 2.0},
            {"amp": 0.3, "freq": 3.0},
            {"amp": 0.2, "freq": 5.0},
            {"amp": 0.1, "freq": 7.0},
        ]
        self.t_max = 4.0
        self.paused = False
        self.anim_time = 0.0

        self.show_individual = True
        self.show_sum = True

        self.active_h = 0

    def tick(self, dt):
        if not self.paused:
            self.anim_time += dt
            if self.anim_time > self.t_max:
                self.anim_time = 0.0

    def reset(self):
        self.harmonics = [
            {"amp": 1.0, "freq": 1.0},
            {"amp": 0.5, "freq": 2.0},
            {"amp": 0.3, "freq": 3.0},
            {"amp": 0.2, "freq": 5.0},
            {"amp": 0.1, "freq": 7.0},
        ]
        self.paused = False
        self.anim_time = 0.0
        self.active_h = 0

    def randomize(self):
        for h in self.harmonics:
            h["amp"] = random.uniform(0.1, 1.0)
            h["freq"] = random.uniform(0.5, 8.0)

    def value_at(self, idx, t):
        h = self.harmonics[idx]
        return h["amp"] * math.sin(2 * math.pi * h["freq"] * t)

    def sum_at(self, t):
        return sum(self.value_at(i, t) for i in range(5))

    def total_amplitude(self):
        s = sum(h["amp"] for h in self.harmonics)
        return max(0.5, s)


# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Harmonic Sum · Сложение 5 гармоник")
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
        self.canvas.create_text(60, 40, text="∑",
                                fill=NEON_CYAN,
                                font=("Segoe UI", 30, "bold"))
        self.canvas.create_text(100, 40, text="HARMONIC SUM",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(320, 44,
                                text="· СЛОЖЕНИЕ 5 ГАРМОНИК",
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

        self.canvas.create_text(card_x + 20, y + 25, anchor="w",
                                text="▸ x(t) = Σ Aᵢ · sin(2π · fᵢ · t)",
                                fill=NEON_CYAN, font=FONT_LABEL)

        if self.state.paused:
            self.canvas.create_text(card_x + card_w - 20, y + 25, anchor="e",
                                    text="⏸ ПАУЗА",
                                    fill=NEON_AMBER, font=FONT_LABEL)

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

        n_hor = 10
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
                                text="x", fill=NEON_AMBER,
                                font=("Consolas", 11, "italic"))

        # подписи времени
        for i in range(0, 5):
            t_label = i * 1.0
            xx = gx0 + (t_label / self.state.t_max) * (gx1 - gx0)
            self.canvas.create_line(xx, mid_y - 4, xx, mid_y + 4,
                                    fill=NEON_AMBER, width=2)
            self.canvas.create_text(xx, mid_y + 18,
                                    text=f"{t_label:.1f}",
                                    fill=NEON_AMBER,
                                    font=("Consolas", 10, "bold"))

        # подписи Y
        max_amp = self.state.total_amplitude()
        for v in [-max_amp, 0, max_amp]:
            y_ = mid_y - (v / max_amp) * half_h * 0.85
            self.canvas.create_line(gx0 - 4, y_, gx0 + 4, y_,
                                    fill=NEON_AMBER, width=2)
            self.canvas.create_text(gx0 - 10, y_, anchor="e",
                                    text=f"{v:+.1f}",
                                    fill=NEON_AMBER,
                                    font=("Consolas", 9, "bold"))

        n_pts = 1000
        max_amp = self.state.total_amplitude()

        # отдельные гармоники
        if self.state.show_individual:
            for i in range(5):
                pts = []
                for j in range(n_pts):
                    t = j / (n_pts - 1) * self.state.t_max
                    x_val = self.state.value_at(i, t)
                    y_norm = x_val / max_amp
                    y_norm = max(-1.0, min(1.0, y_norm))
                    px = gx0 + (j / (n_pts - 1)) * (gx1 - gx0)
                    py = mid_y - y_norm * half_h
                    pts.extend([px, py])
                self.canvas.create_line(*pts,
                                        fill=lerp(H_COLORS[i], BG_DEEP, 0.5),
                                        width=1)

        # сумма
        if self.state.show_sum:
            pts = []
            for j in range(n_pts):
                t = j / (n_pts - 1) * self.state.t_max
                x_val = self.state.sum_at(t)
                y_norm = x_val / max_amp
                y_norm = max(-1.0, min(1.0, y_norm))
                px = gx0 + (j / (n_pts - 1)) * (gx1 - gx0)
                py = mid_y - y_norm * half_h
                pts.extend([px, py])
            self.canvas.create_line(*pts,
                                    fill=lerp(NEON_CYAN, BG_DEEP, 0.7),
                                    width=6)
            self.canvas.create_line(*pts,
                                    fill=NEON_CYAN, width=2)

        # анимационный маркер
        if not self.state.paused:
            t_marker = self.state.anim_time
            x_val = self.state.sum_at(t_marker)
            y_norm = x_val / max_amp
            y_norm = max(-1.0, min(1.0, y_norm))
            px = gx0 + (t_marker / self.state.t_max) * (gx1 - gx0)
            py = mid_y - y_norm * half_h

            for r in range(12, 0, -3):
                col = lerp(NEON_AMBER, BG_DEEP, r / 14)
                self.canvas.create_oval(px - r, py - r,
                                        px + r, py + r,
                                        fill="", outline=col, width=1)
            self.canvas.create_oval(px - 7, py - 7, px + 7, py + 7,
                                    fill=NEON_AMBER, outline="#ffffff", width=2)

    # ---------- ПАНЕЛЬ УПРАВЛЕНИЯ ----------
    def _draw_panel(self, w, y, h):
        panel_w = 420
        panel_x = w - 50 - panel_w

        round_rect(self.canvas, panel_x, y, panel_x + panel_w, y + h, 14,
                   fill=BG_GLASS, outline=lerp(NEON_PURP, BG_DEEP, 0.5),
                   width=2)

        self.canvas.create_text(panel_x + 20, y + 22, anchor="w",
                                text="▸ 5 ГАРМОНИК",
                                fill=NEON_PURP, font=FONT_LABEL)
        self.canvas.create_text(panel_x + panel_w - 20, y + 22, anchor="e",
                                text="кликни по номеру ниже",
                                fill=TEXT_DIM, font=("Segoe UI", 8, "italic"))

        h_start_y = y + 45
        h_card_h = 60
        h_gap = 5

        for i in range(5):
            hy = h_start_y + i * (h_card_h + h_gap)
            self._draw_harmonic_card(panel_x + 15, hy, panel_w - 30,
                                      h_card_h, i)

        btn_y = h_start_y + 5 * (h_card_h + h_gap) + 10

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
                       "∿ ОТДЕЛЬНЫЕ", NEON_BLUE, "toggle_ind",
                       active=self.state.show_individual)
        self._draw_btn(panel_x + 15 + b_w + b_gap, btn_y + b_h + b_gap,
                       b_w, b_h,
                       "∑ СУММА", NEON_CYAN, "toggle_sum",
                       active=self.state.show_sum)
        self._draw_btn(panel_x + 15 + 2 * (b_w + b_gap),
                       btn_y + b_h + b_gap, b_w, b_h,
                       "📋 СТАТИСТИКА", NEON_GREEN, "stats")

    def _draw_harmonic_card(self, x, y, w, h, idx):
        h_data = self.state.harmonics[idx]
        col = H_COLORS[idx]
        is_active = (self.state.active_h == idx)

        outline_col = col if is_active else "#2a3040"
        outline_w = 2 if is_active else 1
        round_rect(self.canvas, x, y, x + w, y + h, 8,
                   fill=lerp(col, BG_DEEP, 0.9),
                   outline=outline_col, width=outline_w)

        if is_active:
            self.canvas.create_text(x + 12, y + h / 2,
                                    text="▶", fill=col,
                                    font=("Consolas", 12, "bold"))

        self.canvas.create_text(x + 30, y + 18, anchor="w",
                                text=f"#{idx+1}",
                                fill=col, font=("Consolas", 11, "bold"))

        self.canvas.create_text(x + 65, y + 18, anchor="w",
                                text=f"A = {h_data['amp']:.2f}",
                                fill=TEXT_MAIN, font=("Consolas", 10))

        self.canvas.create_text(x + w - 15, y + 18, anchor="e",
                                text=f"f = {h_data['freq']:.2f} Гц",
                                fill=TEXT_MAIN, font=("Consolas", 10))

        # ползунок амплитуды
        bar_x0 = x + 30
        bar_x1 = x + w / 2 - 10
        bar_y = y + 40
        bar_h = 6

        round_rect(self.canvas, bar_x0, bar_y - bar_h/2,
                   bar_x1, bar_y + bar_h/2, 3,
                   fill="#0f141c", outline="")

        k_a = h_data['amp'] / 1.0
        k_a = max(0.0, min(1.0, k_a))
        if k_a > 0.005:
            round_rect(self.canvas, bar_x0, bar_y - bar_h/2,
                       bar_x0 + (bar_x1 - bar_x0) * k_a, bar_y + bar_h/2,
                       3, fill=col, outline="")
        cx_ = bar_x0 + (bar_x1 - bar_x0) * k_a
        self.canvas.create_oval(cx_ - 6, bar_y - 6, cx_ + 6, bar_y + 6,
                                fill="#ffffff", outline=col, width=1)

        self.canvas.create_text(x + 30, y + 55, anchor="w",
                                text="amp",
                                fill=TEXT_DIM, font=("Consolas", 8))

        self.slider_zones[f"h{idx}_amp"] = (bar_x0 - 10, bar_y - 12,
                                              bar_x1 + 10, bar_y + 12,
                                              0.0, 1.0)

        # ползунок частоты
        bar_x0 = x + w / 2 + 10
        bar_x1 = x + w - 20
        bar_y = y + 40

        round_rect(self.canvas, bar_x0, bar_y - bar_h/2,
                   bar_x1, bar_y + bar_h/2, 3,
                   fill="#0f141c", outline="")

        k_f = (h_data['freq'] - 0.1) / (10.0 - 0.1)
        k_f = max(0.0, min(1.0, k_f))
        if k_f > 0.005:
            round_rect(self.canvas, bar_x0, bar_y - bar_h/2,
                       bar_x0 + (bar_x1 - bar_x0) * k_f, bar_y + bar_h/2,
                       3, fill=col, outline="")
        cx_ = bar_x0 + (bar_x1 - bar_x0) * k_f
        self.canvas.create_oval(cx_ - 6, bar_y - 6, cx_ + 6, bar_y + 6,
                                fill="#ffffff", outline=col, width=1)

        self.canvas.create_text(x + w / 2 + 10, y + 55, anchor="w",
                                text="freq (0.1..10 Гц)",
                                fill=TEXT_DIM, font=("Consolas", 8))

        self.slider_zones[f"h{idx}_freq"] = (bar_x0 - 10, bar_y - 12,
                                               bar_x1 + 10, bar_y + 12,
                                               0.1, 10.0)

        # зона для активации (клик по номеру)
        self.btn_zones[f"act_h{idx}"] = (x + 20, y, x + 80, y + 30)

    # ---------- КНОПКИ ----------
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

        # сначала — активация гармоник
        for key, (x0, y0, x1, y1) in self.btn_zones.items():
            if key.startswith("act_h"):
                if x0 <= x <= x1 and y0 <= y <= y1:
                    idx = int(key[5:])
                    self.state.active_h = idx
                    return

        # ползунки
        for key, (x0, y0, x1, y1, vmin, vmax) in self.slider_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                self.drag_slider = key
                if key.startswith("h") and "_" in key:
                    try:
                        idx = int(key[1:key.index("_")])
                        self.state.active_h = idx
                    except Exception:
                        pass
                self._set_slider_from_mouse(key, x)
                return

        # обычные кнопки
        for key, (x0, y0, x1, y1) in self.btn_zones.items():
            if key.startswith("act_h"):
                continue
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

        if key.startswith("h") and "_" in key:
            idx = int(key[1:key.index("_")])
            kind = key[key.index("_")+1:]
            if kind == "amp":
                self.state.harmonics[idx]["amp"] = val
            elif kind == "freq":
                self.state.harmonics[idx]["freq"] = val

    def _do_action(self, key):
        if key == "pause":
            self.state.paused = not self.state.paused
        elif key == "reset":
            self.state.reset()
        elif key == "random":
            self.state.randomize()
        elif key == "toggle_ind":
            self.state.show_individual = not self.state.show_individual
        elif key == "toggle_sum":
            self.state.show_sum = not self.state.show_sum
        elif key == "stats":
            self._show_stats()

    def _show_stats(self):
        from tkinter import messagebox

        lines = []
        lines.append("СЛОЖЕНИЕ 5 ГАРМОНИК")
        lines.append("=" * 40)
        total_amp = 0
        for i, h in enumerate(self.state.harmonics):
            total_amp += h["amp"]
            lines.append(f"#{i+1}  A = {h['amp']:.3f}  f = {h['freq']:.3f} Гц  "
                         f"T = {1/h['freq']:.3f} с")

        lines.append("=" * 40)
        lines.append(f"Максимальная сумма амплитуд: {total_amp:.3f}")
        lines.append(f"Время наблюдения: 0.0 .. {self.state.t_max:.1f} с")
        lines.append(f"Точек графика: 1000")

        max_sum = 0.0
        min_sum = 0.0
        for j in range(1000):
            t = j / 999 * self.state.t_max
            v = self.state.sum_at(t)
            max_sum = max(max_sum, v)
            min_sum = min(min_sum, v)
        lines.append("")
        lines.append(f"Максимум суммы:  {max_sum:+.3f}")
        lines.append(f"Минимум суммы:   {min_sum:+.3f}")
        lines.append(f"Размах:          {max_sum - min_sum:.3f}")

        messagebox.showinfo("Статистика", "\n".join(lines))

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