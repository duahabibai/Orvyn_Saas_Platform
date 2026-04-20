"use client";
import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { useToast } from "@/components/ui";

// Simple bar chart component using CSS
function SimpleBarChart({ data }: { data: { label: string; value: number; color: string }[] }) {
  const maxValue = Math.max(...data.map(d => d.value), 1);

  return (
    <div className="flex items-end justify-around h-40 gap-2 px-4">
      {data.map((item, i) => (
        <div key={i} className="flex flex-col items-center gap-2 flex-1">
          <div
            className={`w-full rounded-t-lg transition-all duration-500 ${item.color}`}
            style={{ height: `${(item.value / maxValue) * 100}%`, minHeight: item.value > 0 ? '8px' : '0' }}
          />
          <span className="text-[10px] font-bold text-gray-500 text-center truncate w-full">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

// Simple donut chart using CSS conic-gradient
function SimpleDonutChart({ value, total, label, color }: { value: number; total: number; label: string; color: string }) {
  const percentage = total > 0 ? (value / total) * 100 : 0;
  const gradient = `conic-gradient(${color} ${percentage}%, #374151 ${percentage}%)`;

  return (
    <div className="flex flex-col items-center">
      <div
        className="w-28 h-28 rounded-full relative"
        style={{ background: gradient }}
      >
        <div className="absolute inset-6 bg-gray-900 rounded-full flex items-center justify-center border border-gray-700">
          <div className="text-center">
            <p className="text-xl font-black text-white">{Math.round(percentage)}%</p>
            <p className="text-[8px] text-gray-500 uppercase tracking-wider">{label}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AdminDashboardPage() {
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
    } catch (err: any) {
      showToast(err.message || "Failed to fetch data", "error");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400 animate-pulse text-center">
          <div className="w-12 h-12 border-4 border-violet-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-sm font-medium">Loading Admin Dashboard...</p>
        </div>
      </div>
    );
  }

  // Calculate plan distribution
  const starterCount = users.filter(u => u.plan === "starter").length;
  const growthCount = users.filter(u => u.plan === "growth").length;
  const totalUsers = users.length;

  // Calculate role distribution
  const userCount = users.filter(u => u.role === "user").length;
  const adminCount = users.filter(u => u.role === "admin").length;
  const superAdminCount = users.filter(u => u.role === "super_admin").length;

  // Mock data for user growth (last 6 months)
  const userGrowthData = [
    { label: "May", value: Math.max(0, totalUsers - 5), color: "bg-gray-600" },
    { label: "Jun", value: Math.max(0, totalUsers - 4), color: "bg-gray-600" },
    { label: "Jul", value: Math.max(0, totalUsers - 3), color: "bg-gray-600" },
    { label: "Aug", value: Math.max(0, totalUsers - 2), color: "bg-violet-600" },
    { label: "Sep", value: Math.max(0, totalUsers - 1), color: "bg-violet-500" },
    { label: "Oct", value: totalUsers, color: "bg-gradient-to-t from-violet-600 to-fuchsia-600" },
  ];

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <ToastContainer />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Admin Dashboard</h1>
          <p className="text-gray-400 font-medium mt-1 text-sm">Platform-wide insights and management</p>
        </div>
        <button
          onClick={fetchData}
          className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-sm font-semibold transition-all shadow-lg shadow-violet-900/30"
        >
          Refresh Data
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: "Total Users", value: stats.total_users, icon: "👥", color: "violet", change: "+12%" },
            { label: "Messages Sent", value: stats.total_messages, icon: "💬", color: "emerald", change: "+24%" },
            { label: "Total Contacts", value: stats.total_contacts, icon: "👤", color: "fuchsia", change: "+8%" },
            { label: "Active Bots", value: users.filter(u => u.bot?.status !== false).length, icon: "🤖", color: "amber", change: "+3" },
          ].map(s => (
            <div key={s.label} className="bg-gray-900/50 backdrop-blur-sm p-4 rounded-xl border border-gray-800 shadow-xl">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest">{s.label}</p>
                  <p className="text-2xl font-black text-white mt-1.5">{s.value}</p>
                  <p className="text-[9px] font-bold text-emerald-400 mt-1">{s.change} this month</p>
                </div>
                <div className={`w-10 h-10 rounded-lg bg-${s.color}-500/20 border border-${s.color}-500/30 flex items-center justify-center text-xl`}>
                  {s.icon}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* User Growth Chart */}
        <div className="bg-gray-900/50 backdrop-blur-sm p-5 rounded-xl border border-gray-800 shadow-xl">
          <h3 className="text-base font-bold text-white mb-4">User Growth (Last 6 Months)</h3>
          <SimpleBarChart data={userGrowthData} />
        </div>

        {/* Plan Distribution */}
        <div className="bg-gray-900/50 backdrop-blur-sm p-5 rounded-xl border border-gray-800 shadow-xl">
          <h3 className="text-base font-bold text-white mb-4">Plan Distribution</h3>
          <div className="flex items-center justify-around">
            <SimpleDonutChart
              value={growthCount}
              total={totalUsers}
              label="Growth"
              color="#8b5cf6"
            />
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-violet-500"></div>
                <div>
                  <p className="text-xs font-bold text-white">{growthCount}</p>
                  <p className="text-[9px] text-gray-500 uppercase">Growth Plans</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-gray-600"></div>
                <div>
                  <p className="text-xs font-bold text-white">{starterCount}</p>
                  <p className="text-[9px] text-gray-500 uppercase">Starter Plans</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Role Distribution */}
      <div className="bg-gray-900/50 backdrop-blur-sm p-5 rounded-xl border border-gray-800 shadow-xl">
        <h3 className="text-base font-bold text-white mb-4">User Roles</h3>
        <div className="grid grid-cols-3 gap-4">
          {[
            { role: "Users", count: userCount, color: "from-violet-500 to-fuchsia-600", bg: "bg-violet-500/10" },
            { role: "Admins", count: adminCount, color: "from-emerald-500 to-teal-600", bg: "bg-emerald-500/10" },
            { role: "Super Admins", count: superAdminCount, color: "from-amber-500 to-orange-600", bg: "bg-amber-500/10" },
          ].map(r => (
            <div key={r.role} className={`${r.bg} rounded-xl p-4 border border-white/5`}>
              <p className="text-[8px] font-black text-gray-500 uppercase tracking-widest">{r.role}</p>
              <p className="text-3xl font-black text-white mt-1.5">{r.count}</p>
              <div className={`h-1.5 rounded-full bg-gradient-to-r ${r.color} mt-3`}></div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Users Table */}
      <div className="bg-gray-900/50 backdrop-blur-sm p-5 rounded-xl border border-gray-800 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-bold text-white">Recent Users</h3>
          <a href="/dashboard/admin/users" className="text-xs font-semibold text-violet-400 hover:text-violet-300 transition-colors">
            View All →
          </a>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="pb-3 text-[9px] font-black text-gray-500 uppercase tracking-widest">Email</th>
                <th className="pb-3 text-[9px] font-black text-gray-500 uppercase tracking-widest">Plan</th>
                <th className="pb-3 text-[9px] font-black text-gray-500 uppercase tracking-widest">Role</th>
                <th className="pb-3 text-[9px] font-black text-gray-500 uppercase tracking-widest">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/50">
              {users.slice(0, 5).map(user => (
                <tr key={user.id} className="group">
                  <td className="py-3">
                    <p className="font-semibold text-white text-sm">{user.email}</p>
                  </td>
                  <td className="py-3">
                    <span className={`px-2.5 py-1 rounded-md text-[9px] font-black uppercase tracking-widest ${
                      user.plan === 'growth'
                        ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30'
                        : 'bg-gray-700/20 text-gray-400 border border-gray-700/30'
                    }`}>
                      {user.plan}
                    </span>
                  </td>
                  <td className="py-3">
                    <span className={`px-2.5 py-1 rounded-md text-[9px] font-black uppercase tracking-widest ${
                      user.role === 'super_admin' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                      user.role === 'admin' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                      'bg-gray-700/20 text-gray-400 border border-gray-700/30'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="py-3 text-xs text-gray-500">
                    {new Date(user.created_at).toLocaleDateString()}
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
