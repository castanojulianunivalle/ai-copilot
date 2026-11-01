// HU-07: dashboard analítico. Los conteos se calculan en Supabase (función metricas_tickets), que rechaza a los
// clientes; aquí solo se dibujan. Cambiar un filtro vuelve a consultar sin recargar la página.
import { useEffect, useState } from 'react';
import { BarChart3, Bot, CalendarRange, CheckCircle2, Clock, Inbox, Loader2, AlertTriangle } from 'lucide-react';
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { supabase } from '../lib/supabase';

type Conteo = { nombre: string; total: number };
export type Metricas = {
  total: number;
  abiertos: number;
  en_proceso: number;
  cerrados: number;
  en_revision: number;
  por_ia: number;
  confianza_media: number | null;
  por_dia: { dia: string; total: number }[];
  por_estado: Conteo[];
  por_categoria: Conteo[];
  por_prioridad: Conteo[];
  por_sentimiento: Conteo[];
};

const ESTADOS = ['Abierto', 'En proceso', 'Cerrado'];
const COLOR_PRIORIDAD: Record<string, string> = { Alta: '#dc2626', Media: '#f59e0b', Baja: '#16a34a' };
const COLOR_ESTADO: Record<string, string> = { Abierto: '#2563eb', 'En proceso': '#f59e0b', Cerrado: '#16a34a' };
const COLOR_BASE = '#6366f1';

function hace(dias: number): string {
  const d = new Date();
  d.setDate(d.getDate() - dias);
  return d.toISOString().slice(0, 10);
}

export async function cargarMetricas(desde: string, hasta: string, estado: string): Promise<Metricas> {
  const { data, error } = await supabase.rpc('metricas_tickets', {
    p_desde: desde || null, p_hasta: hasta || null, p_estado: estado || null,
  });
  if (error) throw new Error(error.message);
  return data as Metricas;
}

function Tarjeta({ titulo, valor, icono, detalle }: { titulo: string; valor: string | number; icono: JSX.Element; detalle?: string }) {
  return (
    <div className="rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 p-4">
      <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">{icono}{titulo}</div>
      <p className="text-2xl font-bold mt-1">{valor}</p>
      {detalle && <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{detalle}</p>}
    </div>
  );
}

function Panel({ titulo, children }: { titulo: string; children: JSX.Element }) {
  return (
    <div className="rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-sm font-semibold mb-3">{titulo}</h3>
      <div className="h-64">{children}</div>
    </div>
  );
}

const tooltip = { contentStyle: { borderRadius: 8, fontSize: 13 }, cursor: { fill: 'rgba(99,102,241,0.08)' } };

