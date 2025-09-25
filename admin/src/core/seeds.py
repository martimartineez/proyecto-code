from src.core import board


def run():
    sitio1 = board.agregar_sitioseed(
        nombre="Sitio Histórico 1",
        descripcion="Descripción breve del sitio histórico 1",
        descripcion_completa="Descripción completa del sitio histórico 1",
        ciudad="Ciudad A",
        provincia="Provincia A",
        ubicacion="40.7128,-74.0060",
        estado_conservacion="Bueno",
        fecha_inauguracion="1850-01-01",
        categoria="Monumento",
        fecha_registro="2022-01-15",
        visible=True,
    )
    sitio2 = board.agregar_sitioseed(
        nombre="Sitio Histórico 2",
        descripcion="Descripción breve del sitio histórico 2",
        descripcion_completa="Descripción completa del sitio histórico 2",
        ciudad="Ciudad B",
        provincia="Provincia B",
        ubicacion="24.7128,-74.0060",
        estado_conservacion="Regular",
        fecha_inauguracion="1900-01-01",
        categoria="Edificio",
        fecha_registro="2023-03-22",
        visible=True,
    )
    sitio3 = board.agregar_sitioseed(
        nombre="Sitio Histórico 3",
        descripcion="Descripción breve del sitio histórico 3",
        descripcion_completa="Descripción completa del sitio histórico 3",
        ciudad="Ciudad C",
        provincia="Provincia C",
        ubicacion="42.7128,-74.0060",
        estado_conservacion="Malo",
        fecha_inauguracion="1750-01-01",
        categoria="Parque",
        fecha_registro="2021-11-05",
        visible=False,
    )

    print(f"Seeded sitios:\n {sitio1}\n {sitio2}\n {sitio3}")
