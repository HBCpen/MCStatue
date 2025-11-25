import React, { useRef, useEffect, useMemo } from 'react';
import { useFrame, useLoader } from '@react-three/fiber';
import { TextureLoader, NearestFilter, SRGBColorSpace } from 'three';
import * as THREE from 'three';

const SkinPart = ({ texture, width, height, depth, u, v, position, overlayU, overlayV }) => {
    const geometry = useMemo(() => {
        const geo = new THREE.BoxGeometry(width, height, depth);
        const uvAttribute = geo.attributes.uv;

        // Helper to set UVs for a face
        // faceIndex: 0=right, 1=left, 2=top, 3=bottom, 4=front, 5=back
        // textureU, textureV: bottom-left of the face in texture (pixels)
        // w, h: width and height of the face in texture (pixels)
        const setFaceUV = (faceIndex, textureU, textureV, w, h) => {
            // Standard BoxGeometry UV mapping:
            // 0: (0, 1), 1: (1, 1), 2: (0, 0), 3: (1, 0)
            // We need to map these to our texture coordinates

            // Texture coordinates are 0..1, origin bottom-left
            // Minecraft skin origin is top-left in most editors, but Three.js texture origin is bottom-left.
            // Let's assume standard bottom-left origin for calculations, or flip Y.
            // Standard skin: Head Top is at (8, 0) to (16, 8) in top-left coordinates?
            // No, usually:
            // Head:
            // Top: (8, 0) size 8x8
            // Bottom: (16, 0) size 8x8
            // Right: (0, 8) size 8x8
            // Front: (8, 8) size 8x8
            // Left: (16, 8) size 8x8
            // Back: (24, 8) size 8x8
            // (Coordinates are x, y from top-left)

            // In Three.js (0,0) is bottom-left.
            // So y_three = 64 - y_skin.

            const texW = 64;
            const texH = 64;

            const u0 = textureU / texW;
            const v0 = (64 - (textureV + h)) / texH; // Bottom of face
            const u1 = (textureU + w) / texW;
            const v1 = (64 - textureV) / texH; // Top of face

            // BoxGeometry faces are defined by 4 vertices.
            // We need to verify vertex order.
            // Usually: Top-Left, Top-Right, Bottom-Left, Bottom-Right?
            // Let's try standard mapping.

            const offset = faceIndex * 4;

            // 0: top-left (u0, v1)
            // 1: top-right (u1, v1)
            // 2: bottom-left (u0, v0)
            // 3: bottom-right (u1, v0)

            uvAttribute.setXY(offset + 0, u0, v1);
            uvAttribute.setXY(offset + 1, u1, v1);
            uvAttribute.setXY(offset + 2, u0, v0);
            uvAttribute.setXY(offset + 3, u1, v0);
        };

        // Right (x+) -> Face 0
        setFaceUV(0, u + depth, v + depth, depth, height); // Wait, standard layout check
        // Left (x-) -> Face 1
        setFaceUV(1, u + depth + width + depth, v + depth, depth, height); // ?

        // Let's use the standard unfolding:
        // Top: (u + depth, v) size (width, depth)
        // Bottom: (u + depth + width, v) size (width, depth)
        // Right: (u, v + depth) size (depth, height)
        // Front: (u + depth, v + depth) size (width, height)
        // Left: (u + depth + width, v + depth) size (depth, height)
        // Back: (u + depth + width + depth, v + depth) size (width, height)

        // BoxGeometry Faces:
        // 0: Right (x+)
        // 1: Left (x-)
        // 2: Top (y+)
        // 3: Bottom (y-)
        // 4: Front (z+)
        // 5: Back (z-)

        // Mapping:
        // Right Face (x+) corresponds to Left side of texture? 
        // If I look at the model, the "Right" arm is on my left.
        // The "Right" face of the box is x+.
        // In skin layout, "Right" usually means the right side of the character (viewer's left).
        // Let's assume standard mapping:
        // Right (x+): Left Face in texture? (u + depth + width, v + depth)
        // Left (x-): Right Face in texture? (u, v + depth)
        // Top (y+): Top in texture (u + depth, v)
        // Bottom (y-): Bottom in texture (u + depth + width, v)
        // Front (z+): Front in texture (u + depth, v + depth)
        // Back (z-): Back in texture (u + depth + width + depth, v + depth)

        // Let's try this:
        setFaceUV(0, u + depth + width, v + depth, depth, height); // Right (x+) -> Texture Left
        setFaceUV(1, u, v + depth, depth, height); // Left (x-) -> Texture Right
        setFaceUV(2, u + depth, v, width, depth); // Top (y+) -> Texture Top
        setFaceUV(3, u + depth + width, v, width, depth); // Bottom (y-) -> Texture Bottom
        setFaceUV(4, u + depth, v + depth, width, height); // Front (z+) -> Texture Front
        setFaceUV(5, u + depth + width + depth, v + depth, width, height); // Back (z-) -> Texture Back

        uvAttribute.needsUpdate = true;
        return geo;
    }, [width, height, depth, u, v]);

    const overlayGeometry = useMemo(() => {
        if (overlayU === undefined) return null;
        const geo = new THREE.BoxGeometry(width + 0.5, height + 0.5, depth + 0.5); // Slightly larger
        const uvAttribute = geo.attributes.uv;

        // Same mapping logic but with overlay offsets
        const setFaceUV = (faceIndex, textureU, textureV, w, h) => {
            const texW = 64;
            const texH = 64;
            const u0 = textureU / texW;
            const v0 = (64 - (textureV + h)) / texH;
            const u1 = (textureU + w) / texW;
            const v1 = (64 - textureV) / texH;
            const offset = faceIndex * 4;
            uvAttribute.setXY(offset + 0, u0, v1);
            uvAttribute.setXY(offset + 1, u1, v1);
            uvAttribute.setXY(offset + 2, u0, v0);
            uvAttribute.setXY(offset + 3, u1, v0);
        };

        setFaceUV(0, overlayU + depth + width, overlayV + depth, depth, height);
        setFaceUV(1, overlayU, overlayV + depth, depth, height);
        setFaceUV(2, overlayU + depth, overlayV, width, depth);
        setFaceUV(3, overlayU + depth + width, overlayV, width, depth);
        setFaceUV(4, overlayU + depth, overlayV + depth, width, height);
        setFaceUV(5, overlayU + depth + width + depth, overlayV + depth, width, height);

        uvAttribute.needsUpdate = true;
        return geo;
    }, [width, height, depth, overlayU, overlayV]);

    return (
        <group position={position}>
            <mesh geometry={geometry}>
                <meshStandardMaterial map={texture} transparent alphaTest={0.5} />
            </mesh>
            {overlayGeometry && (
                <mesh geometry={overlayGeometry}>
                    <meshStandardMaterial map={texture} transparent side={THREE.DoubleSide} alphaTest={0.1} />
                </mesh>
            )}
        </group>
    );
};

