/**
 * Sprint 8 · HU-07 · AISCOP-34: componentes de gráficas con Recharts.
 *
 * Reglas aplicadas (guía de visualización):
 * - Un solo eje por gráfica. Nunca dos escalas Y: creados y cerrados son la
 *   misma unidad y comparten eje; si hiciera falta comparar magnitudes de
 *   escalas distintas, serían dos gráficas.
 * - Leyenda siempre presente con dos o más series; con una sola serie no hay
 *   leyenda porque el título ya la nombra.
 * - Rejilla y ejes recesivos; el dato es lo que tiene contraste.
 * - Tooltip al pasar por encima en todas las gráficas.
 * - Cada gráfica ofrece vista de tabla: la identidad nunca depende solo del
 *   color, y quien use lector de pantalla tiene los números.
 * - Los textos van con tinta de texto, nunca con el color de la serie.
 */
import { useState } from 'react';
import { Table2, BarChart3 } from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { usePaleta, type Paleta } from './paleta';

// ---------------------------------------------------------------------------
// Envoltorio común: título, alternancia gráfica/tabla y estado vacío
// ---------------------------------------------------------------------------
type PanelProps = {
  titulo: string;
  descripcion?: string;
  hayDatos: boolean;
  tabla: React.ReactNode;
  children: React.ReactNode;
};

function Panel({ titulo, descripcion, hayDatos, tabla, children }: PanelProps) {
  const [verTabla, setVerTabla] = useState(false);

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-base font-semibold text-gray-900 dark:text-gray-50">{titulo}</h3>
          {descripcion && (
            <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{descripcion}</p>
          )}
        </div>
        {hayDatos && (
          <button
            type="button"
            onClick={() => setVerTabla((v) => !v)}
            className="shrink-0 rounded-lg border border-gray-200 p-2 text-gray-500 transition-colors hover:bg-gray-50 focus-visible:ring-2 focus-visible:ring-primary-400 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700"
            aria-label={verTabla ? 'Ver como gráfica' : 'Ver como tabla'}
            title={verTabla ? 'Ver como gráfica' : 'Ver como tabla'}
          >
            {verTabla ? <BarChart3 className="h-4 w-4" /> : <Table2 className="h-4 w-4" />}
          </button>
        )}
      </div>

      {!hayDatos ? (
        <p className="py-10 text-center text-sm text-gray-500 dark:text-gray-400">
          Todavía no hay datos suficientes para esta gráfica.
        </p>
      ) : verTabla ? (
        <div className="max-h-72 overflow-auto">{tabla}</div>
      ) : (
        children
      )}
    </section>
  );
}

