"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiPost, apiGet } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      // Use fetch directly to avoid apiPost token issue on first request
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://orvyn-saas-platform.onrender.com'}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || "Login failed");
      }

      const res = await response.json();
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("refreshToken", res.refresh_token);

      // Now fetch user info with the token
      const userResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://orvyn-saas-platform.onrender.com'}/api/auth/me`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${res.access_token}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error("Failed to fetch user info");
      }

      const user = await userResponse.json();
      if (user.role === "super_admin") {
        router.push("/dashboard/admin");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Please check your email and password and try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSocialLogin = (provider: string) => {
    console.log(`${provider} login clicked`);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-4 sm:p-6 font-sans overflow-y-auto">
      <div className="w-full max-w-[450px] space-y-6 sm:space-y-8 py-8">
        <div className="text-center space-y-4">
          <div className="inline-flex bg-white p-3 sm:p-4 rounded-2xl border border-slate-200 shadow-sm mb-2">
            <img src="/logo.png" alt="ORVYN" className="w-10 h-10 sm:w-12 sm:h-12 object-contain" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 platform-name">Welcome Back</h1>
            <p className="text-slate-500 text-sm mt-1">Sign in to manage your WhatsApp bot</p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-[2rem] p-6 sm:p-10 shadow-xl shadow-slate-200/50 relative overflow-hidden group">
          <form onSubmit={handleLogin} className="space-y-4 sm:space-y-6 relative z-10">
            {error && (
              <div className="bg-red-50 border border-red-100 text-red-600 text-sm font-medium p-3 sm:p-4 rounded-xl text-center">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700 ml-1">Email Address</label>
                <input
                  type="email"
                  placeholder="e.g. name@company.com"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-5 py-3.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center ml-1">
                  <label className="text-sm font-semibold text-slate-700">Password</label>
                </div>
                <input
                  type="password"
                  placeholder="Enter your password"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-5 py-3.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-4 rounded-xl font-bold text-sm hover:bg-blue-700 transition-all duration-300 shadow-lg shadow-blue-200 disabled:opacity-50 active:scale-[0.98]"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="mt-8 sm:mt-10 relative z-10">
            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-100"></div>
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-white px-4 text-slate-400 font-medium">Or continue with</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleSocialLogin("Google")}
                className="flex items-center justify-center gap-2 p-3 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all group"
              >
                <img src="https://www.svgrepo.com/show/475656/google-color.svg" className="w-5 h-5" alt="Google" />
                <span className="text-sm font-semibold text-slate-600">Google</span>
              </button>
              <button
                onClick={() => handleSocialLogin("Facebook")}
                className="flex items-center justify-center gap-2 p-3 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all group"
              >
                <img src="https://www.svgrepo.com/show/475647/facebook-color.svg" className="w-5 h-5" alt="Facebook" />
                <span className="text-sm font-semibold text-slate-600">Facebook</span>
              </button>
            </div>
          </div>
        </div>

        <p className="text-center text-sm font-medium text-slate-500">
          Don't have an account?{" "}
          <Link href="/signup" className="text-blue-600 hover:text-blue-700 font-bold">Create Account</Link>
        </p>
      </div>
    </div>
  );
}
