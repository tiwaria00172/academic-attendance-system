import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Save, Loader2 } from 'lucide-react';

export default function FaceVerification({
  result, attendance, onChange, onConfirm, loading, disabled,
}) {
  const auto    = attendance.filter((r) => r.type === 'auto_marked');
  const confirm = attendance.filter((r) => r.type === 'needs_confirmation');
  const absent  = attendance.filter((r) => r.type === 'not_detected');

  const setStatus = (studentId, status) => {
    onChange(attendance.map((r) =>
      r.student_id === studentId ? { ...r, status } : r
    ));
  };

  const confidenceBar = (v) => {
    const pct = Math.round((v || 0) * 100);
    const color = pct >= 45 ? 'bg-emerald-500' : pct >= 30 ? 'bg-amber-500' : 'bg-rose-500';
    return (
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
        </div>
        <span className="text-xs font-medium text-slate-500 w-10 text-right">{pct}%</span>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Summary bar */}
      <div className="glass-card p-4 flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-lg font-bold text-slate-800">Review Attendance</h2>
        <div className="flex items-center gap-4 text-sm">
          <span className="flex items-center gap-1 text-emerald-600 font-medium">
            <CheckCircle2 size={14} /> {auto.length} auto
          </span>
          <span className="flex items-center gap-1 text-amber-600 font-medium">
            <AlertTriangle size={14} /> {confirm.length} review
          </span>
          <span className="flex items-center gap-1 text-rose-500 font-medium">
            <XCircle size={14} /> {absent.length} absent
          </span>
          <span className="text-slate-400">|</span>
          <span className="text-slate-600 font-semibold">
            {result.total_faces_detected} faces detected
          </span>
        </div>
      </div>

      {/* Auto-marked */}
      {auto.length > 0 && (
        <Section icon={CheckCircle2} title="Auto-Marked Present" count={auto.length}
                 accent="emerald">
          {auto.map((s) => (
            <Row key={s.student_id} s={s} disabled={disabled}
                 setStatus={setStatus} bar={confidenceBar(s.confidence)} />
          ))}
        </Section>
      )}

      {/* Needs confirmation */}
      {confirm.length > 0 && (
        <Section icon={AlertTriangle} title="Needs Your Confirmation" count={confirm.length}
                 accent="amber">
          {confirm.map((s) => (
            <div key={s.student_id} className="bg-white rounded-xl p-4 space-y-3
                                                border border-slate-100 shadow-sm">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <p className="font-bold text-slate-800 text-sm sm:text-base break-words">{s.name}</p>
                  <p className="text-xs text-slate-400 font-semibold">Roll Number: {s.roll}</p>
                </div>
                <div className="w-full sm:w-48">{confidenceBar(s.confidence)}</div>
              </div>
              {s.alternatives?.length > 0 && (
                <p className="text-xs text-slate-500">
                  Could also be: {s.alternatives[0].name} ({Math.round(s.alternatives[0].similarity*100)}%)
                </p>
              )}
              <div className="flex gap-2 pt-1">
                <button onClick={() => setStatus(s.student_id, 'present')} disabled={disabled}
                        className={`flex-1 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all
                          ${s.status === 'present'
                            ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/25'
                            : 'bg-slate-100 text-slate-600 hover:bg-emerald-50 hover:text-emerald-600'}`}>
                  ✓ Present
                </button>
                <button onClick={() => setStatus(s.student_id, 'absent')} disabled={disabled}
                        className={`flex-1 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all
                          ${s.status === 'absent'
                            ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/25'
                            : 'bg-slate-100 text-slate-600 hover:bg-rose-50 hover:text-rose-600'}`}>
                  ✗ Absent
                </button>
              </div>
            </div>
          ))}
        </Section>
      )}

      {/* Not detected */}
      {absent.length > 0 && (
        <Section icon={XCircle} title="Absent / Not Detected" count={absent.length}
                 accent="rose">
          {absent.map((s) => (
            <Row key={s.student_id} s={s} disabled={disabled}
                 setStatus={setStatus} />
          ))}
        </Section>
      )}

      {/* Confirm button */}
      <button onClick={onConfirm} disabled={loading || disabled}
              className="btn-primary w-full py-3.5 flex items-center justify-center gap-2 text-base">
        {loading
          ? <><Loader2 size={20} className="animate-spin" /> Saving…</>
          : <><Save size={20} /> Confirm &amp; Save Attendance</>}
      </button>
    </div>
  );
}

/* ── helpers ─────────────────────────────── */
function Section({ icon: Icon, title, count, accent, children }) {
  const colors = {
    emerald: 'border-emerald-400 bg-emerald-50/40 text-emerald-700',
    amber:   'border-amber-400 bg-amber-50/40 text-amber-700',
    rose:    'border-rose-400 bg-rose-50/40 text-rose-700',
  };
  return (
    <div className={`rounded-2xl border-l-4 p-5 ${colors[accent]} animate-slide-up`}>
      <div className="flex items-center gap-2 mb-4">
        <Icon size={20} />
        <h3 className="font-bold text-base">{title} ({count})</h3>
      </div>
      <div className="space-y-2 max-h-80 overflow-y-auto pr-1">{children}</div>
    </div>
  );
}

function Row({ s, disabled, setStatus, bar }) {
  return (
    <div className="bg-white rounded-xl p-3 sm:px-4 sm:py-3 flex flex-col sm:flex-row sm:items-center justify-between border border-slate-100 gap-2 sm:gap-3 shadow-sm hover:border-emerald-200 transition-all">
      <div className="w-full sm:flex-1">
        <div className="flex flex-wrap items-center justify-between sm:justify-start gap-1 sm:gap-2">
          <p className="font-bold text-slate-800 text-sm sm:text-base break-words">{s.name}</p>
          <span className="text-[10px] sm:text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">Roll: {s.roll}</span>
        </div>
        {bar && <div className="mt-2 w-full">{bar}</div>}
      </div>
      <div className="flex items-center justify-end w-full sm:w-auto pt-2 sm:pt-0 border-t sm:border-0 border-slate-100">
        <select value={s.status} disabled={disabled}
                onChange={(e) => setStatus(s.student_id, e.target.value)}
                className={`text-xs font-bold px-3 py-2 rounded-lg border-0 cursor-pointer w-full sm:w-auto
                  ${s.status === 'present'
                    ? 'bg-emerald-100 text-emerald-800 shadow-sm'
                    : 'bg-rose-100 text-rose-800 shadow-sm'}
                  disabled:opacity-50`}>
          <option value="present">✓ Present</option>
          <option value="absent">✗ Absent</option>
        </select>
      </div>
    </div>
  );
}
