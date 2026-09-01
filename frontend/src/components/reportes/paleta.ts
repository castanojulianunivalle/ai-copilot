/**
 * Sprint 8 · HU-07 · AISCOP-34: paleta de las gráficas.
 *
 * Recharts pinta SVG, así que necesita valores de color reales; no puede
 * consumir clases de Tailwind. Este módulo observa la clase `dark` del
 * documento —que es como el resto de la app conmuta el tema— y devuelve los
 * valores del modo activo.
 *
 * El modo oscuro son pasos propios, escalonados para el fondo oscuro, no una
 * inversión automática del claro: invertir un color validado deja de estar
 * validado.
 *
 * Ambos juegos pasan las comprobaciones de la guía de visualización contra la
 * superficie real de la tarjeta (#ffffff en claro, gray-800 #1f2937 en oscuro):
 *
 *   claro   CVD ΔE 24.7 (protanopia) · visión normal 33.6 · contraste ≥ 3:1
 *   oscuro  CVD ΔE 26.8 (protanopia) · visión normal 31.8 · contraste ≥ 3:1
 *
 * Los umbrales son 8 y 15, así que hay margen de sobra. Si se añade una tercera
 * serie hay que volver a pasar el validador: el margen actual no se hereda.
 */
import { useEffect, useState } from 'react';

export type Paleta = {
  serie1: string;
  serie2: string;
  rejilla: string;
  eje: string;
  tintaPrimaria: string;
  tintaSecundaria: string;
  tintaTenue: string;
  superficie: string;
  superficieTooltip: string;
  borde: string;
};

const CLARO: Paleta = {
  serie1: '#2a78d6',
  serie2: '#eb6834',
  rejilla: '#e5e7eb',
  eje: '#d1d5db',
  tintaPrimaria: '#111827',
  tintaSecundaria: '#4b5563',
  tintaTenue: '#9ca3af',
  superficie: '#ffffff',
  superficieTooltip: '#ffffff',
  borde: 'rgba(17,24,39,0.10)',
};

const OSCURO: Paleta = {
  serie1: '#3987e5',
  serie2: '#d95926',
  rejilla: '#374151',
  eje: '#4b5563',
  tintaPrimaria: '#f9fafb',
  tintaSecundaria: '#d1d5db',
  tintaTenue: '#9ca3af',
  superficie: '#1f2937',
  superficieTooltip: '#111827',
  borde: 'rgba(249,250,251,0.12)',
};

function esOscuro(): boolean {
  return typeof document !== 'undefined' && document.documentElement.classList.contains('dark');
}

/** Devuelve la paleta activa y la actualiza cuando el usuario cambia el tema. */
export function usePaleta(): Paleta {
  const [oscuro, setOscuro] = useState(esOscuro);

  useEffect(() => {
    // El toggle de tema conmuta una clase en <html>, no emite ningún evento, así
    // que la única forma de enterarse es observar el atributo.
    const observador = new MutationObserver(() => setOscuro(esOscuro()));
    observador.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });
    return () => observador.disconnect();
  }, []);

  return oscuro ? OSCURO : CLARO;
}
