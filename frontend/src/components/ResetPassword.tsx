import { useState } from 'react';
import { motion } from 'framer-motion';
import ThemeToggle from './ThemeToggle';

type Props = {
  onSubmit: (password: string) => Promise<{ error?: string }>;
};

export default function ResetPassword({ onSubmit }: Props) {
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (password.length < 8) { setError('La contraseña debe tener mínimo 8 caracteres'); return; }
    if (password !== confirm) { setError('Las contraseñas no coinciden'); return; }
    setLoading(true);
    try {
      const { error } = await onSubmit(password);
      if (error) setError(error);
      else setSuccess('Contraseña actualizada. Ya puedes iniciar sesión.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 flex flex-col items-center justify-center">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="flex justify-center mb-6">
          <img src="/logo.svg" alt="Logo" className="h-16 w-16" />
        </div>
        <h1 className="text-2xl font-bold text-center mb-2">Mesa de Ayuda</h1>
        <p className="text-gray-500 dark:text-gray-400 text-center mb-6">Restablece tu contraseña</p>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="new-password" className="block text-sm font-medium mb-1">Nueva contraseña</label>
              <input
                id="new-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-gray-900 dark:text-gray-100"
                autoComplete="new-password"
                disabled={loading}
                minLength={8}
              />
            </div>
            <div>
              <label htmlFor="confirm-password" className="block text-sm font-medium mb-1">Confirmar contraseña</label>
              <input
                id="confirm-password"
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-gray-900 dark:text-gray-100"
                autoComplete="new-password"
                disabled={loading}
              />
            </div>
            {error && <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>}
            {success && <p className="text-green-600 dark:text-green-400 text-sm">{success}</p>}
            <button
              type="submit"
              disabled={loading || !!success}
              className="w-full py-2 px-4 rounded-lg bg-primary-500 hover:bg-primary-600 text-white font-medium disabled:opacity-50"
            >
              {loading ? 'Guardando...' : 'Guardar nueva contraseña'}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
