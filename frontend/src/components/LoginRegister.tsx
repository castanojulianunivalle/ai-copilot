import { useState } from 'react';
import { motion } from 'framer-motion';
import { LogIn, UserPlus } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

type Props = {
  onSignIn: (email: string, password: string) => Promise<{ error?: string }>;
  onSignUp: (email: string, password: string) => Promise<{ error?: string }>;
  onResetPassword: (email: string) => Promise<{ error?: string }>;
};

export default function LoginRegister({ onSignIn, onSignUp, onResetPassword }: Props) {
  const [mode, setMode] = useState<'login' | 'register' | 'forgot'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (mode === 'forgot') {
      if (!email.trim()) { setError('Ingresa tu email'); return; }
      setLoading(true);
      try {
        const { error } = await onResetPassword(email);
        if (error) setError(error);
        else setSuccess('Te enviamos un correo con el enlace para restablecer tu contraseña.');
      } catch {
        setError('No pudimos conectar con el servidor. Revisa tu conexión e intenta de nuevo.');
      } finally {
        setLoading(false);
      }
      return;
    }

    if (!email.trim() || !password.trim()) {
      setError('Email y contraseña son requeridos');
      return;
    }
    if (mode === 'register' && password.length < 8) {
      setError('La contraseña debe tener mínimo 8 caracteres');
      return;
    }
    setLoading(true);
    try {
      const fn = mode === 'login' ? onSignIn : onSignUp;
      const { error } = await fn(email, password);
      if (error) setError(error);
      else if (mode === 'register') {
        setSuccess('Cuenta creada. Revisa tu email para confirmar (o inicia sesión si ya está activa).');
      }
    } catch {
      setError('No pudimos conectar con el servidor. Revisa tu conexión e intenta de nuevo.');
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
        <p className="text-gray-500 dark:text-gray-400 text-center mb-6">Support Co-Pilot - Semestre 1</p>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          {mode !== 'forgot' && (
            <div className="flex gap-2 mb-6">
              <button
                type="button"
                onClick={() => { setMode('login'); setError(''); setSuccess(''); }}
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                  mode === 'login'
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                <span className="flex items-center justify-center gap-2">
                  <LogIn className="w-4 h-4" /> Iniciar sesión
                </span>
              </button>
              <button
                type="button"
                onClick={() => { setMode('register'); setError(''); setSuccess(''); }}
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                  mode === 'register'
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                <span className="flex items-center justify-center gap-2">
                  <UserPlus className="w-4 h-4" /> Registrarse
                </span>
              </button>
            </div>
          )}

          {mode === 'forgot' && (
            <div className="mb-6">
              <h2 className="text-lg font-semibold">Recuperar contraseña</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Ingresa tu email y te enviaremos un enlace para restablecer tu contraseña.
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@email.com"
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-gray-900 dark:text-gray-100"
                autoComplete="email"
                disabled={loading}
              />
            </div>
            {mode !== 'forgot' && (
              <div>
                <label htmlFor="password" className="block text-sm font-medium mb-1">Contraseña</label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-gray-900 dark:text-gray-100"
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                  disabled={loading}
                  minLength={8}
                />
                {mode === 'login' && (
                  <button
                    type="button"
                    onClick={() => { setMode('forgot'); setError(''); setSuccess(''); }}
                    className="mt-1 text-xs text-primary-500 hover:underline float-right"
                  >
                    ¿Olvidaste tu contraseña?
                  </button>
                )}
              </div>
            )}
            {error && <p className="text-red-600 dark:text-red-400 text-sm clear-both">{error}</p>}
            {success && <p className="text-green-600 dark:text-green-400 text-sm clear-both">{success}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 px-4 rounded-lg bg-primary-500 hover:bg-primary-600 text-white font-medium disabled:opacity-50 clear-both"
            >
              {loading ? 'Procesando...' : mode === 'login' ? 'Iniciar sesión' : mode === 'register' ? 'Registrarse' : 'Enviar enlace'}
            </button>
            {mode === 'forgot' && (
              <button
                type="button"
                onClick={() => { setMode('login'); setError(''); setSuccess(''); }}
                className="w-full py-2 px-4 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600 font-medium"
              >
                Volver al inicio de sesión
              </button>
            )}
          </form>
        </div>
      </motion.div>
    </div>
  );
}
