import sys
import litemapy

def verify_litematic(path):
    try:
        schem = litemapy.Schematic.load(path)
        print(f"Successfully loaded {path}")
        
        reg = list(schem.regions.values())[0]
        print(f"Region Name: {list(schem.regions.keys())[0]}")
        print(f"Dimensions: {reg.width}x{reg.height}x{reg.length}")
        
        block_count = 0
        blocks = {}
        
        for x in range(reg.width):
            for y in range(reg.height):
                for z in range(reg.length):
                    block = reg.getblock(x, y, z)
                    if block.blockid != "minecraft:air":
                        block_count += 1
                        blocks[block.blockid] = blocks.get(block.blockid, 0) + 1
                        
        print(f"Total non-air blocks: {block_count}")
        print("Block distribution:")
        for block, count in blocks.items():
            print(f"  {block}: {count}")
            
        if block_count == 0:
            print("ERROR: Schematic is empty!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_litematic.py <file.litematic>")
        sys.exit(1)
        
    verify_litematic(sys.argv[1])
