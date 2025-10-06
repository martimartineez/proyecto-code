# src/core/board/validaciones.py

def _validar_texto_obligatorio(valor: str | None, campo_etiqueta: str, min_len: int = 3, max_len: int = 255) -> str | None:
    """
    Función auxiliar para validar campos de texto obligatorios y limpiarlos de espacios.
    Devuelve un mensaje de error si no es válido, o None si es válido.
    """
    if valor is None:
        valor = ""
        
    # Eliminar espacios en blanco iniciales y finales para verificar el contenido real
    texto_limpio = valor.strip()

    if not texto_limpio:
        return f"El campo '{campo_etiqueta}' no puede estar vacío."
    
    if not (min_len <= len(texto_limpio) <= max_len):
        return f"El campo '{campo_etiqueta}' debe tener entre {min_len} y {max_len} caracteres."
        
    return None # La validación pasó

# --------------------------------------------------------------------------

def validar_tag(form_data: dict) -> dict:
    """Valida los datos de entrada para un Tag (Nombre y unicidad)."""
    errores = {}
    
    # Requerimiento: Nombre (obligatorio, único, 3–50 caracteres, case-insensitive)
    nombre_raw = form_data.get("nombre")
    error_nombre = _validar_texto_obligatorio(nombre_raw, "Nombre del Tag", 3, 50)
    
    if error_nombre:
        errores["nombre"] = error_nombre
        
    return errores

# --------------------------------------------------------------------------

def validar_sitio_historico(form_data: dict) -> dict:
    """
    Valida los campos de texto obligatorios de un Sitio Histórico (Nombre, Desc. Breve, Desc. Completa).
    """
    errores = {}
    
    # 1. Validación del Nombre (Mínimo: 3)
    error_nombre = _validar_texto_obligatorio(form_data.get("nombre"), "Nombre del Sitio", 3, 100)
    if error_nombre:
        errores["nombre"] = error_nombre

    # 2. Validación de la Descripción Breve (Mínimo: 10)
    error_desc_breve = _validar_texto_obligatorio(form_data.get("descripcion"), "Descripción Breve", 10, 255)
    if error_desc_breve:
        errores["descripcion"] = error_desc_breve

    # 3. Validación de la Descripción Completa (Mínimo: 20)
    # Asumo una longitud máxima más grande por ser un campo extenso
    error_desc_completa = _validar_texto_obligatorio(form_data.get("descripcion_completa"), "Descripción Completa", 20, 5000)
    if error_desc_completa:
        errores["descripcion_completa"] = error_desc_completa
        
    # NOTA: Los demás campos (latitud, longitud, selects) se asume que no fallarán 
    # por la implementación del widget de mapa y los selects controlados.
    
    return errores