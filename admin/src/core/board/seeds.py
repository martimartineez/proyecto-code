from __future__ import annotations
from typing import List

from src.core.database import db
from src.core.board.provincia import Provincia
from src.core.board.ciudad import Ciudad
from src.core.board.categoria_sitio import CategoriaSitio


def seed_geografia() -> None:
    """Seed Provincias y Ciudades si la tabla está vacía."""
    # Evitar duplicados si ya hay datos
    if db.session.query(Provincia).count() > 0:
        return

    # Provincias base
    provincias_data = [
        ("Buenos Aires", ["La Plata", "Mar del Plata", "Bahía Blanca"]),
        ("Córdoba", ["Córdoba", "Villa Carlos Paz", "Río Cuarto"]),
        ("Santa Fe", ["Santa Fe", "Rosario", "Rafaela"]),
        ("Mendoza", ["Mendoza", "San Rafael"]),
        ("Tucumán", ["San Miguel de Tucumán"]),
    ]

    provincias: List[Provincia] = []
    for nombre_prov, ciudades in provincias_data:
        prov = Provincia(nombre=nombre_prov)
        db.session.add(prov)
        provincias.append(prov)
    db.session.flush()  # asigna IDs a provincias

    # Crear ciudades vinculadas
    for prov, (_, ciudades) in zip(provincias, provincias_data):
        for nombre_ciudad in ciudades:
            db.session.add(Ciudad(nombre=nombre_ciudad, idProvincia=prov.id))

    db.session.commit()
    print("Seed de provincias y ciudades completado")


def seed_categorias() -> None:
    """Seed de categorías de sitios si la tabla está vacía."""
    if db.session.query(CategoriaSitio).count() > 0:
        return
    nombres = [
        "Monumento",
        "Museo",
        "Sitio Arqueológico",
        "Edificio Histórico",
        "Plaza",
        "Iglesia",
    ]
    for nombre in nombres:
        db.session.add(CategoriaSitio(nombre=nombre))

    db.session.commit()
    print("Seed de categorías completado")
