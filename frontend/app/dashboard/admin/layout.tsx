"use client";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { ReactNode, useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

const adminNavItems = [
  { href: "/dashboard/admin", label: "Dashboard", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
  )},
  { href: "/dashboard/admin/users", label: "User Management", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
  )},
  { href: "/dashboard/admin/revenue", label: "Revenue", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
  )},
  { href: "/dashboard/admin/logs", label: "System Logs", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
  )},
  { href: "/dashboard/admin/settings", label: "Admin Settings", icon: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
  )},
];

export default function AdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [userRole, setUserRole] = useState<string>("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  useEffect(() => {
    setMounted(true);
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    apiGet("/api/auth/me")
      .then(user => {
        setUserRole(user.role);
        // Redirect non-super-admin users
        if (user.role !== "super_admin") {
          router.push("/dashboard");
        }
      })
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
  if (userRole !== "super_admin") return null;

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100 font-sans overflow-hidden">
      {/* Super Admin Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-72 bg-gray-900 border-r border-gray-800 transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex flex-col h-full">
          {/* Brand Logo */}
          <div className="p-6 pb-4 flex items-center justify-between border-b border-gray-800">
            <Link href="/dashboard/admin" className="flex items-center gap-3 group">
              <div className="bg-gradient-to-br from-violet-600 to-fuchsia-600 p-2.5 rounded-xl shadow-xl shadow-violet-900/30 group-hover:shadow-violet-900/50 transition-all">
                <img src="/logo.png" alt="ORVYN" className="w-9 h-9 object-contain brightness-0 invert" />
              </div>
              <div>
                <span className="text-xl font-black tracking-tight text-white">ORVYN</span>
                <p className="text-[9px] font-bold text-violet-400 uppercase tracking-widest leading-none mt-0.5">Super Admin</p>
              </div>
            </Link>
            <button className="lg:hidden p-2 text-gray-400 hover:bg-gray-800 rounded-lg" onClick={() => setIsSidebarOpen(false)}>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>

          {/* Super Admin Badge */}
          <div className="px-4 py-4">
            <div className="bg-gradient-to-r from-violet-600/20 to-fuchsia-600/20 rounded-xl p-3.5 border border-violet-500/30">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-violet-500/20 border border-violet-500/40 flex items-center justify-center">
                  <svg className="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <p className="text-[8px] font-black text-violet-300 uppercase tracking-widest">Access Level</p>
                  <p className="text-xs font-black text-white">Super Admin</p>
                </div>
              </div>
            </div>
          </div>

          {/* Admin Navigation */}
          <nav className="flex-1 px-3 py-6 space-y-1 overflow-y-auto">
            <p className="px-3 text-[9px] font-black text-gray-500 uppercase tracking-widest mb-3">Admin Panel</p>
            {adminNavItems.map(item => {
              const active = pathname === item.href || (item.href !== "/dashboard/admin" && pathname?.startsWith(item.href));
              return (
                <Link key={item.href} href={item.href}
                  className={`flex items-center gap-3 px-3.5 py-3 rounded-xl text-sm font-bold transition-all duration-200 group ${
                    active
                      ? "bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white shadow-lg shadow-violet-900/50"
                      : "text-gray-400 hover:bg-gray-800 hover:text-white"
                  }`}>
                  <span className={`${active ? "text-white" : "text-gray-500 group-hover:text-violet-400"}`}>{item.icon}</span>
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* Sidebar Footer */}
          <div className="p-4 border-t border-gray-800">
            <button onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 py-3 text-sm font-semibold text-red-400 bg-red-500/10 border border-red-500/30 rounded-xl hover:bg-red-500/20 hover:text-red-300 transition-all">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Log Out
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-gray-900/80 backdrop-blur-md border-b border-gray-800 flex items-center justify-between px-6 z-40 sticky top-0">
          <div className="flex items-center gap-4">
            <button className="lg:hidden p-2 text-gray-400 hover:bg-gray-800 rounded-lg" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7"/></svg>
            </button>
            <h2 className="text-base font-black text-white tracking-tight capitalize">
              {pathname === "/dashboard/admin" ? "Admin Overview" : pathname?.split("/").pop()?.replace("-", " ")}
            </h2>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-3 pl-4 border-l border-gray-800">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-fuchsia-600 shadow-lg shadow-violet-900/30 overflow-hidden flex items-center justify-center">
                <img src="/logo.png" alt="Profile" className="w-4 h-4 object-contain brightness-0 invert" />
              </div>
              <div>
                <p className="text-xs font-bold text-white">Super Admin</p>
                <p className="text-[9px] text-violet-400 font-medium">Full Access</p>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6 relative">
          <div className="max-w-7xl mx-auto space-y-6 pb-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
