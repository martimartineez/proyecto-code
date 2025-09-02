def dividir(a,b):
    try:
        resultado = a / b
        return resultado
    except ZeroDivisionError:
        return "No se puede dividir por 0"
