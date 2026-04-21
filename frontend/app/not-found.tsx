"use client";
import Link from "next/link";
import { useEffect } from "react";

export default function NotFound() {
  useEffect(() => {
    // Check if user is logged in and redirect to appropriate dashboard after 5 seconds
    const token = localStorage.getItem("token");
    if (token) {
      const timer = setTimeout(() => {
        window.location.href = "/dashboard";
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="max-w-2xl mx-auto text-center space-y-8">
        {/* Animated 404 */}
        <div className="relative">
          <div className="text-[150px] font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 leading-none animate-bounce">
            404
          </div>
          <div className="absolute inset-0 blur-3xl bg-gradient-to-r from-blue-400 to-indigo-400 opacity-20 -z-10"></div>
        </div>

        {/* Message */}
        <div className="space-y-4">
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight">
            Page Not Found
          </h1>
          <p className="text-xl text-slate-600 max-w-md mx-auto">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        {/* Logo */}
        <div className="flex justify-center">
          <div className="bg-white p-6 rounded-3xl shadow-xl shadow-blue-100 border border-slate-100">
            <img src="/logo.png" alt="ORVYN" className="w-20 h-20 object-contain" />
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
          <Link
            href="/"
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl font-bold shadow-lg shadow-blue-200 hover:shadow-xl hover:shadow-blue-300 transition-all hover:-translate-y-0.5"
          >
            Go to Homepage
          </Link>
          <Link
            href="/dashboard"
            className="px-8 py-4 bg-white text-slate-900 rounded-2xl font-bold border-2 border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-all"
          >
            Go to Dashboard
          </Link>
          <Link
            href="/login"
            className="px-8 py-4 bg-slate-100 text-slate-700 rounded-2xl font-bold hover:bg-slate-200 transition-all"
          >
            Sign In
          </Link>
        </div>

        {/* Help Text */}
        <div className="pt-8">
          <p className="text-sm text-slate-500">
            Redirecting to dashboard in 5 seconds...
          </p>
        </div>
      </div>
    </div>
  );
}
