import datetime
from collections import deque

from enums import FranjaHoraria, EstadoAsignacion
from trabajador import Trabajador
from supervisor import Supervisor
from credencial import Credencial
from area_de_trabajo import AreaDeTrabajo
from trabajo import Trabajo
from sistema_asignacion import SistemaAsignacion
from loader_datos import cargar_datos, guardar_datos

# asignaciones pendientes y aprobadas durante la semana
asignaciones = []
# cola FIFO de asignaciones pendientes: la primera en entrar es la primera en aprobarse
cola_pendientes = deque()


def pedir_fecha(mensaje):
    while True:
        entrada = input(mensaje)
        try:
            return datetime.datetime.strptime(entrada, "%Y-%m-%d").date()
        except ValueError:
            print("Error: Formato inválido. Asegúrate de usar AAAA-MM-DD con una fecha real.\n")

def pedir_franja(mensaje):
    """Pide una franja hasta que sea válida; acepta 'mañana', 'TARDE', etc."""
    while True:
        entrada = input(mensaje).strip().capitalize()
        try:
            return FranjaHoraria(entrada)
        except ValueError:
            print("Error: Franja inválida. Las opciones son Mañana, Tarde o Noche.\n")

def pedir_numero_positivo(mensaje):
    while True:
        try:
            valor = float(input(mensaje))
        except ValueError:
            print("Error: Debe ingresar un número.\n")
            continue
        if valor > 0:
            return valor
        print("Error: El valor debe ser mayor a cero.\n")

def pedir_habilidades(mensaje):
    """Separa por comas, quita espacios sobrantes y descarta entradas vacías."""
    return {h.strip() for h in input(mensaje).split(",") if h.strip()}

def pedir_atributos_opcionales():
    """Pide atributos opcionales del personal como pares clave=valor (idiomas, área
    de origen, turno preferido, certificaciones iniciales, etc.) para pasarlos como
    **kwargs a Trabajador.registrar_personal()."""
    atributos = {}
    entrada = input(
        "Ingrese atributos opcionales como clave=valor separados por comas "
        "(ej: idioma=Ingles,area_origen=Mecanica) o deje vacío: "
    )
    for par in entrada.split(","):
        if "=" in par:
            clave, valor = par.split("=", 1)
            atributos[clave.strip()] = valor.strip()
    return atributos

def buscar_trabajador(id_trabajador):
    """Devuelve el trabajador (o supervisor) con ese ID, o None si no existe."""
    for t in Trabajador.registro.trabajadores:
        if t.id_trabajador == id_trabajador:
            return t
    return None

def buscar_trabajo(id_trabajo):
    """Devuelve el trabajo con ese ID, o None si no existe."""
    for t in Trabajo.registro.trabajos:
        if t.id_trabajo == id_trabajo:
            return t
    return None

def buscar_area(id_area):
    """Devuelve el área con ese ID, o None si no existe."""
    for a in AreaDeTrabajo.registro.areas:
        if a.id_area == id_area:
            return a
    return None

