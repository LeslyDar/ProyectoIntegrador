============================================
SIMULADOR DE SISTEMA OPERATIVO
============================================

1. NOMBRE DEL PROYECTO
Simulador Interactivo de Sistema Operativo con Planificación y Comunicación

2. BREVE DESCRIPCIÓN DEL PROYECTO
Simulador educativo que permite crear, planificar y gestionar procesos, recursos y comunicación entre procesos, utilizando algoritmos FCFS y Round Robin a través de una interfaz en consola.

3. INFORMACIÓN DEL CURSO
- Materia: Sistemas Operativos
- Institución: Universidad Autonoma de Tamaulipas

4. SEMESTRE
Sexto semestre de 2025

5. PROFESOR(ES)
Muñoz Quintero Dante Alfonso

6. INTEGRANTES DEL EQUIPO
- Aguilar Gómez Lesly Dariana
- Hernández Juárez José Ángel
- Torres Alvidena Manuel De Jesús
- Vega González Victor Itiel
  
--------------------------------------------
FUNCIONALIDADES PRINCIPALES DEL CÓDIGO
--------------------------------------------

● Gestión de Procesos:
  - Crear, suspender, reanudar y finalizar procesos.
  - Visualizar procesos activos con sus estados y recursos asignados.

● Planificación de Procesos:
  - Algoritmos FCFS y Round Robin (con quantum configurable).
  - Simulación cíclica de ejecución de procesos.

● Gestión de Recursos:
  - Asignación/liberación de CPU y memoria.
  - Visualización del estado actual de los recursos del sistema.

● Comunicación y Sincronización:
  - Envío y recepción de mensajes entre procesos.
  - Simulación del problema productor-consumidor usando semáforos.

● Interfaz de Usuario (CLI con 'rich'):
  - Menú interactivo, tablas informativas y visualización del estado del sistema.
  - Acceso a logs, mensajes y opciones de simulación.

● Persistencia y Herramientas:
  - Registro de eventos.
  - Generación automática de procesos (opcional).
  - Detección de interbloqueos (opcional).

--------------------------------------------
REQUISITOS Y EJECUCIÓN
--------------------------------------------
● Requisitos:
  - Python 3.8 o superior
  - Librería 'rich' → Instalar con: `pip install rich`

● Ejecución:
  > python main.py

--------------------------------------------
PROPÓSITO
--------------------------------------------
Este proyecto busca facilitar el aprendizaje práctico de los conceptos de planificación, gestión de recursos y comunicación en sistemas operativos mediante una interfaz clara y simulaciones controladas.

