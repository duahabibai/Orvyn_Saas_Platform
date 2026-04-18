"use client";
import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import { useToast } from "@/components/ui";

interface Usage {
  plan: string;
  whatsapp_messages_sent: number;
  whatsapp_limit: number;
  ai_requests_made: number;
  ai_limit: number;
  conversations_count: number;
  reset_date?: string;
}

const PLANS = {
  starter: {
    name: "Starter",
    price: "$1",
    period: "/month",
    color: "amber",
    gradient: "from-amber-500 to-orange-500",
    bg: "bg-amber-50",
    border: "border-amber-200",
    text: "text-amber-700",
    button: "bg-amber-500 hover:bg-amber-600",
    features: [
      { text: "WhatsApp Bot Access", included: true },
      { text: "Service-based Flows Only", included: true },
      { text: "Basic Website Content Fetch", included: true },
      { text: "Limited Predefined Templates", included: true },
      { text: "AI Bot Integration (Your API Key)", included: true },
      { text: "Up to 200 Conversations/Month", included: true },
      { text: "Basic Lead Capture", included: true },
      { text: "Test Mode (Sandbox)", included: true },
      { text: "Basic Dashboard", included: true },
      { text: "Email Support", included: true },
      { text: "Product-based Flows", included: false },
      { text: "WooCommerce Integration", included: false },
      { text: "Product Listing / Search", included: false },
      { text: "Live Chat Takeover", included: false },
      { text: "Multi-language Support", included: false },
      { text: "Advanced Automation", included: false },
      { text: "Advanced Analytics", included: false },
      { text: "Unlimited Templates", included: false },
    ],
  },
  growth: {
    name: "Growth",
    price: "$3",
    period: "/month",
    color: "emerald",
    gradient: "from-emerald-500 to-teal-500",
    bg: "bg-emerald-50",
    border: "border-emerald-200",
    text: "text-emerald-700",
    button: "bg-emerald-500 hover:bg-emerald-600",
    popular: true,
    features: [
      { text: "Everything in Starter", included: true },
      { text: "Product + Service Flows (Both)", included: true },
      { text: "WooCommerce Integration Enabled", included: true },
      { text: "Product Listing + Search", included: true },
      { text: "Advanced Website Learning", included: true },
      { text: "Unlimited Templates", included: true },
      { text: "Smart AI Responses", included: true },
      { text: "Up to 1500 Conversations/Month", included: true },
      { text: "Full Automation Funnel", included: true },
      { text: "User Tagging", included: true },
      { text: "Broadcast Campaigns", included: true },
      { text: "Advanced Dashboard", included: true },
      { text: "Multi-language Support", included: true },
      { text: "Live Chat Takeover", included: true },
      { text: "Priority Support", included: true },
    ],
  },
};

