"use client";
import { useState } from "react";

const helpSections = [
  {
    id: "overview",
    title: "Overview",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
    ),
    content: [
      {
        heading: "What is ORVYN?",
        text: "ORVYN is a WhatsApp automation platform that connects your website with WhatsApp Business to automate sales, inquiries, and customer support. It intelligently responds to customer messages using your website data."
      },
      {
        heading: "How It Works",
        text: "ORVYN syncs with your website or WooCommerce store to understand your products and services. When customers message your WhatsApp number, the bot automatically responds with relevant information based on their queries."
      }
    ]
  },
  {
    id: "setup-guide",
    title: "Setup Guide",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
    ),
    content: [
      {
        heading: "WhatsApp Token & Setup",
        text: "1. Go to the Meta Developer Portal and create a WhatsApp App. 2. In App Settings, find your 'Phone Number ID'. 3. Generate a 'Permanent Access Token' (recommended) or a temporary one. 4. In the WhatsApp integration tab, paste your Phone Number ID and Token. 5. Set a 'Verify Token' (any string) and copy the Webhook URL. 6. In Meta Portal, under WhatsApp > Configuration, paste the Webhook URL and Verify Token, then subscribe to 'messages' in Webhook Fields."
      },
      {
        heading: "WooCommerce Integration",
        text: "1. In your WordPress admin, go to WooCommerce > Settings > Advanced > REST API. 2. Click 'Add Key', set permissions to 'Read/Write', and generate keys. 3. Copy the Consumer Key and Consumer Secret. 4. In our Integrations > Website tab, enter your store URL and paste the keys. 5. Click 'Configure' then 'Synchronize Products' to load your catalog."
      }
    ]
  },
  {
    id: "setup",
    title: "Account Setup",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
      </svg>
    ),
    content: [
      {
        heading: "Step 1: WhatsApp Configuration",
        text: "Navigate to the Integrations page and provide your WhatsApp Cloud API phone number ID and generate a Meta Access Token from the Meta Developer Portal."
      },
      {
        heading: "Step 2: Website URL",
        text: "Enter your website URL. This is used to sync your products, services, and business information with the bot."
      },
      {
        heading: "Step 3: Verify Token",
        text: "Set a verify token and add the webhook URL (shown on the Integrations page) to your Meta Developer Portal webhook configuration."
      }
    ]
  },
  {
    id: "website",
    title: "Website Sync",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
      </svg>
    ),
    content: [
      {
        heading: "Product Based Business",
        text: "For WooCommerce stores. ORVYN syncs your products and categories automatically. Customers can browse products, check prices, and get product recommendations via WhatsApp."
      },
      {
        heading: "Service Based Business",
        text: "For WordPress or custom websites. ORVYN extracts service details, pricing information, and contact details from your website pages."
      },
      {
        heading: "Data Refresh",
        text: "Changes to your website URL or business type trigger an automatic data refresh. You can also manually synchronize products from the Integrations page."
      }
    ]
  },
  {
    id: "modes",
    title: "Bot Modes",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>
      </svg>
    ),
    content: [
      {
        heading: "Default Mode (Smart Sales)",
        text: "Uses built-in sales logic integrated with your website data. Best for automated product recommendations and service inquiries."
      },
      {
        heading: "Predefined Mode (Custom Rules)",
        text: "Uses keyword-based triggers to respond to specific customer messages. Set up custom responses for keywords like 'price', 'hours', 'location', etc."
      },
      {
        heading: "AI Powered Mode",
        text: "Uses large language models (GPT-4, Claude, Gemini, or Qwen) to answer questions based on your website content and custom instructions."
      }
    ]
  },
  {
    id: "troubleshooting",
    title: "Troubleshooting",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
      </svg>
    ),
    content: [
      {
        heading: "Bot Not Responding",
        text: "Verify your Meta Access Token has not expired. Confirm your WhatsApp number is correctly linked in the Integrations page. Ensure the webhook URL matches what is configured in the Meta Developer Portal."
      },
      {
        heading: "Empty or Incorrect Responses",
        text: "Update your website URL in the dashboard. Ensure your website is publicly accessible. Check if your product or service pages use standard HTML structures that the crawler can recognize."
      },
      {
        heading: "Sync Errors",
        text: "For WooCommerce, verify your Consumer Key and Secret are correct. For WordPress sites, ensure the REST API is enabled. Check that your website URL is accessible without authentication."
      }
    ]
  },
  {
    id: "api",
    title: "API Reference",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
      </svg>
    ),
    content: [
      {
        heading: "REST Endpoints",
        text: "The platform exposes internal REST endpoints for custom integrations. Available endpoints include /api/bots, /api/integrations, /api/webhook, and /api/auth."
      },
      {
        heading: "Authentication",
        text: "All API requests require a Bearer token obtained through the authentication endpoints. Include the token in the Authorization header."
      },
      {
        heading: "Webhook Events",
        text: "The webhook endpoint receives WhatsApp messages and status updates. Configure your webhook URL in the Meta Developer Portal to point to: your-domain.com/webhook"
      }
    ]
  }
];

