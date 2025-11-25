import csv
import json
import urllib.request
import sys

CSV_URL = "https://raw.githubusercontent.com/RandomGamingDev/mc_block_color_mapper/main/blockmodel_avgs.csv"
OUTPUT_FILE = "block_palette.json"

# Blocks to exclude (transparent, non-solid, or weird rendering)
EXCLUDED_KEYWORDS = [
    "glass", "pane", "door", "trapdoor", "fence", "gate", "sign", "button", "pressure_plate", 
    "rail", "torch", "lantern", "chain", "bars", "ladder", "vine", "plant", "flower", "sapling", 
    "mushroom", "fungus", "roots", "sprout", "grass", "fern", "dead_bush", "seagrass", "kelp", 
    "coral", "pickle", "candle", "cake", "brewing_stand", "cauldron", "hopper", "comparator", 
    "repeater", "lever", "tripwire", "hook", "daylight_detector", "scaffolding", "carpet", "snow", 
    "slab", "stairs", "wall", "leaves", "cobweb", "fire", "water", "lava", "portal", "structure", 
    "jigsaw", "command", "barrier", "light", "air", "void", "bed", "banner", "head", "skull",
    "shulker_box", "chest", "barrel", "lectern", "loom", "stonecutter", "grindstone", "smithing_table",
    "fletching_table", "cartography_table", "composter", "beehive", "bee_nest", "campfire", "bell",
    "piston", "observer", "dispenser", "dropper", "spawner", "beacon", "conduit", "end_rod", "dragon_egg",
    "anvil", "enchanting_table", "end_portal_frame", "pot", "stem", "bamboo", "pointed_dripstone", 
    "amethyst_cluster", "bud", "azalea", "dripleaf", "sculk_vein", "sculk_sensor", "sculk_shrieker",
    "glow_lichen", "hanging_roots", "spore_blossom"
]

def fetch_and_process_palette():
    print(f"Downloading CSV from {CSV_URL}...")
    try:
        with urllib.request.urlopen(CSV_URL) as response:
            csv_data = response.read().decode('utf-8').splitlines()
    except Exception as e:
        print(f"Error downloading CSV: {e}")
        sys.exit(1)

    print("Processing data...")
    palette = {}
    reader = csv.DictReader(csv_data)
    
    count = 0
    for row in reader:
        block_name = row['block_name']
        
        # Filter out unwanted blocks
        if any(keyword in block_name for keyword in EXCLUDED_KEYWORDS):
            continue
            
        # Filter out transparency (alpha < 255)
        try:
            alpha = float(row['a'])
            if alpha < 255:
                continue
                
            r = int(float(row['r']))
            g = int(float(row['g']))
            b = int(float(row['b']))
            
            # Key is RGB tuple string, Value is block ID
            # We use a string key for JSON compatibility, will parse back to tuple in python
            key = f"{r},{g},{b}"
            palette[key] = f"minecraft:{block_name}"
            count += 1
            
        except ValueError:
            continue

    print(f"Found {count} suitable solid blocks.")
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(palette, f, indent=2)
        
    print(f"Saved palette to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_and_process_palette()
