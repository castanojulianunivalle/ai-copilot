// HU-13: detalle de un ticket. El agente lo atiende (tomar, comentar, cambiar estado); el cliente ve en qué va su
// caso y conversa con soporte. Mismo componente, contenido distinto según el rol.
import { useCallback, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  X, Loader2, Hand, LogOut as Soltar, PlayCircle, CheckCircle2, RotateCcw, Send, Lock, MessageSquare,
  ArrowRightLeft, UserCheck, Sparkles, AlertTriangle, Edit, Trash2,
} from 'lucide-react';
import {
  Evento, Persona, Ticket, PASOS_CLIENTE, estadoColor, fechaRelativa, llamarApi, nombreCorto, origenClasificacion,
  prioridadColor, requiereRevision, sentimientoColor, textoMotivo,
} from '../lib/tickets';

type Props = {
  ticket: Ticket;
  rol: 'cliente' | 'agente' | 'administrador';
  usuarioId: string;
  token?: string;
  agentes: Persona[];
  onCerrar: () => void;
  onCambio: () => Promise<void> | void;
  notificar: (tipo: 'success' | 'error' | 'info', mensaje: string) => void;
  onEditar?: (t: Ticket) => void;
  onEliminar?: (t: Ticket) => void;
};

export default function PanelTicket({
  ticket, rol, usuarioId, token, agentes, onCerrar, onCambio, notificar, onEditar, onEliminar,
}: Props) {
  const esEquipo = rol !== 'cliente';
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [cargando, setCargando] = useState(true);
  const [texto, setTexto] = useState('');
  const [interno, setInterno] = useState(false);
  const [ocupado, setOcupado] = useState<string | null>(null);

  const quien = (id?: string | null) => agentes.find(a => a.id === id) ?? null;
  const asignado = ticket.asignado_a ? quien(ticket.asignado_a) : null;
  const esMio = ticket.asignado_a === usuarioId;
  const deOtro = !!ticket.asignado_a && !esMio;
  const puedeOperar = !deOtro || rol === 'administrador';

  const cargarEventos = useCallback(async () => {
    try {
      setEventos(await llamarApi<Evento[]>(token, `/tickets/${ticket.id}/eventos`));
    } catch (e) {
      console.error(e);
    } finally {
      setCargando(false);
    }
  }, [ticket.id, token]);

  useEffect(() => {
    setCargando(true);
    cargarEventos();
    // Si otro agente comenta o cambia el estado mientras el panel está abierto, se ve sin recargar.
    const intervalo = setInterval(cargarEventos, 15000);
    return () => clearInterval(intervalo);
  }, [cargarEventos]);

  // alExito corre apenas la API confirma y antes de recargar: si se vaciara la caja después de recargar, borraría lo
  // que alguien alcanzó a escribir mientras tanto.
  const accion = async (nombre: string, ruta: string, opciones: RequestInit, exito: string, alExito?: () => void) => {
    setOcupado(nombre);
    try {
      await llamarApi(token, ruta, opciones);
      alExito?.();
      notificar('success', exito);
      await Promise.all([onCambio(), cargarEventos()]);
      return true;
    } catch (e) {
      notificar('error', (e as Error).message);
      return false;
    } finally {
      setOcupado(null);
    }
  };

  const tomar = () => accion('tomar', `/tickets/${ticket.id}/tomar`, { method: 'POST' }, 'Tomaste el ticket');
  const liberar = () => accion('liberar', `/tickets/${ticket.id}/liberar`, { method: 'POST' }, 'Devolviste el ticket a la cola');
  const reasignar = (agenteId: string) =>
    accion('reasignar', `/tickets/${ticket.id}/asignar`, { method: 'POST', body: JSON.stringify({ agente_id: agenteId }) },
      'Ticket reasignado');

  // El comentario escrito acompaña al cambio de estado, salvo que sea una nota interna (esa no la vería el cliente).
  const cambiarEstado = async (estado: string, exito: string) => {
    const comentario = !interno && texto.trim() ? texto.trim() : null;
    await accion(estado, `/tickets/${ticket.id}/estado?estado=${encodeURIComponent(estado)}`,
      { method: 'PATCH', body: JSON.stringify({ comentario }) }, exito, () => comentario && setTexto(''));
  };

  const comentar = async () => {
    if (!texto.trim()) return;
    await accion('comentar', `/tickets/${ticket.id}/comentarios`,
      { method: 'POST', body: JSON.stringify({ texto: texto.trim(), interno: esEquipo && interno }) },
      interno ? 'Nota interna guardada' : esEquipo ? 'Respuesta enviada al cliente' : 'Mensaje enviado',
      () => setTexto(''));
  };

  const pasoActual = PASOS_CLIENTE.findIndex(p => p.estado === ticket.estado);

  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex justify-end z-50"
      onClick={onCerrar}
    >
      <motion.aside
        initial={{ x: 480 }} animate={{ x: 0 }} exit={{ x: 480 }} transition={{ type: 'tween', duration: 0.2 }}
        className="h-full w-full max-w-xl bg-white dark:bg-gray-900 shadow-2xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
        role="dialog" aria-label={esEquipo ? 'Atención del ticket' : 'Detalle de tu solicitud'}
      >
        {/* Encabezado */}
        <div className="p-5 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-xs font-mono text-gray-500">#{ticket.id.slice(-8)} · {fechaRelativa(ticket.created_at)}</p>
              <h2 className="text-lg font-semibold mt-1 break-words">{ticket.titulo}</h2>
            </div>
            <button onClick={onCerrar} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800" aria-label="Cerrar panel">
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="flex flex-wrap items-center gap-2 mt-3 text-xs">
            <span className={`px-2 py-0.5 rounded border font-medium ${estadoColor(ticket.estado)}`}>{ticket.estado}</span>
            {esEquipo && ticket.prioridad && (
              <span className={`px-2 py-0.5 rounded border ${prioridadColor(ticket.prioridad)}`}>Prioridad {ticket.prioridad}</span>
            )}
            {ticket.category && <span className="px-2 py-0.5 rounded border border-gray-300 dark:border-gray-700">{ticket.category}</span>}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* Cliente: en qué va su caso */}
          {!esEquipo && (
            <ol className="grid grid-cols-3 gap-2" aria-label="Avance de tu solicitud">
              {PASOS_CLIENTE.map((p, i) => (
                <li key={p.estado} className={`rounded-lg border p-2 text-center ${
                  i <= pasoActual ? 'border-primary-500 bg-primary-500/10' : 'border-gray-200 dark:border-gray-800 opacity-60'}`}>
                  <p className={`text-sm font-semibold ${i === pasoActual ? 'text-primary-600 dark:text-primary-300' : ''}`}>{p.titulo}</p>
                  {i === pasoActual && <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{p.detalle}</p>}
                </li>
              ))}
            </ol>
          )}

          <section>
            <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-1">{esEquipo ? 'Lo que escribió el cliente' : 'Tu solicitud'}</h3>
            <p className="whitespace-pre-wrap text-sm leading-relaxed bg-gray-50 dark:bg-gray-800/60 rounded-lg p-3">{ticket.description}</p>
            {!esEquipo && ticket.estado === 'Abierto' && !ticket.asignado_a && (onEditar || onEliminar) && (
              <div className="flex gap-2 mt-2">
                {onEditar && (
                  <button onClick={() => onEditar(ticket)} className="text-xs px-2 py-1 rounded border border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center gap-1">
                    <Edit className="w-3.5 h-3.5" /> Editar
                  </button>
                )}
                {onEliminar && (
                  <button onClick={() => onEliminar(ticket)} className="text-xs px-2 py-1 rounded border border-red-400/50 text-red-600 dark:text-red-300 hover:bg-red-500/10 flex items-center gap-1">
                    <Trash2 className="w-3.5 h-3.5" /> Eliminar
                  </button>
                )}
              </div>
            )}
          </section>

          {/* Agente: la clasificación de la IA y quién atiende */}
          {esEquipo && (
            <>
              <section className="rounded-lg border border-gray-200 dark:border-gray-800 p-3">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-2 flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5" /> Clasificación automática
                </h3>
                <div className="flex flex-wrap gap-2 text-xs">
                  {ticket.sentimiento && <span className={`px-2 py-0.5 rounded border ${sentimientoColor(ticket.sentimiento)}`}>{ticket.sentimiento}</span>}
                  <span className="px-2 py-0.5 rounded border bg-primary-500/10 text-primary-700 dark:text-primary-300 border-primary-500/40">{origenClasificacion(ticket)}</span>
                </div>
                {requiereRevision(ticket) && (
                  <p className="mt-2 text-sm px-3 py-2 rounded border bg-yellow-400/20 text-yellow-800 dark:text-yellow-300 border-yellow-500/50 flex gap-2">
                    <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" /> {textoMotivo(ticket)}
                  </p>
                )}
              </section>

              <section className="rounded-lg border border-gray-200 dark:border-gray-800 p-3">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-2">Responsable</h3>
                <div className="flex flex-wrap items-center gap-2">
                  {!ticket.asignado_a && (
                    <>
                      <span className="text-sm text-gray-600 dark:text-gray-300">Libre: nadie lo ha tomado.</span>
                      {ticket.estado !== 'Cerrado' && (
                        <button onClick={tomar} disabled={!!ocupado} className="btn-primary text-sm py-1.5 flex items-center gap-1.5 disabled:opacity-50">
                          {ocupado === 'tomar' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Hand className="w-4 h-4" />} Tomar ticket
                        </button>
                      )}
                    </>
                  )}
                  {esMio && (
                    <>
                      <span className="text-sm flex items-center gap-1 text-green-700 dark:text-green-300"><UserCheck className="w-4 h-4" /> Lo estás atendiendo tú</span>
                      <button onClick={liberar} disabled={!!ocupado} className="text-sm px-2.5 py-1 rounded border border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center gap-1 disabled:opacity-50">
                        <Soltar className="w-4 h-4" /> Devolver a la cola
                      </button>
                    </>
                  )}
                  {deOtro && (
                    <>
                      <span className="text-sm">Lo atiende <strong>{asignado?.email ?? 'otro agente'}</strong>.</span>
                      {rol === 'administrador' && (
                        <button onClick={liberar} disabled={!!ocupado} className="text-sm px-2.5 py-1 rounded border border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50">Liberar</button>
                      )}
                    </>
                  )}
                </div>
                {rol === 'administrador' && ticket.estado !== 'Cerrado' && (
                  <label className="mt-3 flex items-center gap-2 text-sm">
                    <ArrowRightLeft className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-600 dark:text-gray-300">Reasignar a</span>
                    <select
                      value=""
                      onChange={(e) => e.target.value && reasignar(e.target.value)}
                      disabled={!!ocupado}
                      className="rounded border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-2 py-1 text-sm"
                    >
                      <option value="">elige un agente…</option>
                      {agentes.filter(a => a.id !== ticket.asignado_a).map(a => (
                        <option key={a.id} value={a.id}>{a.email ?? a.id}</option>
                      ))}
                    </select>
                  </label>
                )}
              </section>
            </>
          )}

          {/* Historial */}
          <section>
            <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-2 flex items-center gap-1">
              <MessageSquare className="w-3.5 h-3.5" /> {esEquipo ? 'Historial' : 'Conversación con soporte'}
            </h3>
            {cargando ? (
              <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
            ) : eventos.length === 0 ? (
              <p className="text-sm text-gray-500">{esEquipo ? 'Sin movimientos todavía.' : 'Todavía no hay mensajes. Te avisaremos aquí cuando un agente responda.'}</p>
            ) : (
              <ul className="space-y-3">
                {eventos.map(ev => <ItemHistorial key={ev.id} ev={ev} usuarioId={usuarioId} esEquipo={esEquipo} />)}
              </ul>
            )}
          </section>
        </div>

        {/* Redactar y actuar */}
        {(esEquipo || ticket.estado !== 'Cerrado') && (
          <div className="border-t border-gray-200 dark:border-gray-800 p-4 space-y-3 bg-gray-50 dark:bg-gray-900">
            {esEquipo && deOtro && rol !== 'administrador' && (
              <p className="text-xs text-gray-500">Este ticket lo tiene otro agente: puedes dejar notas, pero los cambios de estado son de quien lo atiende.</p>
            )}
            <textarea
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              placeholder={esEquipo ? (interno ? 'Nota para el equipo (el cliente no la ve)…' : 'Respuesta para el cliente…') : 'Escribe un mensaje para el agente…'}
              maxLength={2000}
              rows={3}
              className={`w-full rounded-lg border px-3 py-2 text-sm bg-white dark:bg-gray-800 resize-y focus-visible:ring-2 focus-visible:ring-primary-400 ${
                interno ? 'border-yellow-500/60' : 'border-gray-300 dark:border-gray-700'}`}
              aria-label={esEquipo ? 'Comentario' : 'Mensaje'}
            />
            <div className="flex flex-wrap items-center justify-between gap-2">
              {esEquipo ? (
                <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
                  <input type="checkbox" checked={interno} onChange={(e) => setInterno(e.target.checked)} />
                  <Lock className="w-3.5 h-3.5 text-yellow-600" /> Nota interna
                </label>
              ) : <span />}
              <button onClick={comentar} disabled={!texto.trim() || !!ocupado}
                className="px-3 py-1.5 rounded-lg border border-primary-500/60 text-primary-700 dark:text-primary-300 hover:bg-primary-500/10 text-sm flex items-center gap-1.5 disabled:opacity-40">
                {ocupado === 'comentar' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                {esEquipo ? (interno ? 'Guardar nota' : 'Responder') : 'Enviar'}
              </button>
            </div>

            {esEquipo && (
              <div className="flex flex-wrap gap-2 pt-1 border-t border-gray-200 dark:border-gray-800">
                {ticket.estado === 'Abierto' && (
                  <button onClick={() => cambiarEstado('En proceso', 'Empezaste a atender el ticket')} disabled={!!ocupado || !puedeOperar}
                    className="btn-primary text-sm py-1.5 flex items-center gap-1.5 disabled:opacity-40">
                    {ocupado === 'En proceso' ? <Loader2 className="w-4 h-4 animate-spin" /> : <PlayCircle className="w-4 h-4" />} Empezar atención
                  </button>
                )}
                {ticket.estado !== 'Cerrado' && (
                  <button onClick={() => cambiarEstado('Cerrado', 'Ticket resuelto y cerrado')} disabled={!!ocupado || !puedeOperar}
                    className="text-sm px-3 py-1.5 rounded-lg bg-green-600 hover:bg-green-700 text-white flex items-center gap-1.5 disabled:opacity-40">
                    {ocupado === 'Cerrado' ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />} Resolver y cerrar
                  </button>
                )}
                {ticket.estado === 'Cerrado' && (
                  <button onClick={() => cambiarEstado('Abierto', 'Ticket reabierto')} disabled={!!ocupado || !puedeOperar}
                    className="text-sm px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center gap-1.5 disabled:opacity-40">
                    <RotateCcw className="w-4 h-4" /> Reabrir
                  </button>
                )}
                {!interno && texto.trim() && ticket.estado !== 'Cerrado' && (
                  <p className="w-full text-xs text-gray-500">El texto escrito se enviará al cliente junto con el cambio de estado.</p>
                )}
              </div>
            )}
          </div>
        )}
      </motion.aside>
    </motion.div>
  );
}

