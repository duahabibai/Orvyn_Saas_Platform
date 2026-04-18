"use client";
import Link from "next/link";
import Image from "next/image";
import { useState } from "react";

const NavLink = ({ href, children }: { href: string; children: React.ReactNode }) => (
  <Link href={href} className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">
    {children}
  </Link>
);

const FeatureCard = ({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) => (
  <div className="group p-8 bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-indigo-100 transition-all duration-300 hover:-translate-y-1">
    <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-xl flex items-center justify-center text-white mb-6 group-hover:scale-110 transition-transform">
      {icon}
    </div>
    <h3 className="text-xl font-bold text-slate-900 mb-3">{title}</h3>
    <p className="text-slate-500 leading-relaxed">{description}</p>
  </div>
);

const PricingCard = ({ tier, price, description, features, cta, popular }: { tier: string; price: string; description: string; features: string[]; cta: string; popular?: boolean }) => (
  <div className={`relative p-8 rounded-2xl border ${popular ? 'bg-slate-900 border-slate-800 text-white scale-105 shadow-2xl' : 'bg-white border-slate-100 text-slate-900 shadow-lg'}`}>
    {popular && (
      <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-indigo-500 to-violet-600 text-white px-4 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wide">
        Most Popular
      </div>
    )}
    <h3 className={`text-lg font-semibold mb-2 ${popular ? 'text-slate-300' : 'text-slate-600'}`}>{tier}</h3>
    <div className="mb-4">
      <span className={`text-5xl font-bold ${popular ? 'text-white' : 'text-slate-900'}`}>{price}</span>
      {price !== 'Custom' && <span className={`text-sm ${popular ? 'text-slate-400' : 'text-slate-500'}`}>/month</span>}
    </div>
    <p className={`text-sm mb-6 ${popular ? 'text-slate-400' : 'text-slate-500'}`}>{description}</p>
    <ul className="space-y-3 mb-8">
      {features.map((feature, i) => (
        <li key={i} className="flex items-start gap-3 text-sm">
          <svg className={`w-5 h-5 flex-shrink-0 mt-0.5 ${popular ? 'text-indigo-400' : 'text-indigo-600'}`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          <span className={popular ? 'text-slate-300' : 'text-slate-600'}>{feature}</span>
        </li>
      ))}
    </ul>
    <Link href="/signup" className={`block w-full py-3 px-6 rounded-xl text-center font-semibold transition-all ${popular ? 'bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white' : 'bg-slate-900 hover:bg-slate-800 text-white'}`}>
      {cta}
    </Link>
  </div>
);

const StatCard = ({ value, label }: { value: string; label: string }) => (
  <div className="text-center">
    <div className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600 mb-2">{value}</div>
    <div className="text-sm font-medium text-slate-500">{label}</div>
  </div>
);

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white text-slate-900">
      {/* Navigation */}
      <nav className="fixed w-full bg-white/80 backdrop-blur-lg z-50 border-b border-slate-100">
        <div className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <Image src="/logo.png" alt="ORVYN Logo" width={180} height={50} className="h-10 w-auto" />
          </div>
          <div className="hidden md:flex gap-8 items-center">
            <NavLink href="#features">Features</NavLink>
            <NavLink href="#how-it-works">How It Works</NavLink>
            <NavLink href="#pricing">Pricing</NavLink>
            <NavLink href="#faq">FAQ</NavLink>
          </div>
          <div className="hidden md:flex gap-4 items-center">
            <Link href="/login" className="text-sm font-medium text-slate-600 hover:text-indigo-600">Login</Link>
            <Link href="/signup" className="bg-gradient-to-br from-indigo-600 to-violet-600 text-white px-6 py-2.5 rounded-lg font-semibold text-sm shadow-md shadow-indigo-200 hover:shadow-lg hover:shadow-indigo-300 transition-all hover:-translate-y-0.5">Get Started</Link>
          </div>
          <button className="md:hidden p-2" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileMenuOpen ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /> : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />}
            </svg>
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-slate-100 px-6 py-4 space-y-4">
            <NavLink href="#features">Features</NavLink>
            <NavLink href="#how-it-works">How It Works</NavLink>
            <NavLink href="#pricing">Pricing</NavLink>
            <NavLink href="#faq">FAQ</NavLink>
            <div className="pt-4 border-t border-slate-100 flex flex-col gap-3">
              <Link href="/login" className="text-sm font-medium text-slate-600">Login</Link>
              <Link href="/signup" className="bg-gradient-to-br from-indigo-600 to-violet-600 text-white px-6 py-2.5 rounded-lg font-semibold text-sm text-center">Get Started</Link>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <header className="pt-40 pb-24 px-6 text-center bg-gradient-to-b from-indigo-50 via-white to-white overflow-hidden relative">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2UyZThmMCIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-40"></div>
        <div className="relative">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-indigo-100 rounded-full shadow-sm mb-8">
            <span className="flex h-2 w-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-sm font-medium text-slate-600">Now with AI-powered responses</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 text-slate-900">
            Turn WhatsApp Conversations<br />
            into <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Revenue</span>
          </h1>
          <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto leading-relaxed">
            Deploy an intelligent sales assistant that syncs with your WooCommerce store, answers customer questions, and closes sales — all on WhatsApp.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link href="/signup" className="bg-gradient-to-r from-indigo-600 to-violet-600 text-white px-8 py-4 rounded-xl font-semibold shadow-lg shadow-indigo-200 hover:shadow-xl hover:shadow-indigo-300 transition-all hover:-translate-y-0.5">Start Free Trial</Link>
            <Link href="#how-it-works" className="bg-white text-slate-900 px-8 py-4 rounded-xl font-semibold border border-slate-200 hover:border-slate-300 hover:bg-slate-50 transition-all">See How It Works</Link>
          </div>
          <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto">
            <StatCard value="10K+" label="Messages Automated" />
            <StatCard value="98%" Label="Response Rate" />
            <StatCard value="24/7" Label="Uptime" />
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">Everything You Need to Scale</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">Powerful features to automate your sales, support, and lead generation on WhatsApp.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={<svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}
              title="AI Sales Assistant"
              description="Intelligent responses powered by AI that understand customer intent and drive conversions naturally."
            />
            <FeatureCard
              icon={<svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg>}
              title="WooCommerce Sync"
              description="Real-time product catalog sync. Share products, check inventory, and process orders instantly."
            />
            <FeatureCard
              icon={<svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>}
              title="Lead Analytics"
              description="Track conversations, monitor conversion rates, and gain insights into customer behavior."
            />
            <FeatureCard
              icon={<svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>}
              title="Multi-language Support"
              description="Automatically detect and respond in English, Urdu, Roman Urdu, and 50+ languages."
            />
            <FeatureCard
              icon={<svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>}
              title="Enterprise Security"
              description="End-to-end encryption for all conversations. SOC 2 compliant data handling."
            />
            <FeatureCard
              icon={<svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" /></svg>}
              title="Multi-tenant Ready"
              description="Manage multiple businesses from one dashboard. Perfect for agencies and resellers."
            />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-24 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">Up and Running in Minutes</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">Three simple steps to transform your customer communication.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-12">
            {[
              { step: "01", title: "Connect WhatsApp", description: "Link your WhatsApp Business account using Meta's Cloud API in just a few clicks." },
              { step: "02", title: "Sync Your Store", description: "Connect WooCommerce to automatically import products, prices, and inventory." },
              { step: "03", title: "Go Live", description: "Activate your AI assistant and start handling customer conversations automatically." }
            ].map((item, i) => (
              <div key={i} className="relative">
                <div className="text-8xl font-black text-slate-100 absolute -top-6 -left-4 select-none">{item.step}</div>
                <div className="relative">
                  <h3 className="text-2xl font-bold text-slate-900 mb-3">{item.title}</h3>
                  <p className="text-slate-600 leading-relaxed">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 px-6 bg-slate-50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">Simple, Transparent Pricing</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">Start free and upgrade as you grow. No hidden fees.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            <PricingCard
              tier="Starter"
              price="$0"
              description="Perfect for testing the waters"
              features={["1 WhatsApp number", "100 conversations/month", "Basic AI responses", "WooCommerce sync", "Email support"]}
              cta="Start Free"
            />
            <PricingCard
              tier="Professional"
              price="$49"
              description="For growing businesses"
              features={["3 WhatsApp numbers", "2,000 conversations/month", "Advanced AI with context", "Real-time analytics", "Priority support", "Custom branding"]}
              cta="Start Trial"
              popular
            />
            <PricingCard
              tier="Enterprise"
              price="Custom"
              description="For high-volume operations"
              features={["Unlimited WhatsApp numbers", "Unlimited conversations", "Custom AI training", "Dedicated account manager", "24/7 phone support", "SLA guarantee", "White-label option"]}
              cta="Contact Sales"
            />
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-24 px-6 bg-white">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">Frequently Asked Questions</h2>
            <p className="text-lg text-slate-600">Everything you need to know about ORVYN.</p>
          </div>
          <div className="space-y-4">
            {[
              { q: "Do I need a WhatsApp Business account?", a: "Yes, you'll need a WhatsApp Business account connected to Meta's Cloud API. We guide you through the setup process." },
              { q: "Can I use this with Shopify or other platforms?", a: "Currently we support WooCommerce and WordPress. Shopify integration is coming soon." },
              { q: "What happens if I exceed my conversation limit?", a: "You'll be notified before reaching your limit. Upgrade anytime or purchase additional conversation packs." },
              { q: "Is my data secure?", a: "Absolutely. All conversations are encrypted end-to-end, and we're SOC 2 compliant. We never sell your data." }
            ].map((faq, i) => (
              <details key={i} className="group bg-slate-50 rounded-xl border border-slate-100">
                <summary className="flex items-center justify-between cursor-pointer p-6 font-semibold text-slate-900">
                  {faq.q}
                  <svg className="w-5 h-5 text-slate-400 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                </summary>
                <div className="px-6 pb-6 text-slate-600">{faq.a}</div>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-gradient-to-br from-indigo-600 to-violet-700 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-extrabold mb-6">Ready to Transform Your Sales?</h2>
          <p className="text-xl text-indigo-100 mb-10 max-w-2xl mx-auto">Join hundreds of businesses using ORVYN to automate WhatsApp sales and support.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup" className="bg-white text-indigo-600 px-8 py-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5">Start Your Free Trial</Link>
            <Link href="/contact" className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-xl font-semibold hover:bg-white/10 transition-all">Talk to Sales</Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 bg-slate-900 text-slate-400">
        <div className="max-w-7xl mx-auto grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <Image src="/logo.png" alt="ORVYN" width={120} height={40} className="h-8 w-auto mb-4 brightness-0 invert" />
            <p className="text-sm">Turn conversations into conversions with AI-powered WhatsApp automation.</p>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4">Product</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="#features" className="hover:text-white transition-colors">Features</Link></li>
              <li><Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link></li>
              <li><Link href="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4">Company</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="#about" className="hover:text-white transition-colors">About</Link></li>
              <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
              <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
              <li><Link href="/terms" className="hover:text-white transition-colors">Terms</Link></li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto pt-8 border-t border-slate-800 text-center text-sm">
          © 2026 ORVYN. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
