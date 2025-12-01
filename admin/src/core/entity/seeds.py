from __future__ import annotations
from typing import List

import requests

from src.core.database import db
from src.core.entity.provincia import Provincia
from src.core.entity.ciudad import Ciudad
from src.core.entity.categoria_sitio import CategoriaSitio


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


def seed_geografia_completa() -> None:
    """
    Carga TODAS las provincias y localidades de Argentina usando la API GeoRef.
    - Inserta provincias que falten (sin borrar existentes).
    - Inserta ciudades (localidades) que falten por provincia.
    Idempotente: puede correrse múltiples veces sin duplicar.
    """
    BASE = "https://apis.datos.gob.ar/georef/api"

    # 1) Provincias
    try:
        resp = requests.get(
            f"{BASE}/provincias",
            params={"campos": "id,nombre", "orden": "nombre", "max": 1000},
            timeout=30,
        )
        resp.raise_for_status()
    except Exception as exc:
        print(f"[seed_geografia_completa] Error obteniendo provincias: {exc}")
        return

    provincias_api = resp.json().get("provincias", [])

    # Mapa nombre provincia -> objeto Provincia (DB)
    provincias_db: dict[str, Provincia] = {}

    # Pre-cargar existentes
    for p in db.session.query(Provincia).all():
        provincias_db[p.nombre] = p

    # Crear faltantes
    for p in provincias_api:
        nombre = p.get("nombre")
        if not nombre:
            continue
        if nombre not in provincias_db:
            obj = Provincia(nombre=nombre)
            db.session.add(obj)
            db.session.flush()  # asigna id
            provincias_db[nombre] = obj

    db.session.commit()

    # 2) Localidades por provincia
    # Pre-cargar ciudades existentes en un set por provincia para evitar consultas repetidas
    ciudades_existentes: dict[int, set[str]] = {}
    for c in db.session.query(Ciudad).all():
        ciudades_existentes.setdefault(c.idProvincia, set()).add(c.nombre)

    creadas = 0
    for nombre_prov, prov_obj in provincias_db.items():
        try:
            r = requests.get(
                f"{BASE}/localidades",
                params={
                    "provincia": nombre_prov,
                    "campos": "id,nombre",
                    "max": 5000,  # debería cubrir todas por provincia
                    "orden": "nombre",
                },
                timeout=60,
            )
            r.raise_for_status()
        except Exception as exc:
            print(
                f"[seed_geografia_completa] Error obteniendo localidades de {nombre_prov}: {exc}"
            )
            continue

        localidades = r.json().get("localidades", [])
        existentes = ciudades_existentes.setdefault(prov_obj.id, set())
        for loc in localidades:
            nombre_loc = loc.get("nombre")
            if not nombre_loc:
                continue
            # Evitar duplicado por (nombre, provincia)
            if nombre_loc in existentes:
                continue
            db.session.add(Ciudad(nombre=nombre_loc, idProvincia=prov_obj.id))
            existentes.add(nombre_loc)
            creadas += 1

        # Commit periódico para no acumular demasiadas en memoria
        db.session.commit()

    print(
        "Seed completo GeoRef: provincias=",
        len(provincias_db),
        ", nuevas ciudades=",
        creadas,
    )


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
