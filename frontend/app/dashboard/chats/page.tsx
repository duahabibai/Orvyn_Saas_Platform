"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function ConversationsPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [phones, setPhones] = useState<string[]>([]);
  const [selectedPhone, setSelectedPhone] = useState<string>("");
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api("/api/chats?limit=200").then((data: any) => {
      setMessages(data);
      const unique = [...new Set(data.map((m: any) => m.phone_number))] as string[];
      setPhones(unique);
      if (unique.length > 0) setSelectedPhone(unique[0]);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedPhone) {
      api(`/api/chats?phone_number=${encodeURIComponent(selectedPhone)}&limit=100`).then((data: any) => {
        setChatMessages(data.reverse());
      }).catch(() => {});
    }
  }, [selectedPhone]);

  if (loading) return <div className="text-slate-500 animate-pulse">Loading conversations...</div>;

  return (
    <div className="h-[calc(100vh-160px)] flex flex-col space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Conversations</h1>
        <p className="text-slate-500 font-medium">Real-time interaction log between ORVYN and your customers</p>
      </div>

      <div className="flex-1 flex gap-8 min-h-0">
        {/* Sidebar: Contacts */}
        <div className="w-80 bg-white rounded-[2.5rem] border border-slate-200 shadow-xl shadow-slate-200/50 flex flex-col overflow-hidden">
          <div className="p-6 border-b border-slate-100 bg-slate-50/50">
            <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest">Active Chats ({phones.length})</h2>
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar">
            {phones.map(phone => (
              <button key={phone} onClick={() => setSelectedPhone(phone)}
                className={`w-full text-left p-6 border-b border-slate-50 transition-all duration-200 group relative ${
                  selectedPhone === phone ? "bg-blue-50/50" : "hover:bg-slate-50"
                }`}>
                {selectedPhone === phone && <div className="absolute left-0 top-0 bottom-0 w-1 bg-blue-600" />}
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
                    selectedPhone === phone ? "bg-blue-600 text-white shadow-lg shadow-blue-200" : "bg-slate-100 text-slate-500"
                  }`}>
                    {phone.slice(-2)}
                  </div>
                  <div>
                    <p className={`font-bold text-sm ${selectedPhone === phone ? "text-blue-600" : "text-slate-700"}`}>{phone}</p>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tight">WhatsApp User</p>
                  </div>
                </div>
              </button>
            ))}
            {phones.length === 0 && (
              <div className="p-10 text-center space-y-2 opacity-40">
                <span className="text-4xl block">📬</span>
                <p className="text-[10px] font-black uppercase tracking-widest">No chats yet</p>
              </div>
            )}
          </div>
        </div>

        {/* Chat Window */}
        <div className="flex-1 bg-white rounded-[2.5rem] border border-slate-200 shadow-2xl shadow-slate-200/50 flex flex-col overflow-hidden relative">
          {!selectedPhone ? (
            <div className="flex-1 flex flex-col items-center justify-center p-10 text-center space-y-4">
              <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center text-4xl">💬</div>
              <h2 className="text-xl font-black text-slate-900">Select a conversation</h2>
              <p className="text-slate-400 font-medium max-w-xs">Pick a contact from the left to view the message history with ORVYN.</p>
            </div>
          ) : (
            <>
              <div className="p-6 border-b border-slate-100 bg-white/80 backdrop-blur-md flex items-center justify-between sticky top-0 z-10">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-sm shadow-xl">
                    {selectedPhone.slice(-2)}
                  </div>
                  <div>
                    <h2 className="font-black text-slate-900 leading-tight">{selectedPhone}</h2>
                    <div className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                      <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Active via WhatsApp</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar bg-slate-50/30">
                {chatMessages.map((m: any) => (
                  <div key={m.id} className={`flex flex-col ${m.sender === "user" ? "items-start" : "items-end"} group animate-in fade-in slide-in-from-top-2 duration-300`}>
                    <div className={`max-w-[80%] rounded-3xl px-6 py-4 shadow-sm text-sm font-medium ${
                      m.sender === "user" 
                      ? "bg-white text-slate-700 border border-slate-100 rounded-bl-none" 
                      : "bg-blue-600 text-white rounded-br-none shadow-blue-100"
                    }`}>
                      <p className="leading-relaxed">{m.message}</p>
                    </div>
                    <div className="flex items-center gap-2 mt-2 px-2">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                        {new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                      {m.sender === "bot" && (
                        <span className="text-[10px] font-black text-blue-500 uppercase tracking-widest">Sent by ORVYN</span>
                      )}
                    </div>
                  </div>
                ))}
                {chatMessages.length === 0 && (
                  <div className="flex flex-col items-center justify-center py-20 opacity-30">
                    <span className="text-4xl mb-4">🔇</span>
                    <p className="text-xs font-black uppercase tracking-widest">No messages in this chat</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
