"""Generate Dyson-style bladeless fan icons for the menu bar."""
from PIL import Image, ImageDraw

SIZE = 22  # macOS menu bar icon size (will provide @2x too)


def draw_fan_icon(size, filled=False, white=False):
    """Draw a Dyson-style bladeless fan: oval loop on a small base/stand."""
    scale = size
    img = Image.new("RGBA", (scale, scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    color = (255, 255, 255, 255) if white else (0, 0, 0, 255)
    lw = max(1, scale // 16)

    # Oval ring (the bladeless fan loop) - tall elongated oval like Dyson
    oval_margin_x = scale // 4
    oval_top = scale // 14
    oval_bottom = int(scale * 0.72)
    outer = [oval_margin_x, oval_top, scale - oval_margin_x, oval_bottom]
    inner_inset = lw + max(1, scale // 12)
    inner = [
        outer[0] + inner_inset,
        outer[1] + inner_inset,
        outer[2] - inner_inset,
        outer[3] - inner_inset,
    ]

    if filled:
        # Filled version for ON state - solid oval with blue center
        draw.ellipse(outer, fill=color)
        # Fill the inner hole with blue
        draw.ellipse(inner, fill=(30, 144, 255, 255))
    else:
        # Outline version for OFF state
        draw.ellipse(outer, outline=color, width=lw)

    # Base/stand - small rectangle + foot
    base_width = scale // 5
    base_x = (scale - base_width) // 2
    base_top = oval_bottom - lw
    base_bottom = int(scale * 0.88)
    draw.rectangle([base_x, base_top, base_x + base_width, base_bottom], fill=color)

    # Foot - wider bottom
    foot_width = scale // 3
    foot_x = (scale - foot_width) // 2
    foot_top = base_bottom
    foot_bottom = scale - scale // 10
    draw.rounded_rectangle(
        [foot_x, foot_top, foot_x + foot_width, foot_bottom],
        radius=lw,
        fill=color,
    )

    return img


# Generate @1x and @2x for both states
for name, filled in [("icon_off", False), ("icon_on_dark", True), ("icon_on_light", True)]:
    use_white = (name == "icon_on_dark")
    for sz, suffix in [(22, ""), (44, "@2x")]:
        img = draw_fan_icon(sz, filled, white=use_white)
        img.save(f"{name}{suffix}.png")

print("Generated icons for all states and appearances.")
