import os
from PIL import Image, ImageDraw

os.makedirs("sprites", exist_ok=True)

# Grid scale: 16x16 grid scaled to 128x128 pixel art
SCALE = 8
SIZE = 16 * SCALE

def create_base_canvas():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)

# Color Palette matching user's image
ORANGE = (245, 140, 50, 255)
DARK_ORANGE = (210, 110, 30, 255)
WHITE = (255, 255, 255, 255)
OFF_WHITE = (240, 240, 240, 255)
PINK = (245, 160, 180, 255)
BLACK = (20, 20, 20, 255)
RED_COLLAR = (230, 50, 50, 255)
YELLOW_TAG = (255, 215, 0, 255)
RED_EYES = (255, 30, 30, 255)

def draw_pixel(draw, x, y, color):
    draw.rectangle([x * SCALE, y * SCALE, (x + 1) * SCALE - 1, (y + 1) * SCALE - 1], fill=color)

def draw_cat(pose="idle"):
    img, draw = create_base_canvas()
    
    # Tail (upright with white tip)
    tail_x = 2
    tail_y_start = 9
    if pose == "sit":
        # Tail curled back
        for y in range(7, 12):
            draw_pixel(draw, 1, y, ORANGE)
        draw_pixel(draw, 1, 6, WHITE)
    else:
        for y in range(5, 10):
            draw_pixel(draw, tail_x, y, ORANGE)
        draw_pixel(draw, tail_x, 4, WHITE)

    # Body (Orange back half, White front half)
    # Back / Hips (Orange)
    for x in range(3, 8):
        for y in range(8, 12):
            draw_pixel(draw, x, y, ORANGE)
            
    # Front / Belly (White)
    for x in range(8, 12):
        for y in range(8, 12):
            draw_pixel(draw, x, y, WHITE)

    # Orange patch on front leg
    draw_pixel(draw, 10, 11, ORANGE)

    # Legs
    if pose == "idle":
        draw_pixel(draw, 4, 12, ORANGE)
        draw_pixel(draw, 5, 12, ORANGE)
        draw_pixel(draw, 4, 13, ORANGE)
        draw_pixel(draw, 5, 13, ORANGE)
        
        draw_pixel(draw, 6, 12, WHITE)
        draw_pixel(draw, 7, 12, WHITE)
        draw_pixel(draw, 6, 13, WHITE)
        draw_pixel(draw, 7, 13, WHITE)

        draw_pixel(draw, 9, 12, WHITE)
        draw_pixel(draw, 10, 12, WHITE)
        draw_pixel(draw, 9, 13, WHITE)
        draw_pixel(draw, 10, 13, WHITE)
    elif pose == "walk1":
        # Back legs walk pose 1
        draw_pixel(draw, 3, 12, ORANGE)
        draw_pixel(draw, 4, 13, ORANGE)
        
        draw_pixel(draw, 6, 12, WHITE)
        draw_pixel(draw, 7, 13, WHITE)
        
        # Front legs step 1 (Right paw forward)
        draw_pixel(draw, 9, 12, WHITE)
        draw_pixel(draw, 8, 13, WHITE)
        draw_pixel(draw, 11, 12, ORANGE)
        draw_pixel(draw, 12, 13, ORANGE)
    elif pose == "walk2":
        # Back legs walk pose 2 (Opposite legs)
        draw_pixel(draw, 4, 12, ORANGE)
        draw_pixel(draw, 3, 13, ORANGE)
        
        draw_pixel(draw, 7, 12, WHITE)
        draw_pixel(draw, 6, 13, WHITE)
        
        # Front legs step 2 (Left paw forward)
        draw_pixel(draw, 8, 12, WHITE)
        draw_pixel(draw, 9, 13, WHITE)
        draw_pixel(draw, 10, 12, ORANGE)
        draw_pixel(draw, 11, 13, ORANGE)
    elif pose == "sit":
        # Legs tucked
        for x in range(4, 11):
            draw_pixel(draw, x, 12, ORANGE if x < 7 else WHITE)
    elif pose == "smash":
        # Back legs plant
        draw_pixel(draw, 4, 12, ORANGE)
        draw_pixel(draw, 5, 13, ORANGE)
        draw_pixel(draw, 7, 12, WHITE)
        draw_pixel(draw, 8, 13, WHITE)
        # Front paw raised high to smash!
        draw_pixel(draw, 11, 6, WHITE)
        draw_pixel(draw, 12, 5, WHITE)
        draw_pixel(draw, 13, 5, ORANGE)

    # Red Collar & Bell
    for x in range(8, 12):
        draw_pixel(draw, x, 7, RED_COLLAR)
    draw_pixel(draw, 9, 8, YELLOW_TAG)

    # Head (Split: Left ear/back orange, right face white)
    # Head base
    for x in range(7, 13):
        for y in range(2, 7):
            if x <= 8:
                draw_pixel(draw, x, y, ORANGE)
            else:
                draw_pixel(draw, x, y, WHITE)

    # Ears
    draw_pixel(draw, 7, 1, ORANGE)
    draw_pixel(draw, 8, 1, PINK)
    draw_pixel(draw, 11, 1, PINK)
    draw_pixel(draw, 12, 1, WHITE)

    # Eyes & Nose
    eye_color = RED_EYES if pose in ["angry", "smash"] else BLACK
    draw_pixel(draw, 9, 4, eye_color)
    draw_pixel(draw, 12, 4, eye_color)
    draw_pixel(draw, 11, 5, PINK) # Pink nose

    # Angry Steam Effect
    if pose in ["angry", "smash"]:
        draw_pixel(draw, 6, 0, (255, 100, 100, 255))
        draw_pixel(draw, 7, 0, (255, 50, 50, 255))
        draw_pixel(draw, 13, 0, (255, 100, 100, 255))

    return img

def main():
    poses = ["idle", "walk1", "walk2", "sit", "angry", "smash"]
    for pose in poses:
        img = draw_cat(pose)
        filepath = os.path.join("sprites", f"cat_{pose}.png")
        img.save(filepath)
        print(f"Generated {filepath}")
    # Also save cat_walk.png as alias to cat_walk1.png for backwards compatibility
    img1 = draw_cat("walk1")
    img1.save(os.path.join("sprites", "cat_walk.png"))

if __name__ == "__main__":
    main()