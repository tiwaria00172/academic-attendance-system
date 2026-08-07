import React, { useRef, useEffect, useState } from 'react';
import { Camera, RefreshCw, Sparkles, CheckCircle2, AlertCircle, ArrowRight, X } from 'lucide-react';

export default function ThreeAngleWebcamModal({ onComplete, onClose, studentName }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const [cameraActive, setCameraActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [step, setStep] = useState(1); // 1=Front, 2=Left, 3=Right, 4=Done/Uploading
  const [capturedFiles, setCapturedFiles] = useState({ front: null, left: null, right: null });
  const [previewUrls, setPreviewUrls] = useState({ front: null, left: null, right: null });

  useEffect(() => {
    let isMounted = true;
    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          // Request lower resolution — 640×480 is plenty for face encoding
          // and dramatically reduces server CPU time on Render free tier
          video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
        });
        if (isMounted && videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
          setCameraActive(true);
        }
      } catch (err) {
        if (isMounted) {
          setErrorMessage('Camera access denied or device not found. Please allow camera permissions on your phone/browser.');
        }
      }
    }
    startCamera();

    return () => {
      isMounted = false;
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop());
      }
    };
  }, []);

  const handleCapture = () => {
    const video = videoRef.current;
    if (!video) return;

    // Capture at 640×480 — sufficient for 128D face encoding, dramatically
    // faster to upload and process on Render's free-tier CPU
    const CAPTURE_W = 640;
    const CAPTURE_H = 480;
    const canvas = document.createElement('canvas');
    canvas.width  = CAPTURE_W;
    canvas.height = CAPTURE_H;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, CAPTURE_W, CAPTURE_H);

    // 0.85 quality — still excellent for face encoding, ~30% smaller file
    canvas.toBlob((blob) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);

      if (step === 1) {
        const file = new File([blob], `front_live_${Date.now()}.jpg`, { type: 'image/jpeg' });
        setCapturedFiles(prev => ({ ...prev, front: file }));
        setPreviewUrls(prev => ({ ...prev, front: url }));
        setStep(2);
      } else if (step === 2) {
        const file = new File([blob], `left_live_${Date.now()}.jpg`, { type: 'image/jpeg' });
        setCapturedFiles(prev => ({ ...prev, left: file }));
        setPreviewUrls(prev => ({ ...prev, left: url }));
        setStep(3);
      } else if (step === 3) {
        const file = new File([blob], `right_live_${Date.now()}.jpg`, { type: 'image/jpeg' });
        const finalFiles = { ...capturedFiles, right: file };
        setCapturedFiles(finalFiles);
        setPreviewUrls(prev => ({ ...prev, right: url }));
        setStep(4); // uploading indicator

        // Stop camera tracks and return all 3 files
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(t => t.stop());
        }
        onComplete(finalFiles);
      }
    }, 'image/jpeg', 0.85);
  };

  const getStepTitle = () => {
    if (step === 4) return '⏳ Uploading & Processing...';
    if (step === 1) return '1️⃣ Look Straight into Camera (Front View)';
    if (step === 2) return '2️⃣ Turn Head Slightly Left (~45° Angle)';
    return '3️⃣ Turn Head Slightly Right (~45° Angle)';
  };

  const getStepDesc = () => {
    if (step === 4) return 'All 3 photos captured! Server is extracting your AI face vectors. This takes 10–20 seconds...';
    if (step === 1) return 'Position your face in the center of the frame and look directly at the lens.';
    if (step === 2) return 'Rotate your head slowly to your left so we capture your left facial profile.';
    return 'Rotate your head slowly to your right so we capture your right facial profile.';
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-3xl p-5 sm:p-6 max-w-xl w-full shadow-2xl text-white space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-purple-500/20 text-purple-400">
              <Sparkles size={20} />
            </div>
            <div>
              <h3 className="font-bold text-base sm:text-lg">Live 3-Angle Camera Capture</h3>
              <p className="text-xs text-slate-400">{studentName ? `Enrolling: ${studentName}` : 'AI Face Vector Studio'}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors">
            <X size={18} />
          </button>
        </div>

        {/* Step Guide Bar */}
        <div className="flex items-center justify-between bg-slate-800/60 p-3 rounded-2xl border border-slate-700/50">
          <div className={`flex-1 text-center py-1.5 rounded-xl text-xs font-bold transition-all ${step === 1 ? 'bg-purple-600 text-white shadow-lg' : previewUrls.front ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-500'}`}>
            {previewUrls.front ? '✅ 1. Front' : '1. Front'}
          </div>
          <div className="w-4 text-center text-slate-600">→</div>
          <div className={`flex-1 text-center py-1.5 rounded-xl text-xs font-bold transition-all ${step === 2 ? 'bg-purple-600 text-white shadow-lg' : previewUrls.left ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-500'}`}>
            {previewUrls.left ? '✅ 2. Left' : '2. Left'}
          </div>
          <div className="w-4 text-center text-slate-600">→</div>
          <div className={`flex-1 text-center py-1.5 rounded-xl text-xs font-bold transition-all ${step === 3 ? 'bg-purple-600 text-white shadow-lg' : previewUrls.right ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-500'}`}>
            {previewUrls.right ? '✅ 3. Right' : '3. Right'}
          </div>
        </div>

        {/* Instruction Banner */}
        <div className="bg-purple-950/40 border border-purple-500/30 rounded-2xl p-3 text-center">
          <h4 className="text-sm font-extrabold text-purple-300">{getStepTitle()}</h4>
          <p className="text-xs text-purple-200/80 mt-0.5">{getStepDesc()}</p>
        </div>

        {/* Error Message */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-rose-500/20 border border-rose-500/30 text-rose-300 flex items-center gap-3">
            <AlertCircle size={20} className="shrink-0" />
            <p className="text-sm">{errorMessage}</p>
          </div>
        )}

        {/* Video Viewport */}
        <div className="relative aspect-video bg-black rounded-2xl overflow-hidden border-2 border-slate-700 flex items-center justify-center shadow-inner">
          {!cameraActive && !errorMessage && (
            <div className="flex flex-col items-center gap-2 text-slate-500">
              <RefreshCw size={28} className="animate-spin text-purple-500" />
              <p className="text-sm">Starting camera stream...</p>
            </div>
          )}
          
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="absolute inset-0 w-full h-full object-cover transform -scale-x-100"
          />

          {/* Guide Overlay Grid */}
          {cameraActive && (
            <div className="absolute inset-0 pointer-events-none border-4 border-purple-500/30 rounded-2xl flex items-center justify-center">
              <div className="w-48 sm:w-56 h-60 sm:h-64 border-2 border-dashed border-purple-400/60 rounded-full flex items-center justify-center">
                <span className="text-[10px] text-purple-300 bg-black/60 px-2 py-1 rounded-full uppercase tracking-wider font-semibold">
                  Align Face Here
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Capture Button / Uploading State */}
        <div className="pt-2">
          {step === 4 ? (
            <div className="w-full py-4 rounded-2xl bg-indigo-900/60 border border-indigo-500/40 flex flex-col items-center justify-center gap-2">
              <div className="flex items-center gap-3">
                <RefreshCw size={20} className="animate-spin text-indigo-400" />
                <span className="text-indigo-200 font-bold text-sm">Uploading & extracting face vectors…</span>
              </div>
              <p className="text-xs text-indigo-400/80">Please wait 10–20 seconds. Do NOT close this window.</p>
            </div>
          ) : (
            <button
              onClick={handleCapture}
              disabled={!cameraActive}
              className={`w-full py-4 rounded-2xl font-extrabold text-base flex items-center justify-center gap-2 transition-all shadow-xl ${
                !cameraActive
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-purple-500/30 active:scale-95'
              }`}
            >
              <Camera size={22} />
              <span>Capture {step === 1 ? 'Front' : step === 2 ? 'Left 45°' : 'Right 45°'} Angle</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
