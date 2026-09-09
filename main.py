import clases as c

def solicitar_rol():
    while True:
        rol = input("Ingrese el rol que desea utilizar: ")

        if rol in ("1", "2"):
            return rol

        print("Opción inválida. Por favor, seleccione 1 o 2.")

def gestion():
    print("Ha seleccionado el rol de Gestion")
    print("Agregar al sistema:")
    print("1. Trabajador")
    print("2. Supervisor")
    print("3. Credencial a un trabajador")
    print("4. Habilidad a un trabajador")
    print("5. Area de trabajo")
    print("6. Trabajo pendiente ")

    opcion = solicitar_opcion_gestion()

    if opcion == "1":
        "s"
    elif opcion == "2":
        "s"
    elif opcion == "3":
        "s"
    elif opcion == "4":
            "s"
    elif opcion == "5":
            "s"
    elif opcion == "6":
            "s"

def solicitar_opcion_gestion():
    while True:
         opcion = input("Ingrese la opcion que desea elegir: ")
         if opcion in ("1","2","3","4","5","6"):
             return opcion
         print("Opcion invalida. Por favor seleccione 1, 2 o 3")

def supervisor():
    print("Ha seleccionado el rol de supervisor.")
    print("1. Asignar trabajo")
    print("2. Mirar trabajos pendientes sin asignar") 
    print("3. Mirar disponibilidad por franja horaria")

    opcion = solicitar_opcion()

    if opcion == "1":
        "s" 
        
    elif opcion == "2":
        "s"
    elif opcion == "3":
        "s"

def solicitar_opcion():
    while True:
     opcion = input("Ingrese la opcion que desea elegir: ")
     if opcion in ("1","2","3"):
         return opcion
     print("Opcion invalida. Por favor seleccione 1, 2 o 3")


def main():
    print("----------------------MENU SISTEMA DE ASIGNACION DE TRABAJADORES----------------------")
    print("----------------------          QUE ROL DESEA UTILIZAR          ----------------------")
    print("----------------------           1. Rol de Supervisor           ----------------------")
    print("----------------------           2. Rol de Gestion           ----------------------")

    rol = solicitar_rol()

    if rol == "1":
        supervisor()
    elif rol == "2":
        gestion()

main()





