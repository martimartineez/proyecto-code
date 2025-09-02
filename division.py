def dividir(a,b):
    try:
        resultado = a / b
        return resultado
    except ZeroDivisionError:
        print("No se puede dividir por 0")
