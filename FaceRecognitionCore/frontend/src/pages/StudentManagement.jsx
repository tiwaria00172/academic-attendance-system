import React, { useEffect, useState } from 'react';
import { studentsAPI, classroomsAPI } from '../services/api';
import {
  Users, UserPlus, Upload, CheckCircle2, AlertCircle, Loader2,
  RefreshCw, Camera, School, Plus, UserCheck
} from 'lucide-react';
import ThreeAngleWebcamModal from '../components/ThreeAngleWebcamModal';

export default function StudentManagement() {
  const [students, setStudents] = useState([]);
  const [classrooms, setClassrooms] = useState([]);
  const [loading, setLoading]       = useState(true);
  const [classroomsLoading, setClassroomsLoading] = useState(true);
  const [classroomsError, setClassroomsError]     = useState(null);
  const [showAdd, setShowAdd]   = useState(false);
  const [newRoll, setNewRoll]   = useState('');
  const [newName, setNewName]   = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newDept, setNewDept]   = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg]           = useState(null);
  const [uploadingId, setUploadingId] = useState(null);
  const [showLiveModal, setShowLiveModal] = useState(false);
  const [angleStudent, setAngleStudent]   = useState(null);

  // Enrollment panel state
  const [selectedClassroom, setSelectedClassroom] = useState('');
  const [classroomDetail, setClassroomDetail]   = useState(null);
  const [enrollingIds, setEnrollingIds]         = useState(new Set());
  const [enrollMsg, setEnrollMsg]               = useState(null);

  const fetchStudents = () => {
    setLoading(true);
    studentsAPI.list()
      .then((r) => setStudents(r.data.students || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  const fetchClassrooms = () => {
    setClassroomsLoading(true);
    setClassroomsError(null);
    classroomsAPI.list()
      .then((r) => {
        const rooms = r.data.classrooms || [];
        setClassrooms(rooms);
        if (rooms.length > 0 && !selectedClassroom) setSelectedClassroom(String(rooms[0].id));
      })
      .catch((err) => {
        const msg = err.response?.data?.error || err.message || 'Could not load classrooms';
        setClassroomsError(msg);
      })
      .finally(() => setClassroomsLoading(false));
  };

  useEffect(() => {
    fetchStudents();
    fetchClassrooms();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load detailed classroom (includes enrolled students) when selection changes
  useEffect(() => {
    if (!selectedClassroom) return;
    classroomsAPI.get(selectedClassroom)
      .then((r) => setClassroomDetail(r.data.classroom))
      .catch(() => setClassroomDetail(null));
  }, [selectedClassroom]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newRoll || !newName) return;
    setSubmitting(true);
    setMsg(null);
    try {
      await studentsAPI.create({ roll_number: newRoll, name: newName, email: newEmail, department: newDept });
      setMsg({ type: 'success', text: 'Student created successfully!' });
      setNewRoll(''); setNewName(''); setNewEmail(''); setNewDept('');
      setShowAdd(false);
      fetchStudents();
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.error || 'Failed to create student' });
    } finally {
      setSubmitting(false);
    }
  };

  const handlePhotoUpload = async (studentId, file) => {
    if (!file) return;
    setUploadingId(studentId);
    setMsg(null);
    try {
      await studentsAPI.uploadPhoto(studentId, file);
      setMsg({ type: 'success', text: 'Photo uploaded and AI face vector extracted! Server cache reloaded.' });
      fetchStudents();
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.error || 'Could not extract face from photo' });
    } finally {
      setUploadingId(null);
    }
  };

  const handleSync = async () => {
    setLoading(true);
    try {
      const r = await studentsAPI.sync();
      setMsg({ type: 'success', text: `Synced ${r.data.synced} new students from training folder.` });
      fetchStudents();
    } catch {
      setMsg({ type: 'error', text: 'Sync failed' });
    } finally {
      setLoading(false);
    }
  };

  // Enroll a student into the selected classroom
  const handleEnroll = async (studentId) => {
    if (!selectedClassroom) return;
    setEnrollingIds(prev => new Set(prev).add(studentId));
    setEnrollMsg(null);
    try {
      await classroomsAPI.enroll(selectedClassroom, [studentId]);
      setEnrollMsg({ type: 'success', text: 'Student added to classroom roster ✅' });
      const r = await classroomsAPI.get(selectedClassroom);
      setClassroomDetail(r.data.classroom);
    } catch (err) {
      setEnrollMsg({ type: 'error', text: err.response?.data?.error || 'Enrollment failed' });
    } finally {
      setEnrollingIds(prev => { const s = new Set(prev); s.delete(studentId); return s; });
    }
  };

  // Enrolled student IDs for the current classroom
  const enrolledIds = new Set((classroomDetail?.students || []).map(s => s.id));

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">

      {/* ── Header ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <Users className="text-purple-600" />
            Admin Student &amp; Photo Management
          </h1>
          <p className="text-slate-500 mt-1">
            Enroll students, upload reference ID photos, and assign students to classrooms.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={handleSync}
                  className="px-4 py-2.5 rounded-xl bg-slate-200 hover:bg-slate-300 text-slate-700
                             font-medium text-sm transition-colors flex items-center gap-2">
            <RefreshCw size={16} />
            Sync from Training Folder
          </button>
          <button onClick={() => setShowAdd(!showAdd)}
                  className="btn-primary flex items-center gap-2 px-4 py-2.5 text-sm">
            <UserPlus size={16} />
            {showAdd ? 'Cancel' : 'Add Student'}
          </button>
        </div>
      </div>

      {/* ── Global message ── */}
      {msg && (
        <div className={`p-4 rounded-xl flex items-center gap-3 text-sm animate-fade-in ${
          msg.type === 'success' ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-600' : 'bg-rose-500/10 border border-rose-500/20 text-rose-600'
        }`}>
          {msg.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          <span>{msg.text}</span>
        </div>
      )}

      {/* ── Add Student form ── */}
      {showAdd && (
        <form onSubmit={handleCreate} className="glass-card p-6 space-y-4 border-l-4 border-purple-500 animate-slide-up">
          <h2 className="text-lg font-bold text-slate-800 mb-2">Add New Student</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Roll Number / ID *</label>
              <input value={newRoll} onChange={(e) => setNewRoll(e.target.value)} required
                     placeholder="e.g. 101" className="input-field" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Full Name *</label>
              <input value={newName} onChange={(e) => setNewName(e.target.value)} required
                     placeholder="e.g. John Doe" className="input-field" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Email</label>
              <input type="email" value={newEmail} onChange={(e) => setNewEmail(e.target.value)}
                     placeholder="john@school.edu" className="input-field" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Department</label>
              <input value={newDept} onChange={(e) => setNewDept(e.target.value)}
                     placeholder="Computer Science" className="input-field" />
            </div>
          </div>
          <button type="submit" disabled={submitting} className="btn-primary py-2 px-6 text-sm">
            {submitting ? 'Saving...' : 'Save Student'}
          </button>
        </form>
      )}

      {/* ══════════════════════════════════════════════════════════
          🏫 CLASSROOM ENROLLMENT PANEL
          ══════════════════════════════════════════════════════════ */}
      <div className="glass-card p-6 border-l-4 border-blue-500 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
              <School className="text-blue-600" size={20} />
              Classroom Enrollment Manager
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Assign students to a classroom so the AI camera scan marks them present/absent correctly.
            </p>
          </div>
          {classroomsLoading ? (
            <div className="flex items-center gap-2 text-sm text-slate-400 shrink-0">
              <Loader2 size={14} className="animate-spin" /> Loading classrooms…
            </div>
          ) : classroomsError ? (
            <p className="text-xs text-rose-500 font-semibold shrink-0">⚠️ {classroomsError}</p>
          ) : classrooms.length > 0 ? (
            <select
              value={selectedClassroom}
              onChange={(e) => setSelectedClassroom(e.target.value)}
              className="input-field !w-auto !py-2 font-semibold text-sm"
            >
              {classrooms.map((c) => (
                <option key={c.id} value={c.id}>{c.name} ({c.department || 'General'})</option>
              ))}
            </select>
          ) : (
            <p className="text-xs text-amber-600 font-semibold shrink-0">No classrooms yet — create one first.</p>
          )}
        </div>

        {enrollMsg && (
          <div className={`p-3 rounded-xl text-xs font-semibold flex items-center gap-2 ${
            enrollMsg.type === 'success'
              ? 'bg-emerald-50 border border-emerald-200 text-emerald-700'
              : 'bg-rose-50 border border-rose-200 text-rose-700'
          }`}>
            {enrollMsg.type === 'success' ? '✅' : '⚠️'} {enrollMsg.text}
          </div>
        )}

        {/* Currently enrolled */}
        {classroomDetail && (
          <div>
            <p className="text-xs font-bold uppercase text-slate-400 mb-2 flex items-center gap-1">
              <UserCheck size={13} /> Currently enrolled in {classroomDetail.name}
              <span className="ml-1 px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">
                {(classroomDetail.students || []).length} students
              </span>
            </p>
            {(classroomDetail.students || []).length === 0 ? (
              <p className="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 font-semibold">
                ⚠️ No students enrolled yet — this is why attendance shows 0 results after a scan.
                Use the buttons below to add students to this classroom.
              </p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {(classroomDetail.students || []).map((s) => (
                  <span key={s.id}
                        className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
                    <UserCheck size={11} />
                    {s.name} <span className="text-blue-500">({s.roll_number})</span>
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Student list with enroll buttons */}
        {loading ? (
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Loader2 size={16} className="animate-spin" /> Loading students…
          </div>
        ) : students.length === 0 ? (
          <p className="text-xs text-slate-500">No students in database. Add students above first.</p>
        ) : (
          <div>
            <p className="text-xs font-bold uppercase text-slate-400 mb-2">All Students — click + to enroll</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {students.map((s) => {
                const isEnrolled = enrolledIds.has(s.id);
                const isLoading  = enrollingIds.has(s.id);
                return (
                  <div key={s.id}
                       className={`flex items-center justify-between px-3 py-2.5 rounded-xl border transition-all ${
                         isEnrolled
                           ? 'bg-blue-50 border-blue-200'
                           : 'bg-white border-slate-200 hover:border-blue-300'
                       }`}>
                    <div>
                      <p className="text-sm font-bold text-slate-800 leading-tight">{s.name}</p>
                      <p className="text-[11px] text-slate-400 font-semibold">ID: {s.roll_number}</p>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {s.has_face_data
                        ? <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">AI✓</span>
                        : <span className="text-[10px] font-bold text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">No Photo</span>}
                      {isEnrolled ? (
                        <span className="w-7 h-7 flex items-center justify-center rounded-lg bg-blue-500 text-white">
                          <CheckCircle2 size={14} />
                        </span>
                      ) : (
                        <button
                          onClick={() => handleEnroll(s.id)}
                          disabled={isLoading || !selectedClassroom}
                          className="w-7 h-7 flex items-center justify-center rounded-lg bg-slate-100 hover:bg-blue-600 hover:text-white text-slate-500 transition-all disabled:opacity-50"
                          title="Enroll in classroom"
                        >
                          {isLoading ? <Loader2 size={13} className="animate-spin" /> : <Plus size={14} />}
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* ── Student Cards (Photo management) ── */}
      <div>
        <h2 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
          <Camera className="text-purple-600" size={20} />
          AI Face Photo Management
        </h2>

        {loading ? (
          <div className="flex items-center justify-center h-40">
            <Loader2 className="animate-spin text-purple-600" size={32} />
          </div>
        ) : students.length === 0 ? (
          <div className="glass-card p-12 text-center text-slate-500">
            No students found. Click &quot;Add Student&quot; or &quot;Sync from Training Folder&quot;.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {students.map((s) => (
              <div key={s.id} className="stat-card flex flex-col justify-between space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-purple-100 text-purple-700 uppercase">
                      ID: {s.roll_number}
                    </span>
                    <h3 className="text-lg font-bold text-slate-800 mt-1">{s.name}</h3>
                    <p className="text-xs text-slate-500">{s.department || 'General'}</p>
                  </div>
                  <div className={`px-2 py-1 rounded text-xs font-semibold ${s.has_face_data ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                    {s.has_face_data ? 'AI Registered ✅' : 'No Photo ⚠️'}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-xs text-slate-400">
                    {s.has_face_data ? 'Ready for face match' : 'Upload ID photo to register'}
                  </span>
                  <div className="flex items-center gap-1.5">
                    <button type="button" onClick={() => setAngleStudent(s)}
                            className="px-2.5 py-1 rounded bg-purple-100 hover:bg-purple-200 text-purple-700 text-xs font-bold transition-colors">
                      📸 3 Angles
                    </button>
                    <label className="cursor-pointer btn-primary !py-1 !px-2.5 !text-xs flex items-center gap-1 bg-gradient-to-r from-purple-600 to-indigo-600">
                      {uploadingId === s.id ? <Loader2 size={12} className="animate-spin" /> : <Upload size={12} />}
                      <span>1 Photo</span>
                      <input type="file" accept="image/*" className="hidden"
                             onChange={(e) => handlePhotoUpload(s.id, e.target.files[0])}
                             disabled={uploadingId === s.id} />
                    </label>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 📸 3-Angle Upload Modal for Admin */}
      {angleStudent && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <h3 className="text-lg font-extrabold text-slate-800 flex items-center gap-2">
                <span>📸</span> 3-Angle AI Enrollment: {angleStudent.name}
              </h3>
              <button onClick={() => setAngleStudent(null)} className="text-slate-400 hover:text-slate-600 font-bold text-lg">×</button>
            </div>
            <p className="text-xs text-slate-500">
              Upload Front, Left (~45°), and Right (~45°) photos for Roll Number <b>{angleStudent.roll_number}</b> to generate a multi-template recognition vector.
            </p>
            <div className="bg-gradient-to-r from-purple-50 to-indigo-50 p-3 rounded-2xl border border-purple-200/60 flex items-center justify-between gap-2">
              <span className="text-xs text-purple-900 font-bold flex items-center gap-1">⚡ Fast Option: Live Webcam</span>
              <button
                type="button"
                onClick={() => setShowLiveModal(true)}
                className="px-3 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shrink-0 active:scale-95 transition-all"
              >
                <Camera size={14} />
                <span>Live 3-Angle Capture</span>
              </button>
            </div>

            <form onSubmit={async (e) => {
              e.preventDefault();
              const front = e.target.front.files[0];
              const left  = e.target.left.files[0];
              const right = e.target.right.files[0];
              if (!front && !left && !right) { setMsg({ type: 'error', text: 'Select at least 1 angle file' }); return; }
              setUploadingId(angleStudent.id);
              setAngleStudent(null);
              setMsg(null);
              try {
                const res = await studentsAPI.uploadPhotoAngles(angleStudent.id, { front, left, right });
                setMsg({ type: 'success', text: res.data.message });
                fetchStudents();
              } catch (err) {
                setMsg({ type: 'error', text: err.response?.data?.error || '3-angle upload failed' });
              } finally {
                setUploadingId(null);
              }
            }} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">1. Frontal View *</label>
                <input name="front" type="file" accept="image/*" className="input-field !py-1 !text-xs" required />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">2. Left Profile (~45°)</label>
                <input name="left" type="file" accept="image/*" className="input-field !py-1 !text-xs" />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">3. Right Profile (~45°)</label>
                <input name="right" type="file" accept="image/*" className="input-field !py-1 !text-xs" />
              </div>
              <div className="flex justify-end gap-2 pt-2 border-t">
                <button type="button" onClick={() => setAngleStudent(null)} className="px-4 py-2 rounded-xl bg-slate-100 text-slate-600 text-xs font-bold">Cancel</button>
                <button type="submit" className="btn-primary !py-2 !px-5 text-xs font-bold">Extract &amp; Register Profile</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showLiveModal && angleStudent && (
        <ThreeAngleWebcamModal
          studentName={angleStudent.name}
          onComplete={async (files) => {
            setShowLiveModal(false);
            setUploadingId(angleStudent.id);
            const cur = angleStudent;
            setAngleStudent(null);
            setMsg(null);
            try {
              const res = await studentsAPI.uploadPhotoAngles(cur.id, { front: files.front, left: files.left, right: files.right });
              setMsg({ type: 'success', text: res.data.message });
              fetchStudents();
            } catch (err) {
              setMsg({ type: 'error', text: err.response?.data?.error || '3-angle live upload failed' });
            } finally {
              setUploadingId(null);
            }
          }}
          onClose={() => setShowLiveModal(false)}
        />
      )}
    </div>
  );
}
