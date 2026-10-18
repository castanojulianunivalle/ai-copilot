import { useEffect, useState } from 'react';
import { API_URL } from '../lib/api';

type SaludApi = { version?: string; commit?: string };

// HU-10: pie con la versión del frontend y la de la API que responde. En la
// demo muestra que la nube corre el tag presentado sin abrir la consola de Render.
export default function VersionInfo() {
  const [api, setApi] = useState<SaludApi | null>(null);
  const [sinRespuesta, setSinRespuesta] = useState(false);

  useEffect(() => {
    let vigente = true;
    fetch(`${API_URL}/health`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((salud: SaludApi) => { if (vigente) setApi(salud); })
      .catch(() => { if (vigente) setSinRespuesta(true); });
    return () => { vigente = false; };
  }, []);

  const estadoApi = api ? `API v${api.version} · ${api.commit}` : sinRespuesta ? 'API sin respuesta' : 'API…';

  return (
    <footer className="mt-8 mb-2 text-center text-xs text-gray-500 dark:text-gray-400" data-testid="version">
      Frontend v{__APP_VERSION__} · {__APP_COMMIT__} — {estadoApi}
    </footer>
  );
}
