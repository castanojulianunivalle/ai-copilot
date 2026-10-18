// URL de la API. En Render la fija VITE_API_URL al construir; en local cae al puerto de siempre.
export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8001').replace(/\/$/, '');
