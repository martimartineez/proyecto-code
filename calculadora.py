#import 
def calcular(operacion, num_uno, num_dos):
    if(operacion == "+"):
        return sumar(num_uno,num_dos)
    elif(operacion == "-"):
        return restar(num_uno,num_dos)
    elif(operacion == "*"):
        return multiplicar(num_uno,num_dos)
    elif(operacion == "/"):
        return dividir(num_uno,num_dos)
    else:
        return "ingrese una opcion valida (+, -, *, /): "

num_uno = float(input("ingrese el primer numero: "))
num_dos = float(input("ingrese el segundo numero: "))
operacion = input("ingrese la opreaciion a realizar (+, -, *, /): ")

print(calculadora.calcular(operacion,num_uno,num_dos))