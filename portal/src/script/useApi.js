export function useApi() {
    async function callProtectedApi(url, options = {}) {
        try {
            const response = await fetch(url, {
                credentials: "include",
                ...options
            });

            // Solo redirigir si NO está autenticado
            if (response.status === 401 || response.status === 403) {
                localStorage.setItem('redirectAfterLogin', window.location.pathname);
                window.location.href = '/login';
                return null;
            }

            // Si la respuesta es 204 (No Content)
            if (response.status === 204) {
                return { ok: true };
            }

            // Para otros errores, retornar null sin redirigir
            if (!response.ok) {
                return null;
            }

            return await response.json(); // Aquí sí hay JSON

        } catch (error) {
            console.error('API error:', error);
            return null;
        }
    }

    return { callProtectedApi };
}
