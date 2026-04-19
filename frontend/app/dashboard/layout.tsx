"use client";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { ReactNode, useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

function PlanBadge() {
  const [plan, setPlan] = useState<string>("starter");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet("/api/auth/usage")
      .then(data => {
        if (data?.plan) setPlan(data.plan);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return null;

  return (
    <div className="px-4 pb-6">
      <Link href="/dashboard/subscription" className="block">
        <div className={`rounded-2xl p-4 border-2 transition-all hover:scale-105 ${
          plan === 'starter'
            ? 'bg-amber-50 border-amber-200 hover:border-amber-300'
            : 'bg-emerald-50 border-emerald-200 hover:border-emerald-300'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Current Plan</p>
              <p className={`text-sm font-black uppercase tracking-wide ${
                plan === 'starter' ? 'text-amber-700' : 'text-emerald-700'
              }`}>
                {plan}
              </p>
            </div>
            <div className={`px-3 py-1.5 rounded-xl text-[9px] font-bold uppercase tracking-widest ${
              plan === 'starter'
                ? 'bg-amber-500 text-white'
                : 'bg-emerald-500 text-white'
            }`}>
              {plan === 'starter' ? 'Upgrade' : 'Active'}
            </div>
          </div>
        </div>
      </Link>
    </div>
  );
}

const navItems = [
  { href: "/dashboard", label: "My Dashboard", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
  )},
  { href: "/dashboard/chats", label: "Conversations", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/></svg>
  )},
  { href: "/dashboard/test-chat", label: "Sandbox", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.673.337a4 4 0 01-2.586.346l-1.541-.308A1 1 0 017 13.82V18a2 2 0 002 2h3.014a3 3 0 012.121.879l1.07 1.07A1 1 0 0016.914 22h3.014a2 2 0 002-2v-4.572zM6 7a2 2 0 100-4 2 2 0 000 4z"/></svg>
  )},
  { href: "/dashboard/leads", label: "Contacts", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
  )},
  { href: "/dashboard/settings", label: "Automation Settings", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
  )},
  { href: "/dashboard/integrations", label: "Integrations", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>
  )},
  { href: "/dashboard/help", label: "Help Center", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
  )},
  { href: "/dashboard/subscription", label: "Subscription", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/></svg>
  )},
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [userRole, setUserRole] = useState<string>("user");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  useEffect(() => {
    setMounted(true);
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    apiGet("/api/auth/me")
      .then(user => setUserRole(user.role))
      .catch(() => {
        localStorage.removeItem("token");
        router.push("/login");
      });
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    router.push("/login");
  };

  if (!mounted) return null;

  return (
    <div className="flex h-screen bg-[#F8FAFC] text-[#0F172A] font-sans overflow-hidden">
      {/* Friendly Light Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-[#F1F5F9] transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex flex-col h-full">
          {/* Brand Logo */}
          <div className="p-8 pb-6 flex items-center justify-between">
            <Link href="/dashboard" className="flex items-center gap-4 group">
              <div className="bg-[#2563EB] p-3 rounded-2xl shadow-xl shadow-blue-100 group-hover:scale-105 transition-all">
                <img src="/logo.png" alt="ORVYN" className="w-12 h-12 object-contain brightness-0 invert" />
              </div>
              <div>
                <span className="text-2xl font-black tracking-tight text-[#0F172A] platform-name">ORVYN</span>
                <p className="text-[10px] font-bold text-blue-600 uppercase tracking-widest leading-none mt-0.5">Smart Bot</p>
              </div>
            </Link>
            <button className="lg:hidden p-2 text-slate-500 hover:bg-slate-100 rounded-lg" onClick={() => setIsSidebarOpen(false)}>
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>

          {/* Plan Display */}
          <PlanBadge />

          {/* Easy Navigation */}
          <nav className="flex-1 px-4 py-8 space-y-1.5 overflow-y-auto">
            <p className="px-5 text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Main Menu</p>
            {navItems.map(item => {
              const active = pathname === item.href || (item.href !== "/dashboard" && pathname?.startsWith(item.href));
              return (
                <Link key={item.href} href={item.href}
                  className={`flex items-center gap-3.5 px-5 py-3.5 rounded-2xl text-[14px] font-bold transition-all duration-200 group ${
                    active 
                      ? "nav-item-active" 
                      : "text-slate-500 hover:bg-slate-50 hover:text-blue-600"
                  }`}>
                  <span className={`${active ? "text-white" : "text-slate-400 group-hover:text-blue-600"}`}>{item.icon}</span>
                  {item.label}
                </Link>
              );
            })}

            {/* SUPER ADMIN ACCESS - STRICTLY HIDDEN FROM USERS */}
            {userRole === "admin" && (
              <div className="pt-8 mt-8 border-t border-slate-100">
                <p className="px-5 text-xs font-semibold text-slate-400 uppercase tracking-wide mb-4">Admin Only</p>
                <Link href="/dashboard/admin"
                  className={`flex items-center gap-3.5 px-5 py-3.5 rounded-2xl text-sm font-semibold transition-all duration-200 group ${
                    pathname?.startsWith("/dashboard/admin")
                      ? "bg-slate-900 text-white shadow-lg"
                      : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
                  }`}>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  Control Panel
                </Link>
              </div>
            )}
          </nav>

          {/* Sidebar Footer */}
          <div className="p-6 mt-auto">
            <div className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
              <button onClick={handleLogout}
                className="w-full flex items-center justify-center gap-2 py-3 text-sm font-semibold text-rose-600 bg-white border border-rose-200 rounded-xl hover:bg-rose-500 hover:text-white transition-all shadow-sm">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Log Out
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main App Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Simple Top Header */}
        <header className="h-20 bg-white/80 backdrop-blur-md border-b border-[#F1F5F9] flex items-center justify-between px-8 z-40 sticky top-0">
          <div className="flex items-center gap-4">
            <button className="lg:hidden p-2 text-slate-500" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7"/></svg>
            </button>
            <h2 className="text-lg font-black text-slate-800 tracking-tight capitalize">
              {pathname === "/dashboard" ? "Welcome Back!" : pathname?.split("/").pop()?.replace("-", " ")}
            </h2>
          </div>
          
          <div className="flex items-center gap-6">
            <button className="relative p-3 bg-slate-50 border border-slate-100 rounded-2xl text-slate-500 hover:bg-blue-50 hover:text-blue-600 transition-all group animate-pulse-soft">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
              <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-rose-500 rounded-full border-2 border-white"></span>
            </button>
            
            <div className="flex items-center gap-4 border-l border-slate-100 pl-6">
              <div className="w-10 h-10 rounded-2xl bg-blue-600 shadow-lg shadow-blue-100 overflow-hidden flex items-center justify-center border-2 border-white">
                <img src="/logo.png" alt="Profile" className="w-6 h-6 object-contain brightness-0 invert" />
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Page Content */}
        <main className="flex-1 overflow-y-auto p-8 relative">
          <div className="max-w-7xl mx-auto space-y-8 pb-12">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
