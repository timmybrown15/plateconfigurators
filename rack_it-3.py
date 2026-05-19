import tkinter as tk
import math

BAR_INFO = {
    "Standard Bar": {"weight": 45, "color": "#b0b8c1"},
    "EZ Curl Bar":  {"weight": 15, "color": "#a8c4a2"},
    "Trap Bar":     {"weight": 55, "color": "#c4a8a2"},
}

PLATE_INFO = [
    {"weight": 45,  "color": "#c0392b", "width": 18, "height": 72},
    {"weight": 25,  "color": "#2980b9", "width": 14, "height": 60},
    {"weight": 10,  "color": "#27ae60", "width": 10, "height": 50},
    {"weight": 5,   "color": "#8e44ad", "width":  8, "height": 42},
    {"weight": 2.5, "color": "#e67e22", "width":  6, "height": 34},
]


def configurate(total_weight, bar_weight):
    x = (total_weight - bar_weight) / 2
    result = []
    for p in PLATE_INFO:
        n = int(x // p["weight"])
        result.append((p["weight"], n))
        x -= n * p["weight"]
    remainder = round(x, 2)
    return result, remainder


# ─────────────────────────────────────────────────────────────────────────────
#  Bar drawing functions
# ─────────────────────────────────────────────────────────────────────────────

def draw_standard_bar(canvas, cx, cy, sleeve_half, bar_half, color):
    """Straight Olympic bar with knurling."""
    t = 10  # shaft thickness

    # Main shaft
    canvas.create_rectangle(cx - bar_half, cy - t // 2,
                             cx + bar_half, cy + t // 2,
                             fill=color, outline="#777", width=1)
    # Knurling marks (centre grip area)
    for xk in range(cx - 60, cx + 61, 9):
        canvas.create_line(xk, cy - t // 2 - 1,
                           xk, cy + t // 2 + 1,
                           fill="#888", width=1)
    # Shoulder knurling
    for side in [-1, 1]:
        base = cx + side * (sleeve_half - 40)
        for xk in range(base, base + side * 30, side * 9):
            canvas.create_line(xk, cy - t // 2 - 1,
                               xk, cy + t // 2 + 1,
                               fill="#888", width=1)


def draw_ez_curl_bar(canvas, cx, cy, sleeve_half, bar_half, color):
    """EZ curl bar with smooth sinusoidal grip section, matching real bar shape."""
    t = 9

    # Outer straight sleeves
    canvas.create_rectangle(cx - bar_half, cy - t // 2,
                             cx - sleeve_half, cy + t // 2,
                             fill=color, outline="#777", width=1)
    canvas.create_rectangle(cx + sleeve_half, cy - t // 2,
                             cx + bar_half, cy + t // 2,
                             fill=color, outline="#777", width=1)

    # Build the centreline of the wavy grip as a sine curve
    # The real EZ bar has ~3 full waves across the grip section
    grip_w = sleeve_half * 2      # total pixel width of wavy section
    amp = 16                       # wave amplitude (how far it dips up/down)
    waves = 2.5                    # number of full sine cycles
    steps = 200

    centre_pts = []
    for i in range(steps + 1):
        frac = i / steps
        x = cx - sleeve_half + frac * grip_w
        y = cy + amp * math.sin(frac * waves * 2 * math.pi)
        centre_pts.append((x, y))

    # Build a filled polygon by offsetting each point perpendicular to the curve
    half_t = t / 2
    upper_pts = []
    lower_pts = []

    for i, (x, y) in enumerate(centre_pts):
        # Tangent direction
        if i == 0:
            dx = centre_pts[1][0] - x
            dy = centre_pts[1][1] - y
        elif i == steps:
            dx = x - centre_pts[-2][0]
            dy = y - centre_pts[-2][1]
        else:
            dx = centre_pts[i+1][0] - centre_pts[i-1][0]
            dy = centre_pts[i+1][1] - centre_pts[i-1][1]

        length = math.hypot(dx, dy) or 1
        # Normal (perpendicular) pointing "up"
        nx = -dy / length
        ny =  dx / length

        upper_pts.append((x + nx * half_t, y + ny * half_t))
        lower_pts.append((x - nx * half_t, y - ny * half_t))

    poly = upper_pts + list(reversed(lower_pts))
    flat = [coord for pt in poly for coord in pt]
    canvas.create_polygon(flat, fill=color, outline="#777", width=1)

    # Knurling — tick marks perpendicular to curve every ~12px along grip
    knurl_spacing = 12
    dist = 0
    for i in range(1, len(centre_pts)):
        x0, y0 = centre_pts[i-1]
        x1, y1 = centre_pts[i]
        dist += math.hypot(x1 - x0, y1 - y0)
        if dist >= knurl_spacing:
            dist = 0
            dx = x1 - x0
            dy = y1 - y0
            length = math.hypot(dx, dy) or 1
            nx = -dy / length
            ny =  dx / length
            canvas.create_line(x1 + nx * (half_t + 2), y1 + ny * (half_t + 2),
                               x1 - nx * (half_t + 2), y1 - ny * (half_t + 2),
                               fill="#888", width=1)


def draw_trap_bar(canvas, cx, cy, color):
    """Hex/trap bar viewed from the side — hexagonal frame with handles."""
    # The trap bar is shown as a top-down perspective hex outline
    # with two protruding sleeves left and right

    hex_w = 110   # half-width of hex
    hex_h = 55    # half-height of hex
    bar_half = 220
    sleeve_half = hex_w
    t = 9

    # Outer sleeves
    canvas.create_rectangle(cx - bar_half, cy - t // 2,
                             cx - sleeve_half, cy + t // 2,
                             fill=color, outline="#777", width=1)
    canvas.create_rectangle(cx + sleeve_half, cy - t // 2,
                             cx + bar_half, cy + t // 2,
                             fill=color, outline="#777", width=1)

    # Hex frame (flat-top hexagon outline, thick border)
    # 6 corners of a rectangle-ish hex
    pts = [
        cx - hex_w,        cy,
        cx - hex_w + 28,   cy - hex_h,
        cx + hex_w - 28,   cy - hex_h,
        cx + hex_w,        cy,
        cx + hex_w - 28,   cy + hex_h,
        cx - hex_w + 28,   cy + hex_h,
    ]
    canvas.create_polygon(pts, fill="", outline=color, width=11)
    canvas.create_polygon(pts, fill="", outline="#555", width=1)

    # Centre handle bars (the two parallel grip tubes inside the hex)
    grip_offset = 20
    for yo in [-grip_offset, grip_offset]:
        canvas.create_rectangle(cx - 55, cy + yo - 4,
                                 cx + 55, cy + yo + 4,
                                 fill=color, outline="#666", width=1)
        # Knurling
        for xk in range(cx - 50, cx + 51, 9):
            canvas.create_line(xk, cy + yo - 4,
                               xk, cy + yo + 4,
                               fill="#888", width=1)


def draw_bar_diagram(canvas, plates_per_side, bar_name):
    canvas.delete("all")
    W = int(canvas["width"])
    H = int(canvas["height"])
    cx = W // 2
    cy = H // 2

    color = BAR_INFO[bar_name]["color"]
    bar_half = 220
    sleeve_half = 155

    # ── Draw the correct bar shape ────────────────────────────────────────────
    if bar_name == "Standard Bar":
        draw_standard_bar(canvas, cx, cy, sleeve_half, bar_half, color)
    elif bar_name == "EZ Curl Bar":
        draw_ez_curl_bar(canvas, cx, cy, sleeve_half, bar_half, color)
    elif bar_name == "Trap Bar":
        draw_trap_bar(canvas, cx, cy, color)

    # ── Draw plates outward from sleeve on both sides ─────────────────────────
    gap = 2
    left_x  = cx - sleeve_half
    right_x = cx + sleeve_half

    for plate_w, count in plates_per_side:
        if count == 0:
            continue
        info = next(p for p in PLATE_INFO if p["weight"] == plate_w)
        pw = info["width"]
        ph = info["height"]
        col = info["color"]

        for _ in range(count):
            lx1, lx2 = left_x - pw, left_x
            canvas.create_rectangle(lx1, cy - ph // 2, lx2, cy + ph // 2,
                                     fill=col, outline="#333", width=1)
            canvas.create_text((lx1 + lx2) // 2, cy,
                                text=str(plate_w), fill="white",
                                font=("Arial", 7, "bold"), angle=90)
            left_x = lx1 - gap

            rx1, rx2 = right_x, right_x + pw
            canvas.create_rectangle(rx1, cy - ph // 2, rx2, cy + ph // 2,
                                     fill=col, outline="#333", width=1)
            canvas.create_text((rx1 + rx2) // 2, cy,
                                text=str(plate_w), fill="white",
                                font=("Arial", 7, "bold"), angle=90)
            right_x = rx2 + gap

    # End collars / caps
    cap_w = 8
    canvas.create_rectangle(cx - bar_half, cy - 16,
                             cx - bar_half + cap_w, cy + 16,
                             fill="#666", outline="#444")
    canvas.create_rectangle(cx + bar_half - cap_w, cy - 16,
                             cx + bar_half, cy + 16,
                             fill="#666", outline="#444")


# ─────────────────────────────────────────────────────────────────────────────
#  Bar preview (input screen)
# ─────────────────────────────────────────────────────────────────────────────

def draw_bar_preview(canvas, bar_name):
    canvas.delete("all")
    W = int(canvas["width"])
    H = int(canvas["height"])
    cx, cy = W // 2, H // 2
    color = BAR_INFO[bar_name]["color"]

    if bar_name == "Standard Bar":
        draw_standard_bar(canvas, cx, cy, 120, 180, color)
    elif bar_name == "EZ Curl Bar":
        draw_ez_curl_bar(canvas, cx, cy, 120, 180, color)
    elif bar_name == "Trap Bar":
        draw_trap_bar(canvas, cx, cy, color)


# ─────────────────────────────────────────────────────────────────────────────
#  Result screen population
# ─────────────────────────────────────────────────────────────────────────────

def show_result(bar_name, total_weight, diagram_canvas, result_label):
    plates, remainder = configurate(total_weight, BAR_INFO[bar_name]["weight"])

    lines = [f"Bar: {bar_name}  ({BAR_INFO[bar_name]['weight']} lb)",
             f"Total: {total_weight} lb", ""]
    has_plates = any(c > 0 for _, c in plates)
    if has_plates:
        for plate_w, count in plates:
            if count:
                lines.append(f"  {count}x {plate_w} lb  per side")
    else:
        lines.append("  No plates needed")
    if remainder > 0:
        lines.append(f"\n  ⚠  {remainder} lb can't be made with standard plates")

    result_label.config(text="\n".join(lines))
    draw_bar_diagram(diagram_canvas, plates, bar_name)


# ─────────────────────────────────────────────────────────────────────────────
#  App
# ─────────────────────────────────────────────────────────────────────────────

def build_app():
    root = tk.Tk()
    root.title("Rack It!")
    root.geometry("680x640")
    root.resizable(False, False)
    root.configure(bg="#1a1a2e")

    # ── Screen 1 — Input ──────────────────────────────────────────────────────
    screen1 = tk.Frame(root, bg="#1a1a2e")
    screen1.place(relx=0, rely=0, relwidth=1, relheight=1)

    tk.Label(screen1, text="🏋  Rack It!", font=("Times New Roman", 28, "bold"),
             bg="#1a1a2e", fg="#e0e0e0").pack(pady=20)

    tk.Label(screen1, text="Select Bar", font=("Arial", 13),
             bg="#1a1a2e", fg="#aaaaaa").pack()

    bar_choice = tk.StringVar(value="Standard Bar")

    # Live bar preview canvas
    preview_canvas = tk.Canvas(screen1, width=400, height=110,
                                bg="#0f0f23", highlightthickness=0)
    preview_canvas.pack(pady=8)

    def on_bar_change(*_):
        draw_bar_preview(preview_canvas, bar_choice.get())

    bar_choice.trace_add("write", on_bar_change)

    bar_menu = tk.OptionMenu(screen1, bar_choice, *BAR_INFO.keys())
    bar_menu.config(font=("Arial", 12), bg="#16213e", fg="#e0e0e0",
                    activebackground="#0f3460", activeforeground="white",
                    highlightthickness=0, width=18)
    bar_menu["menu"].config(bg="#16213e", fg="#e0e0e0")
    bar_menu.pack(pady=4)

    tk.Label(screen1, text="Target Weight (lb)", font=("Arial", 13),
             bg="#1a1a2e", fg="#aaaaaa").pack(pady=(14, 2))

    weight_entry = tk.Entry(screen1, font=("Arial", 14), width=10,
                            bg="#16213e", fg="#e0e0e0",
                            insertbackground="white", justify="center",
                            relief="flat", highlightthickness=1,
                            highlightbackground="#444",
                            highlightcolor="#e94560")
    weight_entry.pack(ipady=6)

    error_label = tk.Label(screen1, text="", font=("Arial", 10),
                           bg="#1a1a2e", fg="#e94560")
    error_label.pack(pady=4)

    # ── Screen 2 — Result ─────────────────────────────────────────────────────
    screen2 = tk.Frame(root, bg="#1a1a2e")

    top_bar = tk.Frame(screen2, bg="#1a1a2e")
    top_bar.pack(fill="x", padx=16, pady=(14, 0))

    tk.Button(top_bar, text="← Back", font=("Arial", 10),
              bg="#16213e", fg="#aaaaaa",
              activebackground="#0f3460", activeforeground="white",
              relief="flat", padx=10, pady=4,
              command=lambda: (screen2.place_forget(),
                               screen1.place(relx=0, rely=0,
                                             relwidth=1, relheight=1))
              ).pack(side="left")

    tk.Label(top_bar, text="Rack It!", font=("Arial", 14, "bold"),
             bg="#1a1a2e", fg="#e0e0e0").pack(side="left", padx=14)

    result_label = tk.Label(screen2, text="", font=("Courier", 11),
                            bg="#1a1a2e", fg="#e0e0e0", justify="left")
    result_label.pack(padx=20, pady=(10, 0), anchor="w")

    diagram_canvas = tk.Canvas(screen2, width=660, height=180,
                                bg="#0f0f23", highlightthickness=0)
    diagram_canvas.pack(pady=14)

    # ── Rack It! button ───────────────────────────────────────────────────────
    def on_rack_it():
        error_label.config(text="")
        raw = weight_entry.get().strip()
        if not raw:
            error_label.config(text="Please enter a weight.")
            return
        try:
            total = float(raw)
        except ValueError:
            error_label.config(text="Enter a valid number.")
            return

        bar_name = bar_choice.get()
        bar_w = BAR_INFO[bar_name]["weight"]

        if total < bar_w:
            error_label.config(text=f"Weight must be ≥ {bar_w} lb (bar weight).")
            return

        show_result(bar_name, total, diagram_canvas, result_label)
        screen1.place_forget()
        screen2.place(relx=0, rely=0, relwidth=1, relheight=1)

    tk.Button(screen1, text="Rack It! 🏋",
              font=("Arial", 14, "bold"),
              bg="#e94560", fg="white",
              activebackground="#c73652", activeforeground="white",
              relief="flat", padx=24, pady=10,
              command=on_rack_it).pack(pady=16)

    weight_entry.bind("<Return>", lambda e: on_rack_it())

    # Draw initial preview
    draw_bar_preview(preview_canvas, bar_choice.get())

    root.mainloop()


if __name__ == "__main__":
    build_app()
