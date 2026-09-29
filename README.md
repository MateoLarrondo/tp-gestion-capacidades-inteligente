# Trabajo Práctico: Sistema de Gestión de Capacidades y Asignación Inteligente

## Situación Hipotética

Imaginemos que son parte del equipo de desarrollo de software en *Innovación Industrial Tech (IIT)*, una empresa líder en la gestión de infraestructuras críticas y plantas de producción de alta tecnología. IIT opera en diversos sectores, desde la manufactura avanzada hasta el mantenimiento de complejos centros de datos y sistemas energéticos. La eficiencia operativa, la seguridad del personal y el cumplimiento normativo son pilares fundamentales de su negocio.

Actualmente, IIT enfrenta un desafío significativo: la asignación manual de su personal técnico, a las distintas labores diarias. Este proceso es ineficiente, propenso a errores y no optimiza el uso de los recursos humanos. El personal debe ser asignado a diferentes áreas de trabajo (por ejemplo, "Planta de Ensamble Robótico", "Sala de Servidores Críticos", "Mantenimiento de Líneas de Alta Tensión"), cada una con sus propias complejidades y requisitos.

Cada miembro del personal posee un conjunto único de habilidades técnicas y credenciales profesionales específicas (como "Seguridad Eléctrica Nivel 3", "Manejo de Sustancias Peligrosas", "Certificación Cisco CCNA", "Trabajo en Altura"). Estas credenciales profesionales tienen una fecha de inicio y una fecha de expiración, y es fundamental que estén activas al momento de considerar a alguien para una asignación.

Las labores a realizar son diversas: desde mantenimiento preventivo, reparaciones urgentes, instalaciones de nuevos equipos, hasta supervisiones de seguridad. Cada labor tiene una duración prevista, y demanda un conjunto específico de competencias y credenciales para su ejecución segura y correcta. Además, ciertas labores solo pueden realizarse en un área de trabajo específica.

La jornada operativa se organiza en franjas horarias (Mañana, Tarde, Noche), y cada área de trabajo tiene un límite de personal por franja para asegurar la seguridad y el espacio adecuado. La empresa busca asegurar que ningún trabajador exceda el máximo de horas laborales semanales establecido por su contrato y que siempre se respeten las regulaciones laborales.

Los *Supervisores* de cada área de trabajo son responsables de validar las asignaciones finales, asegurándose de que el personal cumpla con todos los requisitos y de que las tareas se distribuyan equitativamente, o según prioridades específicas. Necesitan una herramienta que les permita visualizar rápidamente quién está disponible, quién es apto para una labor y qué labores aún no tienen asignación.

El sistema actual es ineficiente y no permite, por ejemplo, identificar rápidamente a un profesional con las credenciales activas para una labor urgente en un área específica, o determinar si un trabajador ya ha alcanzado su límite de horas semanales. Se requiere un sistema robusto que permita gestionar estas asignaciones de forma inteligente y segura.

Su misión es diseñar y desarrollar un prototipo de este *Sistema de Gestión de Capacidades y Asignación*, que permita automatizar y validar la asignación de personal a las diversas labores, considerando sus competencias, las credenciales activas, la disponibilidad de las áreas de trabajo y sus franjas horarias, y la carga laboral semanal de cada individuo. El diseño debe ser modular y permitir la futura incorporación de funcionalidades, como la priorización de tareas o la gestión de vacaciones.

## Requerimientos Técnicos Obligatorios

## Reglas de Negocio

