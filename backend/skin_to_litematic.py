import sys
import math
from PIL import Image
import litemapy

import json
import os

# Load Block Palette from JSON
PALETTE_FILE = "block_palette.json"

def get_block_palette():
    if not os.path.exists(PALETTE_FILE):
        print(f"Error: {PALETTE_FILE} not found. Please run fetch_palette.py first.")
        sys.exit(1)
        
    with open(PALETTE_FILE, 'r') as f:
        data = json.load(f)
        
    palette = {}
    for rgb_str, block_id in data.items():
        r, g, b = map(int, rgb_str.split(','))
        palette[(r, g, b)] = block_id
        
    return palette

BLOCK_PALETTE = {} # Will be loaded in main

def load_skin(path):
    try:
        img = Image.open(path).convert("RGBA")
        if img.size != (64, 64):
            print(f"Warning: Skin size is {img.size}, expected (64, 64). Resizing...")
            img = img.resize((64, 64))
        return img
    except Exception as e:
        print(f"Error loading skin: {e}")
        sys.exit(1)

def find_closest_block(rgba, palette):
    r, g, b, a = rgba
    if a < 128: # Transparent
        return "minecraft:air"
    
    min_dist = float('inf')
    closest_block = "minecraft:stone" # Default fallback
    
    for color, block_id in palette.items():
        cr, cg, cb = color
        dist = math.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        if dist < min_dist:
            min_dist = dist
            closest_block = block_id
            
    return closest_block