export default function SubscriptionPage() {
  const [usage, setUsage] = useState<Usage | null>(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const { showToast, ToastContainer } = useToast();

  useEffect(() => {
    apiGet<Usage>("/api/auth/usage")
      .then((data) => setUsage(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleUpgrade = async () => {
    setUpgrading(true);
    try {
      const response = await apiPost("/api/auth/upgrade-plan", {});
      console.log("Upgrade response:", response);
      showToast("Successfully upgraded to Growth plan!", "success");
      apiGet<Usage>("/api/auth/usage").then(setUsage).catch(console.error);
    } catch (err: any) {
      console.error("Upgrade error:", err);
      const errorMsg = err.message || err.response?.data?.message || "Failed to upgrade plan";
      showToast(errorMsg, "error");
    } finally {
      setUpgrading(false);
    }
  };

  const handleDowngrade = async () => {
    if (!confirm("Are you sure you want to downgrade to Starter? You will lose access to Growth features.")) return;
    try {
      await apiPost("/api/auth/downgrade-plan", {});
      showToast("Downgraded to Starter plan", "success");
      apiGet<Usage>("/api/auth/usage").then(setUsage).catch(console.error);
    } catch (err: any) {
      showToast(err.message || "Failed to downgrade", "error");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-500 font-medium">Loading subscription...</p>
        </div>
      </div>
    );
  }

  const currentPlan = usage?.plan || "starter";
  const resetDate = usage?.reset_date
    ? new Date(usage.reset_date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
    : 'End of billing cycle';

  return (
    <div className="space-y-10 max-w-7xl mx-auto pb-12">
      <ToastContainer />

      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <h1 className="text-4xl font-black text-slate-900 tracking-tight">Choose Your Plan</h1>
        <p className="text-slate-500 font-medium mt-3">Select the perfect plan for your business needs</p>
        {currentPlan && (
          <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-full text-sm font-semibold">
            <span className="text-slate-500">Current Plan:</span>
            <span className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest ${
              currentPlan === 'starter'
                ? 'bg-amber-100 text-amber-700'
                : 'bg-emerald-100 text-emerald-700'
            }`}>
              {currentPlan}
            </span>
            <span className="text-slate-400">•</span>
            <span className="text-slate-500">Resets: {resetDate}</span>
          </div>
        )}
      </div>

      {/* Current Usage */}
      {usage && (
        <div className="bg-white rounded-[2.5rem] border border-slate-200 shadow-xl p-8 max-w-3xl mx-auto">
          <h3 className="text-lg font-black text-slate-900 mb-6 flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></span>
            Current Usage
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-50 rounded-2xl p-5">
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">WhatsApp Messages</p>
              <p className="text-2xl font-black text-slate-900">{usage.whatsapp_messages_sent} / {usage.whatsapp_limit}</p>
              <div className="mt-3 h-2 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${Math.min((usage.whatsapp_messages_sent / usage.whatsapp_limit) * 100, 100)}%` }}
                ></div>
              </div>
            </div>
            <div className="bg-slate-50 rounded-2xl p-5">
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">AI Requests</p>
              <p className="text-2xl font-black text-slate-900">{usage.ai_requests_made} / {usage.ai_limit}</p>
              <div className="mt-3 h-2 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-purple-500 rounded-full"
                  style={{ width: `${Math.min((usage.ai_requests_made / usage.ai_limit) * 100, 100)}%` }}
                ></div>
              </div>
            </div>
            <div className="bg-slate-50 rounded-2xl p-5">
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Conversations</p>
              <p className="text-2xl font-black text-slate-900">{usage.conversations_count || 0}</p>
              <p className="text-xs text-slate-500 font-medium mt-3">This billing cycle</p>
            </div>
          </div>
        </div>
      )}

      {/* Plan Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
        {/* Starter Plan */}
        <div className={`premium-card rounded-[2.5rem] p-10 bg-white border-2 ${currentPlan === 'starter' ? 'border-amber-500 shadow-2xl shadow-amber-100' : 'border-slate-100'} relative overflow-hidden`}>
          {currentPlan === 'starter' && (
            <div className="absolute top-6 right-6 px-4 py-2 bg-amber-500 text-white text-xs font-black uppercase tracking-widest rounded-full">
              Current Plan
            </div>
          )}
          <div className="mb-8">
            <div className="flex items-baseline gap-1 mb-2">
              <span className="text-5xl font-black text-slate-900">{PLANS.starter.price}</span>
              <span className="text-slate-500 font-medium">{PLANS.starter.period}</span>
            </div>
            <h3 className="text-2xl font-black text-slate-900">{PLANS.starter.name}</h3>
            <p className="text-slate-500 text-sm font-medium mt-1">Perfect for small businesses getting started</p>
          </div>

          <ul className="space-y-4 mb-10">
            {PLANS.starter.features.map((feature, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className={`mt-0.5 w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${
                  feature.included ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-400'
                }`}>
                  {feature.included ? (
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  )}
                </div>
                <span className={`text-sm font-medium ${feature.included ? 'text-slate-700' : 'text-slate-400 line-through'}`}>
                  {feature.text}
                </span>
              </li>
            ))}
          </ul>

          {currentPlan === 'starter' ? (
            <button disabled className="w-full py-4 bg-slate-100 text-slate-400 font-black rounded-2xl cursor-not-allowed">
              CURRENT PLAN
            </button>
          ) : (
            <button
              onClick={handleDowngrade}
              disabled={upgrading}
              className="w-full py-4 bg-amber-100 text-amber-700 font-black rounded-2xl hover:bg-amber-200 transition-colors disabled:opacity-50"
            >
              {upgrading ? 'Processing...' : 'Downgrade to Starter'}
            </button>
          )}
        </div>

        {/* Growth Plan */}
        <div className={`premium-card rounded-[2.5rem] p-10 bg-white border-2 ${currentPlan === 'growth' ? 'border-emerald-500 shadow-2xl shadow-emerald-100' : 'border-emerald-200'} relative overflow-hidden`}>
          {PLANS.growth.popular && currentPlan !== 'growth' && (
            <div className="absolute top-0 right-0 bg-emerald-500 text-white px-6 py-2 text-xs font-black uppercase tracking-widest rounded-bl-2xl">
              Most Popular
            </div>
          )}
          {currentPlan === 'growth' && (
            <div className="absolute top-6 right-6 px-4 py-2 bg-emerald-500 text-white text-xs font-black uppercase tracking-widest rounded-full">
              Current Plan
            </div>
          )}
          <div className="mb-8">
            <div className="flex items-baseline gap-1 mb-2">
              <span className="text-5xl font-black text-slate-900">{PLANS.growth.price}</span>
              <span className="text-slate-500 font-medium">{PLANS.growth.period}</span>
            </div>
            <h3 className="text-2xl font-black text-emerald-600">{PLANS.growth.name}</h3>
            <p className="text-slate-500 text-sm font-medium mt-1">For growing businesses that need more power</p>
          </div>

          <ul className="space-y-4 mb-10">
            {PLANS.growth.features.map((feature, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className="mt-0.5 w-5 h-5 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center flex-shrink-0">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-sm font-semibold text-slate-700">{feature.text}</span>
              </li>
            ))}
          </ul>

          {currentPlan === 'growth' ? (
            <button disabled className="w-full py-4 bg-slate-100 text-slate-400 font-black rounded-2xl cursor-not-allowed">
              CURRENT PLAN
            </button>
          ) : (
            <button
              onClick={handleUpgrade}
              disabled={upgrading}
              className={`w-full py-4 ${PLANS.growth.button} text-white font-black rounded-2xl transition-all disabled:opacity-50`}
            >
              {upgrading ? 'Upgrading...' : 'Upgrade to Growth'}
            </button>
          )}
        </div>
      </div>

      {/* Feature Comparison Table */}
      <div className="bg-white rounded-[2.5rem] border border-slate-200 shadow-xl overflow-hidden max-w-5xl mx-auto mt-12">
        <div className="p-8 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-blue-50">
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Feature Comparison</h2>
          <p className="text-slate-500 text-sm font-medium mt-1">Detailed breakdown of what's included in each plan</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-slate-50">
                <th className="px-8 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Feature</th>
                <th className="px-8 py-5 text-center text-[10px] font-black text-slate-400 uppercase tracking-widest">Starter</th>
                <th className="px-8 py-5 text-center text-[10px] font-black text-emerald-600 uppercase tracking-widest">Growth</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {[
                { feature: "WhatsApp Messages/Month", starter: "200", growth: "1500" },
                { feature: "AI Requests/Month", starter: "200", growth: "1500" },
                { feature: "Product-based Flows", starter: false, growth: true },
                { feature: "Service-based Flows", starter: true, growth: true },
                { feature: "WooCommerce Integration", starter: false, growth: true },
                { feature: "Product Listing & Search", starter: false, growth: true },
                { feature: "Predefined Rules", starter: "Limited (10)", growth: "Unlimited" },
                { feature: "Templates", starter: "Limited", growth: "Unlimited" },
                { feature: "Multi-language Support", starter: false, growth: true },
                { feature: "Live Chat Takeover", starter: false, growth: true },
                { feature: "Broadcast Campaigns", starter: false, growth: true },
                { feature: "User Tagging", starter: false, growth: true },
                { feature: "Advanced Analytics", starter: false, growth: true },
                { feature: "Support", starter: "Email", growth: "Priority" },
              ].map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="px-8 py-5 text-sm font-semibold text-slate-700">{row.feature}</td>
                  <td className="px-8 py-5 text-center">
                    {typeof row.starter === 'boolean' ? (
                      row.starter ? (
                        <svg className="w-5 h-5 mx-auto text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5 mx-auto text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      )
                    ) : (
                      <span className="text-sm font-medium text-slate-600">{row.starter}</span>
                    )}
                  </td>
                  <td className="px-8 py-5 text-center">
                    {typeof row.growth === 'boolean' ? (
                      row.growth ? (
                        <svg className="w-5 h-5 mx-auto text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5 mx-auto text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      )
                    ) : (
                      <span className="text-sm font-medium text-emerald-600">{row.growth}</span>
                    )}
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
