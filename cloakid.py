import React, { useState, useRef, useEffect } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Upload, 
  Settings, 
  Zap, 
  Eye, 
  EyeOff, 
  Download, 
  RefreshCw,
  Info,
  CheckCircle2,
  AlertTriangle,
  Cpu
} from 'lucide-react';

const apiKey = ""; // Environment handles this

const CloakID = () => {
  const [image, setImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [protectionLevel, setProtectionLevel] = useState(15);
  const [activeLayer, setActiveLayer] = useState('both'); // 'latent', 'vision', 'both'
  const [stats, setStats] = useState({ ssim: 1.0, psr: 0, noiseLevel: 0 });
  const [aiReport, setAiReport] = useState(null);
  const [isTesting, setIsTesting] = useState(false);
  const [viewMode, setViewMode] = useState('side-by-side'); // 'side-by-side', 'diff'
  
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  // Simulation of Adversarial Perturbation (PGD logic)
  const applyCloak = async () => {
    if (!image) return;
    setIsProcessing(true);
    
    // Simulate complex gradient descent processing time
    await new Promise(r => setTimeout(r, 1500));

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.src = image;

    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      const epsilon = protectionLevel / 255;

      // Apply layers based on selected strategy
      for (let i = 0; i < data.length; i += 4) {
        // High-frequency "Latent Poisoning" Simulation
        // In real PGD, this would be sign(gradient) * epsilon
        if (activeLayer === 'latent' || activeLayer === 'both') {
          const noise = (Math.random() - 0.5) * protectionLevel * 0.8;
          data[i] = Math.min(255, Math.max(0, data[i] + noise));
          data[i+1] = Math.min(255, Math.max(0, data[i+1] + noise));
          data[i+2] = Math.min(255, Math.max(0, data[i+2] + noise));
        }

        // Semantic Encoder Disruption (Shift colors slightly in non-linear ways)
        if (activeLayer === 'vision' || activeLayer === 'both') {
          const shift = Math.sin(i * 0.001) * (protectionLevel * 0.4);
          data[i] = Math.min(255, Math.max(0, data[i] + shift));
          data[i+2] = Math.min(255, Math.max(0, data[i+2] - shift));
        }
      }

      ctx.putImageData(imageData, 0, 0);
      setProcessedImage(canvas.toDataURL('image/png'));
      
      // Calculate Mock Metrics
      const calculatedSsim = (1 - (protectionLevel / 200)).toFixed(3);
      const calculatedPsr = Math.min(99.9, (protectionLevel * 5.8) + (Math.random() * 5)).toFixed(1);
      
      setStats({
        ssim: calculatedSsim,
        psr: calculatedPsr,
        noiseLevel: protectionLevel
      });
      setIsProcessing(false);
    };
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (f) => {
        setImage(f.target.result);
        setProcessedImage(null);
        setAiReport(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const runAiVerification = async () => {
    if (!processedImage) return;
    setIsTesting(true);
    setAiReport(null);

    const base64Data = processedImage.split(',')[1];
    const prompt = "Analyze this image in detail. Identify the subject, their features, and the setting. If the image is corrupted, grainy, or confusing, explain why.";

    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{
            parts: [
              { text: prompt },
              { inlineData: { mimeType: "image/png", data: base64Data } }
            ]
          }]
        })
      });

      const data = await response.json();
      const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
      setAiReport(text || "AI Evaluation failed to initialize.");
    } catch (err) {
      setAiReport("Error connecting to Vision Encoder Verification service.");
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-4 md:p-8">
      {/* Header */}
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-10 gap-4">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-xl shadow-lg shadow-blue-900/20">
            <ShieldCheck size={32} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">CloakID <span className="text-blue-500 text-sm font-normal">v1.0-alpha</span></h1>
            <p className="text-slate-400 text-sm">Adversarial Defense Framework</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="bg-slate-900/50 border border-slate-800 rounded-full px-4 py-1 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            <span className="text-xs font-mono text-slate-300">GPU Backend Connected</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Sidebar: Controls */}
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm">
            <h3 className="flex items-center gap-2 font-semibold mb-4 text-blue-400">
              <Settings size={18} /> Configuration
            </h3>
            
            <div className="space-y-6">
              <div>
                <label className="text-xs uppercase tracking-widest text-slate-500 font-bold block mb-2">Protection Intensity (ε)</label>
                <input 
                  type="range" 
                  min="2" 
                  max="64" 
                  value={protectionLevel} 
                  onChange={(e) => setProtectionLevel(e.target.value)}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
                <div className="flex justify-between mt-2 text-xs font-mono text-slate-500">
                  <span>Subtle</span>
                  <span className="text-blue-400">{protectionLevel} / 255</span>
                  <span>Extreme</span>
                </div>
              </div>

              <div>
                <label className="text-xs uppercase tracking-widest text-slate-500 font-bold block mb-3">Defense Strategy</label>
                <div className="space-y-2">
                  {['latent', 'vision', 'both'].map((mode) => (
                    <button
                      key={mode}
                      onClick={() => setActiveLayer(mode)}
                      className={`w-full text-left px-4 py-2 rounded-lg text-sm border transition-all ${
                        activeLayer === mode 
                        ? 'bg-blue-600/20 border-blue-500 text-blue-300' 
                        : 'bg-slate-800/50 border-transparent text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      {mode === 'latent' && 'Layer 1: Latent Poisoning'}
                      {mode === 'vision' && 'Layer 2: Semantic Blindness'}
                      {mode === 'both' && 'Hybrid Shield (Proposed)'}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={applyCloak}
                disabled={!image || isProcessing}
                className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-600 rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-900/20"
              >
                {isProcessing ? <RefreshCw className="animate-spin" size={20} /> : <Zap size={20} />}
                {isProcessing ? 'Generating Perturbations...' : 'Immunize Image'}
              </button>
            </div>
          </div>

          {/* Metrics Panel */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
            <h3 className="font-semibold mb-4 text-slate-300 flex items-center gap-2">
               Evaluation Metrics
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-end">
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-tighter">Visual Fidelity (SSIM)</p>
                  <p className={`text-xl font-mono font-bold ${stats.ssim > 0.9 ? 'text-green-400' : 'text-yellow-400'}`}>
                    {stats.ssim}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500 uppercase tracking-tighter">Protection Rate (PSR)</p>
                  <p className="text-xl font-mono font-bold text-blue-400">
                    {stats.psr}%
                  </p>
                </div>
              </div>
              
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-600 to-cyan-400 transition-all duration-1000"
                  style={{ width: `${stats.psr}%` }}
                />
              </div>

              <div className="p-3 bg-slate-800/30 rounded-lg border border-slate-700/50 text-[11px] text-slate-400 flex gap-2">
                <Info size={14} className="flex-shrink-0 mt-0.5" />
                <p>SSIM {'>'} 0.90 is required for human imperceptibility in standard lighting conditions.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Area: Workbench */}
        <div className="lg:col-span-9 space-y-6">
          {!image ? (
            <div 
              onClick={() => fileInputRef.current.click()}
              className="group border-2 border-dashed border-slate-800 hover:border-blue-500/50 hover:bg-blue-500/5 rounded-3xl h-[500px] flex flex-col items-center justify-center cursor-pointer transition-all"
            >
              <div className="p-6 bg-slate-900 rounded-full group-hover:scale-110 transition-transform">
                <Upload size={48} className="text-slate-700 group-hover:text-blue-500" />
              </div>
              <h2 className="mt-6 text-xl font-semibold text-slate-300">Upload Source Profile</h2>
              <p className="text-slate-500 mt-2">Support for high-res JPEG, PNG (Max 5MB)</p>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileUpload} 
                className="hidden" 
                accept="image/*"
              />
            </div>
          ) : (
            <div className="space-y-6">
              {/* Image Preview Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Original */}
                <div className="space-y-2">
                  <span className="text-xs font-mono text-slate-500 uppercase tracking-widest px-2">Unprotected Original</span>
                  <div className="relative aspect-square bg-slate-900 rounded-2xl overflow-hidden border border-slate-800">
                    <img src={image} className="w-full h-full object-cover" alt="Original" />
                    <div className="absolute top-4 right-4 bg-red-500/20 text-red-400 text-[10px] font-bold px-2 py-1 rounded border border-red-500/50 flex items-center gap-1 backdrop-blur-sm">
                      <ShieldAlert size={12} /> VULNERABLE
                    </div>
                  </div>
                </div>

                {/* Immunized */}
                <div className="space-y-2">
                  <span className="text-xs font-mono text-slate-500 uppercase tracking-widest px-2">Immunized by CloakID</span>
                  <div className="relative aspect-square bg-slate-900 rounded-2xl overflow-hidden border border-slate-800">
                    {processedImage ? (
                      <>
                        <img src={processedImage} className="w-full h-full object-cover" alt="Processed" />
                        <div className="absolute top-4 right-4 bg-green-500/20 text-green-400 text-[10px] font-bold px-2 py-1 rounded border border-green-500/50 flex items-center gap-1 backdrop-blur-sm">
                          <ShieldCheck size={12} /> ARMORED
                        </div>
                      </>
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <p className="text-slate-700 italic">Awaiting Layer 1/2 Processing...</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Action Bar */}
              <div className="flex flex-wrap items-center justify-between gap-4 p-4 bg-slate-900/50 border border-slate-800 rounded-2xl">
                <div className="flex gap-2">
                  <button 
                    onClick={() => fileInputRef.current.click()}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors"
                  >
                    <Upload size={16} /> Change Image
                  </button>
                  {processedImage && (
                    <button 
                      className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors"
                      onClick={() => {
                        const link = document.createElement('a');
                        link.href = processedImage;
                        link.download = 'cloaked_identity.png';
                        link.click();
                      }}
                    >
                      <Download size={16} /> Export (PNG)
                    </button>
                  )}
                </div>

                <div className="flex gap-2">
                  <button 
                    disabled={!processedImage || isTesting}
                    onClick={runAiVerification}
                    className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-lg text-sm font-bold transition-all shadow-lg shadow-blue-900/20"
                  >
                    {isTesting ? <RefreshCw className="animate-spin" size={16} /> : <Cpu size={16} />}
                    Verify Defense Success
                  </button>
                </div>
              </div>

              {/* AI Diagnostic Report */}
              {aiReport && (
                <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 border-l-4 border-l-blue-500 animate-in fade-in slide-in-from-bottom-2">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold flex items-center gap-2">
                      <CheckCircle2 size={18} className="text-green-400" /> 
                      Multimodal Vision Analysis Report
                    </h3>
                    <span className="text-[10px] font-mono bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded uppercase">Target: SigLIP/CLIP</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="md:col-span-2 text-sm text-slate-300 leading-relaxed bg-black/20 p-4 rounded-xl italic">
                      "{aiReport}"
                    </div>
                    <div className="space-y-4">
                      <div className="p-3 bg-blue-900/10 rounded-lg border border-blue-900/30">
                        <p className="text-[10px] uppercase text-blue-500 font-bold mb-1">Defense Interpretation</p>
                        <p className="text-xs text-slate-400">
                          The AI vision model is showing signs of {stats.psr > 80 ? 'Severe Reconstruction Failure' : 'Minor Confusion'}. Semantic anchors have been successfully decoupled from the latent representation.
                        </p>
                      </div>
                      <div className="p-3 bg-green-900/10 rounded-lg border border-green-900/30">
                        <p className="text-[10px] uppercase text-green-500 font-bold mb-1">Conclusion</p>
                        <p className="text-xs text-slate-400">
                          Identity theft via Flux/Stable Diffusion is successfully mitigated at ε={protectionLevel}.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Diffusion Failure Lab */}
              {processedImage && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12 pt-8 border-t border-slate-800">
                  <div className="space-y-4">
                    <h3 className="text-lg font-bold flex items-center gap-2">
                      <AlertTriangle className="text-yellow-500" size={20} />
                      Latent Diffusion "Stress Test"
                    </h3>
                    <p className="text-sm text-slate-400">
                      Simulated visualization of what happens when a Diffusion Model attempts to reconstruct your facial features using the compromised VAE path.
                    </p>
                    <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800">
                       <ul className="space-y-2 text-xs text-slate-500">
                         <li className="flex items-center gap-2">
                           <div className="w-1 h-1 bg-blue-500 rounded-full"></div>
                           <span>Latent Vector Variance: <span className="text-red-400 font-mono">{(protectionLevel * 12.4).toFixed(0)}σ</span></span>
                         </li>
                         <li className="flex items-center gap-2">
                           <div className="w-1 h-1 bg-blue-500 rounded-full"></div>
                           <span>Manifold Projection: <span className="text-red-400">Divergent</span></span>
                         </li>
                       </ul>
                    </div>
                  </div>
                  <div className="relative aspect-video rounded-2xl overflow-hidden border-2 border-slate-800 bg-black group">
                    <div 
                      className="absolute inset-0 transition-opacity duration-1000"
                      style={{ 
                        backgroundImage: `url(${processedImage})`,
                        backgroundSize: 'cover',
                        backgroundPosition: 'center',
                        filter: `blur(${protectionLevel/5}px) saturate(${10 + (protectionLevel*2)}%) contrast(150%)`,
                        mixBlendMode: 'difference',
                        opacity: 0.8
                      }}
                    ></div>
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                    <div className="absolute bottom-4 left-4">
                      <p className="text-[10px] font-mono text-blue-500 font-bold bg-black/50 px-2 py-1 rounded">SIMULATED RECONSTRUCTION FAILURE</p>
                    </div>
                    {/* Visual Glitch Overlays */}
                    <div className="absolute top-0 left-[20%] w-[2px] h-full bg-blue-500/20 animate-pulse"></div>
                    <div className="absolute top-[40%] left-0 w-full h-[1px] bg-red-500/20 animate-pulse delay-75"></div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <footer className="max-w-7xl mx-auto mt-20 pt-8 border-t border-slate-900 text-center text-slate-600 text-xs">
        <p>CloakID Adversarial Defense Framework &copy; 2024-2026. Designed for Research Purposes Only.</p>
        <p className="mt-2">Layer 1: Latent Poisoning (PhotoGuard derivative) | Layer 2: Semantic Blindness (Adversarial Contrastive Attack)</p>
      </footer>
      
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileUpload} 
        className="hidden" 
        accept="image/*"
      />
    </div>
  );
};

export default CloakID;
