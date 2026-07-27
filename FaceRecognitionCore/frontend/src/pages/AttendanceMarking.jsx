import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { attendanceAPI } from '../services/api';
import PhotoUpload from '../components/PhotoUpload';
import FaceVerification from '../components/FaceVerification';
import WebcamScanner from '../components/WebcamScanner';
import { Upload, CheckCircle2, Loader2, ArrowLeft, Camera } from 'lucide-react';

export default function AttendanceMarking() {
  const { classroomId } = useParams();
  const navigate = useNavigate();

  const [step, setStep]         = useState('upload');  // upload → processing → verify → done
  const [photos, setPhotos]     = useState([]);
  const [showWebcam, setShowWebcam] = useState(false);
  const [result, setResult]     = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');

  /* ── process photos ──────────────────────── */
  const handleProcess = async (customPhotos = null) => {
    const targetPhotos = (Array.isArray(customPhotos) && customPhotos.length) ? customPhotos : photos;
    if (!targetPhotos.length) return setError('Select at least one photo');
    setLoading(true);
    setError('');
    setStep('processing');
    try {
      const res = await attendanceAPI.processPhotos(classroomId, targetPhotos);
      const d = res.data;
      setResult(d);

      // Build editable list without duplicates
      const seenIds = new Set();
      const list = [];
      (d.matches.auto_marked || []).forEach((m) => {
        if (!seenIds.has(m.student_id)) {
          seenIds.add(m.student_id);
          list.push({ student_id: m.student_id, name: m.name, roll: m.roll_number,
                      status: 'present', confidence: m.similarity, type: 'auto_marked' });
        }
      });
      (d.matches.needs_confirmation || []).forEach((m) => {
        const bm = m.best_match || {};
        if (bm.student_id && !seenIds.has(bm.student_id)) {
          seenIds.add(bm.student_id);
          list.push({ student_id: bm.student_id, name: bm.name, roll: bm.roll_number,
                      status: 'present', confidence: bm.similarity, type: 'needs_confirmation',
                      alternatives: m.alternatives });
        }
      });
      (d.absent_students || []).forEach((s) => {
        if (!seenIds.has(s.student_id)) {
          seenIds.add(s.student_id);
          list.push({ student_id: s.student_id, name: s.name, roll: s.roll_number,
                      status: 'absent', confidence: 0, type: 'not_detected' });
        }
      });

      setAttendance(list);
      setStep('verify');
    } catch (err) {
      setError(err.response?.data?.error || 'Processing failed');
      setStep('upload');
    } finally {
      setLoading(false);
    }
  };

  /* ── confirm attendance ──────────────────── */
  const handleConfirm = async () => {
    setLoading(true);
    setError('');
    try {
      const payload = attendance.map((r) => ({
        student_id: r.student_id, name: r.name,
        status: r.status, confidence_score: r.confidence, match_type: r.type,
      }));
      await attendanceAPI.confirm(classroomId, payload);
      setStep('done');
    } catch (err) {
      setError(err.response?.data?.error || 'Save failed');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setStep('upload'); setPhotos([]); setShowWebcam(false); setResult(null); setAttendance([]); setError('');
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/')}
                className="p-2 rounded-xl hover:bg-slate-100 transition-colors">
          <ArrowLeft size={20} className="text-slate-500" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Mark Attendance</h1>
          <p className="text-sm text-slate-500">Classroom #{classroomId} — Upload → Verify → Save</p>
        </div>
      </div>

      {/* Progress dots */}
      <div className="flex items-center gap-2 justify-center">
        {['upload','verify','done'].map((s, i) => (
          <React.Fragment key={s}>
            {i > 0 && <div className={`h-0.5 w-8 rounded ${
              ['verify','done'].indexOf(step) >= i ? 'bg-brand-500' : 'bg-slate-200'}`} />}
            <div className={`w-3 h-3 rounded-full transition-colors ${
              step === s || ['verify','done'].indexOf(step) >= ['upload','verify','done'].indexOf(s)
                ? 'bg-brand-500' : 'bg-slate-200'}`} />
          </React.Fragment>
        ))}
      </div>

      {error && (
        <div className="px-4 py-3 rounded-xl bg-rose-50 border border-rose-200
                        text-rose-600 text-sm animate-fade-in">{error}</div>
      )}

      {/* Step 1: Upload or Live Webcam Scanner */}
      {step === 'upload' && (
        showWebcam ? (
          <WebcamScanner
            onCapture={(capturedFiles) => {
              setPhotos(capturedFiles);
              setShowWebcam(false);
              handleProcess(capturedFiles);
            }}
            onClose={() => setShowWebcam(false)}
          />
        ) : (
          <div className="glass-card p-8 animate-slide-up space-y-6">
            <PhotoUpload photos={photos} onChange={setPhotos} />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button onClick={() => handleProcess()}
                      disabled={loading || !photos.length}
                      className="btn-primary w-full flex items-center justify-center gap-2 py-3.5 shadow-lg shadow-brand-500/20">
                {loading
                  ? <><Loader2 size={20} className="animate-spin" /> Processing…</>
                  : <><Upload size={20} /> Process Uploaded Photos</>}
              </button>

              <button onClick={() => setShowWebcam(true)}
                      className="px-6 py-3.5 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-lg shadow-indigo-500/20 active:scale-95">
                <Camera size={20} />
                <span>Launch Live Hybrid Scanner</span>
              </button>
            </div>
            
            <div className="text-center">
              <p className="text-xs text-slate-400">
                💡 Tip: Use the Live Hybrid Scanner for real-time 3D facial mesh tracking &amp; liveness verification before identity check.
              </p>
            </div>
          </div>
        )
      )}

      {/* Step 1.5: Processing */}
      {step === 'processing' && (
        <div className="glass-card p-16 text-center animate-fade-in">
          <Loader2 size={48} className="mx-auto animate-spin text-brand-500 mb-4" />
          <p className="text-lg font-semibold text-slate-700">Detecting &amp; matching faces…</p>
          <p className="text-sm text-slate-400 mt-1">This may take a few seconds</p>
        </div>
      )}

      {/* Step 2: Verification */}
      {(step === 'verify' || step === 'done') && result && (
        <FaceVerification
          result={result}
          attendance={attendance}
          onChange={setAttendance}
          onConfirm={handleConfirm}
          loading={loading}
          disabled={step === 'done'}
        />
      )}

      {/* Step 3: Done */}
      {step === 'done' && (
        <div className="glass-card p-10 text-center animate-slide-up
                        border-2 border-emerald-200 bg-emerald-50/50">
          <CheckCircle2 size={56} className="mx-auto text-emerald-500 mb-4" />
          <h2 className="text-2xl font-bold text-emerald-800">Attendance Saved!</h2>
          <p className="text-emerald-600 mt-1 mb-6">{attendance.length} records saved successfully</p>
          <div className="flex items-center justify-center gap-3">
            <button onClick={reset} className="btn-primary">Mark Another Class</button>
            <button onClick={() => navigate(`/reports/${classroomId}`)}
                    className="btn-ghost">View Report →</button>
          </div>
        </div>
      )}
    </div>
  );
}
