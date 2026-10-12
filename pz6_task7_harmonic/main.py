"""
ОКФРС. Практика 6. Задание 7.
Гармонические колебания с управлением амплитуды и частоты.
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
        # параметры гармоники: x(t) = A·sin(2π·f·t + φ)
        self.amplitude = 1.0        # A: 0.1 .. 3.0
        self.frequency = 1.0        # f: 0.1 .. 5.0 Гц
        self.phase = 0.0            # φ: 0 .. 2π
        self.damping = 0.0          # затухание 0 .. 0.5 (доп. фишка)

        # диапазон по X (время) — 4 секунды
        self.t_max = 4.0

        # анимация
        self.paused = False
        self.anim_time = 0.0        # текущее время анимации (для маркера)
        self.real_t = 0.0

        # показ
        self.show_envelope = True

    def tick(self, dt):
        self.real_t += dt
        if not self.paused:
            self.anim_time += dt
            if self.anim_time > self.t_max:
                self.anim_time = 0.0

    def reset(self):
        self.amplitude = 1.0
        self.frequency = 1.0
        self.phase = 0.0
        self.damping = 0.0
        self.paused = False
        self.anim_time = 0.0

    def value_at(self, t):
        """Значение гармоники в момент времени t."""
        env = math.exp(-self.damping * t) if self.damping > 0 else 1.0
        return self.amplitude * env * math.sin(
            2 * math.pi * self.frequency * t + self.phase)


# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Harmonic Oscillation · Гармонические колебания")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.state = AppState()
        self.btn_zones = {}
        self.slider_zones = {}
        self.drag_slider = None

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
        self.canvas.create_text(100, 40, text="HARMONIC",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(280, 44,
                                text="· ГАРМОНИЧЕСКИЕ КОЛЕБАНИЯ",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 11, "bold"))

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

    # ---------- ГРАФИК ----------
    def _draw_graph(self, w, y, h):
        """График x(t) = A·sin(2π·f·t + φ)."""
        panel_w = 380
        card_x = 50
        card_w = w - 100 - panel_w - 20

        round_rect(self.canvas, card_x, y, card_x + card_w, y + h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(card_x + 20, y + 25, anchor="w",
                                text="▸ x(t) = A · sin(2π · f · t + φ)",
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

        # подписи Y — реальные значения амплитуды
        amp = self.state.amplitude
        for v in [-amp, -amp/2, amp/2, amp]:
            y_ = mid_y - (v / amp) * half_h * 0.85 if amp > 0 else mid_y
            self.canvas.create_line(gx0 - 4, y_, gx0 + 4, y_,
                                    fill=NEON_AMBER, width=2)
            self.canvas.create_text(gx0 - 10, y_, anchor="e",
                                    text=f"{v:+.2f}",
                                    fill=NEON_AMBER,
                                    font=("Consolas", 9, "bold"))

        # === кривая ===
        n_pts = 1000
        pts = []
        for i in range(n_pts):
            t = i / (n_pts - 1) * self.state.t_max
            x_val = self.state.value_at(t)
            # нормируем: полная амплитуда = 3.0 максимум для отображения
            y_norm = x_val / 3.0
            y_norm = max(-1.0, min(1.0, y_norm))
            px = gx0 + (i / (n_pts - 1)) * (gx1 - gx0)
            py = mid_y - y_norm * half_h
            pts.extend([px, py])

        if len(pts) >= 4:
            self.canvas.create_line(*pts,
                                    fill=lerp(NEON_CYAN, BG_DEEP, 0.75),
                                    width=6)
            self.canvas.create_line(*pts,
                                    fill=NEON_CYAN, width=2)

        # === огибающая при затухании ===
        if self.state.damping > 0.01 and self.state.show_envelope:
            # верхняя и нижняя огибающие
            for sign in [+1, -1]:
                pts_env = []
                for i in range(n_pts):
                    t = i / (n_pts - 1) * self.state.t_max
                    env = self.state.amplitude * math.exp(-self.state.damping * t)
                    y_norm = sign * env / 3.0
                    y_norm = max(-1.0, min(1.0, y_norm))
                    px = gx0 + (i / (n_pts - 1)) * (gx1 - gx0)
                    py = mid_y - y_norm * half_h
                    pts_env.extend([px, py])
                self.canvas.create_line(*pts_env,
                                        fill=lerp(NEON_PINK, BG_DEEP, 0.4),
                                        width=1, dash=(4, 4))

        # === анимационный маркер (если не в паузе) ===
        if not self.state.paused:
            t_marker = self.state.anim_time
            x_val = self.state.value_at(t_marker)
            y_norm = x_val / 3.0
            y_norm = max(-1.0, min(1.0, y_norm))
            px = gx0 + (t_marker / self.state.t_max) * (gx1 - gx0)
            py = mid_y - y_norm * half_h

            # ореол маркера
            for r in range(12, 0, -3):
                col = lerp(NEON_AMBER, BG_DEEP, r / 14)
                self.canvas.create_oval(px - r, py - r,
                                        px + r, py + r,
                                        fill="", outline=col, width=1)
            self.canvas.create_oval(px - 7, py - 7, px + 7, py + 7,
                                    fill=NEON_AMBER, outline="#ffffff", width=2)

            # пунктир вниз до оси
            self.canvas.create_line(px, py, px, mid_y,
                                    fill=lerp(NEON_AMBER, BG_DEEP, 0.5),
                                    dash=(3, 3), width=1)
            # значение под маркером
            self.canvas.create_text(px, py - 20,
                                    text=f"{x_val:+.2f}",
                                    fill=NEON_AMBER,
                                    font=("Consolas", 10, "bold"))

    # ---------- ПАНЕЛЬ УПРАВЛЕНИЯ ----------
    def _draw_panel(self, w, y, h):
        """Панель с ползунками справа."""
        panel_w = 380
        panel_x = w - 50 - panel_w

        round_rect(self.canvas, panel_x, y, panel_x + panel_w, y + h, 14,
                   fill=BG_GLASS, outline=lerp(NEON_PURP, BG_DEEP, 0.5),
                   width=2)

        self.canvas.create_text(panel_x + 20, y + 25, anchor="w",
                                text="▸ УПРАВЛЕНИЕ",
                                fill=NEON_PURP, font=FONT_LABEL)

        sliders = [
            ("АМПЛИТУДА",  "amplitude",  0.1, 3.0, self.state.amplitude, NEON_CYAN,  "A"),
            ("ЧАСТОТА",    "frequency",  0.1, 5.0, self.state.frequency, NEON_GREEN, "f, Гц"),
            ("ФАЗА",       "phase",      0.0, 2*math.pi, self.state.phase, NEON_AMBER, "φ, рад"),
            ("ЗАТУХАНИЕ",  "damping",    0.0, 0.5, self.state.damping, NEON_PINK,  "d"),
        ]

        slider_h = 90
        start_y = y + 65
        self.slider_zones = {}

        for i, (label, key, vmin, vmax, val, color, unit) in enumerate(sliders):
            sy = start_y + i * slider_h

            self.canvas.create_text(panel_x + 20, sy, anchor="w",
                                    text=label,
                                    fill=TEXT_DIM, font=FONT_LABEL)

            # значение
            if key == "phase":
                val_text = f"{val:.2f} рад"
            elif key == "frequency":
                val_text = f"{val:.2f} Гц"
            elif key == "damping":
                val_text = f"{val:.3f}"
            else:
                val_text = f"{val:.2f}"
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

            # бегунок
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

            # единицы
            self.canvas.create_text(panel_x + panel_w / 2, bar_y + 30,
                                    text=unit, fill=TEXT_DIM,
                                    font=("Consolas", 9, "italic"))

            self.slider_zones[key] = (bar_x0 - 10, bar_y - 14,
                                       bar_x1 + 10, bar_y + 14,
                                       vmin, vmax)

        # === формула и текущее значение ===
        formula_y = start_y + 4 * slider_h + 15

        round_rect(self.canvas, panel_x + 20, formula_y,
                   panel_x + panel_w - 20, formula_y + 100, 10,
                   fill=BG_PANEL, outline=NEON_CYAN, width=1)

        self.canvas.create_text(panel_x + panel_w / 2, formula_y + 25,
                                text="x(t) = A · sin(2π · f · t + φ)",
                                fill=NEON_CYAN,
                                font=("Consolas", 12, "bold"))

        # текущие значения
        self.canvas.create_text(panel_x + 30, formula_y + 55, anchor="w",
                                text=f"A = {self.state.amplitude:.2f}",
                                fill=NEON_CYAN, font=FONT_MONO_S)
        self.canvas.create_text(panel_x + 30, formula_y + 78, anchor="w",
                                text=f"f = {self.state.frequency:.2f} Гц",
                                fill=NEON_GREEN, font=FONT_MONO_S)
        self.canvas.create_text(panel_x + panel_w / 2 + 20, formula_y + 55,
                                anchor="w",
                                text=f"φ = {self.state.phase:.2f}",
                                fill=NEON_AMBER, font=FONT_MONO_S)
        self.canvas.create_text(panel_x + panel_w / 2 + 20, formula_y + 78,
                                anchor="w",
                                text=f"T = {1/self.state.frequency:.3f} с"
                                     if self.state.frequency > 0 else "T = ∞",
                                fill=NEON_PINK, font=FONT_MONO_S)

    # ---------- КНОПКИ ----------
    def _draw_buttons(self, w, y):
        """Кнопки под графиком."""
        panel_w = 380
        card_x = 50
        card_w = w - 100 - panel_w - 20

        btn_w = 160
        btn_h = 44
        gap = 12
        total = 4 * btn_w + 3 * gap
        start_x = card_x + (card_w - total) / 2

        self._draw_btn(start_x, y, btn_w, btn_h,
                       "⏸ ПАУЗА", NEON_AMBER, "pause",
                       active=self.state.paused)
        self._draw_btn(start_x + btn_w + gap, y, btn_w, btn_h,
                       "↺ СБРОС", NEON_RED, "reset")
        self._draw_btn(start_x + 2 * (btn_w + gap), y, btn_w, btn_h,
                       "▭ ОГИБАЮЩАЯ", NEON_PINK, "toggle_env",
                       active=self.state.show_envelope)
        self._draw_btn(start_x + 3 * (btn_w + gap), y, btn_w, btn_h,
                       "🎲 СЛУЧАЙНО", NEON_PURP, "random")

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

        # график слева
        graph_y = 90
        graph_h = h - 190
        self._draw_graph(w, graph_y, graph_h)

        # панель управления справа
        self._draw_panel(w, graph_y, graph_h)

        # кнопки под графиком
        self._draw_buttons(w, graph_y + graph_h + 10)

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

        if key == "amplitude":  self.state.amplitude = val
        elif key == "frequency": self.state.frequency = val
        elif key == "phase":    self.state.phase = val
        elif key == "damping":  self.state.damping = val

    def _do_action(self, key):
        if key == "pause":
            self.state.paused = not self.state.paused
        elif key == "reset":
            self.state.reset()
        elif key == "toggle_env":
            self.state.show_envelope = not self.state.show_envelope
        elif key == "random":
            import random
            self.state.amplitude = random.uniform(0.5, 2.5)
            self.state.frequency = random.uniform(0.5, 3.0)
            self.state.phase = random.uniform(0, 2 * math.pi)
            self.state.damping = random.choice([0.0, 0.0, 0.15, 0.3])

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