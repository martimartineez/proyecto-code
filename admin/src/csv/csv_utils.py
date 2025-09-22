import io, csv

def csv_exporter(data):
    output = io.StringIO()
    fieldnames = ["Nombre", "Descripcion", "Ciudad", "Provincia", "Estado", "FechaRegistro", "Coordenadas", "Tags"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return output


#conviene que reciba la data directamente o conviene recibir filtros y orden y realizar consulta a bd y desde ahi descargar? o recibir una lista de objetos
#esto donde deberia estar?
#