export default function HelpCenterPage() {
  const [activeSection, setActiveSection] = useState("overview");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredSections = helpSections.filter(section =>
    section.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    section.content.some(item =>
      item.heading.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.text.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-slate-900">Help Center</h1>
        <p className="text-slate-500 max-w-xl mx-auto">
          Find answers and guidance on setting up, configuring, and using ORVYN
        </p>
      </div>

      {/* Search */}
      <div className="relative max-w-2xl mx-auto">
        <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
          <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-10m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search for help topics..."
          className="w-full pl-12 pr-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <nav className="sticky top-6 space-y-2">
            {helpSections.map((section) => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all ${
                  activeSection === section.id
                    ? "bg-blue-600 text-white shadow-md shadow-blue-200"
                    : "bg-white text-slate-600 hover:bg-slate-50 border border-slate-200"
                }`}
              >
                <span className={activeSection === section.id ? "text-white" : "text-slate-400"}>
                  {section.icon}
                </span>
                <span className="text-sm font-medium">{section.title}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-8">
          {filteredSections.map((section) => (
            <div
              key={section.id}
              id={section.id}
              className={`scroll-mt-24 ${activeSection === section.id ? "block" : "hidden lg:block"}`}
            >
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="px-6 py-5 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      activeSection === section.id ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-500"
                    }`}>
                      {section.icon}
                    </div>
                    <h2 className="text-lg font-semibold text-slate-900">{section.title}</h2>
                  </div>
                </div>

                <div className="p-6 space-y-6">
                  {section.content.map((item, index) => (
                    <div key={index} className="space-y-2">
                      <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                        {item.heading}
                      </h3>
                      <p className="text-slate-600 text-sm leading-relaxed pl-3.5">{item.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}

          {filteredSections.length === 0 && (
            <div className="text-center py-12 bg-white rounded-2xl border border-slate-200">
              <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-10m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
              </div>
              <p className="text-slate-500 font-medium">No results found for "{searchQuery}"</p>
              <p className="text-sm text-slate-400 mt-1">Try a different search term</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Links */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-100 p-8">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Links</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/dashboard/integrations"
            className="flex items-center gap-3 p-4 bg-white rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all"
          >
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z"/>
              </svg>
            </div>
            <div>
              <p className="font-medium text-slate-900">Integrations</p>
              <p className="text-xs text-slate-500">Configure WhatsApp & Website</p>
            </div>
          </a>
          <a
            href="/dashboard/settings"
            className="flex items-center gap-3 p-4 bg-white rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all"
          >
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </div>
            <div>
              <p className="font-medium text-slate-900">Settings</p>
              <p className="text-xs text-slate-500">Bot configuration & AI</p>
            </div>
          </a>
          <a
            href="/dashboard/test-chat"
            className="flex items-center gap-3 p-4 bg-white rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all"
          >
            <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
              </svg>
            </div>
            <div>
              <p className="font-medium text-slate-900">Sandbox</p>
              <p className="text-xs text-slate-500">Test your bot responses</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