1.  **Registro y Carga Laboral del Personal:** Cada miembro del personal se identifica de forma única y posee un nombre, un repertorio de habilidades y un conjunto de credenciales profesionales. Asimismo, se le establece un límite máximo de horas de trabajo por semana que no debe ser superado. Al inicio de su registro, no tendrá horas laborales asignadas.
2.  **Vigencia de Credenciales Profesionales:** Cada credencial profesional tiene un nombre, una fecha en que fue obtenida y otra en que caduca. Es fundamental poder determinar si una credencial está activa o vencida en un momento dado.
3.  **Descripción de Labores:** Cada labor se describe con un identificador único, un título, una explicación detallada y una duración estimada en horas. Para su ejecución, requiere un perfil específico de habilidades y un conjunto de credenciales profesionales. Además, cada labor se adscribe a un área de trabajo concreta.
4.  **Aptitud para la Labor:** Un trabajador solo puede ser considerado para una labor si posee *todas* las competencias exigidas por dicha labor y *todas* las credenciales profesionales requeridas que estén activas en la fecha de la asignación. De no cumplirse estos requisitos, el sistema debe indicar claramente la inaptitud del trabajador.
5.  **Respeto por la Carga Horaria Máxima:** Al asignar una labor a un trabajador, el sistema debe asegurar que la duración prevista de la labor no supere el límite máximo de horas semanales del trabajador, tomando en cuenta las horas ya comprometidas para esa semana. Si este límite se sobrepasa, el sistema debe notificar que la carga laboral es excesiva.
6.  **Límite de Personal por Franja Horaria y Área:** Cada franja horaria en un área de trabajo específica tiene un número máximo de personal permitido. No es posible asignar a un trabajador a una franja horaria si al hacerlo se excede la capacidad designada para esa combinación de franja y área. En tal situación, el sistema debe señalar que la franja horaria está completa.
7.  **Exclusividad de Asignación:** Una labor particular solo puede ser confiada a *un único* trabajador para una franja horaria y fecha específica. Si se intenta volver a asignar una labor que ya ha sido comprometida para ese momento, el sistema debe advertir que la labor ya tiene una asignación.
8.  **Facultades de Supervisión:** Los *Supervisores*, además de poder realizar labores como cualquier otro trabajador, poseen la facultad de formalizar una asignación, transformando su estatus de 'Pendiente' a 'Aprobada'.
9.  **Contabilidad de Horas Asignadas:** Cuando una labor es exitosamente propuesta a un trabajador (previo a la formalización por parte de un supervisor), las horas previstas de esa labor deben sumarse a la carga laboral actual del trabajador para la semana.
10. **Credenciales Obligatorias por Área:** Cada área de trabajo puede requerir un conjunto específico de credenciales profesionales que son obligatorias para cualquier trabajador que realice alguna labor en dicho espacio. Un trabajador solo podrá ser asignado a una labor en esa área si posee todas estas credenciales activas. En caso contrario, el sistema debe señalar que el trabajador no es apto para esa área.
11. **Localización de Personal Disponible:** El sistema debe ser capaz de identificar, para una labor, franja horaria y fecha determinadas, qué trabajadores están disponibles. Esto implica que los trabajadores encontrados deben poseer las habilidades y credenciales activas (tanto las de la labor como las obligatorias del área), que la labor no los lleve a exceder su límite de horas semanales, y que la franja horaria en el área de trabajo aún tenga capacidad.
12. **Inicio de Nueva Semana:** Al comienzo de cada nueva semana, la contabilidad de horas laborales asignadas a cada trabajador debe ser reestablecida a cero, reflejando el inicio de un nuevo ciclo.

## Notas
- Se prohíbe el uso de la librería pandas; el objetivo es evaluar el manejo de estructuras nativas (listas, diccionarios) y la lógica de algoritmos manuales.
- Es requisito obligatorio presentar un diagrama de flujo previo a la codificación para organizar la arquitectura lógica y prevenir fallos de diseño.
- Cada implementación debe estar debidamente sustentada; el alumno debe ser capaz de explicar y justificar técnicamente las decisiones tomadas en el código.
- Se recomienda el uso de la librería estándar de Python (como datetime o math) para optimizar tareas específicas y evitar la redacción innecesaria de funciones ya existentes.

## Estructura del repositorio

```
*.py     código del sistema (clases del modelo y main.py) y tests (test_*.py), en la raíz
data/    datos del sistema (JSON)
docs/    diagramas y modelado de la primera entrega
```

## Cómo ejecutar

Desde la raíz del repo:

- Programa: `python main.py`
- Tests: `python -m pytest` o `python -m unittest`
