import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as patches
from matplotlib import cm
import matplotlib.patheffects as path_effects
import matplotlib.colors as mcolors




#cleanup code later







# -------------------------------------------------
# 1) SAMPLE FLOOR PLAN (replace with your generated JSON)
# -------------------------------------------------
floorplan_json = """
{
  "rooms": [
    {"name": "Living Room", "x":0, "y":0, "width":5, "height":4},
    {"name": "Kitchen",      "x":5, "y":0, "width":3, "height":4},
    {"name": "Bedroom 1",    "x":0, "y":4, "width":4, "height":3},
    {"name": "Bathroom",     "x":4, "y":4, "width":2, "height":2}
  ]
}
"""

data = json.loads(floorplan_json)["rooms"]

# -------------------------------------------------
# 2) NOISE LEVELS (replace with your own data)
# -------------------------------------------------
noise_levels = {
    "Living Room": 40,
    "Kitchen": 55,
    "Bedroom 1": 80,
    "Bathroom": 90
}
# Map rating to color
rating_colors = {
    'A': 'green',
    'B': 'lime',
    'C': 'yellowgreen',
    'D': 'yellow',
    'E': 'orange',
    'F': 'darkorange',
    'G': 'red'
}
def get_rating(noise):
    if noise <= 20: return 'A'
    elif noise <= 35: return 'B'
    elif noise <= 50: return 'C'
    elif noise <= 65: return 'D'
    elif noise <= 75: return 'E'
    elif noise <= 90: return 'F'
    else: return 'G'

# -------------------------------------------------
# 3) DRAW FLOOR PLAN + HEATMAP
# -------------------------------------------------

def draw_floorplan_to_pdf(rooms, noise_data, output="floorplan.pdf"):
    max_x = max(room["x"] + room["width"] for room in rooms)
    max_y = max(room["y"] + room["height"] for room in rooms)

    with PdfPages(output) as pdf:
        fig, ax = plt.subplots(figsize=(8, 6))

        # ---- Draw room rectangles (white background)
        for room in rooms:
            rect = patches.Rectangle(
                (room["x"], room["y"]),
                room["width"],
                room["height"],
                linewidth=2,
                edgecolor="black",
                facecolor="white"
            )
            ax.add_patch(rect)

        # ---- Create colormap
        cmap = cm.get_cmap("hot")

        # ---- Draw ripple waves
        for room in rooms:
            name = room["name"]
            noise = noise_data.get(name, 0)

            # Room center
            cx = room["x"] + room["width"] / 2
            cy = room["y"] + room["height"] / 2

            # Number of ripple rings
            # Increased ripple density
            # Ultra dense ripple settings
            rings = 10
            max_radius =4.5
            print(max_radius)
            points = 120
            clip_rect = patches.Rectangle(
                (room["x"], room["y"]),
                room["width"],
                room["height"],
                transform=ax.transData
            )

# Room‐based directional bias
            direction_bias = (noise % 360) * np.pi / 180
            noise_strength = (noise / 100)

            for i in range(rings):
                base_radius = (i + 1) * (max_radius / rings)
                theta = np.linspace(0, 2*np.pi, points)

    # Wavy distortion
                distortion = (
                    np.sin(theta * 6 + i * 0.7) * 0.06 +
                    np.cos(theta * 5 + i * 0.3) * 0.05 +
                    np.sin(theta * 4 + i) * 0.04
                ) 
                directional_wave = 0.08 * np.sin(theta - direction_bias)
                

                r = base_radius * (1 + distortion + directional_wave )
                x = cx + r * np.cos(theta)
                y = cy + r * np.sin(theta)

                rating = get_rating(noise)
                color = rating_colors[rating]
                alpha = min(0.9, 0.2 + noise_strength)

    # Draw ripple with clipping
                line, = ax.plot(x, y, color=color, linewidth=1.1, alpha=alpha)
                line.set_clip_path(clip_rect)

    # Echo shadow ripple with clipping
                shadow_offset = 0.02 * max_radius
                line_shadow, = ax.plot(
                    x ,
                    y ,
                    color=color ,
                    linewidth=10,
                    alpha=alpha * 0.15
                )
                line_shadow.set_clip_path(clip_rect)
                line.set_path_effects([
                    path_effects.Stroke(linewidth=12, foreground=color, alpha=0.1),
                    path_effects.Normal()
                ])


            ax.text(
                room["x"] + room["width"]/2,
                room["y"] + room["height"]/2,
                f"{room['name']}\n{noise_data.get(room['name'], '?')} dB",
                ha='center', va='center',
                fontsize=10, color="black",
                bbox=dict(facecolor="white", alpha=0.3, edgecolor='none')
            )

        # ---- Add colorbar legend
        ratings = list(rating_colors.keys())
        colors = [rating_colors[r] for r in ratings]


        cmap = mcolors.ListedColormap(colors)
        bounds = list(range(len(ratings)+1))  # 0 to 7
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        
        
        cbar = fig.colorbar(sm, ax=ax, ticks=np.arange(0.5, len(ratings)+0.5))
        cbar.ax.set_yticklabels(ratings)  # show letters instead of numbers
        cbar.set_label("Noise Rating")

        # ---- Final layout
        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Apartment Floor Plan with Noise Ripple Waves")
        ax.set_xlabel("Meters (approx)")
        ax.set_ylabel("Meters (approx)")
        ax.grid(False)

        pdf.savefig(fig)
        plt.close(fig)


# -------------------------------------------------
# 4) RUN IT
# -------------------------------------------------
draw_floorplan_to_pdf(data, noise_levels)

print("PDF successfully generated: floorplan.pdf")
