from src.core import board

def run():
    sitio1 = board.agregar_sitio(
        nombre= "Sitio Histórico 1",
        descripcion= "Descripción breve del sitio histórico 1",
        descripcion_completa= "Descripción completa del sitio histórico 1",
        ciudad= "Ciudad A",
        provincia="Provincia A",
        latitud= 40.7128, 
        longitud= -74.0060,
        estado_conservacion= "Bueno",
        anio_fundacion= 1850,
        categoria= "Monumento",
        fecha_registro= "2022-01-15",
        visible= True,
    )
    sitio2 = board.agregar_sitio(
        nombre= "Sitio Histórico 2",
        descripcion= "Descripción breve del sitio histórico 2",
        descripcion_completa= "Descripción completa del sitio histórico 2",
        ciudad= "Ciudad B",
        provincia="Provincia B",
        latitud= 34.0522,
        longitud= -118.2437,
        estado_conservacion= "Regular",
        anio_fundacion= 1900,
        categoria= "Edificio",
        fecha_registro= "2023-03-22",
        visible= True,
    )
    sitio3 = board.agregar_sitio(
        nombre= "Sitio Histórico 3",
        descripcion= "Descripción breve del sitio histórico 3",
        descripcion_completa= "Descripción completa del sitio histórico 3",
        ciudad= "Ciudad C",
        provincia="Provincia C",
        latitud= 51.5074,
        longitud= -0.1278,
        estado_conservacion= "Malo",
        anio_fundacion= 1750,
        categoria= "Parque",
        fecha_registro= "2021-11-05",
        visible= False,
    )
    
    print(f'Seeded sitios:\n {sitio1}\n {sitio2}\n {sitio3}')