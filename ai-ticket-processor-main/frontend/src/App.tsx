import { useEffect, useRef, useState } from 'react';
import { supabase } from './lib/supabase';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Eye, CheckCircle, XCircle, AlertCircle, Loader2, Search, Edit, Trash2, X } from 'lucide-react';
import ThemeToggle from './components/ThemeToggle';

type Ticket = {
  id: string;
  created_at: string;
  description: string;
  category: string | null;
  sentiment: string | null;
  processed: boolean;
};

const sentimentColor = (sentiment?: string | null) => {
  switch ((sentiment || '').toLowerCase()) {
    case 'negativo':
      return 'bg-red-500/10 text-red-300 border-red-500/30';
    case 'positivo':
      return 'bg-green-500/10 text-green-300 border-green-500/30';
    default:
      return 'bg-slate-500/10 text-slate-300 border-slate-500/30';
  }
};

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

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
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [newTicket, setNewTicket] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [realtimeStatus, setRealtimeStatus] = useState('connecting');
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [editingTicket, setEditingTicket] = useState<Ticket | null>(null);
  const [editDescription, setEditDescription] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<{ ticketId: string; description: string } | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [showTour, setShowTour] = useState(false);
  const [tourStepIndex, setTourStepIndex] = useState(0);
  const [highlightedElement, setHighlightedElement] = useState<HTMLElement | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const itemsPerPage = 9; // 3x3 grid
  const currentPageRef = useRef(currentPage);
  const headerRef = useRef<HTMLElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  const tourSteps: TourStep[] = [
    {
      title: 'Bienvenido',
      description: 'Este dashboard muestra los tickets en tiempo real.',
      targetKey: 'header',
    },
    {
      title: 'Crear tickets',
      description: 'Usa el formulario para crear un nuevo ticket de soporte.',
      targetKey: 'form',
    },
    {
      title: 'Buscar y navegar',
      description: 'Filtra por descripción o categoría y usa la paginación.',
      targetKey: 'search',
    },
  ];

  const addNotification = (type: Notification['type'], message: string) => {
    const id = Date.now().toString();
    setNotifications(prev => [...prev, { id, type, message }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const jumpToFirstPage = () => {
    if (currentPageRef.current > 1) {
      setCurrentPage(1);
    }
    if (typeof window !== 'undefined' && window.scrollY > 0) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const finishTour = () => {
    setShowTour(false);
    setTourStepIndex(0);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('supportCopilotTourSeen', 'true');
    }
  };

  useEffect(() => {
    currentPageRef.current = currentPage;
  }, [currentPage]);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const seen = window.localStorage.getItem('supportCopilotTourSeen');
    if (!seen) {
      setTimeout(() => setShowTour(true), 400);
    }
  }, []);

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
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [showTour, tourStepIndex, tourSteps]);

  useEffect(() => {
    const fetchTickets = async () => {
      setLoading(true);
      const { data, error } = await supabase
        .from('tickets')
        .select('*')
        .order('created_at', { ascending: false });
      if (!error && data) setTickets(data as Ticket[]);
      setLoading(false);
    };

    fetchTickets();

    const upsertTicket = (incoming: Ticket) => {
      setTickets((prev) => {
        const index = prev.findIndex((t) => t.id === incoming.id);
        if (index >= 0) {
          const next = [...prev];
          next[index] = incoming;
          return next;
        }
        return [incoming, ...prev];
      });
    };

    const channel = supabase
      .channel('tickets-realtime')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'tickets' },
        (payload) => {
          if (payload.eventType === 'INSERT' && payload.new) {
            upsertTicket(payload.new as Ticket);
            addNotification('success', 'Nuevo ticket recibido');
            jumpToFirstPage();
            return;
          }
          if (payload.eventType === 'UPDATE' && payload.new) {
            upsertTicket(payload.new as Ticket);
            return;
          }
          if (payload.eventType === 'DELETE' && payload.old) {
            setTickets((prev) =>
              prev.filter((ticket) => ticket.id !== (payload.old as Ticket).id)
            );
            return;
          }
          fetchTickets();
        }
      )
      .subscribe((status) => setRealtimeStatus(status));

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTicket.trim()) return;

    setSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/create-ticket`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: newTicket }),
      });
      if (response.ok) {
        setNewTicket('');
        addNotification('success', 'Ticket creado exitosamente');
        jumpToFirstPage();
      } else {
        addNotification('error', 'Error al crear el ticket');
      }
    } catch (error) {
      console.error('Error creating ticket:', error);
      addNotification('error', 'Error de conexión al crear ticket');
    } finally {
      setSubmitting(false);
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: editDescription }),
      });
      if (response.ok) {
        setEditingTicket(null);
        setEditDescription('');
        addNotification('success', 'Ticket actualizado y re-evaluado por IA');
        setSelectedTicket(null);
      } else {
        const error = await response.json();
        addNotification('error', error.detail || 'Error al actualizar el ticket');
      }
    } catch (error) {
      console.error('Error updating ticket:', error);
      addNotification('error', 'Error de conexión al actualizar ticket');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDeleteClick = (ticketId: string, description: string) => {
    setConfirmDelete({ ticketId, description });
  };

  const handleDeleteConfirm = async () => {
    if (!confirmDelete) return;

    setIsDeleting(confirmDelete.ticketId);
    try {
      const response = await fetch(`${API_URL}/tickets/${confirmDelete.ticketId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        addNotification('success', 'Ticket eliminado exitosamente');
        setSelectedTicket(null);
        setConfirmDelete(null);
      } else {
        addNotification('error', 'Error al eliminar el ticket');
      }
    } catch (error) {
      console.error('Error deleting ticket:', error);
      addNotification('error', 'Error de conexión al eliminar ticket');
    } finally {
      setIsDeleting(null);
    }
  };

  // Manejar parámetro de URL para abrir ticket directamente
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const ticketId = params.get('ticket');
    if (ticketId && tickets.length > 0) {
      const ticket = tickets.find(t => t.id === ticketId);
      if (ticket) {
        setSelectedTicket(ticket);
        // Limpiar el parámetro de la URL
        window.history.replaceState({}, '', window.location.pathname);
      }
    }
  }, [tickets]);

  const filteredTickets = tickets.filter(ticket =>
    ticket.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ticket.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(filteredTickets.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedTickets = filteredTickets.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div className="min-h-screen p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
      <main className="container mx-auto max-w-4xl">
        <motion.header
          ref={headerRef}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mb-6 flex items-center justify-between p-6 bg-gradient-to-r from-primary-500 to-primary-600 dark:from-primary-600 dark:to-primary-700 rounded-xl shadow-lg ${
            highlightedElement === headerRef.current ? 'ring-4 ring-yellow-400 ring-offset-4 ring-offset-slate-900 relative z-50' : ''
          }`}
        >
          <div className="flex items-center gap-3">
            <img src="/logo.svg" alt="AI Support Co-Pilot Logo" className="h-12 w-12" />
            <div>
              <h1 className="text-2xl font-bold text-white">AI Support Co-Pilot</h1>
              <p className="text-primary-100 dark:text-primary-200">
                Dashboard en tiempo real de tickets procesados.
              </p>
              <div className="mt-2 text-xs text-primary-200 dark:text-primary-300">
                Realtime: <span className="text-white" aria-live="polite">{realtimeStatus}</span>
              </div>
            </div>
          </div>
          <ThemeToggle />
        </motion.header>

        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6 card"
        >
          <h2 className="mb-3 font-semibold">Gestion de tickets</h2>
          <form
            ref={formRef}
            onSubmit={handleSubmit}
            className={`flex gap-2 ${
              highlightedElement === formRef.current ? 'ring-4 ring-yellow-400 ring-offset-4 ring-offset-slate-900 relative z-50' : ''
            }`}
            aria-label="Crear ticket"
          >
            <input
              type="text"
              aria-label="Descripción del ticket"
              value={newTicket}
              onChange={(e) => setNewTicket(e.target.value)}
              placeholder="Describe el problema o consulta..."
              className="flex-1 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus-visible:ring-2 focus-visible:ring-primary-400"
              disabled={submitting}
            />
            <button
              type="submit"
              disabled={submitting || !newTicket.trim()}
              className="btn-primary disabled:opacity-50 flex items-center gap-2"
              aria-disabled={submitting || !newTicket.trim()}
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              {submitting ? 'Creando...' : 'Crear'}
            </button>
          </form>
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between px-1 py-3 border-b border-slate-800">
            <h2 className="font-semibold">Tickets ({filteredTickets.length})</h2>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  ref={searchRef}
                  type="text"
                  placeholder="Buscar tickets..."
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setCurrentPage(1); // Reset to first page on search
                  }}
                  className={`pl-10 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-1 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus-visible:ring-2 focus-visible:ring-primary-400 ${
                    highlightedElement === searchRef.current ? 'ring-4 ring-yellow-400 ring-offset-4 ring-offset-slate-900 relative z-50' : ''
                  }`}
                />
              </div>
              {loading && <Loader2 className="w-4 h-4 animate-spin text-slate-400" />}
            </div>
          </div>
          <div className="p-4">
            {paginatedTickets.length === 0 && !loading && (
              <div className="text-slate-400 text-center py-8">No hay tickets aún.</div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <AnimatePresence>
                {paginatedTickets.map((ticket) => (
                  <motion.div
                    key={ticket.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="card p-4 cursor-pointer hover:bg-slate-800/50 transition-colors relative group"
                    onClick={() => setSelectedTicket(ticket)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="text-sm text-gray-500 dark:text-gray-400 font-mono">#{ticket.id.slice(-8)}</div>
                    </div>
                    <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2 line-clamp-2">{ticket.description}</h3>
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                      <span>{ticket.category || 'Sin categoría'}</span>
                      <span>{new Date(ticket.created_at).toLocaleDateString()}</span>
                    </div>
                    <div 
                      className="absolute top-2 right-2 flex gap-1.5 z-10"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <button
                        onClick={() => handleEdit(ticket)}
                        className="p-2 rounded-md bg-blue-500/30 hover:bg-blue-500/50 text-blue-400 hover:text-blue-200 transition-all shadow-md hover:shadow-lg border border-blue-500/30 hover:border-blue-500/50"
                        title="Editar ticket"
                        aria-label="Editar ticket"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteClick(ticket.id, ticket.description)}
                        disabled={isDeleting === ticket.id}
                        className="p-2 rounded-md bg-red-500/30 hover:bg-red-500/50 text-red-400 hover:text-red-200 transition-all shadow-md hover:shadow-lg border border-red-500/30 hover:border-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Eliminar ticket"
                        aria-label="Eliminar ticket"
                      >
                        {isDeleting === ticket.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-6">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="btn-primary disabled:opacity-50 px-3 py-1 text-sm"
                >
                  Anterior
                </button>
                <span className="text-gray-600 dark:text-gray-400 text-sm">
                  Página {currentPage} de {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="btn-primary disabled:opacity-50 px-3 py-1 text-sm"
                >
                  Siguiente
                </button>
              </div>
            )}
          </div>
        </motion.section>

        {/* Modal para detalles de ticket */}
        <AnimatePresence>
          {selectedTicket && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
              onClick={() => setSelectedTicket(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Detalles del Ticket</h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(selectedTicket)}
                      className="p-2 rounded-md bg-blue-500/30 hover:bg-blue-500/50 text-blue-400 hover:text-blue-200 transition-all shadow-md hover:shadow-lg border border-blue-500/30 hover:border-blue-500/50"
                      title="Editar ticket"
                      aria-label="Editar ticket"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteClick(selectedTicket.id, selectedTicket.description)}
                      disabled={isDeleting === selectedTicket.id}
                      className="p-2 rounded-md bg-red-500/30 hover:bg-red-500/50 text-red-400 hover:text-red-200 transition-all shadow-md hover:shadow-lg border border-red-500/30 hover:border-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Eliminar ticket"
                      aria-label="Eliminar ticket"
                    >
                      {isDeleting === selectedTicket.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
                <div className="space-y-2">
                  <p><strong>ID:</strong> <span className="font-mono text-sm">{selectedTicket.id}</span></p>
                  <p><strong>Descripción:</strong> {selectedTicket.description}</p>
                  <p><strong>Categoría:</strong> {selectedTicket.category || 'Sin categoría'}</p>
                  <p><strong>Sentimiento:</strong> {selectedTicket.sentiment || 'Neutral'}</p>
                  <p><strong>Estado:</strong> {selectedTicket.processed ? 'Procesado' : 'Pendiente'}</p>
                  <p><strong>Creado:</strong> {new Date(selectedTicket.created_at).toLocaleString()}</p>
                </div>
                <button
                  onClick={() => setSelectedTicket(null)}
                  className="btn-primary mt-4 w-full"
                >
                  Cerrar
                </button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Modal para editar ticket */}
        <AnimatePresence>
          {editingTicket && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
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
                <h3 className="text-lg font-semibold mb-4">Editar Ticket</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  El ticket será re-evaluado por IA después de guardar.
                </p>
                <textarea
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  placeholder="Descripción del ticket..."
                  className="w-full rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus-visible:ring-2 focus-visible:ring-primary-400 min-h-[100px] resize-y"
                  disabled={isUpdating}
                />
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={handleUpdate}
                    disabled={isUpdating || !editDescription.trim()}
                    className="btn-primary flex-1 disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {isUpdating ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Actualizando...
                      </>
                    ) : (
                      'Guardar cambios'
                    )}
                  </button>
                  <button
                    onClick={() => {
                      setEditingTicket(null);
                      setEditDescription('');
                    }}
                    disabled={isUpdating}
                    className="px-4 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
                  >
                    Cancelar
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Modal de confirmación para eliminar */}
        <AnimatePresence>
          {confirmDelete && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
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
                  <h3 className="text-lg font-semibold">Confirmar eliminación</h3>
                </div>
                <p className="text-gray-600 dark:text-gray-300 mb-2">
                  ¿Estás seguro de que quieres eliminar este ticket?
                </p>
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 mb-4">
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Descripción:</p>
                  <p className="text-sm text-gray-900 dark:text-gray-100 line-clamp-2">
                    {confirmDelete.description}
                  </p>
                </div>
                <p className="text-sm text-red-600 dark:text-red-400 mb-4">
                  Esta acción no se puede deshacer.
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={handleDeleteConfirm}
                    disabled={isDeleting === confirmDelete.ticketId}
                    className="btn-primary flex-1 disabled:opacity-50 flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700"
                  >
                    {isDeleting === confirmDelete.ticketId ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Eliminando...
                      </>
                    ) : (
                      <>
                        <Trash2 className="w-4 h-4" />
                        Eliminar
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => setConfirmDelete(null)}
                    disabled={isDeleting === confirmDelete.ticketId}
                    className="px-4 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
                  >
                    Cancelar
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Notificaciones */}
        <div className="fixed top-4 right-4 z-40 space-y-2">
          <AnimatePresence>
            {notifications.map((notification) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: 300 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 300 }}
                className={`p-4 rounded-lg shadow-lg ${
                  notification.type === 'success' ? 'bg-green-600' :
                  notification.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
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
                        return `polygon(
                          0% 0%,
                          0% 100%,
                          ${rect.left}px 100%,
                          ${rect.left}px ${rect.top}px,
                          ${rect.right}px ${rect.top}px,
                          ${rect.right}px ${rect.bottom}px,
                          ${rect.left}px ${rect.bottom}px,
                          ${rect.left}px 100%,
                          100% 100%,
                          100% 0%
                        )`;
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
                    !isMobile && highlightedElement
                      ? {
                          top: Math.min(
                            highlightedElement.getBoundingClientRect().bottom + 16,
                            window.innerHeight - 280
                          ),
                          left: Math.max(
                            16,
                            Math.min(
                              highlightedElement.getBoundingClientRect().left,
                              window.innerWidth - 400
                            )
                          ),
                        }
                      : {
                          maxHeight: '80vh',
                          overflowY: 'auto',
                        }
                  }
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-base sm:text-lg font-semibold pr-2 flex-1">
                      {tourSteps[tourStepIndex]?.title}
                    </h3>
                    <button
                      onClick={finishTour}
                      className="flex-shrink-0 p-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-slate-500 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                      aria-label="Cerrar tour"
                      title="Cerrar tour"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 mb-4">
                    {tourSteps[tourStepIndex]?.description}
                  </p>
                  <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-0 mt-4 sm:mt-5">
                    <span className="text-xs text-slate-400 text-center sm:text-left order-2 sm:order-1">
                      Paso {tourStepIndex + 1} de {tourSteps.length}
                    </span>
                    <div className="flex gap-2 justify-center sm:justify-end order-1 sm:order-2">
                      <button
                        onClick={() => setTourStepIndex((prev) => Math.max(prev - 1, 0))}
                        disabled={tourStepIndex === 0}
                        className="px-4 py-2 text-sm rounded border border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors min-w-[90px]"
                      >
                        Atrás
                      </button>
                      <button
                        onClick={() => {
                          if (tourStepIndex >= tourSteps.length - 1) {
                            finishTour();
                          } else {
                            setTourStepIndex((prev) => Math.min(prev + 1, tourSteps.length - 1));
                          }
                        }}
                        className="btn-primary px-4 py-2 text-sm min-w-[110px]"
                      >
                        {tourStepIndex >= tourSteps.length - 1 ? 'Finalizar' : 'Siguiente'}
                      </button>
                    </div>
                  </div>
                  {isMobile && (
                    <button
                      onClick={finishTour}
                      className="mt-3 w-full text-center text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 underline py-2"
                    >
                      Omitir tour completo
                    </button>
                  )}
                </motion.div>
              )}
            </>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
