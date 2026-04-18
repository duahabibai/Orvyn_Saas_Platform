"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useToast } from "@/components/ui";

const MODELS: Record<string, any[]> = {
  openrouter: [
    {"value": "openai/gpt-4o", "label": "GPT-4o", "desc": "Most intelligent model", "badge": "Premium"},
    {"value": "anthropic/claude-3.5-sonnet", "label": "Claude 3.5 Sonnet", "desc": "Best for coding & nuance", "badge": "Popular"},
    {"value": "google/gemini-pro-1.5", "label": "Gemini Pro 1.5", "desc": "Huge context window", "badge": "New"},
    {"value": "meta-llama/llama-3.1-70b-instruct", "label": "Llama 3.1 70B", "desc": "Top open source model", "badge": "Open"},
    {"value": "openai/gpt-oss-20b:free", "label": "GPT-OSS 20B", "desc": "Good for simple tasks", "badge": "Free"},
  ],
  openai: [
    {"value": "gpt-4o", "label": "GPT-4o", "desc": "Flagship high-intelligence model", "badge": "Latest"},
    {"value": "gpt-4o-mini", "label": "GPT-4o Mini", "desc": "Fast & affordable for most tasks", "badge": "Fast"},
    {"value": "o1", "label": "O1", "desc": "Advanced reasoning & logic", "badge": "Reasoning"},
    {"value": "o1-mini", "label": "O1 Mini", "desc": "Fast reasoning & logic", "badge": "Logic"},
    {"value": "o3-mini", "label": "O3 Mini", "desc": "Latest reasoning model", "badge": "Latest"},
  ],
  gemini: [
    {"value": "gemini-2.0-flash", "label": "Gemini 2.0 Flash", "desc": "Ultra-fast flagship model", "badge": "Speed"},
    {"value": "gemini-2.0-pro", "label": "Gemini 2.0 Pro", "desc": "Highest intelligence Gemini", "badge": "Pro"},
    {"value": "gemini-2.0-flash-lite", "label": "Gemini 2.0 Lite", "desc": "Efficient everyday model", "badge": "Efficient"},
  ],
  qwen: [
    {"value": "qwen-plus", "label": "Qwen Plus", "desc": "Enhanced capabilities", "badge": "Balanced"},
    {"value": "qwen-max", "label": "Qwen Max", "desc": "Maximum intelligence", "badge": "Powerful"},
    {"value": "qwen-turbo", "label": "Qwen Turbo", "desc": "Extremely fast response", "badge": "Turbo"},
    {"value": "qwen-long", "label": "Qwen Long", "desc": "Long context support", "badge": "Context"},
  ],
};

const PROVIDER_INFO: Record<string, any> = {
  openrouter: { label: "OpenRouter", icon: "🌐", color: "text-blue-600", bg: "bg-blue-50" },
  openai: { label: "OpenAI", icon: "🤖", color: "text-emerald-600", bg: "bg-emerald-50" },
  gemini: { label: "Google Gemini", icon: "✨", color: "text-indigo-600", bg: "bg-indigo-50" },
  qwen: { label: "Alibaba Qwen", icon: "🐉", color: "text-rose-600", bg: "bg-rose-50" },
};

