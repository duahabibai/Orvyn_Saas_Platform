"use client";
import { useEffect, useState } from "react";
import { apiGet, apiDelete, api } from "@/lib/api";
import { useToast } from "@/components/ui";

export default function AdminPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { showToast, ToastContainer } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [u, s] = await Promise.all([
        apiGet("/api/auth/admin/users"),
        apiGet("/api/auth/admin/stats")
      ]);
      setUsers(u);
      setStats(s);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleStatus = async (userId: number) => {
    try {
      await api(`/api/auth/admin/users/${userId}/status`, { method: "PATCH" });
      fetchData();
    } catch (err: any) {
      showToast(err.message, "error");
    }
  };

  const deleteUser = async (userId: number) => {
    // Using a simple state-based confirmation instead of confirm()
    if (!window.confirm("Are you sure? This will delete all user data.")) return;
    try {
      await apiDelete(`/api/auth/admin/users/${userId}`);
      showToast("User deleted successfully", "success");
      fetchData();
    } catch (err: any) {
      showToast(err.message, "error");
    }
  };

  if (loading) return <div className="text-slate-500 animate-pulse">Loading Admin Panel...</div>;

  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <ToastContainer />
      
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Admin Control Center</h1>
        <p className="text-slate-500 font-medium mt-1">Platform-wide management and usage statistics</p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { label: "Total Users", value: stats.total_users, icon: "👥", color: "blue" },
            { label: "Messages Sent", value: stats.total_messages, icon: "💬", color: "emerald" },
            { label: "Total Contacts", value: stats.total_contacts, icon: "👤", color: "purple" },
          ].map(s => (
            <div key={s.label} className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-xl shadow-slate-200/50 flex items-center justify-between">
              <div>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{s.label}</p>
                <p className="text-3xl font-black text-slate-900">{s.value}</p>
              </div>
              <div className={`w-14 h-14 rounded-2xl bg-${s.color}-50 text-${s.color}-600 flex items-center justify-center text-2xl`}>
                {s.icon}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white rounded-[2.5rem] border border-slate-200 shadow-2xl shadow-slate-200/50 overflow-hidden">
        <div className="p-8 border-b border-slate-100 flex justify-between items-center">
          <h2 className="text-xl font-black text-slate-900">User Management</h2>
          <button onClick={fetchData} className="text-xs font-bold text-blue-600 hover:underline">Refresh Data</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-slate-50/50">
                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">ID</th>
                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">User Email</th>
                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Role</th>
                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest text-center">Status</th>
                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {users.map(user => (
                <tr key={user.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-8 py-5 font-bold text-slate-400">#{user.id}</td>
                  <td className="px-8 py-5">
                    <p className="font-bold text-slate-900">{user.email}</p>
                    <p className="text-[10px] text-slate-400 font-medium">Joined {new Date().toLocaleDateString()}</p>
                  </td>
                  <td className="px-8 py-5">
                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                      user.role === 'admin' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-8 py-5 text-center">
                    <button onClick={() => toggleStatus(user.id)}
                      className={`px-4 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${
                        user.is_active !== false ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
                      }`}>
                      {user.is_active !== false ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="px-8 py-5 text-right space-x-2">
                    <button onClick={() => deleteUser(user.id)}
                      className="text-rose-500 hover:bg-rose-50 px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all">
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
