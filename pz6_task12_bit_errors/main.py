"""
ОКФРС. Практика 6. Задание 12.
Влияние искажений на битовом уровне на читаемость текста.
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
BG_CELL    = "#0e1218"
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
# РАБОТА С БИТАМИ
# ============================================================
def text_to_bits(text):
    data = text.encode("utf-8")
    bits = []
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits


def bits_to_text(bits):
    n = (len(bits) // 8) * 8
    bits = bits[:n]
    data = bytearray()
    for i in range(0, n, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        data.append(byte)
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return "?"


def invert_bits(bits, positions):
    result = bits.copy()
    for p in positions:
        if 0 <= p < len(result):
            result[p] = 1 - result[p]
    return result


def hamming_distance(a, b):
    n = min(len(a), len(b))
    return sum(1 for i in range(n) if a[i] != b[i])


def similarity_percent(original, modified):
    """
    Простая правильная метрика: сколько символов совпало на той же позиции.
    Знаменатель — длина ОРИГИНАЛА.
    """
    if not original:
        return 100.0
    matched = 0
    for i in range(min(len(original), len(modified))):
        if original[i] == modified[i]:
            matched += 1
    return matched / len(original) * 100.0


# ============================================================
# СОСТОЯНИЕ
# ============================================================
class AppState:
    def __init__(self):
        self.original_text = "Привет, мир!"
        self.original_bits = text_to_bits(self.original_text)

        self.error_count = 1
        self.error_mode = "random"
        self.error_positions = []
        self.modified_bits = list(self.original_bits)
        self.modified_text = self.original_text

        self.pulse_t = 0.0
        self.apply_errors()

    def tick(self, dt):
        self.pulse_t += dt

    def reset(self):
        self.error_count = 1
        self.error_mode = "random"
        self.original_text = "Привет, мир!"
        self.original_bits = text_to_bits(self.original_text)
        self.apply_errors()

    def apply_errors(self):
        n_bits = len(self.original_bits)
        if n_bits == 0:
            self.error_positions = []
            self.modified_bits = list(self.original_bits)
            self.modified_text = self.original_text
            return

        k = min(self.error_count, n_bits)

        if self.error_mode == "random":
            self.error_positions = random.sample(range(n_bits), k)
        elif self.error_mode == "first":
            self.error_positions = list(range(k))
        elif self.error_mode == "burst":
            start = random.randint(0, max(0, n_bits - k))
            self.error_positions = list(range(start, start + k))
        else:
            self.error_positions = random.sample(range(n_bits), k)

        self.modified_bits = invert_bits(self.original_bits,
                                          self.error_positions)
        self.modified_text = bits_to_text(self.modified_bits)

    def set_text(self, text):
        self.original_text = text
        self.original_bits = text_to_bits(text)
        # пересчитать количество ошибок — не больше чем бит
        self.error_count = min(self.error_count, max(1, len(self.original_bits)))
        self.apply_errors()

    def set_errors(self, n):
        max_n = max(1, len(self.original_bits))
        self.error_count = max(0, min(int(n), max_n))
        self.apply_errors()

    def set_mode(self, mode):
        self.error_mode = mode
        self.apply_errors()

    def stats(self):
        total = len(self.original_bits)
        errors = len(self.error_positions)
        ber = errors / total if total > 0 else 0
        sim = similarity_percent(self.original_text, self.modified_text)
        hd = hamming_distance(self.original_bits, self.modified_bits)
        return {
            "total_bits": total,
            "errors": errors,
            "ber": ber,
            "similarity": sim,
            "hamming": hd,
        }


# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Bit Errors · Влияние искажений на текст")
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
        self.entry_widget = None

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
        self.canvas.create_text(60, 40, text="⚡",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="BIT ERRORS",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(290, 44,
                                text="· ВЛИЯНИЕ ИСКАЖЕНИЙ НА ТЕКСТ",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 11, "bold"))

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

    # ---------- ВВОД ----------
    def _draw_input_panel(self, w, y):
        card_h = 100
        round_rect(self.canvas, 50, y, w - 50, y + card_h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(70, y + 22, anchor="w",
                                text="▸ ИСХОДНЫЙ ТЕКСТ",
                                fill=NEON_CYAN, font=FONT_LABEL)

        # === КНОПКИ СПРАВА — считаем их первыми ===
        btn_w = 130
        btn_h = 40
        gap = 10
        btn_y = y + 45

        btn_x2 = w - 70 - btn_w                 # правая кнопка
        btn_x1 = btn_x2 - btn_w - gap           # левая кнопка

        # entry занимает до btn_x1 - 20
        entry_x = 70
        entry_y = y + 45
        entry_w = btn_x1 - entry_x - 20
        entry_h = 40

        if entry_w < 200:
            entry_w = 200

        round_rect(self.canvas, entry_x, entry_y,
                   entry_x + entry_w, entry_y + entry_h, 8,
                   fill="#050810", outline=BORDER_HL, width=1)

        if self.entry_widget is None or not self.entry_widget.winfo_exists():
            self.entry_widget = tk.Entry(
                self.root,
                bg="#050810", fg=NEON_GREEN,
                insertbackground=NEON_CYAN,
                font=("Consolas", 14, "bold"),
                bd=0, highlightthickness=0)
            self.entry_widget.insert(0, self.state.original_text)
            self.entry_widget.bind("<KeyRelease>", self._on_entry_change)
        else:
            if self.root.focus_get() != self.entry_widget:
                self.entry_widget.delete(0, tk.END)
                self.entry_widget.insert(0, self.state.original_text)

        self.entry_widget.place(x=entry_x + 12, y=entry_y + 6,
                                 width=entry_w - 24, height=entry_h - 12)

        # кнопки
        self._draw_btn(btn_x1, btn_y, btn_w, btn_h,
                       "🎲 ЗАНОВО", NEON_PURP, "rerandom")
        self._draw_btn(btn_x2, btn_y, btn_w, btn_h,
                       "↺ СБРОС", NEON_RED, "reset")

    def _draw_btn(self, x, y, w, h, text, color, key, active=False):
        if active:
            round_rect(self.canvas, x, y, x + w, y + h, 8,
                       fill=lerp(color, BG_DEEP, 0.5),
                       outline=color, width=2)
        else:
            round_rect(self.canvas, x, y, x + w, y + h, 8,
                       fill=lerp(color, BG_DEEP, 0.8),
                       outline=color, width=1)
        self.canvas.create_text(x + w / 2, y + h / 2,
                                text=text, fill=color,
                                font=("Segoe UI", 11, "bold"))
        self.btn_zones[key] = (x, y, x + w, y + h)

    # ---------- СРАВНЕНИЕ ----------
    def _draw_comparison(self, w, y, h):
        round_rect(self.canvas, 50, y, w - 50, y + h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(70, y + 25, anchor="w",
                                text="▸ СРАВНЕНИЕ ТЕКСТА",
                                fill=NEON_CYAN, font=FONT_LABEL)

        stats = self.state.stats()

        # две колонки
        col_w = (w - 140) / 2
        x_left = 70
        x_right = 70 + col_w + 20

        # ОРИГИНАЛ
        self.canvas.create_text(x_left, y + 55, anchor="w",
                                text="ОРИГИНАЛ",
                                fill=NEON_GREEN, font=FONT_LABEL)

        round_rect(self.canvas, x_left, y + 75,
                   x_left + col_w, y + 165, 10,
                   fill="#051208",
                   outline=lerp(NEON_GREEN, BG_DEEP, 0.4), width=1)

        self.canvas.create_text(x_left + 20, y + 120, anchor="w",
                                text=self.state.original_text,
                                fill=NEON_GREEN,
                                font=("Consolas", 20, "bold"))

        # ИСКАЖЁННЫЙ
        self.canvas.create_text(x_right, y + 55, anchor="w",
                                text="ПОСЛЕ ИСКАЖЕНИЙ",
                                fill=NEON_RED, font=FONT_LABEL)

        round_rect(self.canvas, x_right, y + 75,
                   x_right + col_w, y + 165, 10,
                   fill="#1a0508",
                   outline=lerp(NEON_RED, BG_DEEP, 0.4), width=1)

        mod_text = self.state.modified_text or "(пусто)"
        self.canvas.create_text(x_right + 20, y + 120, anchor="w",
                                text=mod_text,
                                fill=NEON_RED,
                                font=("Consolas", 20, "bold"))

        # === 4 метрики в ряд ===
        my = y + 180
        m_gap = 12
        m_w = (w - 140 - 3 * m_gap) / 4

        metrics = [
            ("СОВПАДЕНИЕ",
             f"{stats['similarity']:.1f} %",
             NEON_GREEN if stats['similarity'] > 90 else
             (NEON_AMBER if stats['similarity'] > 50 else NEON_RED)),
            ("ОШИБОК",
             f"{stats['errors']} / {stats['total_bits']}",
             NEON_AMBER),
            ("BER",
             f"{stats['ber']*100:.3f} %",
             NEON_PINK),
            ("ХЭММИНГ",
             f"{stats['hamming']}",
             NEON_CYAN),
        ]

        for i, (label, value, color) in enumerate(metrics):
            mx = 70 + i * (m_w + m_gap)

            round_rect(self.canvas, mx, my,
                       mx + m_w, my + 70, 10,
                       fill=BG_PANEL,
                       outline=lerp(color, BG_DEEP, 0.5), width=1)

            self.canvas.create_text(mx + 15, my + 22, anchor="w",
                                    text=label,
                                    fill=TEXT_DIM, font=FONT_LABEL_S)
            self.canvas.create_text(mx + 15, my + 50, anchor="w",
                                    text=value, fill=color,
                                    font=("Consolas", 18, "bold"))

    # ---------- БИТЫ ----------
    def _draw_bits_view(self, w, y, h):
        round_rect(self.canvas, 50, y, w - 50, y + h, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(70, y + 25, anchor="w",
                                text="▸ БИТОВОЕ ПРЕДСТАВЛЕНИЕ (UTF-8)",
                                fill=NEON_CYAN, font=FONT_LABEL)

        # легенда
        lx = w - 70
        self.canvas.create_text(lx - 200, y + 25, anchor="w",
                                text="● бит 1",
                                fill=NEON_GREEN,
                                font=("Segoe UI", 9, "bold"))
        self.canvas.create_text(lx - 100, y + 25, anchor="w",
                                text="● бит 0",
                                fill=TEXT_DIM,
                                font=("Segoe UI", 9, "bold"))
        self.canvas.create_text(lx, y + 25, anchor="e",
                                text="● искажён",
                                fill=NEON_RED,
                                font=("Segoe UI", 9, "bold"))

        bits = self.state.original_bits
        error_set = set(self.state.error_positions)

        if not bits:
            return

        n = len(bits)

        # считаем сколько влезает
        pad_x = 70
        pad_y = y + 55
        avail_w = w - 140
        avail_h = h - 90

        # 16 бит в ряд
        cols = 16
        cell_w = avail_w / cols
        if cell_w > 40:
            cell_w = 40
        rows = math.ceil(n / cols)

        cell_h = min(30, (avail_h - rows * 6) / max(rows, 1))
        if cell_h < 14:
            cell_h = 14

        # центрируем сетку
        grid_w = cols * cell_w
        grid_x = (w - grid_w) / 2

        for i in range(n):
            row = i // cols
            col = i % cols

            bx = grid_x + col * cell_w
            by = pad_y + row * (cell_h + 6)

            bit = bits[i]
            is_error = (i in error_set)

            # фон ячейки
            if is_error:
                bg = NEON_RED
                fg = "#ffffff"
                outline = "#ffffff"
            else:
                if bit == 1:
                    bg = lerp(NEON_GREEN, BG_DEEP, 0.5)
                    outline = NEON_GREEN
                else:
                    bg = "#0a0d14"
                    outline = "#1a2030"
                fg = "#ffffff" if bit == 1 else TEXT_DIM

            round_rect(self.canvas, bx + 1, by,
                       bx + cell_w - 2, by + cell_h, 3,
                       fill=bg, outline=outline, width=1)

            # цифра
            if cell_w >= 12:
                self.canvas.create_text(bx + cell_w / 2, by + cell_h / 2,
                                        text=str(bit),
                                        fill=fg,
                                        font=("Consolas",
                                              max(8, int(cell_h * 0.55)),
                                              "bold"))

        # разделители байт (каждые 8 бит)
        for b in range(1, (n // 8) + 1):
            byte_idx = b * 8
            if byte_idx >= n:
                break
            row = byte_idx // cols
            col = byte_idx % cols
            bx = grid_x + col * cell_w
            by = pad_y + row * (cell_h + 6)
            self.canvas.create_line(bx - 2, by - 4, bx - 2, by + cell_h + 4,
                                    fill=NEON_AMBER, width=2)

        # подписи байт
        byte_y = pad_y + rows * (cell_h + 6) + 15
        for b in range(n // 8):
            if b % 2 != 0:
                continue
            col_start = (b * 8) % cols
            col_end = ((b + 1) * 8 - 1) % cols
            if col_end < col_start:
                col_end = cols - 1
            x_center = grid_x + (col_start + col_end + 1) / 2 * cell_w
            self.canvas.create_text(x_center, byte_y,
                                    text=f"БАЙТ {b+1}",
                                    fill=NEON_AMBER,
                                    font=("Consolas", 8, "bold"))

    # ---------- ПАНЕЛЬ ----------
    def _draw_panel(self, w, y, h):
        panel_w = 400
        panel_x = w - 50 - panel_w

        round_rect(self.canvas, panel_x, y, panel_x + panel_w, y + h, 14,
                   fill=BG_GLASS, outline=lerp(NEON_PURP, BG_DEEP, 0.5),
                   width=2)

        self.canvas.create_text(panel_x + 20, y + 25, anchor="w",
                                text="▸ УПРАВЛЕНИЕ ОШИБКАМИ",
                                fill=NEON_PURP, font=FONT_LABEL)

        # === режим ===
        self.canvas.create_text(panel_x + 20, y + 55, anchor="w",
                                text="РЕЖИМ РАСПОЛОЖЕНИЯ ОШИБОК:",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        modes = [
            ("random", "СЛУЧАЙНЫЕ", NEON_CYAN),
            ("first",  "С НАЧАЛА",  NEON_GREEN),
            ("burst",  "ПАКЕТ",     NEON_AMBER),
        ]

        btn_y = y + 75
        btn_w = 115
        btn_h = 42
        gap = 8

        for i, (key, label, color) in enumerate(modes):
            bx = panel_x + 20 + i * (btn_w + gap)
            active = (self.state.error_mode == key)
            self._draw_mode_btn(bx, btn_y, btn_w, btn_h, key, label, color, active)

        # === ползунок ===
        sy = y + 150

        self.canvas.create_text(panel_x + 20, sy, anchor="w",
                                text="КОЛИЧЕСТВО ИСКАЖЁННЫХ БИТ",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        stats = self.state.stats()

        # ограничим диапазон
        max_slider = max(1, stats['total_bits'])

        self.canvas.create_text(panel_x + panel_w - 20, sy, anchor="e",
                                text=f"{self.state.error_count} / {stats['total_bits']}",
                                fill=NEON_PINK, font=FONT_MONO)

        bar_x0 = panel_x + 20
        bar_x1 = panel_x + panel_w - 20
        bar_y = sy + 40
        bar_h = 14

        round_rect(self.canvas, bar_x0, bar_y - bar_h/2,
                   bar_x1, bar_y + bar_h/2, 7,
                   fill="#0f141c", outline="")

        vmin, vmax = 0, max_slider
        k = (self.state.error_count - vmin) / (vmax - vmin) if vmax > vmin else 0
        k = max(0.0, min(1.0, k))

        if k > 0.005:
            col_fill = NEON_GREEN if k < 0.3 else (
                       NEON_AMBER if k < 0.6 else NEON_RED)
            round_rect(self.canvas, bar_x0, bar_y - bar_h/2,
                       bar_x0 + (bar_x1 - bar_x0) * k, bar_y + bar_h/2,
                       7, fill=col_fill, outline="")

        cx_ = bar_x0 + (bar_x1 - bar_x0) * k
        self.canvas.create_oval(cx_ - 12, bar_y - 12,
                                cx_ + 12, bar_y + 12,
                                fill="#ffffff", outline=NEON_PINK, width=2)

        self.slider_zones["errors"] = (bar_x0 - 10, bar_y - 16,
                                        bar_x1 + 10, bar_y + 16,
                                        vmin, vmax)

        # деления — 5 штук
        for j in range(6):
            kk = j / 5
            xx = bar_x0 + (bar_x1 - bar_x0) * kk
            val = int(vmin + (vmax - vmin) * kk)
            self.canvas.create_line(xx, bar_y + 16, xx, bar_y + 20,
                                    fill=TEXT_DIM, width=1)
            self.canvas.create_text(xx, bar_y + 30,
                                    text=str(val),
                                    fill=TEXT_DIM,
                                    font=("Consolas", 9, "bold"))

        # === быстрые кнопки (5 штук) ===
        qy = y + 250

        self.canvas.create_text(panel_x + 20, qy, anchor="w",
                                text="БЫСТРЫЙ ВЫБОР:",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        q_vals = [1, 2, 4, 8, 16]
        q_btn_w = 68
        q_btn_h = 36
        q_gap = 8
        q_start = panel_x + 20

        for i, n in enumerate(q_vals):
            bx = q_start + i * (q_btn_w + q_gap)
            active = (self.state.error_count == n)
            self._draw_q_btn(bx, qy + 20, q_btn_w, q_btn_h, str(n), n, active)

        # === статистика ===
        info_y = y + 340

        round_rect(self.canvas, panel_x + 20, info_y,
                   panel_x + panel_w - 20, info_y + 190, 10,
                   fill=BG_PANEL,
                   outline=lerp(NEON_CYAN, BG_DEEP, 0.5), width=1)

        self.canvas.create_text(panel_x + panel_w / 2, info_y + 22,
                                text="СТАТИСТИКА",
                                fill=NEON_CYAN,
                                font=FONT_LABEL_S)

        lines = [
            ("Исходных бит",     f"{stats['total_bits']}",                NEON_GREEN),
            ("Искажено бит",     f"{stats['errors']}",                    NEON_RED),
            ("BER",              f"{stats['ber']*100:.3f} %",             NEON_PINK),
            ("Совпадение",       f"{stats['similarity']:.1f} %",          NEON_AMBER),
            ("Хэмминг",          f"{stats['hamming']}",                   NEON_CYAN),
        ]

        for i, (label, value, color) in enumerate(lines):
            ly = info_y + 55 + i * 25
            self.canvas.create_text(panel_x + 35, ly, anchor="w",
                                    text=label, fill=TEXT_DIM,
                                    font=FONT_MONO_S)
            self.canvas.create_text(panel_x + panel_w - 35, ly, anchor="e",
                                    text=value, fill=color,
                                    font=FONT_MONO_S)

        # === большая кнопка внизу ===
        by = y + h - 60
        self._draw_btn(panel_x + 15, by, panel_w - 30, 44,
                       "🎲 ПЕРЕСОЗДАТЬ ОШИБКИ", NEON_PURP, "rerandom")

    def _draw_mode_btn(self, x, y, w, h, key, label, color, active):
        if active:
            for i in range(3, 0, -1):
                round_rect(self.canvas, x - i, y - i,
                           x + w + i, y + h + i, 8 + i,
                           outline=lerp(color, BG_DEEP, i / 4), width=1)
            round_rect(self.canvas, x, y, x + w, y + h, 8,
                       fill=lerp(color, BG_DEEP, 0.6),
                       outline=color, width=2)
            self.canvas.create_text(x + w / 2, y + h / 2,
                                    text=label, fill=color,
                                    font=("Segoe UI", 10, "bold"))
        else:
            round_rect(self.canvas, x, y, x + w, y + h, 8,
                       fill="#0f141c",
                       outline="#2a3040", width=1)
            self.canvas.create_text(x + w / 2, y + h / 2,
                                    text=label, fill=TEXT_DIM,
                                    font=("Segoe UI", 10, "bold"))
        self.btn_zones[f"mode_{key}"] = (x, y, x + w, y + h)

    def _draw_q_btn(self, x, y, w, h, text, n, active):
        color = NEON_CYAN
        if active:
            round_rect(self.canvas, x, y, x + w, y + h, 6,
                       fill=lerp(color, BG_DEEP, 0.5),
                       outline=color, width=2)
            self.canvas.create_text(x + w / 2, y + h / 2,
                                    text=text, fill=color,
                                    font=("Consolas", 13, "bold"))
        else:
            round_rect(self.canvas, x, y, x + w, y + h, 6,
                       fill="#0f141c", outline="#2a3040", width=1)
            self.canvas.create_text(x + w / 2, y + h / 2,
                                    text=text, fill=TEXT_DIM,
                                    font=("Consolas", 13, "bold"))
        self.btn_zones[f"q_{n}"] = (x, y, x + w, y + h)

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

        panel_w = 400
        main_w = w - 100 - panel_w - 20

        self._draw_bg(w, h)
        self._draw_header(w)
        self._draw_input_panel(w, 90)

        # левая колонка
        comp_y = 210
        comp_h = 280
        self._draw_comparison(main_w + 100, comp_y, comp_h)

        bits_y = comp_y + comp_h + 15
        bits_h = h - bits_y - 20
        if bits_h < 150:
            bits_h = 150
        self._draw_bits_view(main_w + 100, bits_y, bits_h)

        # правая панель
        self._draw_panel(w, 210, h - 230)

    # ---------- СОБЫТИЯ ----------
    def _on_entry_change(self, event):
        try:
            text = self.entry_widget.get()
            self.state.set_text(text)
        except Exception:
            pass

    def _on_click(self, event):
        x, y = event.x, event.y

        for key, (x0, y0, x1, y1, vmin, vmax) in self.slider_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                self.drag_slider = key
                self._set_slider_from_mouse(key, x)
                return

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
        val = int(round(vmin + k * (vmax - vmin)))
        if key == "errors":
            self.state.set_errors(val)

    def _do_action(self, key):
        if key == "reset":
            self.state.reset()
            self._update_entry()
        elif key == "rerandom":
            self.state.apply_errors()
        elif key.startswith("mode_"):
            mode = key[5:]
            self.state.set_mode(mode)
        elif key.startswith("q_"):
            n = int(key[2:])
            self.state.set_errors(n)

    def _update_entry(self):
        if self.entry_widget and self.entry_widget.winfo_exists():
            self.entry_widget.delete(0, tk.END)
            self.entry_widget.insert(0, self.state.original_text)

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
        self.root.after(80, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()