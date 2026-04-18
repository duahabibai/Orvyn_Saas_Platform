"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiPost } from "@/lib/api";

export default function SignupPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await apiPost("/api/auth/signup", { 
        full_name: fullName, 
        email, 
        password 
      });
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("refreshToken", res.refresh_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSocialSignup = (provider: string) => {
    // Placeholder for social signup - will be implemented later
    console.log(`${provider} signup clicked`);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-4 sm:p-6 font-sans overflow-y-auto">
      <div className="w-full max-w-[450px] space-y-6 sm:space-y-8 py-8">
        {/* Logo & Header */}
        <div className="text-center space-y-4">
          <div className="inline-flex bg-white p-3 sm:p-4 rounded-2xl border border-slate-200 shadow-sm mb-2">
            <img src="/logo.png" alt="ORVYN" className="w-10 h-10 sm:w-12 sm:h-12 object-contain" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 platform-name">Get Started</h1>
            <p className="text-slate-500 text-sm mt-1">Create your account to start building your bot</p>
          </div>
        </div>

        {/* Main Card */}
        <div className="bg-white border border-slate-200 rounded-[2rem] p-6 sm:p-10 shadow-xl shadow-slate-200/50 relative overflow-hidden group">
          <form onSubmit={handleSignup} className="space-y-4 sm:space-y-6 relative z-10">
            {error && (
              <div className="bg-red-50 border border-red-100 text-red-600 text-sm font-medium p-3 sm:p-4 rounded-xl text-center">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700 ml-1">Full Name</label>
                <input
                  type="text"
                  placeholder="e.g. John Doe"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-5 py-3.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </div>

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
                <label className="text-sm font-semibold text-slate-700 ml-1">Create Password</label>
                <input
                  type="password"
                  placeholder="Enter a secure password"
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
              {loading ? "Creating Account..." : "Create Account"}
            </button>
          </form>

          {/* Social Logins */}
          <div className="mt-8 sm:mt-10 relative z-10">
            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-100"></div>
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-white px-4 text-slate-400 font-medium">Or sign up with</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleSocialSignup("Google")}
                className="flex items-center justify-center gap-2 p-3 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all group"
              >
                <img src="https://www.svgrepo.com/show/475656/google-color.svg" className="w-5 h-5" alt="Google" />
                <span className="text-sm font-semibold text-slate-600">Google</span>
              </button>
              <button
                onClick={() => handleSocialSignup("Facebook")}
                className="flex items-center justify-center gap-2 p-3 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all group"
              >
                <img src="https://www.svgrepo.com/show/475647/facebook-color.svg" className="w-5 h-5" alt="Facebook" />
                <span className="text-sm font-semibold text-slate-600">Facebook</span>
              </button>
            </div>
          </div>
        </div>

        <p className="text-center text-sm font-medium text-slate-500">
          Already have an account?{" "}
          <Link href="/login" className="text-blue-600 hover:text-blue-700 font-bold">Sign In</Link>
        </p>
      </div>
    </div>
  );
}
