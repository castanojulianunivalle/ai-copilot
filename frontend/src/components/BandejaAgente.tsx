// HU-13: bandeja de atención del agente. La cola sigue siendo compartida, pero cada ticket muestra quién lo tiene,
// y las pestañas separan lo libre, lo propio y lo que la IA marcó para revisión.
import { RefObject, useMemo, useState } from 'react';
import { Hand, Loader2, Search, AlertTriangle, Inbox, User, Users, CheckCircle2, ListFilter } from 'lucide-react';
import {
  Persona, Ticket, estadoColor, fechaRelativa, ordenAtencion, prioridadColor, requiereRevision, sentimientoColor,
} from '../lib/tickets';

type Pestana = 'libres' | 'mios' | 'revision' | 'activos' | 'cerrados';

type Props = {
  tickets: Ticket[];
  usuarioId: string;
  agentes: Persona[];
  cargando: boolean;
  tomando: string | null;
  onAbrir: (t: Ticket) => void;
  onTomar: (t: Ticket) => void;
  buscadorRef?: RefObject<HTMLInputElement>;
};

export default function BandejaAgente({ tickets, usuarioId, agentes, cargando, tomando, onAbrir, onTomar, buscadorRef }: Props) {
  const [pestana, setPestana] = useState<Pestana>('libres');
  const [busqueda, setBusqueda] = useState('');

  const abiertos = tickets.filter(t => t.estado !== 'Cerrado');
  const grupos: Record<Pestana, Ticket[]> = useMemo(() => ({
    libres: abiertos.filter(t => !t.asignado_a),
    mios: abiertos.filter(t => t.asignado_a === usuarioId),
    revision: abiertos.filter(requiereRevision),
    activos: abiertos,
    cerrados: tickets.filter(t => t.estado === 'Cerrado'),
  }), [tickets, usuarioId]); // eslint-disable-line react-hooks/exhaustive-deps

  const pestanas: { id: Pestana; titulo: string; icono: JSX.Element; ayuda: string }[] = [
    { id: 'libres', titulo: 'Sin asignar', icono: <Inbox className="w-4 h-4" />, ayuda: 'Tickets abiertos que nadie ha tomado.' },
    { id: 'mios', titulo: 'Mis tickets', icono: <User className="w-4 h-4" />, ayuda: 'Los que estás atendiendo tú.' },
    { id: 'revision', titulo: 'Por revisar', icono: <AlertTriangle className="w-4 h-4" />, ayuda: 'La IA no está segura de la clasificación.' },
    { id: 'activos', titulo: 'Todos abiertos', icono: <Users className="w-4 h-4" />, ayuda: 'Toda la cola abierta del equipo.' },
    { id: 'cerrados', titulo: 'Cerrados', icono: <CheckCircle2 className="w-4 h-4" />, ayuda: 'Casos resueltos.' },
  ];

  const termino = busqueda.toLowerCase();
  const visibles = grupos[pestana]
    .filter(t => !termino || [t.titulo, t.description, t.category, t.sentimiento, t.prioridad]
      .some(c => c?.toLowerCase().includes(termino)))
    .sort(pestana === 'cerrados' ? (a, b) => b.created_at.localeCompare(a.created_at) : ordenAtencion);

  const responsable = (t: Ticket) => {
    if (!t.asignado_a) return null;
    if (t.asignado_a === usuarioId) return 'Tú';
    return agentes.find(a => a.id === t.asignado_a)?.email?.split('@')[0] ?? 'Otro agente';
  };

  return (
    <section className="card p-0 overflow-hidden">
      {/* Resumen y pestañas */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="font-semibold text-lg">Bandeja de atención</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">{pestanas.find(p => p.id === pestana)?.ayuda}</p>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              ref={buscadorRef}
              type="search"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar por texto, categoría…"
              className="pl-9 pr-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm w-60 focus-visible:ring-2 focus-visible:ring-primary-400"
              aria-label="Buscar tickets"
            />
          </div>
        </div>
        <div className="flex flex-wrap gap-1.5 mt-4" role="tablist" aria-label="Filtros de la bandeja">
          {pestanas.map(p => (
            <button
              key={p.id}
              role="tab"
              aria-selected={pestana === p.id}
              onClick={() => setPestana(p.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm border transition-colors ${
                pestana === p.id
                  ? 'bg-primary-500 text-white border-primary-500'
                  : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'}`}
            >
              {p.icono}{p.titulo}
              <span className={`ml-0.5 text-xs px-1.5 rounded-full ${pestana === p.id ? 'bg-white/25' : 'bg-gray-200 dark:bg-gray-700'}`}>
                {grupos[p.id].length}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Lista */}
      {cargando && tickets.length === 0 ? (
        <div className="p-10 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
      ) : visibles.length === 0 ? (
        <div className="p-10 text-center text-gray-500 dark:text-gray-400">
          <ListFilter className="w-8 h-8 mx-auto mb-2 opacity-50" />
          {pestana === 'libres' ? 'No hay tickets sin asignar. ¡Cola al día!' : pestana === 'mios' ? 'No tienes tickets asignados. Toma uno de «Sin asignar».' : 'Nada por aquí.'}
        </div>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-800">
          {visibles.map(t => (
            <li key={t.id} className="flex items-center gap-3 pr-4 hover:bg-gray-50 dark:hover:bg-gray-800/60">
              {/* Zona que abre el panel y zona de acción son hermanas: un botón dentro de otro confunde al teclado y al lector de pantalla */}
              <div
                role="button"
                tabIndex={0}
                onClick={() => onAbrir(t)}
                onKeyDown={(e) => e.key === 'Enter' && onAbrir(t)}
                aria-label={`Abrir ${t.titulo}`}
                className="flex-1 min-w-0 flex items-center gap-3 pl-4 py-3 cursor-pointer focus-visible:bg-gray-100 dark:focus-visible:bg-gray-800"
              >
                <span className={`w-1.5 self-stretch rounded-full ${
                  t.prioridad === 'Alta' ? 'bg-red-500' : t.prioridad === 'Media' ? 'bg-amber-500' : 'bg-slate-400'}`} aria-hidden />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium truncate">{t.titulo}</p>
                    {requiereRevision(t) && (
                      <span title="La IA pide revisión humana"><AlertTriangle className="w-4 h-4 text-yellow-500 shrink-0" /></span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-1.5 mt-1 text-xs text-gray-500 dark:text-gray-400">
                    <span className={`px-1.5 py-0.5 rounded border ${estadoColor(t.estado)}`}>{t.estado}</span>
                    {t.prioridad && <span className={`px-1.5 py-0.5 rounded border ${prioridadColor(t.prioridad)}`}>{t.prioridad}</span>}
                    {t.sentimiento && <span className={`px-1.5 py-0.5 rounded border ${sentimientoColor(t.sentimiento)}`}>{t.sentimiento}</span>}
                    <span>{t.category || 'Sin categoría'}</span>
                    <span>· {fechaRelativa(t.created_at)}</span>
                  </div>
                </div>
              </div>
                <div className="shrink-0 text-right">
                  {responsable(t) ? (
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      t.asignado_a === usuarioId ? 'bg-green-500/15 text-green-700 dark:text-green-300' : 'bg-gray-200 dark:bg-gray-700'}`}>
                      {responsable(t)}
                    </span>
                  ) : t.estado !== 'Cerrado' ? (
                    <button
                      onClick={() => onTomar(t)}
                      disabled={tomando === t.id}
                      className="text-sm px-3 py-1.5 rounded-lg border border-primary-500/60 text-primary-700 dark:text-primary-300 hover:bg-primary-500/10 flex items-center gap-1.5 disabled:opacity-50"
                    >
                      {tomando === t.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Hand className="w-4 h-4" />} Tomar
                    </button>
                  ) : null}
                </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
