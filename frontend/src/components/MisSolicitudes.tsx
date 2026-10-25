// HU-13: vista del cliente. Crea solicitudes y ve en qué va cada una, en su lenguaje: sin prioridades, confianzas
// ni motores de clasificación, que son herramientas del agente.
import { RefObject, useState } from 'react';
import { Plus, Loader2, Clock, UserCheck, CheckCircle2, ChevronRight, LifeBuoy } from 'lucide-react';
import { Ticket, estadoParaCliente, fechaRelativa } from '../lib/tickets';

type Props = {
  tickets: Ticket[];
  cargando: boolean;
  onAbrir: (t: Ticket) => void;
  onCrear: (titulo: string, descripcion: string) => Promise<boolean>;
  formRef?: RefObject<HTMLFormElement>;
};

const iconoEstado = (estado: string) =>
  estado === 'Cerrado' ? <CheckCircle2 className="w-5 h-5 text-green-600" />
    : estado === 'En proceso' ? <UserCheck className="w-5 h-5 text-blue-600" />
      : <Clock className="w-5 h-5 text-amber-600" />;

export default function MisSolicitudes({ tickets, cargando, onAbrir, onCrear, formRef }: Props) {
  const [titulo, setTitulo] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [verCerradas, setVerCerradas] = useState(false);

  const enviar = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!titulo.trim() || !descripcion.trim()) return;
    setEnviando(true);
    const ok = await onCrear(titulo.trim(), descripcion.trim());
    setEnviando(false);
    if (ok) {
      setTitulo('');
      setDescripcion('');
    }
  };

  const activas = tickets.filter(t => t.estado !== 'Cerrado');
  const cerradas = tickets.filter(t => t.estado === 'Cerrado');
  const lista = verCerradas ? cerradas : activas;

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <section className="card lg:col-span-2 h-fit">
        <h2 className="font-semibold text-lg flex items-center gap-2"><LifeBuoy className="w-5 h-5 text-primary-500" /> Nueva solicitud</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Cuéntanos qué pasa. La clasificamos al instante y un agente la toma desde la cola de soporte.
        </p>
        <form ref={formRef} onSubmit={enviar} className="flex flex-col gap-3 mt-4" aria-label="Crear solicitud">
          <label className="text-sm font-medium">
            Asunto
            <input
              type="text"
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              placeholder="Ej.: No puedo pagar mi factura"
              maxLength={150}
              disabled={enviando}
              className="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 font-normal focus-visible:ring-2 focus-visible:ring-primary-400"
              aria-label="Título del ticket"
            />
          </label>
          <label className="text-sm font-medium">
            Describe el problema
            <textarea
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              placeholder="Qué intentabas hacer, qué pasó y desde cuándo. Entre más detalle, más rápido lo resolvemos."
              rows={5}
              disabled={enviando}
              className="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 font-normal resize-y focus-visible:ring-2 focus-visible:ring-primary-400"
              aria-label="Descripción del ticket"
            />
          </label>
          <button type="submit" disabled={enviando || !titulo.trim() || !descripcion.trim()} className="btn-primary flex items-center justify-center gap-2 disabled:opacity-50">
            {enviando ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            {enviando ? 'Enviando…' : 'Enviar solicitud'}
          </button>
        </form>
      </section>

      <section className="card lg:col-span-3">
        <div className="flex items-center justify-between gap-2">
          <h2 className="font-semibold text-lg">Mis solicitudes</h2>
          <div className="flex rounded-lg border border-gray-300 dark:border-gray-700 overflow-hidden text-sm" role="tablist">
            <button role="tab" aria-selected={!verCerradas} onClick={() => setVerCerradas(false)}
              className={`px-3 py-1 ${!verCerradas ? 'bg-primary-500 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-800'}`}>
              En curso ({activas.length})
            </button>
            <button role="tab" aria-selected={verCerradas} onClick={() => setVerCerradas(true)}
              className={`px-3 py-1 ${verCerradas ? 'bg-primary-500 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-800'}`}>
              Resueltas ({cerradas.length})
            </button>
          </div>
        </div>

        {cargando && tickets.length === 0 ? (
          <div className="py-10 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : lista.length === 0 ? (
          <p className="py-10 text-center text-gray-500 dark:text-gray-400">
            {verCerradas ? 'Aún no tienes solicitudes resueltas.' : 'No tienes solicitudes en curso. Si algo falla, cuéntanos en el formulario.'}
          </p>
        ) : (
          <ul className="mt-4 space-y-2">
            {lista.map(t => {
              const paso = estadoParaCliente(t);
              return (
                <li key={t.id}>
                  <button onClick={() => onAbrir(t)}
                    className="w-full text-left flex items-center gap-3 rounded-lg border border-gray-200 dark:border-gray-800 p-3 hover:border-primary-500/60 hover:bg-primary-500/5 transition-colors">
                    {iconoEstado(t.estado)}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{t.titulo}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        <strong className="font-medium text-gray-700 dark:text-gray-300">{paso.titulo}</strong> · {paso.detalle}
                      </p>
                      <p className="text-xs text-gray-400 mt-0.5">{t.category ?? 'Sin categoría'} · enviada {fechaRelativa(t.created_at)}</p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