export default function Reportes() {
  const [desde, setDesde] = useState(hace(30));
  const [hasta, setHasta] = useState(hace(0));
  const [estado, setEstado] = useState('');
  const [datos, setDatos] = useState<Metricas | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    cargarMetricas(desde, hasta, estado)
      .then(d => { if (vigente) { setDatos(d); setError(null); } })
      .catch(e => { if (vigente) setError(e.message); })
      .finally(() => { if (vigente) setCargando(false); });
    return () => { vigente = false; };
  }, [desde, hasta, estado]);

  const vacio = datos !== null && datos.total === 0;
  const campo = 'rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-1.5 text-sm';

  return (
    <section className="space-y-4" aria-label="Reportes">
      <div className="flex flex-wrap items-end gap-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 p-4">
        <h2 className="flex items-center gap-2 text-lg font-semibold mr-auto"><BarChart3 className="w-5 h-5" />Reportes</h2>
        <label className="text-sm">Desde<br /><input type="date" value={desde} max={hasta} onChange={e => setDesde(e.target.value)} className={campo} /></label>
        <label className="text-sm">Hasta<br /><input type="date" value={hasta} min={desde} onChange={e => setHasta(e.target.value)} className={campo} /></label>
        <label className="text-sm">Estado<br />
          <select value={estado} onChange={e => setEstado(e.target.value)} className={campo} aria-label="Estado">
            <option value="">Todos</option>
            {ESTADOS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>
        {cargando && <Loader2 className="w-5 h-5 animate-spin text-primary-500 mb-2" aria-label="Cargando" />}
      </div>

      {error && (
        <div role="alert" className="rounded-lg border border-red-300 bg-red-50 dark:bg-red-900/20 p-4 text-sm text-red-700 dark:text-red-300">
          No se pudieron cargar las métricas: {error}
        </div>
      )}

      {vacio && (
        <div className="rounded-lg border border-dashed border-gray-300 dark:border-gray-600 p-10 text-center text-gray-500 dark:text-gray-400">
          <CalendarRange className="w-8 h-8 mx-auto mb-2" />
          No hay datos en este rango. Prueba con otras fechas u otro estado.
        </div>
      )}

      {datos && !vacio && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <Tarjeta titulo="Tickets" valor={datos.total} icono={<Inbox className="w-4 h-4" />}
                     detalle={`${datos.abiertos} abiertos · ${datos.en_proceso} en proceso`} />
            <Tarjeta titulo="Cerrados" valor={datos.cerrados} icono={<CheckCircle2 className="w-4 h-4" />}
                     detalle={`${Math.round((100 * datos.cerrados) / datos.total)} % del total`} />
            <Tarjeta titulo="Clasificados por IA" valor={`${Math.round((100 * datos.por_ia) / datos.total)} %`} icono={<Bot className="w-4 h-4" />}
                     detalle={datos.confianza_media !== null ? `confianza media ${datos.confianza_media.toFixed(2)}` : undefined} />
            <Tarjeta titulo="Por revisar" valor={datos.en_revision} icono={<AlertTriangle className="w-4 h-4" />}
                     detalle="marcados para revisión humana" />
          </div>

          <div className="grid lg:grid-cols-2 gap-3">
            <Panel titulo="Tickets por día">
              <ResponsiveContainer>
                <LineChart data={datos.por_dia} margin={{ left: -20, right: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis dataKey="dia" tick={{ fontSize: 11 }} tickFormatter={(d: string) => d.slice(5)} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip {...tooltip} />
                  <Line type="monotone" dataKey="total" name="Tickets" stroke={COLOR_BASE} strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </Panel>
            <Panel titulo="Por estado">
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={datos.por_estado} dataKey="total" nameKey="nombre" innerRadius="45%" outerRadius="75%">
                    {datos.por_estado.map(e => <Cell key={e.nombre} fill={COLOR_ESTADO[e.nombre] ?? COLOR_BASE} />)}
                  </Pie>
                  <Tooltip {...tooltip} />
                  <Legend formatter={(nombre: string) => {
                    const e = datos.por_estado.find(x => x.nombre === nombre);
                    return `${nombre}: ${e?.total ?? 0}`;
                  }} />
                </PieChart>
              </ResponsiveContainer>
            </Panel>
            <Panel titulo="Por categoría (clasificación de la IA)">
              <ResponsiveContainer>
                <BarChart data={datos.por_categoria} layout="vertical" margin={{ left: 30, right: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="nombre" width={110} tick={{ fontSize: 11 }} />
                  <Tooltip {...tooltip} />
                  <Bar dataKey="total" name="Tickets" fill={COLOR_BASE} radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Panel>
            <Panel titulo="Por prioridad">
              <ResponsiveContainer>
                <BarChart data={datos.por_prioridad} margin={{ left: -20, right: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis dataKey="nombre" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip {...tooltip} />
                  <Bar dataKey="total" name="Tickets" radius={[4, 4, 0, 0]}>
                    {datos.por_prioridad.map(p => <Cell key={p.nombre} fill={COLOR_PRIORIDAD[p.nombre] ?? COLOR_BASE} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Panel>
          </div>
          <p className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
            <Clock className="w-3.5 h-3.5" />Fechas en hora de Colombia. Los cálculos se hacen en la base de datos.
          </p>
        </>
      )}
    </section>
  );
}
