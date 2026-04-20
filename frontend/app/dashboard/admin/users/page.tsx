"use client";
import { useEffect, useState } from "react";
import { apiGet, apiPost, apiPut, apiDelete, apiPatch } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ui";

interface User {
  id: number;
  email: string;
  full_name: string;
  role: "user" | "admin" | "super_admin";
  plan: "starter" | "growth";
  created_at: string;
  bot?: { status: boolean };
}

export default function UserManagementPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterRole, setFilterRole] = useState<string>("all");
  const [filterPlan, setFilterPlan] = useState<string>("all");
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const { showToast, ToastContainer } = useToast();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
    full_name: "",
    role: "user",
    plan: "starter",
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await apiGet<User[]>("/api/auth/admin/users");
      setUsers(data);
    } catch (err: any) {
      showToast(err.message || "Failed to fetch users", "error");
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.full_name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = filterRole === "all" || user.role === filterRole;
    const matchesPlan = filterPlan === "all" || user.plan === filterPlan;
    return matchesSearch && matchesRole && matchesPlan;
  });

  const openCreateModal = () => {
    setEditingUser(null);
    setFormData({ email: "", password: "", full_name: "", role: "user", plan: "starter" });
    setShowModal(true);
  };

  const openEditModal = (user: User) => {
    setEditingUser(user);
    setFormData({
      email: user.email,
      password: "",
      full_name: user.full_name || "",
      role: user.role,
      plan: user.plan,
    });
    setShowModal(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingUser) {
        await apiPut(`/api/auth/admin/update-user/${editingUser.id}`, {
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role,
          plan: formData.plan,
        });
        showToast("User updated successfully", "success");
      } else {
        if (!formData.password) {
          showToast("Password is required", "error");
          return;
        }
        await apiPost("/api/auth/admin/create-user", formData);
        showToast("User created successfully", "success");
      }
      setShowModal(false);
      fetchUsers();
    } catch (err: any) {
      showToast(err.message || "Operation failed", "error");
    }
  };

  const deleteUser = async (userId: number) => {
    if (!confirm("Are you sure? This will delete all user data.")) return;
    try {
      await apiDelete(`/api/auth/admin/users/${userId}`);
      showToast("User deleted successfully", "success");
      fetchUsers();
    } catch (err: any) {
      showToast(err.message || "Failed to delete user", "error");
    }
  };

  const toggleBotStatus = async (userId: number) => {
    try {
      await apiPatch(`/api/auth/admin/users/${userId}/status`, {});
      showToast("Bot status updated", "success");
      fetchUsers();
    } catch (err: any) {
      showToast(err.message || "Failed to update status", "error");
    }
  };

  const updatePlan = async (userId: number, newPlan: "starter" | "growth") => {
    try {
      await apiPatch(`/api/auth/admin/users/${userId}/plan`, { plan: newPlan });
      showToast(`User plan updated to ${newPlan}`, "success");
      fetchUsers();
    } catch (err: any) {
      showToast(err.message || "Failed to update plan", "error");
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <ToastContainer />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">User Management</h1>
          <p className="text-gray-400 font-medium mt-1 text-sm">Manage users, roles, and subscriptions</p>
        </div>
        <button
          onClick={openCreateModal}
          className="px-4 py-2 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 text-white rounded-xl text-sm font-semibold transition-all shadow-lg shadow-violet-900/30 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
          </svg>
          Add User
        </button>
      </div>

      {/* Filters */}
      <div className="bg-gray-900/50 backdrop-blur-sm p-4 rounded-xl border border-gray-800 shadow-xl">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div className="sm:col-span-2">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search by email or name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
            </div>
          </div>
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
          >
            <option value="all">All Roles</option>
            <option value="user">User</option>
            <option value="admin">Admin</option>
            <option value="super_admin">Super Admin</option>
          </select>
          <select
            value={filterPlan}
            onChange={(e) => setFilterPlan(e.target.value)}
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
          >
            <option value="all">All Plans</option>
            <option value="starter">Starter</option>
            <option value="growth">Growth</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 shadow-xl overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="text-gray-400 animate-pulse">Loading users...</div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-gray-800/50 border-b border-gray-800">
                  <th className="px-5 py-3 text-[9px] font-black text-gray-500 uppercase tracking-widest">User</th>
                  <th className="px-5 py-3 text-[9px] font-black text-gray-500 uppercase tracking-widest">Plan</th>
                  <th className="px-5 py-3 text-[9px] font-black text-gray-500 uppercase tracking-widest">Role</th>
                  <th className="px-5 py-3 text-[9px] font-black text-gray-500 uppercase tracking-widest text-center">Bot Status</th>
                  <th className="px-5 py-3 text-[9px] font-black text-gray-500 uppercase tracking-widest">Joined</th>
                  <th className="px-5 py-3 text-[9px] font-black text-gray-500 uppercase tracking-widest text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/50">
                {filteredUsers.map(user => (
                  <tr key={user.id} className="hover:bg-gray-800/30 transition-colors">
                    <td className="px-5 py-3.5">
                      <div>
                        <p className="font-semibold text-white text-sm">{user.email}</p>
                        {user.full_name && <p className="text-xs text-gray-500">{user.full_name}</p>}
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      <select
                        value={user.plan}
                        onChange={(e) => updatePlan(user.id, e.target.value as "starter" | "growth")}
                        className={`px-2.5 py-1.5 rounded-md text-[9px] font-black uppercase tracking-widest border focus:outline-none focus:ring-2 focus:ring-violet-500 ${
                          user.plan === 'growth'
                            ? 'bg-violet-500/20 text-violet-400 border-violet-500/30'
                            : 'bg-gray-700/20 text-gray-400 border-gray-700/30'
                        }`}
                      >
                        <option value="starter">Starter</option>
                        <option value="growth">Growth</option>
                      </select>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className={`px-2.5 py-1.5 rounded-md text-[9px] font-black uppercase tracking-widest ${
                        user.role === 'super_admin' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        user.role === 'admin' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                        'bg-gray-700/20 text-gray-400 border border-gray-700/30'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <button
                        onClick={() => toggleBotStatus(user.id)}
                        className={`px-3 py-1.5 rounded-md text-[9px] font-black uppercase tracking-widest transition-all ${
                          user.bot?.status !== false
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30'
                            : 'bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30'
                        }`}
                      >
                        {user.bot?.status !== false ? 'Active' : 'Inactive'}
                      </button>
                    </td>
                    <td className="px-5 py-3.5 text-xs text-gray-500">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => router.push(`/dashboard/admin/users/view?id=${user.id}`)}
                          className="p-1.5 text-violet-400 hover:bg-violet-500/20 rounded-md transition-colors"
                          title="View Details"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => openEditModal(user)}
                          className="p-1.5 text-blue-400 hover:bg-blue-500/20 rounded-md transition-colors"
                          title="Edit"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => deleteUser(user.id)}
                          className="p-1.5 text-red-400 hover:bg-red-500/20 rounded-md transition-colors"
                          title="Delete"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {!loading && filteredUsers.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p>No users found matching your filters</p>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-gray-900 rounded-xl border border-gray-700 shadow-2xl w-full max-w-md">
            <div className="p-5 border-b border-gray-700 flex items-center justify-between">
              <h3 className="text-lg font-bold text-white">{editingUser ? "Edit User" : "Create New User"}</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-white">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1.5">Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  placeholder="user@example.com"
                />
              </div>
              {!editingUser && (
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1.5">Password</label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                    placeholder="••••••••"
                  />
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1.5">Full Name</label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  placeholder="John Doe"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1.5">Role</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                    <option value="super_admin">Super Admin</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1.5">Plan</label>
                  <select
                    value={formData.plan}
                    onChange={(e) => setFormData({ ...formData, plan: e.target.value })}
                    className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  >
                    <option value="starter">Starter</option>
                    <option value="growth">Growth</option>
                  </select>
                </div>
              </div>
            </div>
            <div className="p-5 border-t border-gray-700 flex gap-3">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 px-4 py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-lg text-sm font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                className="flex-1 px-4 py-2.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 text-white rounded-lg text-sm font-semibold transition-all"
              >
                {editingUser ? "Update User" : "Create User"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