def build_statue_data(skin_image):
    pixels = skin_image.load()
    statue_blocks = {} # (x, y, z) -> block_id

    # Helper to add a box of blocks
    def add_part(start_x, start_y, width, height, depth, texture_u, texture_v, offset_x, offset_y, offset_z, is_overlay=False):
        # Front Face
        for u in range(width):
            for v in range(height):
                color = pixels[texture_u + depth + u, texture_v + depth + v]
                block = find_closest_block(color, BLOCK_PALETTE)
                if block != "minecraft:air":
                    statue_blocks[(offset_x + u, offset_y + (height - 1 - v), offset_z + depth - 1)] = block
        
        # Back Face
        for u in range(width):
            for v in range(height):
                # Back texture is usually: u + depth + width + depth + u
                # Wait, standard layout:
                # Top (8x8), Bottom (8x8)
                # Right (4x12), Front (8x12), Left (4x12), Back (8x12)
                # Let's use specific texture coordinates for each face to be safe
                pass

    # We will iterate through 3D coordinates of the statue and map to 2D skin coordinates
    # Statue Coordinate System:
    # x: width (left to right)
    # y: height (bottom to top)
    # z: depth (back to front)
    
    # Define parts: (name, dim_w, dim_h, dim_d, tex_u, tex_v, pos_x, pos_y, pos_z)
    # Note: pos is bottom-left-back corner of the part in the statue
    
    parts = [
        # Head (8x8x8) - Top
        {"w": 8, "h": 8, "d": 8, "u": 0, "v": 0, "x": 4, "y": 24, "z": 2, "overlay_u": 32, "overlay_v": 0},
        # Body (8x12x4) - Center
        {"w": 8, "h": 12, "d": 4, "u": 16, "v": 16, "x": 4, "y": 12, "z": 4, "overlay_u": 16, "overlay_v": 32},
        # Right Arm (4x12x4) - Left side of statue
        {"w": 4, "h": 12, "d": 4, "u": 40, "v": 16, "x": 0, "y": 12, "z": 4, "overlay_u": 40, "overlay_v": 32},
        # Left Arm (4x12x4) - Right side of statue
        {"w": 4, "h": 12, "d": 4, "u": 32, "v": 48, "x": 12, "y": 12, "z": 4, "overlay_u": 48, "overlay_v": 48},
        # Right Leg (4x12x4) - Left side of statue
        {"w": 4, "h": 12, "d": 4, "u": 0, "v": 16, "x": 4, "y": 0, "z": 4, "overlay_u": 0, "overlay_v": 32},
        # Left Leg (4x12x4) - Right side of statue
        {"w": 4, "h": 12, "d": 4, "u": 16, "v": 48, "x": 8, "y": 0, "z": 4, "overlay_u": 0, "overlay_v": 48},
    ]

    for part in parts:
        w, h, d = part["w"], part["h"], part["d"]
        base_u, base_v = part["u"], part["v"]
        ox, oy, oz = part["x"], part["y"], part["z"] # Origin of the part
        
        # Texture layout offsets for a box:
        # Top: (d, 0) size (w, d)
        # Bottom: (d + w, 0) size (w, d)
        # Right: (0, d) size (d, h)
        # Front: (d, d) size (w, h)
        # Left: (d + w, d) size (d, h)
        # Back: (d + w + d, d) size (w, h)
        
        faces = [
            # (face_name, u_off, v_off, width_on_tex, height_on_tex, map_func)
            # map_func takes (u, v) on texture and returns (x, y, z) relative to part origin
            
            # Front (z=d-1)
            ("front", d, d, w, h, lambda u, v: (u, h - 1 - v, d - 1)),
            # Back (z=0)
            ("back", d + w + d, d, w, h, lambda u, v: (w - 1 - u, h - 1 - v, 0)),
            # Right (x=0) - Viewer's left
            ("right", 0, d, d, h, lambda u, v: (0, h - 1 - v, u)), # u maps to z? No, u is depth. 
            # Texture Right face: left side of the cube. 
            # If we look at front, Right face is on the left (x=0).
            # Texture u goes from back to front? 
            # Standard: Right face is at x=0. u=0 is back, u=d-1 is front.
            # Let's verify standard skin mapping.
            # Right face texture: (0, d) to (d, d+h). 
            # It maps to the right side of the body part (from the character's perspective), which is x=w-1?
            # No, "Right Arm" means the arm on the right side of the body.
            # But in the texture, "Right" face usually means the face pointing Right (x+).
            # Let's stick to standard unfolding.
            # Box unfolding:
            #  Top
            # Right Front Left Back
            #  Bottom
            
            # Right Face (x=w-1)
            ("right_face", 0, d, d, h, lambda u, v: (w - 1, h - 1 - v, d - 1 - u)), 
            # Wait, this is tricky. Let's assume standard mapping:
            # Face Right (Outer Right of Right Arm, Inner Right of Left Arm? No.)
            # Let's just map all 6 faces.
            
            # Top (y=h-1)
            ("top", d, 0, w, d, lambda u, v: (u, h - 1, d - 1 - v)),
            # Bottom (y=0)
            ("bottom", d + w, 0, w, d, lambda u, v: (w - 1 - u, 0, v)),
            # Right (x=w-1)
            ("right", d + w, d, d, h, lambda u, v: (w - 1, h - 1 - v, d - 1 - u)), # This is actually Left face in texture layout usually?
            # Let's re-verify texture layout.
            # 1.8 Skin:
            # [Right] [Front] [Left] [Back]
            # x: 0..d  d..d+w  d+w..d+w+d  d+w+d..d+w+d+w
            
            # So:
            # 0: Right Face (x=0 for Right Arm? No, Right Face of the cube)
            # If I am the character, my Right arm is on the right. The "Right" face of the arm points away from body.
            # Let's assume standard cuboid mapping:
            # Face 1: Right (x=0? or x=w?)
            # Face 2: Front (z=front)
            # Face 3: Left
            # Face 4: Back
            
            # Correct 1.8 mapping:
            # (u, v)
            # Top: (d, 0)
            # Bottom: (d+w, 0)
            # Right (x=max): (0, d) ? No, usually Right is x=min or x=max depending on perspective.
            # Let's use the "Front" as anchor. Front is (d, d).
            # To the left of Front (in texture) is Right Face. (0, d).
            # To the right of Front (in texture) is Left Face. (d+w, d).
            # To the right of Left is Back. (d+w+d, d).
            
            # So:
            # Texture Right (0, d) -> Physical Right (x=w-1)? Or Physical Left (x=0)?
            # If Front is z=max.
            # Then Right of Front is x=max (Viewer's right).
            # But in texture, "Right" is to the left of "Front".
            # So (0, d) is likely the face at x=0 (Viewer's Left).
            
             # Face at x=0 (Left from viewer, Right from character)
            ("face_x0", 0, d, d, h, lambda u, v: (0, h - 1 - v, u)), # z goes 0..d
            
            # Face at z=d-1 (Front)
            ("face_z_front", d, d, w, h, lambda u, v: (u, h - 1 - v, d - 1)),
            
            # Face at x=w-1 (Right from viewer, Left from character)
            ("face_xw", d + w, d, d, h, lambda u, v: (w - 1, h - 1 - v, d - 1 - u)), # z goes d..0?
            
            # Face at z=0 (Back)
            ("face_z_back", d + w + d, d, w, h, lambda u, v: (w - 1 - u, h - 1 - v, 0)),
        ]
        
        # Process Base Layer
        for name, u_off, v_off, fw, fh, map_func in faces:
            for u in range(fw):
                for v in range(fh):
                    color = pixels[base_u + u_off + u, base_v + v_off + v]
                    bx, by, bz = map_func(u, v)
                    block = find_closest_block(color, BLOCK_PALETTE)
                    if block != "minecraft:air":
                        statue_blocks[(ox + bx, oy + by, oz + bz)] = block

        # Process Overlay Layer
        # Overlay layout is identical to base, just offset
        overlay_u, overlay_v = part["overlay_u"], part["overlay_v"]
        for name, u_off, v_off, fw, fh, map_func in faces:
            for u in range(fw):
                for v in range(fh):
                    color = pixels[overlay_u + u_off + u, overlay_v + v_off + v]
                    bx, by, bz = map_func(u, v)
                    block = find_closest_block(color, BLOCK_PALETTE)
                    if block != "minecraft:air":
                        # Overlay replaces base if not transparent
                        # Or we could put it in front?
                        # For a statue, we usually just replace the block.
                        # Or if we want 3D depth, we could add a layer?
                        # "Skin to 3D model mapping" usually implies 1:1 block to pixel.
                        # But overlays are often "puffed" out.
                        # If we puff it out, we need to adjust coordinates.
                        # Let's try to "puff" it out by 1 block if it's an overlay.
                        
                        # Puff logic:
                        # If face is Front (z=d-1), puff to z=d
                        # If face is Back (z=0), puff to z=-1
                        # If face is x=0, puff to x=-1
                        # If face is x=w-1, puff to x=w
                        # Top/Bottom puff y.
                        
                        px, py, pz = ox + bx, oy + by, oz + bz
                        
                        # Determine puff direction based on face
                        if name == "face_z_front": pz += 1
                        elif name == "face_z_back": pz -= 1
                        elif name == "face_x0": px -= 1
                        elif name == "face_xw": px += 1
                        elif name == "top": py += 1
                        elif name == "bottom": py -= 1
                        
                        statue_blocks[(px, py, pz)] = block

    return statue_blocks

