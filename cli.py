from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import IntPrompt, Prompt
from rich.panel import Panel
from procesos import ProcessManager
from recursos import SystemResources
from planificador import SchedulerFactory
from comunicacion import message_system, producer_consumer

console = Console()


class CLI:
    def __init__(self):
        self.process_manager = ProcessManager()
        self.resources = SystemResources()
        self.scheduler = None
        self.scheduler_algorithm = "fcfs"  # Algoritmo por defecto
        self.quantum = 2  # Quantum por defecto para Round Robin
        self.logs = []  # Lista para almacenar eventos
        self._setup_scheduler()

    def _setup_scheduler(self):
        """Configura el planificador con el algoritmo seleccionado"""
        self.scheduler = SchedulerFactory.create_scheduler(
            self.scheduler_algorithm,
            self.process_manager,
            self.resources,
            self.quantum
        )

    def show_menu(self) -> None:
        """Muestra el menú principal"""
        console.print(f"\n[bold cyan]Simulador de SO[/bold cyan] - [yellow]{self.scheduler.name}[/yellow]",
                      justify="center")
        console.print(
            "1. Crear proceso\n"
            "2. Listar procesos\n"
            "3. Ver recursos\n"
            "4. Cambiar algoritmo\n"
            "5. Ejecutar simulación\n"
            "6. Suspender proceso\n"
            "7. Reanudar proceso\n"
            "8. Terminar proceso\n"
            "9. Ver logs\n"
            "10. Enviar mensaje entre procesos\n"
            "11. Ver mensajes de un proceso\n"
            "12. Simulación Productor-Consumidor\n"
            "0. Salir"
        )

    def create_process_interactive(self) -> None:
        """Crea un nuevo proceso con datos introducidos por el usuario"""
        try:
            priority = IntPrompt.ask("Prioridad (1-5)", default=3)
            memory = IntPrompt.ask("Memoria (MB)", default=256)
            burst_time = IntPrompt.ask("Tiempo de CPU", default=5)

            # Verificar si hay memoria suficiente
            if memory > self.resources.available_memory:
                console.print(
                    f"[red]✗ No hay suficiente memoria disponible. Disponible: {self.resources.available_memory} MB[/red]")
                return

            new_process = self.process_manager.create_process(priority, memory, burst_time)

            # Asignar memoria al proceso
            self.resources.assign_memory(new_process.pid, memory)

            # Crear cola de mensajes para el proceso
            message_system.create_queue(new_process.pid)

            console.print(f"[green]✓ Proceso creado (PID: {new_process.pid})[/green]")
            self.logs.append(
                f"Proceso {new_process.pid} creado con prioridad {priority}, memoria {memory}MB y tiempo {burst_time}")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")

    def list_processes_table(self) -> None:
        """Muestra una tabla con los procesos activos"""
        table = Table(title="Procesos Activos")
        table.add_column("PID")
        table.add_column("Estado")
        table.add_column("Prioridad")
        table.add_column("Memoria (MB)")
        table.add_column("Tiempo restante")
        table.add_column("Mensajes")

        for p in self.process_manager.list_processes():
            # Colorear el estado según su valor
            state_color = {
                "ready": "blue",
                "running": "green",
                "waiting": "yellow",
                "terminated": "red"
            }.get(p.state, "white")

            # Contar mensajes en la cola
            msg_count = message_system.get_queue_size(p.pid)
            msg_display = f"[green]{msg_count}[/green]" if msg_count > 0 else "0"

            table.add_row(
                str(p.pid),
                f"[{state_color}]{p.state}[/{state_color}]",
                str(p.priority),
                str(p.memory),
                str(p.burst_time),
                msg_display
            )

        console.print(table)

        # Mostrar cola de procesos listos
        if self.process_manager.ready_queue:
            ready_pids = [str(p.pid) for p in self.process_manager.ready_queue if p.state == "ready"]
            if ready_pids:
                console.print(f"Cola de listos: {' → '.join(ready_pids)}")

    def show_resources(self) -> None:
        """Muestra el estado de los recursos del sistema"""
        status = self.resources.get_resource_status()
        table = Table(title="Recursos del Sistema")
        table.add_column("Recurso")
        table.add_column("Estado")

        cpu_status = status["CPU"]
        cpu_color = "green" if cpu_status == "Libre" else "red"

        memory_status = status["Memoria"]
        memory_parts = memory_status.split('/')
        memory_used = int(self.resources.total_memory) - int(self.resources.available_memory)
        memory_percentage = (memory_used / int(self.resources.total_memory)) * 100

        memory_color = "green"
        if memory_percentage > 75:
            memory_color = "red"
        elif memory_percentage > 50:
            memory_color = "yellow"

        table.add_row("CPU", f"[{cpu_color}]{cpu_status}[/{cpu_color}]")
        table.add_row("Memoria", f"[{memory_color}]{memory_status}[/{memory_color}]")

        console.print(table)

    def change_algorithm(self) -> None:
        """Cambia el algoritmo de planificación"""
        console.print("[bold]Algoritmos disponibles:[/bold]")
        console.print("1. FCFS (First-Come, First-Served)")
        console.print("2. SJF (Shortest Job First)")
        console.print("3. Prioridad")
        console.print("4. Round Robin")

        option = Prompt.ask("Seleccione un algoritmo", choices=["1", "2", "3", "4"])

        if option == "1":
            self.scheduler_algorithm = "fcfs"
        elif option == "2":
            self.scheduler_algorithm = "sjf"
        elif option == "3":
            self.scheduler_algorithm = "priority"
        elif option == "4":
            self.scheduler_algorithm = "round_robin"
            self.quantum = IntPrompt.ask("Valor del quantum", default=2)

        self._setup_scheduler()
        console.print(f"[green]✓ Algoritmo cambiado a: {self.scheduler.name}[/green]")
        self.logs.append(f"Algoritmo cambiado a {self.scheduler.name}")

    def run_simulation(self) -> None:
        """Ejecuta la simulación por un número específico de ciclos"""
        cycles = IntPrompt.ask("Número de ciclos a ejecutar", default=5)

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Ejecutando {cycles} ciclos...", total=cycles)

            for i in range(cycles):
                result = self.scheduler.execute_cycle()
                self._handle_simulation_event(result)
                progress.update(task, advance=1)

        console.print(f"[green]✓ Simulación completada: {cycles} ciclos ejecutados[/green]")
        self.list_processes_table()
        self.show_resources()

    def _handle_simulation_event(self, event_info: dict) -> None:
        """Maneja los eventos generados durante la simulación"""
        event_type = event_info.get("event")

        if event_type == "process_started":
            process = event_info.get("process")
            self.logs.append(f"Ciclo {self.scheduler.time}: Proceso {process.pid} inició ejecución")

        elif event_type == "process_completed":
            process = event_info.get("process")
            self.logs.append(f"Ciclo {self.scheduler.time}: Proceso {process.pid} completado")

        elif event_type == "process_preempted":
            process = event_info.get("process")
            self.logs.append(f"Ciclo {self.scheduler.time}: Proceso {process.pid} interrumpido por quantum")

        elif event_type == "idle":
            self.logs.append(f"Ciclo {self.scheduler.time}: CPU inactiva")

    def suspend_process(self) -> None:
        """Suspende un proceso en ejecución"""
        pid = IntPrompt.ask("PID del proceso a suspender")

        process = next((p for p in self.process_manager.processes if p.pid == pid), None)
        if not process:
            console.print(f"[red]✗ No se encontró proceso con PID {pid}[/red]")
            return

        if process.state not in ["running", "ready"]:
            console.print(
                f"[red]✗ El proceso {pid} no está en ejecución o listo (estado actual: {process.state})[/red]")
            return

        # Si el proceso está ejecutándose, liberar la CPU
        if process.state == "running":
            self.resources.cpu_available = True

        process.state = "waiting"
        console.print(f"[yellow]⏸ Proceso {pid} suspendido[/yellow]")
        self.logs.append(f"Proceso {pid} suspendido")

    def resume_process(self) -> None:
        """Reanuda un proceso suspendido"""
        pid = IntPrompt.ask("PID del proceso a reanudar")

        process = next((p for p in self.process_manager.processes if p.pid == pid), None)
        if not process:
            console.print(f"[red]✗ No se encontró proceso con PID {pid}[/red]")
            return

        if process.state != "waiting":
            console.print(f"[red]✗ El proceso {pid} no está suspendido (estado actual: {process.state})[/red]")
            return

        process.state = "ready"
        console.print(f"[green]▶ Proceso {pid} reanudado[/green]")
        self.logs.append(f"Proceso {pid} reanudado")

    def terminate_process(self) -> None:
        """Termina un proceso forzadamente"""
        pid = IntPrompt.ask("PID del proceso a terminar")

        process = next((p for p in self.process_manager.processes if p.pid == pid), None)
        if not process:
            console.print(f"[red]✗ No se encontró proceso con PID {pid}[/red]")
            return

        if process.state == "terminated":
            console.print(f"[red]✗ El proceso {pid} ya está terminado[/red]")
            return

        # Si el proceso está ejecutándose, liberar la CPU
        if process.state == "running":
            self.resources.cpu_available = True

        # Liberar memoria
        self.resources.release_memory(process.pid, process.memory)

        process.state = "terminated"
        console.print(f"[red]⏹ Proceso {pid} terminado forzadamente[/red]")
        self.logs.append(f"Proceso {pid} terminado forzadamente")

    def show_logs(self) -> None:
        """Muestra los logs del sistema"""
        if not self.logs:
            console.print("[yellow]No hay eventos registrados[/yellow]")
            return

        console.print("[bold]Últimos eventos:[/bold]")
        for i, log in enumerate(self.logs[-10:]):
            console.print(f"{len(self.logs) - 10 + i + 1}. {log}")

    def send_message(self) -> None:
        """Envía un mensaje de un proceso a otro"""
        # Mostrar procesos activos
        active_processes = [p for p in self.process_manager.processes
                            if p.state != "terminated"]

        if len(active_processes) < 2:
            console.print("[red]✗ Se necesitan al menos dos procesos activos para enviar mensajes[/red]")
            return

        # Listar procesos para seleccionar
        console.print("[bold]Procesos disponibles:[/bold]")
        for p in active_processes:
            console.print(f"PID: {p.pid} - Estado: {p.state}")

        # Seleccionar proceso emisor
        sender_pid = IntPrompt.ask("PID del proceso emisor")
        sender = next((p for p in active_processes if p.pid == sender_pid), None)
        if not sender:
            console.print(f"[red]✗ No se encontró proceso con PID {sender_pid}[/red]")
            return

        # Seleccionar proceso receptor
        receiver_pid = IntPrompt.ask("PID del proceso receptor")
        receiver = next((p for p in active_processes if p.pid == receiver_pid), None)
        if not receiver:
            console.print(f"[red]✗ No se encontró proceso con PID {receiver_pid}[/red]")
            return

        # Introducir mensaje
        message = Prompt.ask("Mensaje")

        # Enviar mensaje
        result = message_system.send_message(sender_pid, receiver_pid, message)
        if result:
            console.print(f"[green]✓ Mensaje enviado de proceso {sender_pid} a proceso {receiver_pid}[/green]")
            self.logs.append(f"Mensaje enviado: {sender_pid} → {receiver_pid}")
        else:
            console.print(f"[red]✗ Error al enviar mensaje[/red]")

    def view_messages(self) -> None:
        """Muestra los mensajes de un proceso"""
        pid = IntPrompt.ask("PID del proceso")

        process = next((p for p in self.process_manager.processes if p.pid == pid), None)
        if not process:
            console.print(f"[red]✗ No se encontró proceso con PID {pid}[/red]")
            return

        # Verificar si hay mensajes
        queue_size = message_system.get_queue_size(pid)
        if queue_size == 0:
            console.print(f"[yellow]El proceso {pid} no tiene mensajes[/yellow]")
            return

        # Mostrar mensajes
        console.print(f"[bold]Mensajes del proceso {pid}:[/bold]")

        table = Table(title=f"Cola de mensajes: Proceso {pid}")
        table.add_column("De")
        table.add_column("Mensaje")

        # Recibir y mostrar todos los mensajes
        for _ in range(queue_size):
            message = message_system.receive_message(pid)
            if message:
                table.add_row(
                    str(message["sender"]),
                    message["content"]
                )

        console.print(table)

    def run_producer_consumer(self) -> None:
        """Ejecuta la simulación del problema productor-consumidor"""
        console.print("[bold]Simulación del problema Productor-Consumidor[/bold]")

        # Mostrar menú de opciones
        console.print("1. Producir un item")
        console.print("2. Consumir un item")
        console.print("3. Ver estado del buffer")
        console.print("4. Ver logs de la simulación")
        console.print("5. Volver al menú principal")

        option = Prompt.ask("Seleccione una opción", choices=["1", "2", "3", "4", "5"])

        if option == "1":
            item = Prompt.ask("Item a producir")
            result = producer_consumer.produce(item)
            if result:
                console.print(f"[green]✓ Item '{item}' producido correctamente[/green]")
            else:
                console.print("[yellow]No se pudo producir el item (buffer lleno o productor bloqueado)[/yellow]")

        elif option == "2":
            item = producer_consumer.consume()
            if item:
                console.print(f"[green]✓ Item '{item}' consumido correctamente[/green]")
            else:
                console.print("[yellow]No se pudo consumir ningún item (buffer vacío o consumidor bloqueado)[/yellow]")

        elif option == "3":
            status = producer_consumer.get_buffer_status()

            # Crear representación visual del buffer
            buffer_visual = "["
            for i in range(status["buffer_size"]):
                if i < len(status["buffer_content"]):
                    buffer_visual += f" [green]{status['buffer_content'][i]}[/green] "
                else:
                    buffer_visual += " □ "
            buffer_visual += "]"

            console.print(Panel(
                f"Tamaño del buffer: {status['buffer_size']}\n"
                f"Items en buffer: {status['items_in_buffer']}\n"
                f"Espacios vacíos: {status['empty_slots']}\n"
                f"Espacios llenos: {status['full_slots']}\n\n"
                f"Buffer: {buffer_visual}",
                title="Estado del Buffer",
                expand=False
            ))

        elif option == "4":
            logs = producer_consumer.get_logs()
            if not logs:
                console.print("[yellow]No hay eventos registrados en la simulación[/yellow]")
            else:
                console.print("[bold]Eventos de la simulación Productor-Consumidor:[/bold]")
                for i, log in enumerate(logs[-10:]):
                    console.print(f"{i + 1}. {log}")

        # Si la opción es 5, simplemente volvemos al menú principal