def solicitar_rol():
    while True:
        rol = input("Ingrese el rol que desea utilizar: ")

        if rol in ("1", "2", "3"):
            return rol

        print("Opción inválida. Por favor, seleccione 1, 2 o 3.")

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
    print("8. Reiniciar semana")

    opcion = solicitar_opcion_gestion()

    if opcion == "1":
        id_trabajador = input("Ingrese el ID del trabajador: ").strip()
        nombre = input("Ingrese el nombre del trabajador: ")
        franja_horaria = pedir_franja("Ingrese la franja horaria (Mañana/Tarde/Noche): ")
        habilidades = pedir_habilidades("Ingrese las habilidades separadas por comas: ")
        limite_horas_semanales = pedir_numero_positivo("Ingrese el límite de horas semanales(menor o igual a 40): ")
        atributos_opcionales = pedir_atributos_opcionales()
        try:
            trabajador = Trabajador.registrar_personal(
                id_trabajador,
                nombre,
                franja_horaria,
                habilidades,
                limite_horas_semanales,
                **atributos_opcionales,
            )
        except ValueError as error:
            print(f"Error: {error}\n")
        else:
            guardar_datos(asignaciones=asignaciones)

    elif opcion == "2":
        id_trabajador = input("Ingrese el ID del supervisor: ").strip()
        nombre = input("Ingrese el nombre del supervisor: ")
        franja_horaria = pedir_franja("Ingrese la franja horaria (Mañana/Tarde/Noche): ")
        habilidades = pedir_habilidades("Ingrese las habilidades separadas por comas: ")
        limite_horas_semanales = pedir_numero_positivo("Ingrese el límite de horas semanales(menor o igual a 40): ")
        area_a_cargo = input("Ingrese el ID del área a cargo del supervisor (ej: A1): ").strip()
        try:
            supervisor = Supervisor(
                id_trabajador=id_trabajador,
                nombre=nombre,
                franja_horaria=franja_horaria,
                habilidades=habilidades,
                credenciales=[],
                limite_horas_semanales=limite_horas_semanales,
                area_a_cargo=area_a_cargo
            )
        except ValueError as error:
            print(f"Error: {error}\n")
        else:
            guardar_datos(asignaciones=asignaciones)
    elif opcion == "3":
        nombre_credencial = input("Ingrese el nombre de la credencial: ")
        fecha_obtencion = pedir_fecha("Ingrese la fecha de obtención de la credencial (YYYY-MM-DD): ")
        fecha_vencimiento = pedir_fecha("Ingrese la fecha de vencimiento de la credencial (YYYY-MM-DD): ")


        try:
            credencial = Credencial(nombre_credencial,fecha_obtencion, fecha_vencimiento)
        except ValueError as error:
            print(f"Error: {error}\n")

    elif opcion == "4":
        trabajador = buscar_trabajador(input("Ingrese el ID del trabajador: ").strip())
        if trabajador is None:
            print("Error: No existe un trabajador con ese ID.\n")
        else:
            nombre_credencial = input("Ingrese el nombre de la credencial: ")
            fecha_obtencion = pedir_fecha("Ingrese la fecha de obtención de la credencial (YYYY-MM-DD): ")
            fecha_vencimiento = pedir_fecha("Ingrese la fecha de vencimiento de la credencial (YYYY-MM-DD): ")
            try:
                credencial = Credencial(nombre_credencial, fecha_obtencion, fecha_vencimiento)
            except ValueError as error:
                print(f"Error: {error}\n")
            else:
                trabajador.credenciales.append(credencial)
                guardar_datos(asignaciones=asignaciones)
    elif opcion == "5":
        trabajador = buscar_trabajador(input("Ingrese el ID del trabajador: ").strip())
        if trabajador is None:
            print("Error: No existe un trabajador con ese ID.\n")
        else:
            habilidad = input("Ingrese la habilidad a agregar: ").strip()
            if habilidad:
                trabajador.habilidades.add(habilidad)
                guardar_datos(asignaciones=asignaciones)
            else:
                print("Error: La habilidad no puede estar vacía.\n")
    elif opcion == "6":
        id_area = input("Ingrese el ID del área: ").strip()
        nombre = input("Ingrese el nombre del área: ")
        credenciales_obligatorias = pedir_habilidades("Ingrese las credenciales obligatorias separadas por comas: ")
        limites = {}
        for franja in FranjaHoraria:
            entrada = input(f"Ingrese el límite de personal en la franja {franja.value} (vacío si no se usa): ").strip()
            if entrada:
                limites[franja] = int(entrada) if entrada.isdigit() else 0
        id_padre = input("Ingrese el ID del área que la contiene (vacío si no está dentro de otra): ").strip()
        area_padre = buscar_area(id_padre)
        if id_padre and area_padre is None:
            print("Error: No existe un área con ese ID.\n")
        else:
            try:
                AreaDeTrabajo(id_area, nombre, credenciales_obligatorias, limites, area_padre)
            except ValueError as error:
                print(f"Error: {error}\n")
            else:
                guardar_datos(asignaciones=asignaciones)
    elif opcion == "7":
        id_trabajo = input("Ingrese el ID del trabajo: ").strip()
        titulo = input("Ingrese el título del trabajo: ")
        descripcion = input("Ingrese la descripción del trabajo: ")
        duracion_horas = pedir_numero_positivo("Ingrese la duración en horas: ")
        habilidades = pedir_habilidades("Ingrese las habilidades requeridas separadas por comas: ")
        credenciales = pedir_habilidades("Ingrese las credenciales requeridas separadas por comas: ")
        area = buscar_area(input("Ingrese el ID del área del trabajo (ej: A1): ").strip())
        if area is None:
            print("Error: No existe un área con ese ID.\n")
        else:
            try:
                Trabajo(id_trabajo, titulo, descripcion, duracion_horas, habilidades, credenciales, area)
            except ValueError as error:
                print(f"Error: {error}\n")
            else:
                guardar_datos(asignaciones=asignaciones)
    elif opcion == "8":
        Trabajador.reiniciar_semana_todos()
        for area in AreaDeTrabajo.registro.areas:
            area.reiniciar_semana()
        SistemaAsignacion.reiniciar_semana()
        asignaciones.clear()
        print("Semana reiniciada: se liberaron las horas, franjas y asignaciones de la semana.\n")

