import React from 'react';

export default function AttendanceTable({ rows }) {
  if (!rows || rows.length === 0) return null;

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-50 text-left">
            <th className="px-4 py-3 font-semibold text-slate-600">Date</th>
            <th className="px-4 py-3 font-semibold text-slate-600">Present</th>
            <th className="px-4 py-3 font-semibold text-slate-600">Absent</th>
            <th className="px-4 py-3 font-semibold text-slate-600">Rate</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((r, i) => {
            const total = (r.present || 0) + (r.absent || 0);
            const rate  = total ? Math.round((r.present || 0) / total * 100) : 0;
            return (
              <tr key={i} className="hover:bg-slate-50/60 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-700">{r.date}</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full
                                   bg-emerald-100 text-emerald-700 text-xs font-bold">
                    {r.present || 0}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full
                                   bg-rose-100 text-rose-700 text-xs font-bold">
                    {r.absent || 0}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-20 h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${
                        rate >= 80 ? 'bg-emerald-500' : rate >= 50 ? 'bg-amber-500' : 'bg-rose-500'
                      }`} style={{ width: `${rate}%` }} />
                    </div>
                    <span className="text-xs font-semibold text-slate-600">{rate}%</span>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
