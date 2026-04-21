"use client";
import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import Link from "next/link";

export default function DashboardPage() {
  const [bot, setBot] = useState<any>(null);
  const [leads, setLeads] = useState<any[]>([]);
  const [usage, setUsage] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [conversations, setConversations] = useState<any[]>([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const [b, l, u, c] = await Promise.all([
          apiGet("/api/bots/me").catch(() => ({ mode: 'default', status: false })),
          apiGet("/api/leads?limit=5").catch(() => []),
          apiGet("/api/auth/usage").catch(() => ({
            whatsapp_messages_sent: 0,
            whatsapp_limit: 200,
            ai_requests_made: 0,
            ai_limit: 200,
            plan: 'starter'
          })),
          apiGet("/api/conversations").catch(() => []),
        ]);
        setBot(b);
        setLeads(l);
        setUsage(u);
        setConversations(c);
      } catch (err) {
        console.error("Dashboard data fetch error:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 animate-pulse">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-44 bg-white rounded-[2rem] border border-[#F1F5F9]"></div>
        ))}
        <div className="lg:col-span-3 h-[500px] bg-white rounded-[2.5rem] border border-[#F1F5F9]"></div>
        <div className="h-[500px] bg-white rounded-[2.5rem] border border-[#F1F5F9]"></div>
      </div>
    );
  }

  const waProgress = usage ? (usage.whatsapp_messages_sent / usage.whatsapp_limit) * 100 : 0;
  const aiProgress = usage ? (usage.ai_requests_made / usage.ai_limit) * 100 : 0;
  const totalConversations = conversations.length || leads.length;
  const totalContacts = leads.length;

  return (
    <div className="space-y-12">
      {/* Premium Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        {/* Card: Bot Status */}
        <div className="premium-card rounded-[2rem] p-8 relative overflow-hidden group bg-white">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-125 duration-700"></div>
          <div className="flex justify-between items-start mb-6">
            <div className="p-3.5 bg-blue-50 text-blue-600 rounded-2xl border border-blue-100 relative z-10">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            </div>
            <div className="flex gap-2">
              <div className={`px-4 py-1.5 rounded-full text-[10px] font-semibold uppercase tracking-wide relative z-10 ${bot?.status ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : 'bg-slate-50 text-slate-500 border border-slate-100'}`}>
                {bot?.status ? 'Active' : 'Offline'}
              </div>
              {usage?.plan === 'starter' && (
                <div className="px-4 py-1.5 rounded-full text-[10px] font-semibold uppercase tracking-wide bg-amber-50 text-amber-600 border border-amber-100 relative z-10">
                  Starter
                </div>
              )}
              {usage?.plan === 'growth' && (
                <div className="px-4 py-1.5 rounded-full text-[10px] font-semibold uppercase tracking-wide bg-emerald-50 text-emerald-600 border border-emerald-100 relative z-10">
                  Growth
                </div>
              )}
            </div>
          </div>
          <p className="text-[#64748B] text-xs font-semibold uppercase tracking-wide mb-1 relative z-10">Bot Mode</p>
          <h3 className="text-2xl font-bold text-[#0F172A] capitalize tracking-tight relative z-10">{bot?.mode || 'Default'}</h3>
        </div>

        {/* Card: Messages */}
        <div className="premium-card rounded-[2rem] p-8 relative overflow-hidden group bg-white">
          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-125 duration-700"></div>
          <div className="flex justify-between items-start mb-6">
            <div className="p-3.5 bg-indigo-50 text-indigo-600 rounded-2xl border border-indigo-100 relative z-10">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/></svg>
            </div>
          </div>
          <p className="text-[#64748B] text-xs font-semibold uppercase tracking-wide mb-1 relative z-10">WhatsApp Messages</p>
          <h3 className="text-2xl font-bold text-[#0F172A] tracking-tight relative z-10">{usage?.whatsapp_messages_sent || 0} <span className="text-sm text-[#94A3B8] font-medium">/ {usage?.whatsapp_limit || 0}</span></h3>
        </div>

        {/* Card: Contacts */}
        <div className="premium-card rounded-[2rem] p-8 relative overflow-hidden group bg-white">
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-50 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-125 duration-700"></div>
          <div className="flex justify-between items-start mb-6">
            <div className="p-3.5 bg-emerald-50 text-emerald-600 rounded-2xl border border-emerald-100 relative z-10">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
            </div>
          </div>
          <p className="text-[#64748B] text-xs font-semibold uppercase tracking-wide mb-1 relative z-10">Total Contacts</p>
          <h3 className="text-2xl font-bold text-[#0F172A] tracking-tight relative z-10">{totalContacts}</h3>
        </div>

        {/* Card: AI */}
        <div className="premium-card rounded-[2rem] p-8 relative overflow-hidden group bg-white">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-50 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-125 duration-700"></div>
          <div className="flex justify-between items-start mb-6">
            <div className="p-3.5 bg-purple-50 text-purple-600 rounded-2xl border border-purple-100 relative z-10">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
            </div>
          </div>
          <p className="text-[#64748B] text-xs font-semibold uppercase tracking-wide mb-1 relative z-10">AI Requests</p>
          <h3 className="text-2xl font-bold text-[#0F172A] tracking-tight relative z-10">{usage?.ai_requests_made || 0} <span className="text-sm text-[#94A3B8] font-medium">/ {usage?.ai_limit || 0}</span></h3>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Activity Pulse Graph */}
        <div className="lg:col-span-2 premium-card rounded-[2.5rem] p-10 bg-white">
          <div className="flex items-center justify-between mb-12">
            <div>
              <h3 className="text-2xl font-bold text-[#0F172A] tracking-tight">Conversation Analytics</h3>
              <p className="text-[#64748B] text-sm font-medium mt-1">Message activity over time</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 bg-blue-500 rounded-full"></div>
                <span className="text-xs font-medium text-[#64748B]">Messages</span>
              </div>
              <div className="flex items-center gap-2 ml-4">
                <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full"></div>
                <span className="text-xs font-medium text-[#64748B]">Contacts</span>
              </div>
            </div>
          </div>

          <div className="relative h-72 w-full mt-8">
            {/* Animated SVG Graph */}
            <svg className="w-full h-full overflow-visible" viewBox="0 0 1000 300" preserveAspectRatio="none">
              <defs>
                <linearGradient id="gradientBlue" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.15" />
                  <stop offset="100%" stopColor="#3B82F6" stopOpacity="0" />
                </linearGradient>
                <linearGradient id="gradientEmerald" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#10B981" stopOpacity="0.15" />
                  <stop offset="100%" stopColor="#10B981" stopOpacity="0" />
                </linearGradient>
              </defs>
              {/* Messages Line */}
              <path
                d="M0,200 C150,180 250,220 350,150 C450,80 550,120 650,90 C750,60 850,140 1000,80"
                fill="none"
                stroke="#3B82F6"
                strokeWidth="4"
                strokeLinecap="round"
                className="path-animate"
              />
              <path
                d="M0,200 C150,180 250,220 350,150 C450,80 550,120 650,90 C750,60 850,140 1000,80 L1000,300 L0,300 Z"
                fill="url(#gradientBlue)"
              />
              {/* Contacts Line */}
              <path
                d="M0,250 C150,230 250,260 350,200 C450,150 550,180 650,160 C750,140 850,190 1000,170"
                fill="none"
                stroke="#10B981"
                strokeWidth="4"
                strokeLinecap="round"
                className="path-animate"
                style={{ animationDelay: '0.5s' }}
              />
              <path
                d="M0,250 C150,230 250,260 350,200 C450,150 550,180 650,160 C750,140 850,190 1000,170 L1000,300 L0,300 Z"
                fill="url(#gradientEmerald)"
              />
              {/* Grid Lines */}
              {[0, 1, 2, 3, 4].map(i => (
                <line key={i} x1="0" y1={i * 75} x2="1000" y2={i * 75} stroke="#F1F5F9" strokeWidth="1" />
              ))}
            </svg>
            <div className="flex justify-between mt-6 px-2">
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => (
                <span key={day} className="text-xs font-medium text-[#94A3B8]">{day}</span>
              ))}
            </div>
          </div>
        </div>

        {/* System Quotas */}
        <div className="space-y-10">
          <div className="premium-card rounded-[2.5rem] p-10 bg-[#0F172A] text-white shadow-2xl shadow-blue-100 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-40 h-40 bg-blue-500/10 rounded-full blur-[80px] -mr-20 -mt-20 group-hover:bg-blue-500/20 transition-all duration-700"></div>

            <h3 className="text-xl font-bold tracking-tight mb-10 flex items-center gap-4">
              <span className="w-8 h-px bg-blue-500"></span> Usage Overview
            </h3>

            <div className="space-y-10 relative z-10">
              {/* WhatsApp Metric */}
              <div>
                <div className="flex justify-between items-end mb-4">
                  <span className="text-xs font-semibold uppercase tracking-wide text-[#94A3B8]">WhatsApp Messages</span>
                  <span className="text-sm font-bold">{usage?.whatsapp_messages_sent} / {usage?.whatsapp_limit}</span>
                </div>
                <div className="h-2.5 bg-white/5 rounded-full overflow-hidden p-0.5 border border-white/10">
                  <div
                    className="h-full bg-blue-500 rounded-full transition-all duration-1000 shadow-[0_0_15px_rgba(59,130,246,0.6)]"
                    style={{ width: `${Math.min(waProgress, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* AI Metric */}
              <div>
                <div className="flex justify-between items-end mb-4">
                  <span className="text-xs font-semibold uppercase tracking-wide text-[#94A3B8]">AI Requests</span>
                  <span className="text-sm font-bold">{usage?.ai_requests_made} / {usage?.ai_limit}</span>
                </div>
                <div className="h-2.5 bg-white/5 rounded-full overflow-hidden p-0.5 border border-white/10">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-1000 shadow-[0_0_15px_rgba(99,102,241,0.6)]"
                    style={{ width: `${Math.min(aiProgress, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Plan Upgrade CTA for Starter Users */}
              {usage?.plan === 'starter' && (
                <div className="mt-8 p-5 bg-amber-500/10 border border-amber-500/30 rounded-2xl">
                  <p className="text-amber-400 text-xs font-semibold mb-3">⚠️ Starter Plan Limits</p>
                  <ul className="text-amber-200/80 text-xs space-y-2 mb-4">
                    <li>• Max 200 conversations/month</li>
                    <li>• Service-based flows only</li>
                    <li>• No WooCommerce integration</li>
                    <li>• Max 10 predefined rules</li>
                  </ul>
                  <button className="w-full bg-amber-500 hover:bg-amber-600 text-white py-2.5 rounded-xl font-semibold text-sm transition-all">
                    Upgrade to Growth ($3/mo)
                  </button>
                </div>
              )}

              <div className="flex gap-3 mt-6">
                <Link href="/dashboard/settings" className="flex-1 text-center bg-white/10 hover:bg-white/20 text-white py-3.5 rounded-xl font-semibold text-sm transition-all">
                  Settings
                </Link>
                <Link href="/dashboard/integrations" className="flex-1 text-center bg-white text-[#0F172A] py-3.5 rounded-xl font-semibold text-sm hover:bg-blue-50 transition-all shadow-xl">
                  Integrations
                </Link>
              </div>
            </div>
          </div>

          {/* Quick Connect Shortcuts */}
          <div className="premium-card rounded-[2.5rem] p-10 bg-white">
            <h3 className="text-lg font-bold text-[#0F172A] tracking-tight mb-8 flex items-center gap-3">
              <span className="w-6 h-px bg-blue-100"></span> Quick Access
            </h3>
            <div className="grid grid-cols-2 gap-5">
              {[
                { label: 'Conversations', icon: (
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/></svg>
                ), href: '/dashboard/chats' },
                { label: 'Integrations', icon: (
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>
                ), href: '/dashboard/integrations' },
                { label: 'Sandbox', icon: (
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.673.337a4 4 0 01-2.586.346l-1.541-.308A1 1 0 017 13.82V18a2 2 0 002 2h3.014a3 3 0 012.121.879l1.07 1.07A1 1 0 0016.914 22h3.014a2 2 0 002-2v-4.572zM6 7a2 2 0 100-4 2 2 0 000 4z"/></svg>
                ), href: '/dashboard/test-chat' },
                { label: 'Documentation', icon: (
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                ), href: '/dashboard/docs' }
              ].map((item) => (
                <Link key={item.label} href={item.href} className="flex flex-col items-center justify-center p-6 rounded-[2rem] bg-[#F8FAFC] border border-[#F1F5F9] hover:bg-white hover:border-blue-200 hover:shadow-xl hover:shadow-blue-50 transition-all duration-300 group">
                  <span className="mb-3 text-slate-400 group-hover:text-blue-600 group-hover:scale-110 transition-all duration-300">{item.icon}</span>
                  <span className="text-xs font-semibold text-[#94A3B8] group-hover:text-[#2563EB] transition-colors">{item.label}</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .path-animate {
          stroke-dasharray: 2000;
          stroke-dashoffset: 2000;
          animation: draw 3s ease-in-out forwards;
        }
        @keyframes draw {
          to { stroke-dashoffset: 0; }
        }
      `}</style>
    </div>
  );
}