def solicitar_opcion_gestion():
    while True:
         opcion = input("Ingrese la opcion que desea elegir: ")
         if opcion in ("1","2","3","4","5","6","7","8"):
             return opcion
         print("Opcion invalida. Por favor seleccione una opcion entre 1 y 8")

def aprobar_siguiente(cola):
    """Pide el supervisor y formaliza la asignación que está al frente de la cola (FIFO)."""
    asignacion = cola[0]  # se mira el frente sin sacarlo, por si la aprobación falla
    aprobador = buscar_trabajador(input("Ingrese su ID de supervisor: ").strip())
    if aprobador is None:
        print("Error: No existe un trabajador con ese ID.\n")
        return
    try:
        asignacion.formalizar(aprobador)
    except (ValueError, PermissionError) as error:
        print(f"Error: {error}\n")
    else:
        cola.popleft()  # recién al aprobarse sale de la cola
        print(f"Asignación {asignacion.id_asignacion} aprobada.\n")

def supervisor():
    print("Ha seleccionado el rol de supervisor.")
    print("1. Asignar trabajo")
    print("2. Mirar asignaciones pendientes")
    print("3. Mirar disponibilidad de trabajadores por franja horaria en cierta fecha")

    opcion = solicitar_opcion()

    if opcion == "1":
        trabajo = buscar_trabajo(input("Ingrese el ID del trabajo: ").strip())
        if trabajo is None:
            print("Error: No existe un trabajo con ese ID.\n")
        else:
            fecha = pedir_fecha("Ingrese la fecha (YYYY-MM-DD): ")
            franja_horaria = pedir_franja("Ingrese la franja horaria (Mañana/Tarde/Noche): ")
            id_trabajador = input("Ingrese el ID del trabajador (vacío para elegirlo automáticamente): ").strip()
            trabajador = buscar_trabajador(id_trabajador)
            if id_trabajador and trabajador is None:
                print("Error: No existe un trabajador con ese ID.\n")
            else:
                asignacion = SistemaAsignacion(len(asignaciones) + 1, trabajo, fecha, franja_horaria)
                try:
                    asignacion.agregar_trabajador(trabajador)
                except ValueError as error:
                    print(f"Error: {error}\n")
                else:
                    asignaciones.append(asignacion)
                    cola_pendientes.append(asignacion)  # entra al final de la cola
                    print(f"Asignación {asignacion.id_asignacion} propuesta para {asignacion.trabajador.nombre} (Pendiente).\n")
    elif opcion == "2":
        if not cola_pendientes:
            print("No hay asignaciones pendientes.\n")
        else:
            # se muestran en orden de llegada; la primera es la próxima a aprobar
            for posicion, a in enumerate(cola_pendientes, start=1):
                print(f"{posicion}. {a.id_asignacion} - {a.trabajo.titulo} | {a.trabajador.nombre} | {a.fecha} {a.franja_horaria.value}")
            siguiente = cola_pendientes[0]
            respuesta = input(f"¿Aprobar la asignación {siguiente.id_asignacion} (primera en la cola)? (s/n): ").strip().lower()
            if respuesta == "s":
                aprobar_siguiente(cola_pendientes)
    elif opcion == "3":
        trabajo = buscar_trabajo(input("Ingrese el ID del trabajo: ").strip())
        if trabajo is None:
            print("Error: No existe un trabajo con ese ID.\n")
        else:
            franja_horaria = pedir_franja("Ingrese la franja horaria (Mañana/Tarde/Noche): ")
            fecha = pedir_fecha("Ingrese la fecha (YYYY-MM-DD): ")
            disponibles = Trabajador.disponibles_en(trabajo, fecha, franja_horaria)
            if not disponibles:
                print("No hay trabajadores disponibles.\n")
            for t in disponibles:
                print(f"{t.id_trabajador} - {t.nombre} ({t.tiempo_libre()} hs libres en la semana)")

def solicitar_opcion():
    while True:
     opcion = input("Ingrese la opcion que desea elegir: ")
     if opcion in ("1","2","3"):
         return opcion
     print("Opcion invalida. Por favor seleccione 1, 2 o 3")

def main():
        cargar_datos()
        activo = True
        while activo:
            print("----------------------MENU SISTEMA DE ASIGNACION DE TRABAJADORES----------------------")
            print("----------------------          QUE ROL DESEA UTILIZAR          ----------------------")
            print("----------------------           1. Rol de Supervisor           ----------------------")
            print("----------------------           2. Rol de Gestion           ----------------------")
            print("----------------------           3. Salir           ----------------------")

            rol = solicitar_rol()

            if rol == "1":
                supervisor()
            elif rol == "2":
                gestion()
            else:
                activo = False

if __name__ == "__main__":
    main()
