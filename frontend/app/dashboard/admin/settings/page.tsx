"use client";
import { useState } from "react";
import { useToast } from "@/components/ui";

export default function AdminSettingsPage() {
  const { showToast, ToastContainer } = useToast();
  const [settings, setSettings] = useState({
    platformName: "ORVYN",
    maintenanceMode: false,
    allowRegistrations: true,
    defaultPlan: "starter",
  });

  const handleSave = () => {
    showToast("Settings saved successfully", "success");
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <ToastContainer />

      <div>
        <h1 className="text-3xl font-black text-white tracking-tight">Admin Settings</h1>
        <p className="text-slate-400 font-medium mt-1">Configure platform-wide settings</p>
      </div>

      {/* Platform Settings */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 shadow-xl p-6">
        <h3 className="text-lg font-bold text-white mb-6">Platform Configuration</h3>
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Platform Name</label>
            <input
              type="text"
              value={settings.platformName}
              onChange={(e) => setSettings({ ...settings, platformName: e.target.value })}
              className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="flex items-center justify-between p-4 bg-slate-900 rounded-xl border border-slate-700">
            <div>
              <p className="text-white font-semibold">Maintenance Mode</p>
              <p className="text-sm text-slate-400">Disable access to the platform for maintenance</p>
            </div>
            <button
              onClick={() => setSettings({ ...settings, maintenanceMode: !settings.maintenanceMode })}
              className={`w-12 h-6 rounded-full transition-colors ${
                settings.maintenanceMode ? 'bg-indigo-600' : 'bg-slate-700'
              } relative`}
            >
              <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                settings.maintenanceMode ? 'right-1' : 'left-1'
              }`} />
            </button>
          </div>
          <div className="flex items-center justify-between p-4 bg-slate-900 rounded-xl border border-slate-700">
            <div>
              <p className="text-white font-semibold">Allow New Registrations</p>
              <p className="text-sm text-slate-400">Enable or disable new user signups</p>
            </div>
            <button
              onClick={() => setSettings({ ...settings, allowRegistrations: !settings.allowRegistrations })}
              className={`w-12 h-6 rounded-full transition-colors ${
                settings.allowRegistrations ? 'bg-indigo-600' : 'bg-slate-700'
              } relative`}
            >
              <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                settings.allowRegistrations ? 'right-1' : 'left-1'
              }`} />
            </button>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Default Plan for New Users</label>
            <select
              value={settings.defaultPlan}
              onChange={(e) => setSettings({ ...settings, defaultPlan: e.target.value })}
              className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="starter">Starter ($1/mo)</option>
              <option value="growth">Growth ($3/mo)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white rounded-xl text-sm font-semibold transition-all shadow-lg shadow-indigo-900/30"
        >
          Save Settings
        </button>
      </div>
    </div>
  );
}
