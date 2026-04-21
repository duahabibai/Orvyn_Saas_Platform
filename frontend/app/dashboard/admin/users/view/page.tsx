"use client";
import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiGet, apiPut, apiPatch } from "@/lib/api";
import { useToast } from "@/components/ui";

interface User {
  id: number;
  email: string;
  full_name: string;
  role: "user" | "admin" | "super_admin";
  plan: "starter" | "growth";
  created_at: string;
  bot?: { status: boolean; mode: string };
}

interface Usage {
  whatsapp_messages_sent: number;
  whatsapp_limit: number;
  ai_requests_made: number;
  ai_limit: number;
}

export default function UserProfilePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const userId = searchParams.get("id");
  const [user, setUser] = useState<User | null>(null);
  const [usage, setUsage] = useState<Usage | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "activity" | "billing" | "support">("overview");
  const { showToast, ToastContainer } = useToast();

  useEffect(() => {
    if (userId) {
      fetchUserData();
    }
  }, [userId]);

  const fetchUserData = async () => {
    setLoading(true);
    try {
      const userData = await apiGet<User>(`/api/auth/admin/user/${userId}`);
      setUser(userData);
      // Mock usage data (you may need to add a new endpoint to get usage for a specific user)
      setUsage({
        whatsapp_messages_sent: Math.floor(Math.random() * 500),
        whatsapp_limit: userData.plan === "growth" ? 1500 : 200,
        ai_requests_made: Math.floor(Math.random() * 300),
        ai_limit: userData.plan === "growth" ? 1500 : 200,
      });
    } catch (err: any) {
      showToast(err.message || "Failed to fetch user data", "error");
      router.push("/dashboard/admin/users");
    } finally {
      setLoading(false);
    }
  };

  const toggleBotStatus = async () => {
    try {
      await apiPatch(`/api/auth/admin/users/${user?.id}/status`, {});
      showToast("Bot status updated", "success");
      fetchUserData();
    } catch (err: any) {
      showToast(err.message || "Failed to update status", "error");
    }
  };

  const updatePlan = async (newPlan: "starter" | "growth") => {
    try {
      await apiPatch(`/api/auth/admin/users/${user?.id}/plan`, { plan: newPlan });
      showToast(`Plan updated to ${newPlan}`, "success");
      fetchUserData();
    } catch (err: any) {
      showToast(err.message || "Failed to update plan", "error");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400 animate-pulse">Loading user profile...</div>
      </div>
    );
  }

  if (!user) return null;

  const usagePercentage = usage ? (usage.whatsapp_messages_sent / usage.whatsapp_limit) * 100 : 0;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <ToastContainer />

      {/* Back Button */}
      <button
        onClick={() => router.push("/dashboard/admin/users")}
        className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
        </svg>
        Back to Users
      </button>

      {/* Profile Header */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 shadow-xl p-8">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-6">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-3xl font-black text-white shadow-xl">
              {user.full_name?.charAt(0) || user.email.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-2xl font-black text-white">{user.full_name || "Unnamed User"}</h1>
              <p className="text-slate-400 font-medium mt-1">{user.email}</p>
              <div className="flex items-center gap-3 mt-3">
                <span className={`px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest ${
                  user.plan === 'growth'
                    ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                    : 'bg-slate-600/20 text-slate-400 border border-slate-600/30'
                }`}>
                  {user.plan} Plan
                </span>
                <span className={`px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest ${
                  user.role === 'super_admin' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                  user.role === 'admin' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                  'bg-slate-600/20 text-slate-400 border border-slate-600/30'
                }`}>
                  {user.role}
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={toggleBotStatus}
              className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                user.bot?.status !== false
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30'
                  : 'bg-rose-500/20 text-rose-400 border border-rose-500/30 hover:bg-rose-500/30'
              }`}
            >
              {user.bot?.status !== false ? 'Bot Active' : 'Bot Inactive'}
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-700">
        {[
          { id: "overview", label: "Overview", icon: "📊" },
          { id: "activity", label: "Activity Log", icon: "📝" },
          { id: "billing", label: "Billing", icon: "💳" },
          { id: "support", label: "Support", icon: "💬" },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-6 py-3 text-sm font-semibold transition-all border-b-2 -mb-px ${
              activeTab === tab.id
                ? 'text-indigo-400 border-indigo-500'
                : 'text-slate-400 border-transparent hover:text-white'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Usage Stats */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 shadow-xl p-6">
            <h3 className="text-lg font-bold text-white mb-6">Usage Statistics</h3>
            {usage && (
              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-slate-400">WhatsApp Messages</span>
                    <span className="text-sm font-bold text-white">
                      {usage.whatsapp_messages_sent} / {usage.whatsapp_limit}
                    </span>
                  </div>
                  <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        usagePercentage > 90 ? 'bg-rose-500' :
                        usagePercentage > 70 ? 'bg-amber-500' :
                        'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(usagePercentage, 100)}%` }}
                    />
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1">{usagePercentage.toFixed(1)}% used this month</p>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-slate-400">AI Requests</span>
                    <span className="text-sm font-bold text-white">
                      {usage.ai_requests_made} / {usage.ai_limit}
                    </span>
                  </div>
                  <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        (usage.ai_requests_made / usage.ai_limit) * 100 > 90 ? 'bg-rose-500' :
                        (usage.ai_requests_made / usage.ai_limit) * 100 > 70 ? 'bg-amber-500' :
                        'bg-indigo-500'
                      }`}
                      style={{ width: `${Math.min((usage.ai_requests_made / usage.ai_limit) * 100, 100)}%` }}
                    />
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1">
                    {((usage.ai_requests_made / usage.ai_limit) * 100).toFixed(1)}% used this month
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Account Details */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 shadow-xl p-6">
            <h3 className="text-lg font-bold text-white mb-6">Account Details</h3>
            <div className="space-y-4">
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Email</p>
                <p className="text-white font-medium">{user.email}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Full Name</p>
                <p className="text-white font-medium">{user.full_name || "Not provided"}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Role</p>
                <p className="text-white font-medium capitalize">{user.role}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Plan</p>
                <p className="text-white font-medium capitalize">{user.plan}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Member Since</p>
                <p className="text-white font-medium">{new Date(user.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 shadow-xl p-6 lg:col-span-2">
            <h3 className="text-lg font-bold text-white mb-6">Quick Actions</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <button
                onClick={() => updatePlan(user.plan === "starter" ? "growth" : "starter")}
                className="p-4 bg-indigo-500/20 border border-indigo-500/30 rounded-xl hover:bg-indigo-500/30 transition-colors text-center"
              >
                <p className="text-indigo-400 font-semibold text-sm">
                  {user.plan === "starter" ? "Upgrade to Growth" : "Downgrade to Starter"}
                </p>
              </button>
              <button className="p-4 bg-emerald-500/20 border border-emerald-500/30 rounded-xl hover:bg-emerald-500/30 transition-colors text-center">
                <p className="text-emerald-400 font-semibold text-sm">Reset Password</p>
              </button>
              <button className="p-4 bg-amber-500/20 border border-amber-500/30 rounded-xl hover:bg-amber-500/30 transition-colors text-center">
                <p className="text-amber-400 font-semibold text-sm">Send Email</p>
              </button>
              <button className="p-4 bg-rose-500/20 border border-rose-500/30 rounded-xl hover:bg-rose-500/30 transition-colors text-center">
                <p className="text-rose-400 font-semibold text-sm">Suspend Account</p>
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === "activity" && (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 shadow-xl p-8">
          <div className="text-center text-slate-400">
            <svg className="w-16 h-16 mx-auto mb-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>Activity log will be displayed here</p>
            <p className="text-sm mt-2">Track user actions and bot interactions</p>
          </div>
        </div>
      )}

      {activeTab === "billing" && (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 shadow-xl p-8">
          <div className="text-center text-slate-400">
            <svg className="w-16 h-16 mx-auto mb-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            <p>Billing information will be displayed here</p>
            <p className="text-sm mt-2">Payment history and subscription details</p>
          </div>
        </div>
      )}

      {activeTab === "support" && (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 shadow-xl p-8">
          <div className="text-center text-slate-400">
            <svg className="w-16 h-16 mx-auto mb-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <p>Support tickets will be displayed here</p>
            <p className="text-sm mt-2">View and respond to user support requests</p>
          </div>
        </div>
      )}
    </div>
  );
}
