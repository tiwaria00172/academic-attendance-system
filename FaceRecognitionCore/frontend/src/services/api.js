import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({ baseURL: API_URL });

// Inject JWT token into every request
api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('access_token');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

// Global 401 handler
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

/* ── Auth ──────────────────────────────────── */
export const authAPI = {
  login:  (username, password) => api.post('/auth/login', { username, password }),
  signup: (username, email, password, role) => api.post('/auth/signup', { username, email, password, role }),
  me:     () => api.get('/auth/me'),
};

/* ── Attendance ────────────────────────────── */
export const attendanceAPI = {
  processPhotos(classroomId, photos) {
    const fd = new FormData();
    fd.append('classroom_id', classroomId);
    photos.forEach((p) => fd.append('photos', p));
    return api.post('/attendance/process', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  confirm: (classroomId, attendance) =>
    api.post('/attendance/confirm', { classroom_id: classroomId, attendance }),
  history: (classroomId, date) =>
    api.get(`/attendance/history/${classroomId}`, { params: { date } }),
};

/* ── Students ──────────────────────────────── */
export const studentsAPI = {
  list:   () => api.get('/students'),
  get:    (id) => api.get(`/students/${id}`),
  create: (data) => api.post('/students', data),
  sync:   () => api.post('/students/sync'),
  uploadPhoto(studentId, photo) {
    const fd = new FormData();
    fd.append('photo', photo);
    return api.post(`/students/${studentId}/photo`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  uploadPhotoAngles(studentId, { front, left, right }) {
    const fd = new FormData();
    if (front) fd.append('front', front);
    if (left)  fd.append('left', left);
    if (right) fd.append('right', right);
    return api.post(`/students/${studentId}/photo_angles`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

/* ── Classrooms ────────────────────────────── */
export const classroomsAPI = {
  list:    () => api.get('/classes'),
  get:     (id) => api.get(`/classes/${id}`),
  create:  (data) => api.post('/classes', data),
  enroll:  (cid, studentIds) => api.post(`/classes/${cid}/enroll`, { student_ids: studentIds }),
};

/* ── Reports ───────────────────────────────── */
export const reportsAPI = {
  summary: (cid) => api.get(`/reports/summary/${cid}`),
  student: (sid) => api.get(`/reports/student/${sid}`),
  daily:   (cid) => api.get(`/reports/daily/${cid}`),
  exportUrl: (cid) => `${api.defaults.baseURL}/reports/export/${cid}`,
  exportCsv: async (cid) => {
    const token = localStorage.getItem('access_token');
    const res = await api.get(`/reports/export/${cid}`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `attendance_report_class_${cid}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
};

export default api;
