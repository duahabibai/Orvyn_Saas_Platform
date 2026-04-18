"use client";
import { useEffect, useState } from "react";
import { apiGet, apiPost, apiPatch } from "@/lib/api";
import { useToast } from "@/components/ui";

interface IntegrationData {
  id: number;
  bot_id: number;
  phone_number_id: string | null;
  whatsapp_number: string | null;
  verify_token: string;
  woocommerce_url: string | null;
  wp_base_url: string | null;
  business_type: string;
  has_whatsapp_token: boolean;
  whatsapp_token_preview: string;
  has_woo_keys: boolean;
  woo_products_cached: boolean;
  woo_categories_cached: any[];
  woo_products_count: number;
  webhook_url: string | null;
}

export default function IntegrationsPage() {
  const [integ, setInteg] = useState<IntegrationData | null>(null);
  const [userPlan, setUserPlan] = useState<string>("starter");
  const [whatsappForm, setWhatsappForm] = useState({
    whatsapp_token: "",
    phone_number_id: "",
    whatsapp_number: "",
    verify_token: "",
  });
  const [ecommerceForm, setEcommerceForm] = useState({
    website_url: "",
    consumer_key: "",
    consumer_secret: "",
  });
  const [integrationType, setIntegrationType] = useState<"product" | "service">("product");

  // Fetch user plan
  useEffect(() => {
    apiGet<any>("/api/auth/usage").then((data) => {
      if (data?.plan) setUserPlan(data.plan);
    }).catch(console.error);
  }, []);

  const [savingWhatsApp, setSavingWhatsApp] = useState(false);
  const [savingEcommerce, setSavingEcommerce] = useState(false);
  const [fetchingProducts, setFetchingProducts] = useState(false);
  const [buttonCode, setButtonCode] = useState("");
  const [activeTab, setActiveTab] = useState<"whatsapp" | "website" | "button">("whatsapp");
  const { showToast, ToastContainer } = useToast();

  const apiUrl = typeof window !== 'undefined' ? (window.location.origin.includes('localhost') ? 'http://localhost:8000' : window.location.origin) : '';
  const webhookUrl = `${apiUrl}/webhook`;

  useEffect(() => {
    apiGet<IntegrationData>("/api/integrations/me").then((data) => {
      setInteg(data);
      const bType = data.business_type || "product";
      setIntegrationType(bType as "product" | "service");
      setWhatsappForm({
        whatsapp_token: "",
        phone_number_id: data.phone_number_id || "",
        whatsapp_number: data.whatsapp_number || "",
        verify_token: data.verify_token || "",
      });
      setEcommerceForm({
        website_url: bType === "product" ? data.woocommerce_url || "" : data.wp_base_url || "",
        consumer_key: "",
        consumer_secret: "",
      });
    }).catch((error) => {
      console.error("Failed to fetch integrations:", error);
      showToast("Failed to load integration settings.", "error");
    });
  }, []);

  const handleSaveWhatsApp = async () => {
    setSavingWhatsApp(true);
    try {
      const payload = {
        whatsapp_token: whatsappForm.whatsapp_token || undefined,
        phone_number_id: whatsappForm.phone_number_id,
        whatsapp_number: whatsappForm.whatsapp_number,
        verify_token: whatsappForm.verify_token,
      };
      await apiPatch("/api/integrations/me", payload);
      showToast("WhatsApp settings saved successfully", "success");
      apiGet<IntegrationData>("/api/integrations/me").then(setInteg).catch(console.error);
    } catch (err: any) {
      showToast("Error saving WhatsApp settings: " + err.message, "error");
    } finally {
      setSavingWhatsApp(false);
    }
  };

  const handleConfigureBase = async () => {
    if (!ecommerceForm.website_url) {
        showToast("Website URL is required.", "warning");
        return;
    }
    // Block product integration for starter users - but ALLOW service integration
    if (userPlan === 'starter' && integrationType === 'product') {
        showToast("⚠️ Product features (WooCommerce) require Growth plan. Select 'Service Based' or upgrade to unlock product features.", "warning");
        return;
    }
    setSavingEcommerce(true);
    try {
        const payload = {
            integration_type: integrationType,
            website_url: ecommerceForm.website_url,
            consumer_key: integrationType === 'product' ? ecommerceForm.consumer_key : undefined,
            consumer_secret: integrationType === 'product' ? ecommerceForm.consumer_secret : undefined,
        };
        await apiPost("/api/integrations/me/configure-base", payload);
        const msg = integrationType === "product"
            ? "Product integration configured successfully!"
            : "Service integration configured successfully! WhatsApp will now use your website data.";
        showToast(msg, "success");
        apiGet<IntegrationData>("/api/integrations/me").then(setInteg).catch(console.error);
    } catch (err: any) {
        showToast("Error configuring integration: " + err.message, "error");
    } finally {
        setSavingEcommerce(false);
    }
  };

  const handleFetchProducts = async () => {
    setFetchingProducts(true);
    try {
      if (!ecommerceForm.website_url) {
          showToast("Please enter your store URL", "warning");
          setFetchingProducts(false);
          return;
      }
      await apiPost("/api/integrations/fetch-woocommerce", {
        woocommerce_url: ecommerceForm.website_url,
        woo_consumer_key: ecommerceForm.consumer_key,
        woo_consumer_secret: ecommerceForm.consumer_secret
      });
      showToast("Products synchronized successfully", "success");
      apiGet<IntegrationData>("/api/integrations/me").then(setInteg).catch(console.error);
    } catch (err: any) {
      showToast("Sync failed: " + err.message, "error");
    } finally {
      setFetchingProducts(false);
    }
  };

  const handleGenerateButton = () => {
    const phone = (whatsappForm.whatsapp_number || "").replace(/\D/g, '');
    if (!phone) {
      showToast("Please enter your WhatsApp number first", "warning");
      return;
    }
    const code = `<!-- WhatsApp Floating Button by ORVYN -->
<a href="https://wa.me/${phone}" target="_blank" style="position: fixed; bottom: 20px; right: 20px; background-color: #25D366; color: white; border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 4px 8px rgba(0,0,0,0.2); z-index: 9999;">
    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="white" viewBox="0 0 24 24">
        <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.438 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/>
    </svg>
</a>`;
    setButtonCode(code);
    showToast("Button code generated successfully", "success");
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    showToast(label + " copied", "success");
  };

  if (!integ) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-500 font-medium">Loading integrations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      <ToastContainer />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Integrations</h1>
          <p className="text-slate-500 mt-1">Connect WhatsApp and your website to power automated conversations</p>
        </div>
        <div className="flex items-center gap-3 bg-white px-4 py-2 rounded-xl border border-slate-200 shadow-sm">
          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium text-slate-600">Bot Active</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 bg-slate-100 p-1.5 rounded-xl w-fit">
        <button
          onClick={() => setActiveTab("whatsapp")}
          className={`px-5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
            activeTab === "whatsapp"
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          WhatsApp API
        </button>
        <button
          onClick={() => setActiveTab("website")}
          className={`px-5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
            activeTab === "website"
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Website Integration
        </button>
        <button
          onClick={() => setActiveTab("button")}
          className={`px-5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
            activeTab === "button"
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Chat Button
        </button>
      </div>

      {/* WhatsApp Tab */}
      {activeTab === "whatsapp" && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-100 bg-gradient-to-r from-emerald-50 to-teal-50">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">WhatsApp Cloud API</h2>
                <div className="flex items-center gap-2">
                  <p className="text-sm text-slate-500">Connect your WhatsApp Business number</p>
                  <span className="text-slate-300">•</span>
                  <a 
                    href="/dashboard/help" 
                    className="text-sm font-medium text-emerald-600 hover:text-emerald-700 hover:underline flex items-center gap-1"
                  >
                    Setup Guide
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Phone Number ID</label>
                <input
                  type="text"
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all"
                  value={whatsappForm.phone_number_id}
                  onChange={(e) => setWhatsappForm(prev => ({ ...prev, phone_number_id: e.target.value }))}
                  placeholder="e.g., 1723579972787150"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">WhatsApp Number</label>
                <input
                  type="text"
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all"
                  value={whatsappForm.whatsapp_number}
                  onChange={(e) => setWhatsappForm(prev => ({ ...prev, whatsapp_number: e.target.value }))}
                  placeholder="e.g., +14085551234"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Verify Token</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    className="flex-1 px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all"
                    value={whatsappForm.verify_token}
                    onChange={(e) => setWhatsappForm(prev => ({ ...prev, verify_token: e.target.value }))}
                    placeholder="Your verification token"
                  />
                  <button
                    onClick={() => copyToClipboard(whatsappForm.verify_token, "Verify Token")}
                    className="px-4 py-2 bg-slate-100 text-slate-700 font-medium rounded-xl hover:bg-slate-200 transition"
                  >
                    Copy
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">WhatsApp API Token</label>
                <input
                  type="password"
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all"
                  value={whatsappForm.whatsapp_token}
                  onChange={(e) => setWhatsappForm(prev => ({ ...prev, whatsapp_token: e.target.value }))}
                  placeholder="Enter your API token"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100">
              <div className="flex items-center justify-between bg-slate-50 rounded-xl p-4">
                <div>
                  <p className="text-sm font-medium text-slate-700">Webhook URL</p>
                  <p className="text-xs text-slate-500 mt-0.5">Add this to your Meta Developer Portal</p>
                </div>
                <div className="flex items-center gap-2">
                  <code className="px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm font-mono text-slate-600">
                    {integ.webhook_url || "http://localhost:8000/webhook"}
                  </code>
                  <button
                    onClick={() => copyToClipboard(integ.webhook_url || "http://localhost:8000/webhook", "Webhook URL")}
                    className="px-3 py-2 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 transition"
                  >
                    Copy
                  </button>
                </div>
              </div>
            </div>

            <button
              onClick={handleSaveWhatsApp}
              className="w-full py-3 bg-emerald-600 text-white font-semibold rounded-xl hover:bg-emerald-700 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
            >
              {savingWhatsApp ? "Saving..." : "Save WhatsApp Settings"}
            </button>
          </div>
        </div>
      )}

      {/* Website Tab */}
      {activeTab === "website" && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-100 bg-gradient-to-r from-blue-50 to-indigo-50">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">Website Integration</h2>
                <p className="text-sm text-slate-500">Connect your store or service website</p>
              </div>
            </div>
          </div>

          {/* Starter Plan Warning for Product Integration */}
          {userPlan === 'starter' && integrationType === 'product' && (
            <div className="p-4 bg-amber-50 border-b border-amber-200">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                <div className="flex-1">
                  <p className="text-amber-800 font-semibold text-sm">Product Features Require Growth Plan</p>
                  <p className="text-amber-700 text-xs mt-1">WooCommerce integration, product listing, and product-based flows are only available in the Growth plan ($3/month). Upgrade to unlock these features.</p>
                </div>
              </div>
            </div>
          )}

          <div className="p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Website URL</label>
              <input
                type="text"
                className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                value={ecommerceForm.website_url}
                onChange={(e) => setEcommerceForm(prev => ({ ...prev, website_url: e.target.value }))}
                placeholder="e.g., https://example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-3">Integration Type</label>
              <div className="flex gap-4">
                <button
                  onClick={() => setIntegrationType("product")}
                  className={`flex-1 py-4 px-4 rounded-xl border-2 transition-all ${
                    integrationType === "product"
                      ? "border-blue-600 bg-blue-50"
                      : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                      integrationType === "product" ? "border-blue-600" : "border-slate-300"
                    }`}>
                      {integrationType === "product" && <div className="w-2.5 h-2.5 bg-blue-600 rounded-full"></div>}
                    </div>
                    <div className="text-left">
                      <p className="font-semibold text-slate-900">Product Based</p>
                      <p className="text-xs text-slate-500">For WooCommerce stores</p>
                    </div>
                  </div>
                </button>
                <button
                  onClick={() => setIntegrationType("service")}
                  className={`flex-1 py-4 px-4 rounded-xl border-2 transition-all ${
                    integrationType === "service"
                      ? "border-blue-600 bg-blue-50"
                      : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                      integrationType === "service" ? "border-blue-600" : "border-slate-300"
                    }`}>
                      {integrationType === "service" && <div className="w-2.5 h-2.5 bg-blue-600 rounded-full"></div>}
                    </div>
                    <div className="text-left">
                      <p className="font-semibold text-slate-900">Service Based</p>
                      <p className="text-xs text-slate-500">For WordPress or custom sites</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            {integrationType === "product" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Consumer Key (Optional)</label>
                  <input
                    type="password"
                    className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    value={ecommerceForm.consumer_key}
                    onChange={(e) => setEcommerceForm(prev => ({ ...prev, consumer_key: e.target.value }))}
                    placeholder="Enter Consumer Key"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Consumer Secret (Optional)</label>
                  <input
                    type="password"
                    className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    value={ecommerceForm.consumer_secret}
                    onChange={(e) => setEcommerceForm(prev => ({ ...prev, consumer_secret: e.target.value }))}
                    placeholder="Enter Consumer Secret"
                  />
                </div>
              </div>
            )}

            {integ.woo_products_cached && integ.business_type === "product" && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"/>
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-emerald-900">Products Synchronized</p>
                    <p className="text-sm text-emerald-700">{integ.woo_products_count} products and {integ.woo_categories_cached.length} categories cached</p>
                  </div>
                </div>
              </div>
            )}

            <div className="flex gap-4 pt-4 border-t border-slate-100">
              <button
                onClick={handleConfigureBase}
                className="flex-1 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                {savingEcommerce ? "Configuring..." : "Configure Integration"}
              </button>
              {integrationType === "product" && ecommerceForm.website_url && (
                <button
                  onClick={handleFetchProducts}
                  className="flex-1 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  {fetchingProducts ? "Synchronizing..." : "Synchronize Products"}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Chat Button Tab */}
      {activeTab === "button" && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-100 bg-gradient-to-r from-green-50 to-emerald-50">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-600 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">WhatsApp Chat Button</h2>
                <p className="text-sm text-slate-500">Add a floating chat button to your website</p>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">WhatsApp Number</label>
              <input
                type="text"
                className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition-all"
                value={whatsappForm.whatsapp_number}
                onChange={(e) => setWhatsappForm(prev => ({ ...prev, whatsapp_number: e.target.value }))}
                placeholder="e.g., +14085551234"
              />
            </div>

            <button
              onClick={handleGenerateButton}
              className="w-full py-3 bg-green-600 text-white font-semibold rounded-xl hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            >
              Generate Button Code
            </button>

            {buttonCode && (
              <div className="border-t border-slate-100 pt-6">
                <label className="block text-sm font-medium text-slate-700 mb-3">HTML Code</label>
                <div className="relative">
                  <pre className="bg-slate-900 text-slate-100 p-4 rounded-xl overflow-x-auto text-xs font-mono leading-relaxed">
                    {buttonCode}
                  </pre>
                  <button
                    onClick={() => copyToClipboard(buttonCode, "Button Code")}
                    className="absolute top-2 right-2 px-3 py-1.5 bg-white/10 text-white text-sm font-medium rounded-lg hover:bg-white/20 transition"
                  >
                    Copy
                  </button>
                </div>
                <p className="text-xs text-slate-500 mt-3">Paste this code before the closing tag of your website.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
