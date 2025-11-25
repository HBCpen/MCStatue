import React, { useState, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stage } from '@react-three/drei';
import SkinViewer from './components/SkinViewer';
import './index.css';

function App() {
  const [skinFile, setSkinFile] = useState(null);
  const [skinUrl, setSkinUrl] = useState(null);
  const [converting, setConverting] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSkinFile(file);
      const url = URL.createObjectURL(file);
      setSkinUrl(url);
    }
  };

  const handleConvert = async () => {
    if (!skinFile) return;

    setConverting(true);
    const formData = new FormData();
    formData.append('file', skinFile);

    try {
      const response = await fetch('http://localhost:8000/convert', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = skinFile.name.replace('.png', '.litematic');
        document.body.appendChild(a);
        a.click();
        a.remove();
      } else {
        console.error('Conversion failed');
        alert('Conversion failed!');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error connecting to backend');
    } finally {
      setConverting(false);
    }
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <h1>MC Statue Converter</h1>
        <div className="control-group">
          <label className="file-input-label">
            Upload Skin
            <input type="file" accept=".png" onChange={handleFileChange} hidden />
          </label>
          <span className="file-name">{skinFile ? skinFile.name : "No file selected"}</span>
        </div>

        <button
          className="convert-btn"
          onClick={handleConvert}
          disabled={!skinFile || converting}
        >
          {converting ? "Converting..." : "Convert to Litematic"}
        </button>

        <div className="instructions">
          <p>1. Upload a 64x64 Minecraft Skin.</p>
          <p>2. Preview the 3D model.</p>
          <p>3. Convert to Litematica schematic.</p>
        </div>
      </div>

      <div className="viewer-container">
        <Canvas shadows camera={{ position: [20, 20, 20], fov: 50 }}>
          <Suspense fallback={null}>
            <Stage environment="city" intensity={0.6}>
              {skinUrl && <SkinViewer skinUrl={skinUrl} />}
            </Stage>
          </Suspense>
          <OrbitControls autoRotate />
        </Canvas>
        {!skinUrl && <div className="placeholder-text">Upload a skin to preview</div>}
      </div>
    </div>
  );
}

export default App;
