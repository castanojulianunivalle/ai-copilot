import { useState } from 'react';
import { motion } from 'framer-motion';
import { LogIn, UserPlus, Eye, EyeOff, CheckCircle, XCircle } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

type Props = {
  onSignIn: (email: string, password: string) => Promise<{ error?: string }>;
  onSignUp: (email: string, password: string) => Promise<{ error?: string }>;
};

function validateEmail(email: string): string {
  if (!email.trim()) return 'El email es requerido';
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Formato de email inválido';
  return '';
}

function validatePassword(password: string): string {
  if (!password) return 'La contraseña es requerida';
  if (password.length < 8) return 'Mínimo 8 caracteres';
  if (!/[A-Z]/.test(password)) return 'Debe incluir al menos una mayúscula';
  if (!/[0-9]/.test(password)) return 'Debe incluir al menos un número';
  return '';
}

type PasswordStrength = { label: string; color: string; width: string };

function getPasswordStrength(password: string): PasswordStrength {
  if (!password) return { label: '', color: '', width: '0%' };
  let score = 0;
  if (password.length >= 8) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  if (score <= 1) return { label: 'Débil', color: 'bg-red-500', width: '25%' };
  if (score === 2) return { label: 'Regular', color: 'bg-yellow-500', width: '50%' };
  if (score === 3) return { label: 'Buena', color: 'bg-blue-500', width: '75%' };
  return { label: 'Fuerte', color: 'bg-green-500', width: '100%' };
}

export default function LoginRegister({ onSignIn, onSignUp }: Props) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');

  const emailError = touched.email ? validateEmail(email) : '';
  const passwordError = touched.password ? validatePassword(password) : '';
  const confirmError =
    mode === 'register' && touched.confirm && confirmPassword !== password
      ? 'Las contraseñas no coinciden'
      : '';
  const strength = getPasswordStrength(password);

  const switchMode = (m: 'login' | 'register') => {
    setMode(m);
    setError('');
    setSuccess('');
    setTouched({});
    setPassword('');
    setConfirmPassword('');
    setEmail('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched({ email: true, password: true, confirm: true });
    setError('');
    setSuccess('');

    if (validateEmail(email) || validatePassword(password)) return;
    if (mode === 'register' && password !== confirmPassword) return;

    setLoading(true);
    try {
      const fn = mode === 'login' ? onSignIn : onSignUp;
      const { error } = await fn(email, password);
      if (error) setError(error);
      else if (mode === 'register') {
        setSuccess('Cuenta creada. Revisa tu email para confirmar (o inicia sesión si ya está activa).');
      }
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
          <div className="flex gap-2 mb-6">
            <button
              type="button"
              onClick={() => switchMode('login')}
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
              onClick={() => switchMode('register')}
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

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1">Email</label>
              <div className="relative">
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onBlur={() => setTouched((t) => ({ ...t, email: true }))}
                  placeholder="tu@email.com"
                  className={`w-full rounded-lg border px-4 py-2 pr-10 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 ${
                    emailError
                      ? 'border-red-500 focus:ring-red-500'
                      : email && !emailError
                      ? 'border-green-500'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                  autoComplete="email"
                  disabled={loading}
                />
                {touched.email && email && (
                  <span className="absolute right-3 top-2.5">
                    {emailError ? (
                      <XCircle className="w-4 h-4 text-red-500" />
                    ) : (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    )}
                  </span>
                )}
              </div>
              {emailError && <p className="text-red-500 text-xs mt-1">{emailError}</p>}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1">Contraseña</label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onBlur={() => setTouched((t) => ({ ...t, password: true }))}
                  placeholder="••••••••"
                  className={`w-full rounded-lg border px-4 py-2 pr-10 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 ${
                    passwordError
                      ? 'border-red-500'
                      : password && !passwordError
                      ? 'border-green-500'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((s) => !s)}
                  className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {passwordError && <p className="text-red-500 text-xs mt-1">{passwordError}</p>}
              {mode === 'register' && password && (
                <div className="mt-2">
                  <div className="h-1.5 w-full bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${strength.color}`}
                      style={{ width: strength.width }}
                    />
                  </div>
                  {strength.label && (
                    <p className="text-xs mt-1 text-gray-500 dark:text-gray-400">
                      Fortaleza: <span className="font-medium">{strength.label}</span>
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Confirm Password (register only) */}
            {mode === 'register' && (
              <div>
                <label htmlFor="confirm" className="block text-sm font-medium mb-1">Confirmar contraseña</label>
                <div className="relative">
                  <input
                    id="confirm"
                    type={showConfirm ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    onBlur={() => setTouched((t) => ({ ...t, confirm: true }))}
                    placeholder="••••••••"
                    className={`w-full rounded-lg border px-4 py-2 pr-10 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 ${
                      confirmError
                        ? 'border-red-500'
                        : confirmPassword && confirmPassword === password
                        ? 'border-green-500'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                    autoComplete="new-password"
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm((s) => !s)}
                    className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    tabIndex={-1}
                  >
                    {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {confirmError && <p className="text-red-500 text-xs mt-1">{confirmError}</p>}
              </div>
            )}

            {error && <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>}
            {success && <p className="text-green-600 dark:text-green-400 text-sm">{success}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 px-4 rounded-lg bg-primary-500 hover:bg-primary-600 text-white font-medium disabled:opacity-50 transition-colors"
            >
              {loading ? 'Procesando...' : mode === 'login' ? 'Iniciar sesión' : 'Registrarse'}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