export default function SettingsPage() {
  const [bot, setBot] = useState<any>(null);
  const [settings, setSettings] = useState<any>(null);
  const [usage, setUsage] = useState<any>(null);
  const [mode, setMode] = useState("default");
  const [prompt, setPrompt] = useState("");
  const [provider, setProvider] = useState("openrouter");
  const [modelName, setModelName] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [temperature, setTemperature] = useState(70);
  const [language, setLanguage] = useState("english");
  const [saving, setSaving] = useState(false);
  const [customResponses, setCustomResponses] = useState<Array<{keyword: string, response: string}>>([]);
  const [customProducts, setCustomProducts] = useState<Array<{name: string, description: string, image_url: string}>>([]);
  
  const { showToast, ToastContainer } = useToast();

  useEffect(() => {
    Promise.all([
      api("/api/bots/me").catch(() => null),
      api("/api/bots/settings").catch(() => null),
      api("/api/auth/usage").catch(() => null),
    ]).then(([b, s, u]) => {
      setBot(b);
      setSettings(s);
      setUsage(u);
      if (b) setMode(b.mode);
      if (s) {
        setPrompt(s.prompt || "");
        const currentProvider = s.model_name || "openrouter";
        setProvider(currentProvider);
        
        const availableModels = MODELS[currentProvider] || MODELS.openrouter;
        setModelName(s.specific_model_name || availableModels[0].value);
        
        setTemperature(s.temperature || 70);
        setLanguage(s.language || "english");
        
        if (s.custom_responses && typeof s.custom_responses === "object") {
          const entries = Object.entries(s.custom_responses).map(([keyword, response]) => ({
            keyword,
            response: response as string,
          }));
          setCustomResponses(entries);
        }

        if (s.custom_products && Array.isArray(s.custom_products)) {
          setCustomProducts(s.custom_products);
        }
      }
    });
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const customResponsesObj: Record<string, string> = {};
      customResponses.forEach(cr => {
        if (cr.keyword.trim()) {
          customResponsesObj[cr.keyword.trim().toLowerCase()] = cr.response;
        }
      });

      await Promise.all([
        api("/api/bots/mode", { method: "PATCH", body: JSON.stringify({ mode }) }),
        api("/api/bots/settings", {
          method: "PATCH",
          body: JSON.stringify({
            prompt,
            model_name: provider,
            specific_model_name: modelName,
            temperature,
            language,
            custom_responses: customResponsesObj,
            custom_products: customProducts.filter(p => p.name.trim()),
            ...(apiKey ? { api_key: apiKey } : {}),
          }),
        }),
      ]);
      showToast("Settings saved successfully!", "success");
    } catch (err: any) {
      showToast(err.message || "Failed to save settings", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleProviderChange = (newProvider: string) => {
    setProvider(newProvider);
    const availableModels = MODELS[newProvider] || MODELS.openrouter;
    setModelName(availableModels[0].value);
  };

  const addCustomResponse = () => {
    if (customResponses.length >= 50) {
      showToast("Maximum limit of 50 rules reached", "warning");
      return;
    }
    setCustomResponses([...customResponses, { keyword: "", response: "" }]);
  };

  const handleImportJSON = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.endsWith('.json')) {
      showToast("Please select a valid JSON file", "error");
      return;
    }
    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        let entries: Array<{keyword: string, response: string}> = [];
        if (typeof json === 'object' && !Array.isArray(json)) {
          entries = Object.entries(json).map(([keyword, response]) => ({
            keyword,
            response: typeof response === 'string' ? response : JSON.stringify(response),
          }));
        } else if (Array.isArray(json)) {
          entries = json.map(item => ({
            keyword: item.keyword || item.trigger || item.key || '',
            response: item.response || item.message || item.reply || '',
          })).filter(entry => entry.keyword && entry.response);
        }
        if (entries.length > 0) {
          setCustomResponses(entries.slice(0, 50));
          showToast(`Imported ${entries.length} rules!`, "success");
        }
      } catch (err) {
        showToast("Invalid JSON file", "error");
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  if (!bot) return <div className="text-slate-500 animate-pulse font-bold text-center py-20 uppercase tracking-widest">Loading Automation...</div>;

  return (
    <div className="space-y-10 max-w-4xl pb-32 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <ToastContainer />
      
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Automation Settings</h1>
          <p className="text-slate-500 font-medium">Configure how ORVYN interacts with your customers</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between group hover:border-blue-500 transition-all">
          <div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">WhatsApp Usage</p>
            <p className="text-2xl font-black text-slate-900">{usage?.whatsapp_messages_sent || 0} <span className="text-slate-300 font-medium text-sm">/ {usage?.whatsapp_limit || 0}</span></p>
          </div>
          <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between group hover:border-purple-500 transition-all">
          <div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">AI Smart Usage</p>
            <p className="text-2xl font-black text-slate-900">{usage?.ai_requests_made || 0} <span className="text-slate-300 font-medium text-sm">/ {usage?.ai_limit || 0}</span></p>
          </div>
          <div className="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Modes */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { value: "default", label: "Smart Sales", desc: "Built-in catalog flow" },
          { value: "predefined", label: "Custom Rules", desc: "Keyword-based logic" },
          { value: "ai", label: "AI Powered", desc: "Ultimate intelligence" },
        ].map(opt => (
          <button key={opt.value} onClick={() => setMode(opt.value)}
            className={`flex flex-col items-center text-center gap-3 p-6 rounded-[2rem] border-2 transition-all duration-500 ${
              mode === opt.value
              ? "border-blue-600 bg-white shadow-2xl shadow-blue-100 -translate-y-1"
              : "border-slate-100 bg-white hover:border-slate-300"
            }`}>
            <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-colors ${
              mode === opt.value ? "bg-blue-600 text-white" : "bg-slate-50 text-slate-400"
            }`}>
              {opt.value === "default" && (
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              )}
              {opt.value === "predefined" && (
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              )}
              {opt.value === "ai" && (
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.183.394l-1.158.907a.5.5 0 01-.71-.74l1.9-1.9a2 2 0 00.586-1.414V9.236a2 2 0 00-.586-1.414l-1.9-1.9a.5.5 0 01.71-.74l1.158.907a2 2 0 001.183.394l2.533-.317a6 6 0 013.86.517l.318.158a6 6 0 003.86.517l2.387-.477a2 2 0 011.022.547l.64.718a.5.5 0 01-.064.736l-1.144.858a2 2 0 00-.6 2.012l.4 2.153a.5.5 0 01-.75.547l-1.393-1.045a2 2 0 00-2.31 0l-1.393 1.045a.5.5 0 01-.75-.547l.4-2.153a2 2 0 00-.6-2.012l-1.144-.858a.5.5 0 01-.064-.736l.64-.718z" />
                </svg>
              )}
            </div>
            <div>
              <div className="font-black text-slate-900 tracking-tight">{opt.label}</div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">{opt.desc}</div>
            </div>
          </button>
        ))}
      </div>

      {/* Main Settings Card */}
      <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-2xl shadow-slate-200/40 overflow-hidden">
        {mode === "predefined" && (
          <div className="p-10 space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-black text-slate-900 tracking-tight">Keyword Rules</h2>
                <p className="text-slate-500 text-sm font-medium">Auto-reply when customers use specific words</p>
              </div>
              <div className="flex gap-2">
                <label className="cursor-pointer bg-slate-50 text-slate-600 px-4 py-2 rounded-xl border border-slate-200 hover:bg-slate-100 font-bold text-xs transition-all">
                  Import
                  <input type="file" accept=".json" onChange={handleImportJSON} className="hidden" />
                </label>
                <button onClick={() => {
                  const sampleRules = {
                    "price": "Our prices vary by product. Type 'products' to see our catalog or visit our website!",
                    "order": "To place an order, please tell me: 1) Product name 2) Quantity 3) Your address",
                    "delivery": "We deliver nationwide in 3-5 business days. Delivery charges: Rs. 200 for orders under Rs. 2000, FREE above Rs. 2000",
                    "return": "We offer 7-day return policy on unused items with original packaging. Contact us at support@example.com",
                    "contact": "📞 Phone: +92-300-1234567\n📧 Email: support@example.com\n📍 Address: Karachi, Pakistan"
                  };
                  const blob = new Blob([JSON.stringify(sampleRules, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = 'sample-rules.json';
                  a.click();
                  URL.revokeObjectURL(url);
                  showToast("Sample rules downloaded! Import this file to get started", "success");
                }} className="bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 font-bold text-xs shadow-lg transition-all active:scale-95">
                  Download Sample
                </button>
                <button onClick={addCustomResponse} className="bg-slate-900 text-white px-6 py-2 rounded-xl hover:bg-black font-bold text-xs shadow-lg transition-all active:scale-95">
                  Add Rule
                </button>
              </div>
            </div>

            <div className="space-y-4">
              {customResponses.map((cr, index) => (
                <div key={index} className="group bg-slate-50/50 hover:bg-white rounded-3xl p-6 border border-slate-100 hover:border-blue-200 transition-all duration-300 relative">
                  <button onClick={() => setCustomResponses(customResponses.filter((_, i) => i !== index))}
                    className="absolute top-4 right-4 w-8 h-8 rounded-full bg-rose-50 text-rose-500 flex items-center justify-center font-bold hover:bg-rose-500 hover:text-white transition-all opacity-0 group-hover:opacity-100">✕</button>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Trigger Word</label>
                      <input type="text" value={cr.keyword} onChange={e => {
                        const updated = [...customResponses];
                        updated[index].keyword = e.target.value;
                        setCustomResponses(updated);
                      }} className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm font-black text-blue-600 focus:border-blue-500 outline-none" placeholder="e.g. price" />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Automated Reply</label>
                      <textarea value={cr.response} onChange={e => {
                        const updated = [...customResponses];
                        updated[index].response = e.target.value;
                        setCustomResponses(updated);
                      }} className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm font-medium focus:border-blue-500 outline-none" rows={2} placeholder="The price of our product is..." />
                    </div>
                  </div>
                </div>
              ))}
              {customResponses.length === 0 && (
                <div className="text-center py-10 border-2 border-dashed border-slate-100 rounded-[2rem]">
                  <p className="text-slate-400 font-bold text-sm">No rules added yet</p>
                </div>
              )}
            </div>
          </div>
        )}

        {mode === "default" && (
          <div className="p-16 text-center space-y-6">
            <div className="w-24 h-24 bg-blue-50 text-blue-600 rounded-[2rem] flex items-center justify-center mx-auto">
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h2 className="text-2xl font-black text-slate-900 tracking-tight">Smart Sales Flow Active</h2>
              <p className="text-slate-500 font-medium max-w-sm mx-auto mt-2">ORVYN will automatically handle customer inquiries using your website's products and contact information.</p>
            </div>
          </div>
        )}

        {mode === "ai" && (
          <div className="p-10 space-y-12">
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-10">
              <div className="lg:col-span-3 space-y-6">
                <div>
                  <h2 className="text-2xl font-black text-slate-900 tracking-tight">AI Personality</h2>
                  <p className="text-slate-500 text-sm font-medium">Instruct your AI assistant on how to behave</p>
                </div>
                <div className="relative">
                  <textarea value={prompt} onChange={e => setPrompt(e.target.value)} rows={10}
                    className="w-full bg-slate-50 border border-slate-100 rounded-[2.5rem] p-8 text-sm font-medium focus:bg-white focus:border-blue-500 focus:shadow-xl transition-all outline-none leading-relaxed"
                    placeholder="e.g. You are a professional sales agent for a fashion brand. Be helpful, friendly, and always try to guide customers to our best sellers..." />
                  <div className="absolute bottom-6 right-8 text-[10px] font-black text-slate-300 uppercase tracking-widest">System Prompt</div>
                </div>
              </div>
              
              <div className="lg:col-span-2 space-y-8 bg-slate-50/50 p-8 rounded-[2.5rem] border border-slate-50">
                <h3 className="text-lg font-black text-slate-900 tracking-tight flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" />
                  Brain Configuration
                </h3>
                
                <div className="space-y-6">
                  {/* Provider Dropdown */}
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-2">Provider</label>
                    <div className="relative">
                      <select 
                        value={provider} 
                        onChange={e => handleProviderChange(e.target.value)} 
                        className={`w-full appearance-none p-4 pl-12 rounded-2xl border-2 border-white bg-white shadow-sm font-black text-sm focus:border-blue-500 outline-none transition-all cursor-pointer ${PROVIDER_INFO[provider]?.color}`}
                      >
                        {Object.keys(MODELS).map(p => (
                          <option key={p} value={p}>{PROVIDER_INFO[p]?.label || p.toUpperCase()}</option>
                        ))}
                      </select>
                      <div className="absolute left-4 top-1/2 -translate-y-1/2 text-lg">
                        {PROVIDER_INFO[provider]?.icon}
                      </div>
                      <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
                        <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>
                  </div>

                  {/* Model Dropdown */}
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-2">Specific Model</label>
                    <div className="relative">
                      <select 
                        value={modelName} 
                        onChange={e => setModelName(e.target.value)} 
                        className="w-full appearance-none p-4 rounded-2xl border-2 border-white bg-white shadow-sm font-bold text-sm text-slate-700 focus:border-blue-500 outline-none transition-all cursor-pointer"
                      >
                        {(MODELS[provider] || []).map(m => (
                          <option key={m.value} value={m.value}>{m.label}</option>
                        ))}
                      </select>
                      <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
                        <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>
                    {/* Model Info Display */}
                    <div className="mt-3 px-2">
                      {MODELS[provider]?.find(m => m.value === modelName) && (
                        <div className="space-y-1 animate-in fade-in slide-in-from-top-1">
                          <div className="flex items-center gap-2">
                            <span className="bg-blue-100 text-blue-700 text-[9px] font-black uppercase px-2 py-0.5 rounded-full">
                              {MODELS[provider].find(m => m.value === modelName).badge}
                            </span>
                          </div>
                          <p className="text-[10px] text-slate-400 font-bold leading-tight">
                            {MODELS[provider].find(m => m.value === modelName).desc}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2 pt-4">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-2">Secret API Key</label>
                    <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)} 
                      className="w-full p-4 rounded-2xl border-2 border-white bg-white shadow-sm text-sm focus:border-blue-500 outline-none transition-all font-mono" 
                      placeholder="••••••••••••••••" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Language */}
      <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-2xl shadow-slate-200/40 p-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h3 className="text-xl font-black text-slate-900 tracking-tight">Bot Language</h3>
          <p className="text-slate-500 text-sm font-medium">Customer communication language</p>
        </div>
        <div className="flex bg-slate-50 p-2 rounded-2xl border border-slate-100">
          {['english', 'roman_urdu', 'urdu'].map(l => (
            <button key={l} onClick={() => setLanguage(l)}
              className={`px-8 py-3 rounded-xl font-black text-xs uppercase tracking-widest transition-all ${
                language === l 
                ? "bg-blue-600 text-white shadow-xl shadow-blue-200 scale-105" 
                : "text-slate-400 hover:text-slate-600"
              }`}>{l.replace('_', ' ')}</button>
          ))}
        </div>
      </div>

      <div className="flex justify-center pt-10">
        <button onClick={handleSave} disabled={saving}
          className="group relative bg-slate-900 text-white px-20 py-6 rounded-[2.5rem] font-black text-xl hover:bg-blue-600 disabled:opacity-50 shadow-2xl transition-all active:scale-95 overflow-hidden">
          <span className="relative z-10">{saving ? "SAVING SETTINGS..." : "SAVE ALL SETTINGS"}</span>
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity" />
        </button>
      </div>
    </div>
  );
}
