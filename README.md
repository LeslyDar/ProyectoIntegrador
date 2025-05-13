============================================
SIMULADOR DE SISTEMA OPERATIVO - RESUMEN
============================================

Este proyecto implementa un simulador de sistema operativo orientado al aprendizaje de:
- Planificación de procesos (FCFS y Round Robin)
- Gestión de recursos (CPU y memoria)
- Comunicación y sincronización entre procesos
- Manejo de eventos y trazabilidad mediante logs
Todo esto se controla desde una interfaz interactiva en consola (CLI) usando la librería 'rich'.

------------------------
FUNCIONALIDAD PRINCIPAL
------------------------

1. Procesos
- Crear, suspender, reanudar y terminar procesos (con prioridad, memoria y tiempo de CPU).
- Listado de procesos en tabla con estado, prioridad y recursos asignados.

2. Recursos
- Asignación y liberación de CPU/memoria.
- Visualización de recursos disponibles.

3. Planificación
- Soporte para FCFS y Round Robin (con quantum configurable).
- Simulación por ciclos con control de ejecución.

4. Comunicación
- Envío y recepción de mensajes entre procesos.
- Simulación de productor-consumidor con semáforos.

5. Logs y Estado
- Registro de eventos clave (creación, terminación, errores).
- Vista general del estado del sistema: colas, CPU, memoria y algoritmo activo.

------------------------
ESTRUCTURA DE MÓDULOS
------------------------

- procesos.py: Manejo de procesos y su ciclo de vida.
- recursos.py: Control de CPU y memoria del sistema.
- planificador.py: Implementación de FCFS y Round Robin.
- comunicacion.py: Mensajería entre procesos y sincronización.
- logs.py: Registro y visualización de eventos.
- cli.py: Interfaz de usuario con menú y visualización.
- main.py: Coordinación general y bucle principal de simulación.

------------------------
EJECUCIÓN Y REQUISITOS
------------------------

- Requiere Python 3.8+ y la librería 'rich'.
Instalación:
> pip install rich

Ejecución:
> python main.py

------------------------
PROPÓSITO EDUCATIVO
------------------------

Este simulador fue diseñado para comprender cómo funciona un sistema operativo a nivel lógico, permitiendo experimentar con planificación, recursos, mensajes y sincronización en un entorno controlado y visual.

