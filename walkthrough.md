# Minecraft Skin to Litematica Converter Walkthrough

This project converts Minecraft skin files (`.png`) into Litematica schematics (`.litematic`) that can be loaded into Minecraft to build 3D statues.

## Prerequisites

Ensure you have the required libraries installed:
```bash
pip install litemapy Pillow
```

## Usage

First, fetch the block palette:
```bash
python fetch_palette.py
```

Then, run the conversion script with the path to your skin file:

```bash
python skin_to_litematic.py <path_to_skin.png> [output_filename.litematic]
```

### Example
```bash
python skin_to_litematic.py pipiyo000.png
```
This will generate `pipiyo000.litematic`.

## Verification

You can verify the generated file using the provided verification script:

```bash
python verify_litematic.py pipiyo000.litematic
```

### Sample Output
```
Successfully loaded pipiyo000.litematic
Region Name: Main
Dimensions: 18x34x10
Total non-air blocks: 1523
Block distribution:
  minecraft:white_wool: 1511
  minecraft:white_concrete: 12
```

## Features
- Supports standard 64x64 Minecraft skins.
- Handles both the Base Layer and the Overlay Layer (Hat, Jacket, etc.).
- Maps skin colors to a palette of Minecraft blocks (Wool, Concrete, Terracotta).
- Generates a 3D statue structure.
