import { useEffect, useRef, useState, Fragment } from 'react';
import { supabase } from './lib/supabase';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, Trash2, X, LogOut, Users, Headphones, UserRound, RefreshCw } from 'lucide-react';
import ThemeToggle from './components/ThemeToggle';
import { useAuth } from './contexts/AuthContext';
import LoginRegister from './components/LoginRegister';
import AdminUsers from './components/AdminUsers';
import ResetPassword from './components/ResetPassword';
import VersionInfo from './components/VersionInfo';
import BandejaAgente from './components/BandejaAgente';
import MisSolicitudes from './components/MisSolicitudes';
import PanelTicket from './components/PanelTicket';
import { API_URL } from './lib/api';
import { Persona, Ticket, llamarApi } from './lib/tickets';

type Notification = {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
};

type TourStep = {
  title: string;
  description: string;
  targetKey: 'header' | 'form' | 'search';
};

export default function App() {
  const { session, profile, loading: authLoading, signIn, signUp, signOut, resetPassword } = useAuth();
  const [isPasswordRecovery, setIsPasswordRecovery] = useState(false);

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event) => {
      if (event === 'PASSWORD_RECOVERY') setIsPasswordRecovery(true);
    });
    return () => subscription.unsubscribe();
  }, []);

  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [agentes, setAgentes] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  // Se guarda el id y no el ticket: así el panel muestra siempre la versión recién cargada.
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [tomando, setTomando] = useState<string | null>(null);
  const [editingTicket, setEditingTicket] = useState<Ticket | null>(null);
  const [editDescription, setEditDescription] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<{ ticketId: string; description: string } | null>(null);
  const [showTour, setShowTour] = useState(false);
  const [tourStepIndex, setTourStepIndex] = useState(0);
  const [highlightedElement, setHighlightedElement] = useState<HTMLElement | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const [adminView, setAdminView] = useState(false);
  const headerRef = useRef<HTMLElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  const isCliente = profile?.role === 'cliente';
  const isAgente = profile?.role === 'agente' || profile?.role === 'administrador';
  const isAdministrador = profile?.role === 'administrador';
  const token = session?.access_token;

  const tourSteps: TourStep[] = isAgente
    ? [
        { title: 'Bandeja de atención', description: 'Aquí llegan las solicitudes de los clientes, ya clasificadas por la IA y ordenadas por prioridad.', targetKey: 'header' },
        { title: 'Toma y atiende', description: 'Toma un ticket de «Sin asignar», respóndele al cliente o deja notas internas, y ciérralo al resolverlo. Usa las pestañas y el buscador para filtrar.', targetKey: 'search' },
      ]
    : [
        { title: 'Bienvenido', description: 'Desde aquí pides ayuda al equipo de soporte y sigues tus casos.', targetKey: 'header' },
        { title: 'Crea una solicitud', description: 'Cuéntanos el problema. Verás cuándo un agente la toma y podrás conversar con él.', targetKey: 'form' },
      ];

  const addNotification = (type: Notification['type'], message: string) => {
    const id = `${Date.now()}-${Math.random()}`;
    setNotifications(prev => [...prev, { id, type, message }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const finishTour = () => {
    setShowTour(false);
    setTourStepIndex(0);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('supportCopilotTourSeen-v2', 'true');
    }
  };

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined' || !profile) return;
    if (!window.localStorage.getItem('supportCopilotTourSeen-v2')) {
      setTimeout(() => setShowTour(true), 600);
    }
  }, [profile]);

  useEffect(() => {
    if (!showTour) {
      setHighlightedElement(null);
      return;
    }
    const step = tourSteps[tourStepIndex];
    const targetMap: Record<TourStep['targetKey'], HTMLElement | null> = {
      header: headerRef.current,
      form: formRef.current,
      search: searchRef.current,
    };
    const element = targetMap[step?.targetKey] || null;
    setHighlightedElement(element);
    if (element) element.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, [showTour, tourStepIndex]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchTickets = async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from('tickets')
      .select('*')
      .order('created_at', { ascending: false });
    if (!error && data) setTickets(data as Ticket[]);
    setLoading(false);
  };

  useEffect(() => {
    if (session) fetchTickets();
    else setTickets([]);
  }, [session]); // eslint-disable-line react-hooks/exhaustive-deps

  // El equipo necesita los correos de los agentes para saber quién tiene cada ticket.
  useEffect(() => {
    if (!session || !isAgente) return;
    llamarApi<Persona[]>(token, '/agentes').then(setAgentes).catch(() => setAgentes([]));
  }, [session, isAgente]); // eslint-disable-line react-hooks/exhaustive-deps

  // La bandeja se actualiza sola: otro agente puede tomar o cerrar tickets en cualquier momento.
  useEffect(() => {
    if (!session) return;
    const intervalo = setInterval(fetchTickets, 30000);
    return () => clearInterval(intervalo);
  }, [session]); // eslint-disable-line react-hooks/exhaustive-deps

  const authHeaders = (): HeadersInit => ({
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  });

  const handleCrear = async (titulo: string, description: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_URL}/create-ticket`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ titulo, description }),
      });
      if (!response.ok) {
        addNotification('error', 'No se pudo enviar la solicitud');
        return false;
      }
      addNotification('success', 'Solicitud enviada. Te avisaremos aquí cuando un agente la tome.');
      await fetchTickets();
      return true;
    } catch (error) {
      console.error('Error creating ticket:', error);
      addNotification('error', 'Error de conexión al enviar la solicitud');
      return false;
    }
  };

  const tomarRapido = async (ticket: Ticket) => {
    setTomando(ticket.id);
    try {
      await llamarApi(token, `/tickets/${ticket.id}/tomar`, { method: 'POST' });
      addNotification('success', `Tomaste «${ticket.titulo}»`);
      await fetchTickets();
      setSelectedId(ticket.id);
    } catch (e) {
      addNotification('error', (e as Error).message);
      await fetchTickets();
    } finally {
      setTomando(null);
    }
  };

  const handleEdit = (ticket: Ticket) => {
    setEditingTicket(ticket);
    setEditDescription(ticket.description);
  };

  const handleUpdate = async () => {
    if (!editingTicket || !editDescription.trim()) return;
    setIsUpdating(true);
    try {
      const response = await fetch(`${API_URL}/tickets/${editingTicket.id}`, {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify({ description: editDescription }),
      });
      if (response.ok) {
        setEditingTicket(null);
        setEditDescription('');
        addNotification('success', 'Solicitud actualizada');
        await fetchTickets();
      } else {
        const error = await response.json();
        addNotification('error', error.detail || 'Error al actualizar la solicitud');
      }
    } catch (error) {
      console.error('Error updating ticket:', error);
      addNotification('error', 'Error de conexión al actualizar');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!confirmDelete) return;
    setIsDeleting(confirmDelete.ticketId);
    try {
      const response = await fetch(`${API_URL}/tickets/${confirmDelete.ticketId}`, {
        method: 'DELETE',
        headers: authHeaders(),
      });
      if (response.ok) {
        addNotification('success', 'Solicitud eliminada');
        setSelectedId(null);
        setConfirmDelete(null);
        await fetchTickets();
      } else {
        addNotification('error', 'Error al eliminar la solicitud');
      }
    } catch (error) {
      console.error('Error deleting ticket:', error);
      addNotification('error', 'Error de conexión al eliminar');
    } finally {
      setIsDeleting(null);
    }
  };

  // Abrir un ticket directamente con ?ticket=<id>
  useEffect(() => {
    const ticketId = new URLSearchParams(window.location.search).get('ticket');
    if (ticketId && tickets.some(t => t.id === ticketId)) {
      setSelectedId(ticketId);
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [tickets]);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Loader2 className="w-12 h-12 animate-spin text-primary-500" />
      </div>
    );
  }

  if (isPasswordRecovery) {
    return (
      <ResetPassword
        onSubmit={async (password) => {
          const { error } = await supabase.auth.updateUser({ password });
          if (!error) setIsPasswordRecovery(false);
          return { error: error?.message };
        }}
      />
    );
  }

  if (!session) {
    return (
      <LoginRegister
        onSignIn={async (email, password) => {
          const { error } = await signIn(email, password);
          return { error };
        }}
        onSignUp={async (email, password) => {
          const { error } = await signUp(email, password);
          return { error };
        }}
        onResetPassword={async (email) => {
          const { error } = await resetPassword(email);
          return { error };
        }}
      />
    );
  }

  const selectedTicket = tickets.find(t => t.id === selectedId) ?? null;
  const nombreRol = isAdministrador ? 'Administrador' : isAgente ? 'Agente de soporte' : 'Cliente';

  return (
    <div className="min-h-screen p-4 sm:p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
      <main className={`container mx-auto ${isAgente ? 'max-w-5xl' : 'max-w-6xl'}`}>
        <motion.header
          ref={headerRef}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mb-6 flex flex-wrap items-center justify-between gap-4 p-5 rounded-xl shadow-lg ${
            isAgente
              ? 'bg-gradient-to-r from-slate-800 to-slate-900 dark:from-slate-800 dark:to-slate-950'
              : 'bg-gradient-to-r from-primary-500 to-primary-600 dark:from-primary-600 dark:to-primary-700'
          } ${highlightedElement === headerRef.current ? 'ring-4 ring-yellow-400 ring-offset-4 ring-offset-slate-900 relative z-50' : ''}`}
        >
          <div className="flex items-center gap-3">
            <img src="/logo.svg" alt="AI Support Co-Pilot Logo" className="h-11 w-11" />
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-white">
                {isAgente ? 'Mesa de atención · AI Support Co-Pilot' : 'Centro de ayuda · AI Support Co-Pilot'}
              </h1>
              <p className="text-sm text-white/75">
                {isAgente ? 'Atiende las solicitudes de los clientes, clasificadas por IA.' : 'Pide ayuda y sigue el avance de tus casos.'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {isAdministrador && (
              <button
                onClick={() => setAdminView(!adminView)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors text-white ${adminView ? 'bg-white/30' : 'bg-white/10 hover:bg-white/20'}`}
                title={adminView ? 'Ver la bandeja' : 'Gestión de usuarios'}
              >
                <Users className="w-4 h-4 inline mr-1.5 -mt-0.5" />
                {adminView ? 'Bandeja' : 'Usuarios'}
              </button>
            )}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/10 text-white" title={session.user.email ?? ''}>
              {isAgente ? <Headphones className="w-4 h-4" /> : <UserRound className="w-4 h-4" />}
              <div className="leading-tight">
                <p className="text-sm font-semibold">{nombreRol}</p>
                <p className="text-xs text-white/70 max-w-[160px] truncate">{session.user.email}</p>
              </div>
            </div>
            <button
              onClick={fetchTickets}
              className="p-2 rounded-lg hover:bg-white/20 transition-colors text-white"
              title="Actualizar"
              aria-label="Actualizar"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={() => signOut()}
              className="p-2 rounded-lg hover:bg-white/20 transition-colors text-white"
              title="Cerrar sesión"
              aria-label="Cerrar sesión"
            >
              <LogOut className="w-5 h-5" />
            </button>
            <ThemeToggle />
          </div>
        </motion.header>

        {adminView && isAdministrador ? (
          <AdminUsers />
        ) : (
          <Fragment>
            {isAgente && profile && (
              <BandejaAgente
                tickets={tickets}
                usuarioId={profile.id}
                agentes={agentes}
                cargando={loading}
                tomando={tomando}
                onAbrir={(t) => setSelectedId(t.id)}
                onTomar={tomarRapido}
                buscadorRef={searchRef}
              />
            )}
            {isCliente && (
              <MisSolicitudes
                tickets={tickets}
                cargando={loading}
                onAbrir={(t) => setSelectedId(t.id)}
                onCrear={handleCrear}
                formRef={formRef}
              />
            )}
          </Fragment>
        )}

        {/* Panel del ticket: atención para el agente, seguimiento para el cliente */}
        <AnimatePresence>
          {selectedTicket && profile && (
            <PanelTicket
              key={selectedTicket.id}
              ticket={selectedTicket}
              rol={profile.role}
              usuarioId={profile.id}
              token={token}
              agentes={agentes}
              onCerrar={() => setSelectedId(null)}
              onCambio={fetchTickets}
              notificar={addNotification}
              onEditar={isCliente ? handleEdit : undefined}
              onEliminar={isCliente ? (t) => setConfirmDelete({ ticketId: t.id, description: t.description }) : undefined}
            />
          )}
        </AnimatePresence>

        {/* Modal para editar la solicitud (cliente, mientras nadie la ha tomado) */}
        <AnimatePresence>
          {editingTicket && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-[60]"
              onClick={() => {
                setEditingTicket(null);
                setEditDescription('');
              }}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full"
                onClick={(e) => e.stopPropagation()}
              >
                <h3 className="text-lg font-semibold mb-1">Editar solicitud</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  Al guardar se vuelve a clasificar con el nuevo texto.
                </p>
                <textarea
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  placeholder="Describe el problema…"
                  className="w-full rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus-visible:ring-2 focus-visible:ring-primary-400 min-h-[120px] resize-y"
                  disabled={isUpdating}
                />
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={handleUpdate}
                    disabled={isUpdating || !editDescription.trim()}
                    className="btn-primary flex-1 disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {isUpdating ? (<><Loader2 className="w-4 h-4 animate-spin" /> Guardando…</>) : 'Guardar cambios'}
                  </button>
                  <button
                    onClick={() => {
                      setEditingTicket(null);
                      setEditDescription('');
                    }}
                    disabled={isUpdating}
                    className="px-4 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
                  >
                    Cancelar
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Confirmación para eliminar */}
        <AnimatePresence>
          {confirmDelete && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-[60]"
              onClick={() => setConfirmDelete(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full shadow-xl"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-full bg-red-500/20">
                    <Trash2 className="w-6 h-6 text-red-500" />
                  </div>
                  <h3 className="text-lg font-semibold">¿Eliminar la solicitud?</h3>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 mb-4">
                  <p className="text-sm line-clamp-2">{confirmDelete.description}</p>
                </div>
                <p className="text-sm text-red-600 dark:text-red-400 mb-4">Esta acción no se puede deshacer.</p>
                <div className="flex gap-2">
                  <button
                    onClick={handleDeleteConfirm}
                    disabled={isDeleting === confirmDelete.ticketId}
                    className="btn-primary flex-1 disabled:opacity-50 flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700"
                  >
                    {isDeleting === confirmDelete.ticketId ? (<><Loader2 className="w-4 h-4 animate-spin" /> Eliminando…</>) : (<><Trash2 className="w-4 h-4" /> Eliminar</>)}
                  </button>
                  <button
                    onClick={() => setConfirmDelete(null)}
                    disabled={isDeleting === confirmDelete.ticketId}
                    className="px-4 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
                  >
                    Cancelar
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Notificaciones */}
        <div className="fixed bottom-4 right-4 z-[70] space-y-2" aria-live="polite">
          <AnimatePresence>
            {notifications.map((notification) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: 300 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 300 }}
                className={`p-4 rounded-lg shadow-lg max-w-sm ${
                  notification.type === 'success' ? 'bg-green-600' : notification.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
                } text-white`}
              >
                {notification.message}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Tour de bienvenida con spotlight */}
        <AnimatePresence>
          {showTour && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/60 z-40"
                onClick={finishTour}
                style={{
                  clipPath: highlightedElement && !isMobile
                    ? (() => {
                        const rect = highlightedElement.getBoundingClientRect();
                        return `polygon(0% 0%, 0% 100%, ${rect.left}px 100%, ${rect.left}px ${rect.top}px, ${rect.right}px ${rect.top}px, ${rect.right}px ${rect.bottom}px, ${rect.left}px ${rect.bottom}px, ${rect.left}px 100%, 100% 100%, 100% 0%)`;
                      })()
                    : undefined,
                }}
              />
              {highlightedElement && (
                <motion.div
                  initial={{ opacity: 0, y: 16, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 16, scale: 0.95 }}
                  className={`fixed z-50 bg-white dark:bg-gray-900 rounded-2xl p-4 sm:p-6 max-w-md w-[calc(100%-32px)] sm:w-full shadow-2xl border border-slate-200 dark:border-slate-800 ${
                    isMobile ? 'left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2' : ''
                  }`}
                  style={
                    !isMobile
                      ? {
                          top: Math.min(highlightedElement.getBoundingClientRect().bottom + 16, window.innerHeight - 260),
                          left: Math.max(16, Math.min(highlightedElement.getBoundingClientRect().left, window.innerWidth - 420)),
                        }
                      : { maxHeight: '80vh', overflowY: 'auto' }
                  }
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-base sm:text-lg font-semibold pr-2 flex-1">{tourSteps[tourStepIndex]?.title}</h3>
                    <button
                      onClick={finishTour}
                      className="flex-shrink-0 p-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-slate-500 hover:text-red-500 transition-colors"
                      aria-label="Cerrar tour"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 mb-4">{tourSteps[tourStepIndex]?.description}</p>
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-xs text-slate-400">Paso {tourStepIndex + 1} de {tourSteps.length}</span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setTourStepIndex((prev) => Math.max(prev - 1, 0))}
                        disabled={tourStepIndex === 0}
                        className="px-4 py-2 text-sm rounded border border-slate-300 dark:border-slate-700 disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                      >
                        Atrás
                      </button>
                      <button
                        onClick={() => (tourStepIndex >= tourSteps.length - 1 ? finishTour() : setTourStepIndex(tourStepIndex + 1))}
                        className="btn-primary px-4 py-2 text-sm"
                      >
                        {tourStepIndex >= tourSteps.length - 1 ? 'Entendido' : 'Siguiente'}
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
            </>
          )}
        </AnimatePresence>
        <VersionInfo />
      </main>
    </div>
  );
}
