"use client";

export default function LogsPage() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-black text-white tracking-tight">System Logs</h1>
        <p className="text-slate-400 font-medium mt-1">Monitor platform activity and errors</p>
      </div>

      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 shadow-xl p-12">
        <div className="text-center text-slate-400">
          <svg className="w-20 h-20 mx-auto mb-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-lg font-semibold">System Logs Coming Soon</p>
          <p className="text-sm mt-2">This feature will display platform-wide activity logs, errors, and audit trails</p>
        </div>
      </div>
    </div>
  );
}
