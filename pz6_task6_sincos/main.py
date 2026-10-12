"""
ОКФРС. Практика 6. Задание 6.
Графики sin и cos — чистые, с опциональной панелью параметров.
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
BG_GRAPH   = "#050810"
BG_PANEL   = "#0f141c"
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
# СОСТОЯНИЕ
# ============================================================
class AppState:
    def __init__(self):
        self.sin_amp = 1.0
        self.sin_freq = 1.0
        self.sin_phase = 0.0

        self.cos_amp = 1.0
        self.cos_freq = 1.0
        self.cos_phase = 0.0

        self.x_min = -2 * math.pi
        self.x_max = 2 * math.pi

        self.show_sin = True
        self.show_cos = True
        self.show_grid = True
        self.show_params = False   # панель параметров скрыта
        self.paused = False        # анимация вкл/выкл

        self.anim_t = 0.0          # фаза «дыхания» кривой
        self.t = 0.0

    def tick(self, dt):
        self.t += dt
        if not self.paused:
            self.anim_t += dt

    def reset(self):
        self.sin_amp = 1.0
        self.sin_freq = 1.0
        self.sin_phase = 0.0
        self.cos_amp = 1.0
        self.cos_freq = 1.0
        self.cos_phase = 0.0
        self.show_sin = True
        self.show_cos = True
        self.show_grid = True
        self.paused = False
        self.anim_t = 0.0


# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Sin & Cos")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.state = AppState()
        self.btn_zones = {}
        self.slider_zones = {}   # зоны ползунков
        self.drag_slider = None
        self.drag_start_x = 0
        self.drag_start_val = 0

        self.W, self.H = 1500, 950

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
        self.canvas.create_text(100, 40, text="SIN & COS",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(260, 44,
                                text="· ТРИГОНОМЕТРИЧЕСКИЕ ФУНКЦИИ",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 11, "bold"))

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

    # ---------- ГРАФИК ----------
    def _draw_graph(self, w, y, h, panel_open):
        # если панель параметров открыта — график занимает 65% ширины
        if panel_open:
            card_x = 50
            card_w = w * 0.66
        else:
            card_x = 50
            card_w = w - 100

        round_rect(self.canvas, card_x, y, card_x + card_w, y + h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(card_x + 20, y + 25, anchor="w",
                                text="▸ ГРАФИК ФУНКЦИЙ",
                                fill=NEON_CYAN, font=FONT_LABEL)

        # статус паузы
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

        # фон
        round_rect(self.canvas, gx0, gy0, gx1, gy1, 4,
                   fill=BG_GRAPH, outline="")

        # сетка
        if self.state.show_grid:
            n_vert = 16
            for i in range(n_vert + 1):
                k = i / n_vert
                x = gx0 + (gx1 - gx0) * k
                is_pi = (i % 4 == 0)
                col = "#1a2540" if is_pi else "#0f1420"
                dash = () if is_pi else (2, 3)
                self.canvas.create_line(x, gy0, x, gy1,
                                        fill=col, dash=dash, width=1)

            n_hor = 8
            for i in range(n_hor + 1):
                k = i / n_hor
                y_ = gy0 + (gy1 - gy0) * k
                is_mid = (i == n_hor // 2)
                col = "#2a3040" if is_mid else "#0f1420"
                dash = () if is_mid else (2, 3)
                self.canvas.create_line(gx0, y_, gx1, y_,
                                        fill=col, dash=dash, width=1)

        # оси
        self.canvas.create_line(gx0, mid_y, gx1, mid_y,
                                fill=NEON_AMBER, width=2)
        cx = (gx0 + gx1) / 2
        self.canvas.create_line(cx, gy0, cx, gy1,
                                fill=NEON_AMBER, width=2)

        self.canvas.create_text(gx1 - 15, mid_y - 12, anchor="e",
                                text="x", fill=NEON_AMBER,
                                font=("Consolas", 12, "italic"))
        self.canvas.create_text(cx + 10, gy0 + 12, anchor="w",
                                text="y", fill=NEON_AMBER,
                                font=("Consolas", 12, "italic"))

        # подписи π по X
        x_range = self.state.x_max - self.state.x_min
        pi_labels = [
            (-2 * math.pi, "-2π"),
            (-3 * math.pi / 2, "-3π/2"),
            (-math.pi, "-π"),
            (-math.pi / 2, "-π/2"),
            (0, "0"),
            (math.pi / 2, "π/2"),
            (math.pi, "π"),
            (3 * math.pi / 2, "3π/2"),
            (2 * math.pi, "2π"),
        ]
        for v, label in pi_labels:
            x = gx0 + (v - self.state.x_min) / x_range * (gx1 - gx0)
            if gx0 - 2 <= x <= gx1 + 2:
                self.canvas.create_line(x, mid_y - 4, x, mid_y + 4,
                                        fill=NEON_AMBER, width=2)
                self.canvas.create_text(x, mid_y + 18,
                                        text=label,
                                        fill=NEON_AMBER,
                                        font=("Consolas", 10, "bold"))

        # подписи Y
        y_labels = [(-1.0, "-1"), (-0.5, "-0.5"),
                    (0.5, "0.5"), (1.0, "1")]
        for v, label in y_labels:
            y_ = mid_y - v * half_h
            self.canvas.create_line(cx - 4, y_, cx + 4, y_,
                                    fill=NEON_AMBER, width=2)
            self.canvas.create_text(cx - 10, y_, anchor="e",
                                    text=label,
                                    fill=NEON_AMBER,
                                    font=("Consolas", 10, "bold"))

        # кривые
        n_pts = 800

        if self.state.show_sin:
            pts = []
            for i in range(n_pts):
                t = i / (n_pts - 1)
                x_val = self.state.x_min + t * x_range
                y_val = self.state.sin_amp * math.sin(
                    self.state.sin_freq * x_val + self.state.sin_phase)
                y_val = max(-1.0, min(1.0, y_val))
                px = gx0 + t * (gx1 - gx0)
                py = mid_y - y_val * half_h
                pts.extend([px, py])
            self.canvas.create_line(*pts,
                                    fill=lerp(NEON_GREEN, BG_DEEP, 0.75),
                                    width=6)
            self.canvas.create_line(*pts,
                                    fill=NEON_GREEN, width=2)

        if self.state.show_cos:
            pts = []
            for i in range(n_pts):
                t = i / (n_pts - 1)
                x_val = self.state.x_min + t * x_range
                y_val = self.state.cos_amp * math.cos(
                    self.state.cos_freq * x_val + self.state.cos_phase)
                y_val = max(-1.0, min(1.0, y_val))
                px = gx0 + t * (gx1 - gx0)
                py = mid_y - y_val * half_h
                pts.extend([px, py])
            self.canvas.create_line(*pts,
                                    fill=lerp(NEON_PINK, BG_DEEP, 0.75),
                                    width=6)
            self.canvas.create_line(*pts,
                                    fill=NEON_PINK, width=2)

    # ---------- ПАНЕЛЬ ПАРАМЕТРОВ ----------
    def _draw_params_panel(self, w, y, h):
        """6 ползунков справа."""
        panel_x = w * 0.68
        panel_w = w - panel_x - 40
        panel_h = h

        round_rect(self.canvas, panel_x, y,
                   panel_x + panel_w, y + panel_h, 14,
                   fill=BG_GLASS, outline=lerp(NEON_PURP, BG_DEEP, 0.5),
                   width=2)

        self.canvas.create_text(panel_x + 20, y + 25, anchor="w",
                                text="▸ ПАРАМЕТРЫ",
                                fill=NEON_PURP, font=FONT_LABEL)

        sliders = [
            ("sin · амплитуда",  "sin_amp",   0.1, 2.0, self.state.sin_amp,  NEON_GREEN),
            ("sin · частота",    "sin_freq",  0.1, 4.0, self.state.sin_freq, NEON_GREEN),
            ("sin · фаза",       "sin_phase", 0.0, 2*math.pi, self.state.sin_phase, NEON_GREEN),
            ("cos · амплитуда",  "cos_amp",   0.1, 2.0, self.state.cos_amp,  NEON_PINK),
            ("cos · частота",    "cos_freq",  0.1, 4.0, self.state.cos_freq, NEON_PINK),
            ("cos · фаза",       "cos_phase", 0.0, 2*math.pi, self.state.cos_phase, NEON_PINK),
        ]

        slider_h = 55
        start_y = y + 55
        self.slider_zones = {}

        for i, (label, key, vmin, vmax, val, color) in enumerate(sliders):
            sy = start_y + i * slider_h

            self.canvas.create_text(panel_x + 20, sy, anchor="w",
                                    text=label,
                                    fill=TEXT_DIM, font=FONT_LABEL_S)

            # значение
            if key.endswith("phase"):
                val_text = f"{val:.2f} рад"
            else:
                val_text = f"{val:.2f}"
            self.canvas.create_text(panel_x + panel_w - 20, sy, anchor="e",
                                    text=val_text,
                                    fill=color, font=FONT_MONO_S)

            # полоса
            bar_x0 = panel_x + 20
            bar_x1 = panel_x + panel_w - 20
            bar_y = sy + 22
            bar_h = 8

            round_rect(self.canvas, bar_x0, bar_y - bar_h/2,
                       bar_x1, bar_y + bar_h/2, 4,
                       fill="#0f141c", outline="")

            # заполнение
            k = (val - vmin) / (vmax - vmin) if vmax > vmin else 0
            k = max(0.0, min(1.0, k))
            if k > 0.005:
                round_rect(self.canvas, bar_x0, bar_y - bar_h/2,
                           bar_x0 + (bar_x1 - bar_x0) * k, bar_y + bar_h/2,
                           4, fill=color, outline="")

            # бегунок
            cx_ = bar_x0 + (bar_x1 - bar_x0) * k
            self.canvas.create_oval(cx_ - 8, bar_y - 8,
                                    cx_ + 8, bar_y + 8,
                                    fill="#ffffff", outline=color, width=2)

            # зона для клика/drag
            self.slider_zones[key] = (bar_x0 - 10, bar_y - 14,
                                       bar_x1 + 10, bar_y + 14,
                                       vmin, vmax)

    # ---------- ЛЕГЕНДА ----------
    def _draw_legend(self, w, y, panel_open):
        if panel_open:
            card_w = w * 0.66
        else:
            card_w = w - 100

        card_h = 60
        round_rect(self.canvas, 50, y, 50 + card_w, y + card_h, 12,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_line(80, y + 30, 130, y + 30,
                                fill=NEON_GREEN, width=3)
        self.canvas.create_text(140, y + 30, anchor="w",
                                text="sin(x)", fill=NEON_GREEN,
                                font=("Consolas", 13, "bold"))

        self.canvas.create_line(240, y + 30, 290, y + 30,
                                fill=NEON_PINK, width=3)
        self.canvas.create_text(300, y + 30, anchor="w",
                                text="cos(x)", fill=NEON_PINK,
                                font=("Consolas", 13, "bold"))

        self.canvas.create_text(50 + card_w / 2, y + 30,
                                text="sin²(x) + cos²(x) = 1",
                                fill=NEON_CYAN,
                                font=("Consolas", 12, "italic"))

    # ---------- КНОПКИ ----------
    def _draw_buttons(self, w, y, panel_open):
        if panel_open:
            card_w = w * 0.66
        else:
            card_w = w - 100

        btn_w = 165
        btn_h = 44
        gap = 12
        total = 6 * btn_w + 5 * gap
        start_x = 50 + (card_w - total) / 2

        self._draw_btn(start_x, y, btn_w, btn_h,
                       "∿ sin", NEON_GREEN, "toggle_sin",
                       active=self.state.show_sin)
        self._draw_btn(start_x + btn_w + gap, y, btn_w, btn_h,
                       "∿ cos", NEON_PINK, "toggle_cos",
                       active=self.state.show_cos)
        self._draw_btn(start_x + 2 * (btn_w + gap), y, btn_w, btn_h,
                       "# сетка", NEON_CYAN, "toggle_grid",
                       active=self.state.show_grid)
        self._draw_btn(start_x + 3 * (btn_w + gap), y, btn_w, btn_h,
                       "⏸ пауза", NEON_AMBER, "pause",
                       active=self.state.paused)
        self._draw_btn(start_x + 4 * (btn_w + gap), y, btn_w, btn_h,
                       "↺ сброс", NEON_RED, "reset",
                       active=False)
        self._draw_btn(start_x + 5 * (btn_w + gap), y, btn_w, btn_h,
                       "⚙ параметры", NEON_PURP, "toggle_params",
                       active=self.state.show_params)

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
                                    font=("Segoe UI", 11, "bold"))
        else:
            round_rect(self.canvas, x, y, x + w, y + h, 10,
                       fill="#0f141c",
                       outline="#2a3040", width=1)
            self.canvas.create_text(x + w / 2, y + h / 2,
                                    text=text, fill=TEXT_DIM,
                                    font=("Segoe UI", 11, "bold"))
        self.btn_zones[key] = (x, y, x + w, y + h)

    # ---------- ИНФО ----------
    def _draw_info(self, w, y, panel_open):
        if panel_open:
            card_w = w * 0.66
        else:
            card_w = w - 100

        card_h = 60
        round_rect(self.canvas, 50, y, 50 + card_w, y + card_h, 12,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(80, y + 20, anchor="w",
                                text="sin:",
                                fill=NEON_GREEN, font=FONT_LABEL)
        self.canvas.create_text(130, y + 20, anchor="w",
                                text=f"A={self.state.sin_amp:.2f}  f={self.state.sin_freq:.2f}  φ={self.state.sin_phase:.2f}",
                                fill=TEXT_MAIN, font=FONT_MONO_S)

        self.canvas.create_text(80, y + 42, anchor="w",
                                text="cos:",
                                fill=NEON_PINK, font=FONT_LABEL)
        self.canvas.create_text(130, y + 42, anchor="w",
                                text=f"A={self.state.cos_amp:.2f}  f={self.state.cos_freq:.2f}  φ={self.state.cos_phase:.2f}",
                                fill=TEXT_MAIN, font=FONT_MONO_S)

        # статус
        status = "⏸ ПАУЗА" if self.state.paused else "▶ ИДЁТ"
        scol = NEON_AMBER if self.state.paused else NEON_GREEN
        self.canvas.create_text(50 + card_w - 30, y + card_h / 2,
                                text=status, fill=scol,
                                font=FONT_LABEL)

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

        panel_open = self.state.show_params

        self._draw_bg(w, h)
        self._draw_header(w)

        # график занимает верх
        graph_y = 90
        graph_h = h - 380
        self._draw_graph(w, graph_y, graph_h, panel_open)

        # легенда
        self._draw_legend(w, graph_y + graph_h + 10, panel_open)

        # кнопки
        self._draw_buttons(w, graph_y + graph_h + 80, panel_open)

        # инфо
        self._draw_info(w, graph_y + graph_h + 140, panel_open)

        # панель параметров
        if panel_open:
            self._draw_params_panel(w, 90, h - 130)

    # ---------- КЛИКИ / ПЕРЕТАСКИВАНИЕ ----------
    def _on_click(self, event):
        x, y = event.x, event.y

        # если открыта панель — проверяем ползунки
        if self.state.show_params:
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

        # записываем в состояние
        if key == "sin_amp":    self.state.sin_amp = val
        elif key == "sin_freq": self.state.sin_freq = val
        elif key == "sin_phase": self.state.sin_phase = val
        elif key == "cos_amp":  self.state.cos_amp = val
        elif key == "cos_freq": self.state.cos_freq = val
        elif key == "cos_phase": self.state.cos_phase = val

    def _do_action(self, key):
        if key == "toggle_sin":
            self.state.show_sin = not self.state.show_sin
        elif key == "toggle_cos":
            self.state.show_cos = not self.state.show_cos
        elif key == "toggle_grid":
            self.state.show_grid = not self.state.show_grid
        elif key == "pause":
            self.state.paused = not self.state.paused
        elif key == "reset":
            self.state.reset()
        elif key == "toggle_params":
            self.state.show_params = not self.state.show_params

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