def generate_litematic(statue_blocks, output_path):
    if not statue_blocks:
        print("No blocks generated!")
        return

    # Determine bounds
    min_x = min(k[0] for k in statue_blocks)
    max_x = max(k[0] for k in statue_blocks)
    min_y = min(k[1] for k in statue_blocks)
    max_y = max(k[1] for k in statue_blocks)
    min_z = min(k[2] for k in statue_blocks)
    max_z = max(k[2] for k in statue_blocks)
    
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    length = max_z - min_z + 1
    
    print(f"Statue Dimensions: {width}x{height}x{length}")
    
    reg = litemapy.Region(0, 0, 0, width, height, length)
    schem = litemapy.Schematic(name="SkinStatue", author="Antigravity", regions={ "Main": reg })
    
    for (x, y, z), block_id in statue_blocks.items():
        # Adjust to region coordinates (0,0,0 based)
        rx = x - min_x
        ry = y - min_y
        rz = z - min_z
        
        try:
            reg.setblock(rx, ry, rz, litemapy.BlockState(block_id))
        except Exception as e:
            print(f"Error setting block {block_id} at {rx},{ry},{rz}: {e}")

    schem.save(output_path)
    print(f"Saved litematic to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python skin_to_litematic.py <skin.png> [output.litematic]")
        sys.exit(1)
        
    skin_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else skin_path.replace(".png", ".litematic")
    
    print(f"Loading skin from {skin_path}...")
    img = load_skin(skin_path)
    
    print("Loading block palette...")
    BLOCK_PALETTE = get_block_palette()
    print(f"Loaded {len(BLOCK_PALETTE)} blocks in palette.")
    
    print("Building statue data...")
    data = build_statue_data(img)
    
    print("Generating litematic...")
    generate_litematic(data, output_path)
