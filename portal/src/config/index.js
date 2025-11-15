// Construye la base de la API usando la variable de entorno VITE_API_BASE_URL.
// - En desarrollo (sin env), cae por defecto a '/api' para proxy/local.
const ORIGIN = import.meta.env.VITE_API_BASE_URL || '';
export const API_BASE_URL = `${ORIGIN ? ORIGIN.replace(/\/$/, '') : ''}/api`;



