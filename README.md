# Minecraft Skin to Litematica Converter

A Python tool to convert Minecraft skin files (`.png`) into Litematica schematics (`.litematic`). This allows you to easily build 3D statues of players in your Minecraft world using the Litematica mod.

## Features

- **Standard Skin Support**: Works with standard 64x64 Minecraft skins.
- **Layer Support**: accurately converts both the base layer and the overlay layer (hats, jackets, etc.).
- **3D Mapping**: Converts the 2D skin layout into a correct 3D statue structure.
- **Smart Color Mapping**: Automatically maps skin pixel colors to the closest matching Minecraft block using a comprehensive palette.
- **Dynamic Palette**: Fetches the latest block color data to ensure accurate representation using a wide variety of blocks (Wool, Concrete, Terracotta, etc.).

## Prerequisites

- Python 3.x
- `litemapy` library
- `Pillow` library

## Installation

1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install litemapy Pillow
   ```

## Usage

### 1. Initialize Block Palette
Before running the converter for the first time, you need to fetch the block color data:

```bash
python fetch_palette.py
```
This will generate a `block_palette.json` file containing color data for solid blocks.

### 2. Convert a Skin
Run the conversion script with the path to your skin file:

```bash
python skin_to_litematic.py <path_to_skin.png> [output_filename.litematic]
```

**Example:**
```bash
python skin_to_litematic.py pipiyo000.png
```
This will generate `pipiyo000.litematic` in the same directory.

## Verification
You can verify the contents of a generated schematic using the included verification script:

```bash
python verify_litematic.py <file.litematic>
```

## Web Interface

The project includes a modern web interface with a 3D preview.

### Prerequisites
- Node.js and npm

### Running the Web App

1. **Start the Backend**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Start the Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open your browser to the URL shown in the frontend terminal (usually `http://localhost:5173`).

## License
[MIT License](LICENSE)
