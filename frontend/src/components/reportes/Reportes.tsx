/**
 * Sprint 8 · HU-07 · AISCOP-34: panel de reportes.
 *
 * Carga las vistas agregadas de la API y las pinta. Las cifras de titular van
 * como número grande y no como gráfica: un valor único no necesita ejes, y una
 * dona de dos porciones se lee peor que el porcentaje escrito.
 */
import { useCallback, useEffect, useState } from 'react';
import {
  AlertCircle,
  BrainCircuit,
  CheckCircle2,
  Inbox,
  Loader2,
  RefreshCw,
  ShieldAlert,
} from 'lucide-react';
import {
  GraficaCategorias,
  GraficaSentimiento,
  GraficaSerie,
  TablaDiscrepancias,
  type FilaCategoria,
  type FilaDiscrepancia,
  type FilaSentimiento,
  type FilaSerie,
} from './Graficas';

type Resumen = {
  total: number;
  abiertos: number;
  cerrados: number;
  prioridad_alta: number;
  alta_sin_resolver: number;
  clasificados_ia: number;
  requieren_revision: number;
  tono_negativo: number;
  confianza_media_ia: number | null;
  tasa_resolucion: number | null;
};

type Props = {
  apiUrl: string;
  authHeaders: () => HeadersInit;
};

const SECCIONES = ['resumen', 'por-categoria', 'serie', 'por-sentimiento', 'ia-vs-reglas'] as const;

export default function Reportes({ apiUrl, authHeaders }: Props) {
  const [resumen, setResumen] = useState<Resumen | null>(null);
  const [categorias, setCategorias] = useState<FilaCategoria[]>([]);
  const [serie, setSerie] = useState<FilaSerie[]>([]);
  const [sentimiento, setSentimiento] = useState<FilaSentimiento[]>([]);
  const [discrepancias, setDiscrepancias] = useState<FilaDiscrepancia[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      // En paralelo: son cinco vistas independientes y encadenarlas
      // multiplicaría por cinco la espera del agente.
      const respuestas = await Promise.all(
        SECCIONES.map((s) => fetch(`${apiUrl}/reports/${s}`, { headers: authHeaders() }))
      );

      const fallida = respuestas.find((r) => !r.ok);
      if (fallida) {
        const cuerpo = await fallida.json().catch(() => ({}));
        throw new Error(cuerpo.detail || `Error ${fallida.status} al cargar los reportes`);
      }

      const [r, c, s, sent, ia] = await Promise.all(respuestas.map((r) => r.json()));
      setResumen(r.datos ?? null);
      setCategorias(c.datos ?? []);
      setSerie(s.datos ?? []);
      setSentimiento(sent.datos ?? []);
      setDiscrepancias(ia.datos ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudieron cargar los reportes');
    } finally {
      setCargando(false);
    }
  }, [apiUrl, authHeaders]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  if (cargando) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="h-10 w-10 animate-spin text-primary-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-amber-300 bg-amber-50 p-6 dark:border-amber-700/60 dark:bg-amber-900/20">
        <div className="flex items-start gap-3">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600 dark:text-amber-400" />
          <div className="flex-1">
            <p className="font-medium text-amber-900 dark:text-amber-200">
              No se pudieron cargar los reportes
            </p>
            <p className="mt-1 text-sm text-amber-800 dark:text-amber-300">{error}</p>
            <button
              type="button"
              onClick={cargar}
              className="mt-3 inline-flex items-center gap-2 rounded-lg bg-amber-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-amber-700 focus-visible:ring-2 focus-visible:ring-amber-400"
            >
              <RefreshCw className="h-4 w-4" /> Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  const porcentajeIA =
    resumen && resumen.total > 0 ? Math.round((resumen.clasificados_ia / resumen.total) * 100) : 0;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-50">Reportes</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Métricas de la mesa de ayuda y desempeño de la clasificación automática.
          </p>
        </div>
        <button
          type="button"
          onClick={cargar}
          className="inline-flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-600 transition-colors hover:bg-gray-50 focus-visible:ring-2 focus-visible:ring-primary-400 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        >
          <RefreshCw className="h-4 w-4" /> Actualizar
        </button>
      </div>

      {/* Cifras de titular. Un número único no necesita ejes. */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Cifra
          icono={<Inbox className="h-4 w-4" />}
          etiqueta="Tickets abiertos"
          valor={resumen?.abiertos ?? 0}
          nota={`de ${resumen?.total ?? 0} en total`}
        />
        <Cifra
          icono={<CheckCircle2 className="h-4 w-4" />}
          etiqueta="Tasa de resolución"
          valor={resumen?.tasa_resolucion != null ? `${resumen.tasa_resolucion}%` : '—'}
          nota={`${resumen?.cerrados ?? 0} cerrados`}
        />
        <Cifra
          icono={<ShieldAlert className="h-4 w-4" />}
          etiqueta="Prioridad alta sin resolver"
          valor={resumen?.alta_sin_resolver ?? 0}
          nota={`${resumen?.tono_negativo ?? 0} con tono negativo`}
          alerta={(resumen?.alta_sin_resolver ?? 0) > 0}
        />
        <Cifra
          icono={<BrainCircuit className="h-4 w-4" />}
          etiqueta="Clasificados por IA"
          valor={`${porcentajeIA}%`}
          nota={
            resumen?.confianza_media_ia != null
              ? `${Math.round(resumen.confianza_media_ia * 100)}% de confianza media`
              : 'sin datos de confianza'
          }
        />
      </div>

      {(resumen?.requieren_revision ?? 0) > 0 && (
        <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm text-gray-700 dark:border-gray-700 dark:bg-gray-800/60 dark:text-gray-300">
          <AlertCircle className="h-4 w-4 shrink-0 text-gray-400" />
          <span>
            <strong className="tabular-nums">{resumen?.requieren_revision}</strong> tickets fueron
            clasificados por la IA con confianza baja y conviene revisarlos a mano.
          </span>
        </div>
      )}

      <div className="grid gap-5 xl:grid-cols-2">
        <GraficaCategorias datos={categorias} />
        <div className="space-y-5">
          <GraficaSentimiento datos={sentimiento} />
          <TablaDiscrepancias datos={discrepancias} />
        </div>
      </div>

      <GraficaSerie datos={serie} />
    </div>
  );
}

function Cifra({
  icono,
  etiqueta,
  valor,
  nota,
  alerta = false,
}: {
  icono: React.ReactNode;
  etiqueta: string;
  valor: string | number;
  nota?: string;
  alerta?: boolean;
}) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
        {icono}
        <span className="text-xs font-medium">{etiqueta}</span>
      </div>
      {/* El color de alerta va acompañado del icono y de la etiqueta: nunca
          comunica el estado él solo. */}
      <p
        className={`mt-2 text-3xl font-bold tabular-nums ${
          alerta ? 'text-amber-600 dark:text-amber-400' : 'text-gray-900 dark:text-gray-50'
        }`}
      >
        {valor}
      </p>
      {nota && <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{nota}</p>}
    </div>
  );
}
