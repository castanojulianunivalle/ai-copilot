import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Users, Loader2, Shield, User, UserCog } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

type AdminUser = { id: string; email: string; role: string };

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export default function AdminUsers() {
  const { session } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState<string | null>(null);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/admin/users`, {
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Error al cargar usuarios');
      }
      const data = await res.json();
      setUsers(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error desconocido');
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (session) fetchUsers();
  }, [session]);

  const updateRole = async (userId: string, role: string) => {
    setUpdating(userId);
    try {
      const res = await fetch(`${API_URL}/admin/users/${userId}/role`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ role }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Error al actualizar rol');
      }
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role } : u))
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al actualizar');
    } finally {
      setUpdating(null);
    }
  };

  const roleLabel = (r: string) =>
    r === 'administrador' ? 'Administrador' : r === 'agente' ? 'Agente' : 'Cliente';

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-6 card"
    >
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-primary-400" />
        <h2 className="font-semibold">Gestión de usuarios</h2>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : users.length === 0 ? (
        <p className="text-slate-400 py-8 text-center">No hay usuarios registrados.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-left text-slate-400">
                <th className="pb-2 pr-4">Email</th>
                <th className="pb-2 pr-4">Rol actual</th>
                <th className="pb-2">Cambiar rol</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr
                  key={u.id}
                  className="border-b border-slate-700/50 hover:bg-slate-800/30"
                >
                  <td className="py-3 pr-4 font-mono text-xs text-slate-300">
                    {u.email || '(sin email)'}
                  </td>
                  <td className="py-3 pr-4">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs ${
                        u.role === 'administrador'
                          ? 'bg-purple-500/20 text-purple-300 border-purple-500/40'
                          : u.role === 'agente'
                          ? 'bg-blue-500/20 text-blue-300 border-blue-500/40'
                          : 'bg-slate-500/20 text-slate-300 border-slate-500/40'
                      }`}
                    >
                      {u.role === 'administrador' ? (
                        <Shield className="w-3 h-3" />
                      ) : u.role === 'agente' ? (
                        <UserCog className="w-3 h-3" />
                      ) : (
                        <User className="w-3 h-3" />
                      )}
                      {roleLabel(u.role)}
                    </span>
                  </td>
                  <td className="py-3">
                    <div className="flex gap-2">
                      {(['cliente', 'agente', 'administrador'] as const)
                        .filter((r) => r !== u.role)
                        .map((r) => (
                          <button
                            key={r}
                            onClick={() => updateRole(u.id, r)}
                            disabled={updating === u.id}
                            className="px-2 py-1 rounded border border-primary-500/50 hover:bg-primary-500/20 text-primary-400 text-xs disabled:opacity-50"
                          >
                            {updating === u.id ? (
                              <Loader2 className="w-3 h-3 animate-spin" />
                            ) : (
                              roleLabel(r)
                            )}
                          </button>
                        ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.section>
  );
}