function Tabla({ cabeceras, filas }: { cabeceras: string[]; filas: (string | number)[][] }) {
  return (
    <table className="w-full text-sm">
      <thead className="sticky top-0 bg-white dark:bg-gray-800">
        <tr className="border-b border-gray-200 text-left dark:border-gray-700">
          {cabeceras.map((c, i) => (
            <th
              key={c}
              className={`py-2 font-medium text-gray-500 dark:text-gray-400 ${i > 0 ? 'text-right' : ''}`}
            >
              {c}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {filas.map((fila, i) => (
          <tr key={i} className="border-b border-gray-100 last:border-0 dark:border-gray-700/50">
            {fila.map((celda, j) => (
              <td
                key={j}
                className={`py-1.5 text-gray-700 dark:text-gray-200 ${
                  j > 0 ? 'text-right tabular-nums' : ''
                }`}
              >
                {celda}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function estiloTooltip(p: Paleta) {
  return {
    contentStyle: {
      backgroundColor: p.superficieTooltip,
      border: `1px solid ${p.borde}`,
      borderRadius: 8,
      fontSize: 12,
      color: p.tintaPrimaria,
    },
    labelStyle: { color: p.tintaSecundaria, marginBottom: 4 },
    itemStyle: { color: p.tintaPrimaria },
    cursor: { fill: p.rejilla, fillOpacity: 0.35 },
  };
}

const ejeComun = (p: Paleta) => ({
  stroke: p.eje,
  tick: { fill: p.tintaTenue, fontSize: 11 },
  tickLine: false,
});

// ---------------------------------------------------------------------------
// Tickets por categoría — barras horizontales apiladas
// ---------------------------------------------------------------------------
// Horizontales porque las etiquetas son largas ("Integraciones", "Rendimiento")
// y en vertical habría que rotarlas. Apiladas porque abiertos + cerrados es el
// total: la longitud completa de la barra sigue significando algo.
export type FilaCategoria = {
  categoria: string;
  total: number;
  abiertos: number;
  cerrados: number;
};

export function GraficaCategorias({ datos }: { datos: FilaCategoria[] }) {
  const p = usePaleta();
  const orden = [...datos].sort((a, b) => b.total - a.total);

  return (
    <Panel
      titulo="Tickets por categoría"
      descripcion="Ordenado por volumen. La barra completa es el total."
      hayDatos={orden.length > 0}
      tabla={
        <Tabla
          cabeceras={['Categoría', 'Abiertos', 'Cerrados', 'Total']}
          filas={orden.map((d) => [d.categoria, d.abiertos, d.cerrados, d.total])}
        />
      }
    >
      <ResponsiveContainer width="100%" height={Math.max(220, orden.length * 34)}>
        <BarChart data={orden} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 4 }}>
          <CartesianGrid horizontal={false} stroke={p.rejilla} />
          <XAxis type="number" {...ejeComun(p)} allowDecimals={false} />
          <YAxis type="category" dataKey="categoria" width={104} {...ejeComun(p)} />
          <Tooltip {...estiloTooltip(p)} />
          <Legend
            wrapperStyle={{ fontSize: 12, color: p.tintaSecundaria, paddingTop: 8 }}
            iconType="square"
          />
          {/* stroke del color de la superficie = el separador de 2px entre
              segmentos apilados que pide la guía. */}
          <Bar
            dataKey="abiertos"
            name="Abiertos"
            stackId="estado"
            fill={p.serie1}
            stroke={p.superficie}
            strokeWidth={2}
          />
          <Bar
            dataKey="cerrados"
            name="Cerrados"
            stackId="estado"
            fill={p.serie2}
            stroke={p.superficie}
            strokeWidth={2}
            radius={[0, 4, 4, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Serie diaria — líneas
// ---------------------------------------------------------------------------
export type FilaSerie = {
  dia: string;
  creados: number;
  cerrados: number;
};

const diaCorto = (iso: string) => {
  const d = new Date(iso + 'T00:00:00');
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleDateString('es-CO', { day: '2-digit', month: 'short' });
};

export function GraficaSerie({ datos }: { datos: FilaSerie[] }) {
  const p = usePaleta();

  return (
    <Panel
      titulo="Actividad diaria"
      descripcion="Últimos 90 días. Los días sin tickets se muestran en cero, no se saltan."
      hayDatos={datos.length > 0}
      tabla={
        <Tabla
          cabeceras={['Día', 'Creados', 'Cerrados']}
          filas={[...datos].reverse().map((d) => [diaCorto(d.dia), d.creados, d.cerrados])}
        />
      }
    >
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={datos} margin={{ top: 4, right: 16, bottom: 4, left: -12 }}>
          <CartesianGrid vertical={false} stroke={p.rejilla} />
          <XAxis
            dataKey="dia"
            tickFormatter={diaCorto}
            minTickGap={36}
            {...ejeComun(p)}
          />
          {/* Un solo eje Y: ambas series son conteos de tickets. */}
          <YAxis {...ejeComun(p)} allowDecimals={false} width={44} />
          <Tooltip
            {...estiloTooltip(p)}
            cursor={{ stroke: p.eje, strokeWidth: 1 }}
            labelFormatter={(v) => diaCorto(String(v))}
          />
          <Legend
            wrapperStyle={{ fontSize: 12, color: p.tintaSecundaria, paddingTop: 8 }}
            iconType="plainline"
          />
          {/* Sin punto en cada fecha: con 90 días serían 180 marcas y taparían
              la línea. El punto aparece al pasar por encima. */}
          <Line
            type="monotone"
            dataKey="creados"
            name="Creados"
            stroke={p.serie1}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="cerrados"
            name="Cerrados"
            stroke={p.serie2}
            strokeWidth={2}
            strokeDasharray="5 3"
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Sentimiento — barras de una sola serie
// ---------------------------------------------------------------------------
// Una sola serie y por tanto un solo color: la identidad la llevan las
// etiquetas del eje. Pintar cada barra de un color distinto sería color sin
// información, y además gastaría cuatro ranuras categóricas para nada.
export type FilaSentimiento = {
  sentimiento: string;
  total: number;
  abiertos: number;
};

export function GraficaSentimiento({ datos }: { datos: FilaSentimiento[] }) {
  const p = usePaleta();

  return (
    <Panel
      titulo="Tono detectado por la IA"
      descripcion="Sentimiento del cliente al abrir el ticket."
      hayDatos={datos.length > 0}
      tabla={
        <Tabla
          cabeceras={['Tono', 'Abiertos', 'Total']}
          filas={datos.map((d) => [d.sentimiento, d.abiertos, d.total])}
        />
      }
    >
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={datos} margin={{ top: 4, right: 16, bottom: 4, left: -12 }}>
          <CartesianGrid vertical={false} stroke={p.rejilla} />
          <XAxis dataKey="sentimiento" {...ejeComun(p)} />
          <YAxis {...ejeComun(p)} allowDecimals={false} width={44} />
          <Tooltip {...estiloTooltip(p)} />
          <Bar dataKey="total" name="Tickets" fill={p.serie1} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Discrepancias IA vs reglas — tabla, no gráfica
// ---------------------------------------------------------------------------
// Deliberadamente no es una gráfica. El dato es un cruce de dos categorías y un
// conteo; un mapa de calor de 11×11 sobre datos escasos es casi todo celdas
// vacías. La pregunta que responde ("¿en qué se separan los motores?") se
// contesta mejor con una lista ordenada.
export type FilaDiscrepancia = {
  categoria_reglas: string;
  categoria_llm: string;
  total: number;
  confianza_media: number | null;
};

export function TablaDiscrepancias({ datos }: { datos: FilaDiscrepancia[] }) {
  const discrepantes = datos.filter((d) => d.categoria_reglas !== d.categoria_llm);
  const acuerdos = datos.length - discrepantes.length;

  return (
    <Panel
      titulo="Dónde discrepan la IA y el motor de reglas"
      descripcion={
        datos.length > 0
          ? `${acuerdos} combinaciones coincidentes · ${discrepantes.length} en desacuerdo. Sin etiqueta humana no se sabe quién acierta: son los casos que conviene anotar.`
          : 'Requiere tickets clasificados por ambos motores.'
      }
      hayDatos={discrepantes.length > 0}
      tabla={
        <Tabla
          cabeceras={['Reglas dijo', 'IA dijo', 'Casos', 'Confianza IA']}
          filas={discrepantes.map((d) => [
            d.categoria_reglas,
            d.categoria_llm,
            d.total,
            d.confianza_media != null ? `${Math.round(d.confianza_media * 100)}%` : '—',
          ])}
        />
      }
    >
      <Tabla
        cabeceras={['Reglas dijo', 'IA dijo', 'Casos', 'Confianza IA']}
        filas={discrepantes.map((d) => [
          d.categoria_reglas,
          d.categoria_llm,
          d.total,
          d.confianza_media != null ? `${Math.round(d.confianza_media * 100)}%` : '—',
        ])}
      />
    </Panel>
  );
}
