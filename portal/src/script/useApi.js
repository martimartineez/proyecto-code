// portal/src/script/useApi.js
export function useApi() {
    const API_URL = import.meta.env.VITE_API_BASE_URL || '';

    async function callProtectedApi(url, options = {}) {
        const opts = { ...options };

        // Por defecto incluimos cookies/sesión
        if (!opts.credentials) opts.credentials = 'include';

        // Construimos URL absoluta si nos pasan una ruta relativa
        const fullUrl = /^https?:\/\//i.test(url)
            ? url
            : `${API_URL}${url.startsWith('/') ? '' : '/'}${url}`;

        try {
            const response = await fetch(fullUrl, opts);

            // Si no está autorizado -> guardamos la ruta y redirigimos al login
            if (response.status === 401 || response.status === 403) {
                localStorage.setItem('redirectAfterLogin', window.location.pathname);
                window.location.href = '/login';
                return null;
            }

            if (!response.ok) {
                console.error('API error status:', response.status);
                return null;
            }

            // Manejo de cuerpo vacío y distintos content-types
            if (response.status === 204) return null;
            const contentType = response.headers.get('content-type') || '';
            if (contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API error:', error);
            localStorage.setItem('redirectAfterLogin', window.location.pathname);
            window.location.href = '/login';
            return null;
        }
    }

    return { callProtectedApi };
}
