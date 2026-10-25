// Tipos, textos y llamadas compartidas entre la bandeja del agente y la vista del cliente (HU-13).
import { API_URL } from './api';

export type Estado = 'Abierto' | 'En proceso' | 'Cerrado';

export type Ticket = {
  id: string;
  created_at: string;
  titulo: string;
  description: string;
  category: string | null;
  estado: Estado | string;
  created_by?: string | null;
  // HU-06: salidas del componente inteligente, guardadas con el ticket.
  sentimiento?: string | null;
  prioridad?: string | null;
  confianza_ia?: number | null;
  clasificado_por?: string | null;
  // HU-11 y HU-12: por qué va a revisión y si espera reclasificarse con el modelo.
  motivo_revision?: string | null;
  reclasificar?: boolean | null;
  // HU-13: agente que atiende el ticket.
  asignado_a?: string | null;
  asignado_en?: string | null;
};

export type Persona = { id: string; email: string | null; role: string | null };

export type Evento = {
  id: string;
  ticket_id: string;
  tipo: 'comentario' | 'estado' | 'asignacion';
  texto: string | null;
  interno: boolean;
  estado_antes: string | null;
  estado_despues: string | null;
  asignado_antes: Persona | null;
  asignado_despues: Persona | null;
  autor: Persona | null;
  created_at: string;
};

// ---- Colores ----
export const estadoColor = (estado: string) =>
  estado === 'Cerrado'
    ? 'bg-green-500/10 text-green-700 dark:text-green-300 border-green-500/40'
    : estado === 'En proceso'
      ? 'bg-blue-500/10 text-blue-700 dark:text-blue-300 border-blue-500/40'
      : 'bg-amber-500/10 text-amber-700 dark:text-amber-300 border-amber-500/40';

export const sentimientoColor = (sentimiento: string) => {
  switch (sentimiento) {
    case 'Frustrado':
      return 'bg-red-500/10 text-red-700 dark:text-red-300 border-red-500/40';
    case 'Urgente':
      return 'bg-orange-500/10 text-orange-700 dark:text-orange-300 border-orange-500/40';
    case 'Satisfecho':
      return 'bg-green-500/10 text-green-700 dark:text-green-300 border-green-500/40';
    default:
      return 'bg-slate-500/10 text-slate-600 dark:text-slate-300 border-slate-500/40';
  }
};

export const prioridadColor = (prioridad: string) => {
  switch (prioridad) {
    case 'Alta':
      return 'bg-red-500/10 text-red-700 dark:text-red-300 border-red-500/40';
    case 'Media':
      return 'bg-amber-500/10 text-amber-700 dark:text-amber-300 border-amber-500/40';
    default:
      return 'bg-slate-500/10 text-slate-600 dark:text-slate-300 border-slate-500/40';
  }
};

// Orden de la bandeja: primero lo urgente, y dentro de cada prioridad lo más antiguo.
const PESO_PRIORIDAD: Record<string, number> = { Alta: 0, Media: 1, Baja: 2 };
export const ordenAtencion = (a: Ticket, b: Ticket) =>
  (PESO_PRIORIDAD[a.prioridad ?? ''] ?? 3) - (PESO_PRIORIDAD[b.prioridad ?? ''] ?? 3) ||
  a.created_at.localeCompare(b.created_at);

// ---- Revisión humana (HU-11) ----
// Mismo umbral que la API (CONFIANZA_REVISION_HUMANA en python-api/ai/parser.py), inclusivo.
export const UMBRAL_REVISION = 0.5;

export const formatoConfianza = (confianza: number | null | undefined) =>
  confianza == null ? '' : Number(confianza).toLocaleString('es-CO', { maximumFractionDigits: 2 });

// La API guarda el motivo; los tickets anteriores al Sprint 7 no lo tienen y se deduce de la confianza.
export const motivoRevision = (ticket: Ticket): string | null =>
  ticket.motivo_revision ??
  (ticket.clasificado_por === 'llm' && ticket.confianza_ia != null && Number(ticket.confianza_ia) <= UMBRAL_REVISION
    ? 'confianza_baja'
    : null);

export const requiereRevision = (ticket: Ticket) => motivoRevision(ticket) !== null && ticket.estado !== 'Cerrado';

export const textoMotivo = (ticket: Ticket) =>
  motivoRevision(ticket) === 'urgente_sin_detalle'
    ? 'Es urgente pero no describe el problema: conviene pedirle detalles al cliente.'
    : `La confianza del modelo está en el umbral (${formatoConfianza(UMBRAL_REVISION)}) o por debajo: revisa la categoría.`;

export const origenClasificacion = (ticket: Ticket) =>
  ticket.clasificado_por === 'llm' ? `IA · confianza ${formatoConfianza(ticket.confianza_ia)}` : 'Motor de reglas';

// ---- Lenguaje para el cliente ----
// El cliente no necesita ver prioridades ni confianzas: necesita saber en qué va su caso.
export const PASOS_CLIENTE: { estado: Estado; titulo: string; detalle: string }[] = [
  { estado: 'Abierto', titulo: 'Recibido', detalle: 'Tu solicitud está en la cola de soporte.' },
  { estado: 'En proceso', titulo: 'En atención', detalle: 'Un agente está trabajando en tu caso.' },
  { estado: 'Cerrado', titulo: 'Resuelto', detalle: 'El agente dio por resuelto el caso.' },
];

export const estadoParaCliente = (ticket: Ticket) =>
  PASOS_CLIENTE.find(p => p.estado === ticket.estado) ?? PASOS_CLIENTE[0];

// ---- Fechas ----
export const fechaRelativa = (iso: string) => {
  const minutos = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (minutos < 1) return 'hace un momento';
  if (minutos < 60) return `hace ${minutos} min`;
  const horas = Math.round(minutos / 60);
  if (horas < 24) return `hace ${horas} h`;
  const dias = Math.round(horas / 24);
  return dias < 30 ? `hace ${dias} d` : new Date(iso).toLocaleDateString('es-CO');
};

export const nombreCorto = (persona: Persona | null | undefined) =>
  persona?.email ? persona.email.split('@')[0] : 'alguien';

// ---- API ----
export async function llamarApi<T = unknown>(token: string | undefined, ruta: string, opciones: RequestInit = {}): Promise<T> {
  const r = await fetch(`${API_URL}${ruta}`, {
    ...opciones,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(opciones.headers || {}),
    },
  });
  if (!r.ok) {
    let detalle = `Error ${r.status}`;
    try {
      detalle = (await r.json()).detail || detalle;
    } catch {
      /* respuesta sin JSON */
    }
    throw new Error(detalle);
  }
  return r.json() as Promise<T>;
}