function ItemHistorial({ ev, usuarioId, esEquipo }: { ev: Evento; usuarioId: string; esEquipo: boolean }) {
  const yo = ev.autor?.id === usuarioId;
  const autor = yo ? 'Tú' : ev.autor?.role === 'cliente' ? (esEquipo ? 'Cliente' : 'Tú') : esEquipo ? nombreCorto(ev.autor) : 'Soporte';
  const cuando = <span className="text-xs text-gray-500" title={new Date(ev.created_at).toLocaleString()}>{fechaRelativa(ev.created_at)}</span>;

  if (ev.tipo === 'comentario') {
    const delCliente = ev.autor?.role === 'cliente';
    return (
      <li className={`rounded-lg p-3 text-sm ${
        ev.interno ? 'bg-yellow-400/15 border border-yellow-500/40'
          : delCliente ? 'bg-gray-100 dark:bg-gray-800' : 'bg-primary-500/10 border border-primary-500/30'}`}>
        <div className="flex items-center justify-between mb-1">
          <span className="font-medium flex items-center gap-1">
            {ev.interno && <Lock className="w-3.5 h-3.5 text-yellow-600" />}{autor}{ev.interno && <span className="text-xs font-normal text-yellow-700 dark:text-yellow-300"> · nota interna</span>}
          </span>
          {cuando}
        </div>
        <p className="whitespace-pre-wrap">{ev.texto}</p>
      </li>
    );
  }
  let resumen = '';
  if (ev.tipo === 'estado') {
    resumen = esEquipo
      ? `cambió el estado de ${ev.estado_antes ?? '—'} a ${ev.estado_despues}`
      : ev.estado_despues === 'En proceso' ? 'empezó a atender tu caso'
        : ev.estado_despues === 'Cerrado' ? 'marcó tu caso como resuelto'
          : 'reabrió tu caso';
  } else if (ev.asignado_despues && !ev.asignado_antes && ev.asignado_despues.id === ev.autor?.id) {
    resumen = 'tomó el ticket';
  } else if (!ev.asignado_despues) {
    resumen = 'devolvió el ticket a la cola';
  } else {
    resumen = `asignó el ticket a ${nombreCorto(ev.asignado_despues)}`;
  }
  if (!esEquipo && ev.tipo === 'asignacion') return null;
  return (
    <li className="text-sm">
      <div className="flex items-center justify-between text-gray-600 dark:text-gray-400">
        <span><strong className="text-gray-800 dark:text-gray-200">{autor}</strong> {resumen}</span>
        {cuando}
      </div>
      {ev.texto && <p className="mt-1 ml-3 pl-3 border-l-2 border-primary-500/50 whitespace-pre-wrap">{ev.texto}</p>}
    </li>
  );
}
