"use client";
import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

export default function RevenuePage() {
  const [subscriptions, setSubscriptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSubscriptions();
  }, []);

  const fetchSubscriptions = async () => {
    setLoading(true);
    try {
      const data = await apiGet("/api/auth/admin/subscriptions");
      setSubscriptions(data.subscriptions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const totalMRR = subscriptions.reduce((acc, sub) => {
    return acc + (sub.plan === "growth" ? 3 : 1);
  }, 0);

  const starterCount = subscriptions.filter(s => s.plan === "starter").length;
  const growthCount = subscriptions.filter(s => s.plan === "growth").length;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-black text-white tracking-tight">Revenue & Subscriptions</h1>
        <p className="text-slate-400 font-medium mt-1">Track MRR and subscription health</p>
      </div>

      {/* Revenue Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-emerald-500/20 to-teal-500/20 backdrop-blur-sm p-6 rounded-2xl border border-emerald-500/30 shadow-xl">
          <p className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Monthly Recurring Revenue</p>
          <p className="text-4xl font-black text-white mt-2">${totalMRR}/mo</p>
          <p className="text-[10px] text-emerald-400 mt-1">+{growthCount * 3} from Growth plans</p>
        </div>
        <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-700 shadow-xl">
          <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Starter Subscriptions</p>
          <p className="text-4xl font-black text-white mt-2">{starterCount}</p>
          <p className="text-[10px] text-slate-400 mt-1">${starterCount}/mo revenue</p>
        </div>
        <div className="bg-gradient-to-br from-indigo-500/20 to-violet-500/20 backdrop-blur-sm p-6 rounded-2xl border border-indigo-500/30 shadow-xl">
          <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">Growth Subscriptions</p>
          <p className="text-4xl font-black text-white mt-2">{growthCount}</p>
          <p className="text-[10px] text-indigo-400 mt-1">${growthCount * 3}/mo revenue</p>
        </div>
      </div>

      {/* Subscriptions Table */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 shadow-xl overflow-hidden">
        <div className="p-6 border-b border-slate-700">
          <h3 className="text-lg font-bold text-white">All Subscriptions</h3>
        </div>
        {loading ? (
          <div className="flex items-center justify-center h-48 text-slate-400">Loading...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-900/50 border-b border-slate-700">
                  <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">User</th>
                  <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Plan</th>
                  <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">WhatsApp Usage</th>
                  <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">AI Usage</th>
                  <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">MRR</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {subscriptions.map(sub => (
                  <tr key={sub.user_id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="px-6 py-4">
                      <p className="font-semibold text-white">{sub.email}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest ${
                        sub.plan === 'growth'
                          ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                          : 'bg-slate-600/20 text-slate-400 border border-slate-600/30'
                      }`}>
                        {sub.plan}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden max-w-[100px]">
                          <div
                            className="h-full bg-indigo-500 rounded-full"
                            style={{ width: `${Math.min((sub.whatsapp_messages_sent / sub.whatsapp_limit) * 100, 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-400">{sub.whatsapp_messages_sent}/{sub.whatsapp_limit}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden max-w-[100px]">
                          <div
                            className="h-full bg-violet-500 rounded-full"
                            style={{ width: `${Math.min((sub.ai_requests_made / sub.ai_limit) * 100, 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-400">{sub.ai_requests_made}/{sub.ai_limit}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-white font-bold">${sub.plan === "growth" ? 3 : 1}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