const SkinViewer = ({ skinUrl }) => {
    const texture = useLoader(TextureLoader, skinUrl);

    useEffect(() => {
        if (texture) {
            texture.magFilter = NearestFilter;
            texture.minFilter = NearestFilter;
            texture.colorSpace = SRGBColorSpace;
            texture.needsUpdate = true;
        }
    }, [texture]);

    // Define parts (dimensions and texture offsets)
    // Coordinates relative to center
    // Head: 8x8x8
    // Body: 8x12x4
    // Arms: 4x12x4
    // Legs: 4x12x4

    return (
        <group>
            {/* Head */}
            <SkinPart
                texture={texture} width={8} height={8} depth={8}
                u={0} v={0} overlayU={32} overlayV={0}
                position={[0, 10, 0]} // 12 (body) / 2 + 4 (head) / 2 = 6 + 4 = 10
            />

            {/* Body */}
            <SkinPart
                texture={texture} width={8} height={12} depth={4}
                u={16} v={16} overlayU={16} overlayV={32}
                position={[0, 0, 0]}
            />

            {/* Right Arm (Viewer's Left) */}
            <SkinPart
                texture={texture} width={4} height={12} depth={4}
                u={40} v={16} overlayU={40} overlayV={32}
                position={[-6, 0, 0]} // -4 (body/2) - 2 (arm/2) = -6
            />

            {/* Left Arm (Viewer's Right) */}
            <SkinPart
                texture={texture} width={4} height={12} depth={4}
                u={32} v={48} overlayU={48} overlayV={48}
                position={[6, 0, 0]}
            />

            {/* Right Leg (Viewer's Left) */}
            <SkinPart
                texture={texture} width={4} height={12} depth={4}
                u={0} v={16} overlayU={0} overlayV={32}
                position={[-2, -12, 0]} // -2 (offset), -6 (body/2) - 6 (leg/2) = -12
            />

            {/* Left Leg (Viewer's Right) */}
            <SkinPart
                texture={texture} width={4} height={12} depth={4}
                u={16} v={48} overlayU={0} overlayV={48}
                position={[2, -12, 0]}
            />
        </group>
    );
};

export default SkinViewer;
