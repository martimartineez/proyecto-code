// src/composables/useApi.js
export function useApi() {
    async function callProtectedApi(url, options = {}) {
        try {
            const response = await fetch(url, options);
            console.log('API response status xxxxxxxxxxxxxxxxx:', response);
            if (!response.ok) {
                // Guardar pestaña actual
                localStorage.setItem('redirectAfterLogin', window.location.pathname);

                window.location.href = '/login';
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error('API error:', error);

            // Guardar pestaña actual también en errores de red
            localStorage.setItem('redirectAfterLogin', window.location.pathname);

            window.location.href = '/login';
            return null;
        }
    }

    return { callProtectedApi };
}
