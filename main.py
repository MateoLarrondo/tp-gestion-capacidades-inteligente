import clases as c
import json
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
    print("3. Credencial")
    print("4. Credencial a un trabajador")
    print("5. Habilidad a un trabajador")
    print("6. Area de trabajo")
    print("7. Trabajo pendiente ")

    opcion = solicitar_opcion_gestion()

    if opcion == "1":
        id_trabajador = input("Ingrese el ID del trabajador: ")
        nombre = input("Ingrese el nombre del trabajador: ")
        franja_horaria = input("Ingrese la franja horaria (Mañana/Tarde/Noche): ")
        habilidades = input("Ingrese las habilidades separadas por comas: ").split(",")
        limite_horas_semanales = float(input("Ingrese el límite de horas semanales(menor o igual a 40): "))
        trabajador = c.trabajador(
            id_trabajador=id_trabajador,
            nombre=nombre,
            franja_horaria=c.FranjaHoraria(franja_horaria),
            habilidades=habilidades,
            credenciales=[],
            limite_horas_semanales=limite_horas_semanales
        )
        ###########deberia guardar el trabajador en un archivo json
        ### with open("trabajadores.json", "w") as f:
        ###    json.dump(trabajador.__dict__, f)
        
    elif opcion == "2":
        id_trabajador = input("Ingrese el ID del supervisor: ")
        nombre = input("Ingrese el nombre del supervisor: ")
        franja_horaria = input("Ingrese la franja horaria (Mañana/Tarde/Noche): ")
        habilidades = input("Ingrese las habilidades separadas por comas: ").split(",")
        limite_horas_semanales = float(input("Ingrese el límite de horas semanales(menor o igual a 40): "))
        area_a_cargo = input("Ingrese el área a cargo del supervisor: ")
        supervisor = c.Supervisor(
            id_trabajador=id_trabajador,
            nombre=nombre,
            franja_horaria=c.FranjaHoraria(franja_horaria),
            habilidades=habilidades,
            credenciales=[],
            limite_horas_semanales=limite_horas_semanales,
            area_a_cargo=area_a_cargo
        )
        ###########deberia guardar el supervisor en un archivo json
        ### with open("supervisores.json", "w") as f:
        ###    json.dump(supervisor.__dict__, f)
    elif opcion == "3":
        nombre_credencial = input("Ingrese el nombre de la credencial: ")
        fecha_obtencion = input("Ingrese la fecha de obtención de la credencial (YYYY-MM-DD): ")
        fecha_vencimiento = input("Ingrese la fecha de vencimiento de la credencial (YYYY-MM-DD): ")
        credencial = c.Credencial(nombre_credencial,fecha_obtencion, fecha_vencimiento)

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
    print("2. Mirar asignaciones pendientes") 
    print("3. Mirar disponibilidad de trabajadores por franja horaria en cierta fecha")

    opcion = solicitar_opcion()

    if opcion == "1":
        "s" 
    elif opcion == "2":
        "s"
    elif opcion == "3":
        franja_horaria = input("Ingrese la franja horaria (Mañana/Tarde/Noche): ")
        fecha = input("Ingrese la fecha (YYYY-MM-DD): ")
        """definir si hacemos el json o como"""
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





