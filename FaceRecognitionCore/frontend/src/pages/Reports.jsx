import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { reportsAPI, classroomsAPI } from '../services/api';
import AttendanceTable from '../components/AttendanceTable';
import {
  BarChart3, Users, TrendingUp, CalendarDays, Loader2, Download,
} from 'lucide-react';

export default function Reports() {
  const { classroomId } = useParams();
  const [classrooms, setClassrooms] = useState([]);
  const [selectedId, setSelectedId] = useState(classroomId || '');
  const [summary, setSummary]       = useState(null);
  const [daily, setDaily]           = useState([]);
  const [loading, setLoading]       = useState(false);
  const [exporting, setExporting]   = useState(false);

  useEffect(() => {
    classroomsAPI.list().then((r) => {
      setClassrooms(r.data.classrooms);
      if (!selectedId && r.data.classrooms.length) setSelectedId(String(r.data.classrooms[0].id));
    });
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setLoading(true);
    Promise.all([
      reportsAPI.summary(selectedId),
      reportsAPI.daily(selectedId),
    ]).then(([s, d]) => {
      setSummary(s.data);
      setDaily(d.data.daily || []);
    }).catch(() => {})
      .finally(() => setLoading(false));
  }, [selectedId]);

  const handleExport = async () => {
    if (!selectedId) return;
    setExporting(true);
    try {
      await reportsAPI.exportCsv(selectedId);
    } catch (e) {
      alert('Failed to export CSV report');
    } finally {
      setExporting(false);
    }
  };

  const stats = summary ? [
    { label: 'Sessions Held', value: summary.sessions_held,
      icon: CalendarDays, color: 'text-brand-500', bg: 'bg-brand-50' },
    { label: 'Total Records', value: summary.total_records,
      icon: Users, color: 'text-violet-500', bg: 'bg-violet-50' },
    { label: 'Present',       value: summary.present,
      icon: TrendingUp, color: 'text-emerald-500', bg: 'bg-emerald-50' },
    { label: 'Attendance Rate', value: `${summary.attendance_rate}%`,
      icon: BarChart3, color: 'text-amber-500', bg: 'bg-amber-50' },
  ] : [];

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Attendance Reports</h1>
          <p className="text-sm text-slate-500">Analytics and history for your classrooms</p>
        </div>
        <div className="flex items-center gap-3">
          <select value={selectedId} onChange={(e) => setSelectedId(e.target.value)}
                  className="input-field max-w-xs">
            <option value="">Select classroom</option>
            {classrooms.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          {selectedId && (
            <button onClick={handleExport} disabled={exporting}
                    className="btn-primary !bg-gradient-to-r !from-emerald-600 !to-teal-600 !border-none !text-white flex items-center gap-2 !py-2 !px-4 text-xs font-bold shadow-md shadow-emerald-500/20">
              {exporting ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
              <span>{exporting ? 'Exporting...' : 'Export Spreadsheet (.CSV)'}</span>
            </button>
          )}
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-48">
          <Loader2 className="animate-spin text-brand-500" size={32} />
        </div>
      )}

      {!loading && summary && (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map(({ label, value, icon: Icon, color, bg }, i) => (
              <div key={i} className="stat-card animate-slide-up"
                   style={{ animationDelay: `${i * 80}ms` }}>
                <div className={`w-10 h-10 ${bg} rounded-xl flex items-center justify-center mb-3`}>
                  <Icon size={20} className={color} />
                </div>
                <p className="text-2xl font-bold text-slate-800">{value}</p>
                <p className="text-sm text-slate-500">{label}</p>
              </div>
            ))}
          </div>

          {/* Daily breakdown */}
          {daily.length > 0 && (
            <div className="glass-card p-6">
              <h2 className="text-lg font-bold text-slate-800 mb-4">Daily Breakdown (Last 30 days)</h2>
              <AttendanceTable rows={daily} />
            </div>
          )}

          {daily.length === 0 && (
            <div className="glass-card p-12 text-center">
              <CalendarDays size={48} className="mx-auto text-slate-300 mb-3" />
              <p className="text-slate-500">No attendance records yet for this classroom.</p>
            </div>
          )}
        </>
      )}

      {!loading && !summary && selectedId && (
        <div className="glass-card p-12 text-center">
          <BarChart3 size={48} className="mx-auto text-slate-300 mb-3" />
          <p className="text-slate-500">Select a classroom to view reports</p>
        </div>
      )}
    </div>
  );
}
