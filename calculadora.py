import resta
def calcular(operacion, num_uno, num_dos):
    if(operacion == "+"):
        return suma.sumar(num_uno,num_dos)
    elif(operacion == "-"):
        return resta.restar(num_uno,num_dos)
    elif(operacion == "*"):
        return multiplicacion.multiplicar(num_uno,num_dos)
    elif(operacion == "/"):
        return division.dividir(num_uno,num_dos)
    else:
        return "ingrese una opcion valida (+, -, *, /): "

num_uno = float(input("ingrese el primer numero: "))
num_dos = float(input("ingrese el segundo numero: "))
operacion = str(input("ingrese la opreaciion a realizar (+, -, *, /): "))

print(calcular(operacion,num_uno,num_dos))