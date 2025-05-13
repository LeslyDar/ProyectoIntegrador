import time
from procesos import Process, ProcessManager
from recursos import SystemResources


class Scheduler:
    """Clase base para los algoritmos de planificación"""

    def __init__(self, process_manager: ProcessManager, resources: SystemResources):
        self.process_manager = process_manager
        self.resources = resources
        self.current_process = None
        self.name = "Base Scheduler"
        self.time = 0  # Contador de tiempo global

    def select_next_process(self) -> Process:
        """Selecciona el siguiente proceso a ejecutar (método a implementar en subclases)"""
        raise NotImplementedError("Este método debe ser implementado por las subclases")

    def execute_cycle(self) -> dict:
        """Ejecuta un ciclo de CPU y actualiza el estado de los procesos"""
        self.time += 1

        # Si no hay proceso en ejecución, selecciona uno nuevo
        if self.current_process is None or self.current_process.state != "running":
            next_process = self.select_next_process()
            if next_process:
                # Asigna CPU al proceso
                if self.resources.cpu_available:
                    self.resources.cpu_available = False
                    next_process.state = "running"
                    self.current_process = next_process
                    return {"event": "process_started", "process": next_process}
            return {"event": "idle"}

        # Si hay un proceso en ejecución, reduce su tiempo de CPU
        if self.current_process and self.current_process.state == "running":
            self.current_process.burst_time -= 1

            # Si el proceso ha terminado
            if self.current_process.burst_time <= 0:
                self.current_process.state = "terminated"
                self.resources.cpu_available = True
                self.resources.release_memory(self.current_process.pid, self.current_process.memory)
                result = {"event": "process_completed", "process": self.current_process}
                self.current_process = None
                return result

            return {"event": "process_running", "process": self.current_process}

        return {"event": "idle"}


class FCFSScheduler(Scheduler):
    """First-Come, First-Served (FCFS) Scheduler"""

    def __init__(self, process_manager: ProcessManager, resources: SystemResources):
        super().__init__(process_manager, resources)
        self.name = "First-Come, First-Served (FCFS)"

    def select_next_process(self) -> Process:
        """Selecciona el primer proceso que llegó a la cola de listos"""
        for process in self.process_manager.ready_queue:
            if process.state == "ready":
                return process
        return None


class SJFScheduler(Scheduler):
    """Shortest Job First (SJF) Scheduler"""

    def __init__(self, process_manager: ProcessManager, resources: SystemResources):
        super().__init__(process_manager, resources)
        self.name = "Shortest Job First (SJF)"

    def select_next_process(self) -> Process:
        """Selecciona el proceso con el menor tiempo de CPU requerido"""
        if not self.process_manager.ready_queue:
            return None

        ready_processes = [p for p in self.process_manager.ready_queue if p.state == "ready"]
        if not ready_processes:
            return None

        return min(ready_processes, key=lambda p: p.burst_time)


class PriorityScheduler(Scheduler):
    """Priority Scheduler"""

    def __init__(self, process_manager: ProcessManager, resources: SystemResources):
        super().__init__(process_manager, resources)
        self.name = "Priority Scheduler"

    def select_next_process(self) -> Process:
        """Selecciona el proceso con la mayor prioridad (número más bajo)"""
        if not self.process_manager.ready_queue:
            return None

        ready_processes = [p for p in self.process_manager.ready_queue if p.state == "ready"]
        if not ready_processes:
            return None

        return min(ready_processes, key=lambda p: p.priority)


class RoundRobinScheduler(Scheduler):
    """Round Robin Scheduler with configurable quantum"""

    def __init__(self, process_manager: ProcessManager, resources: SystemResources, quantum: int = 2):
        super().__init__(process_manager, resources)
        self.name = f"Round Robin (Quantum: {quantum})"
        self.quantum = quantum
        self.current_quantum = 0

    def select_next_process(self) -> Process:
        """Selecciona el siguiente proceso en la cola de listos"""
        if not self.process_manager.ready_queue:
            return None

        # Si hay un proceso actual y ha agotado su quantum, lo mueve al final de la cola
        if self.current_process and self.current_process.state == "running" and self.current_quantum >= self.quantum:
            self.current_process.state = "ready"
            self.process_manager.ready_queue.remove(self.current_process)
            self.process_manager.ready_queue.append(self.current_process)
            self.resources.cpu_available = True
            self.current_quantum = 0
            self.current_process = None

        # Selecciona el primer proceso listo
        for process in self.process_manager.ready_queue:
            if process.state == "ready":
                self.current_quantum = 0
                return process

        return None

    def execute_cycle(self) -> dict:
        """Ejecuta un ciclo de CPU con gestión del quantum"""
        result = super().execute_cycle()

        # Incrementa el quantum usado si hay un proceso en ejecución
        if self.current_process and self.current_process.state == "running":
            self.current_quantum += 1

            # Si el proceso ha agotado su quantum, lo interrumpe
            if self.current_quantum >= self.quantum and self.current_process.burst_time > 0:
                self.current_process.state = "ready"
                self.resources.cpu_available = True
                self.process_manager.ready_queue.remove(self.current_process)
                self.process_manager.ready_queue.append(self.current_process)
                result = {"event": "process_preempted", "process": self.current_process}
                self.current_process = None
                self.current_quantum = 0

        return result

    def set_quantum(self, quantum: int) -> None:
        """Cambia el valor del quantum"""
        self.quantum = quantum
        self.name = f"Round Robin (Quantum: {quantum})"
        self.current_quantum = 0  # Reinicia el quantum actual


class SchedulerFactory:
    """Fábrica para crear instancias de planificadores"""

    @staticmethod
    def create_scheduler(algorithm: str, process_manager: ProcessManager,
                         resources: SystemResources, quantum: int = 2) -> Scheduler:
        """
        Crea una instancia del planificador según el algoritmo seleccionado

        Args:
            algorithm: Nombre del algoritmo ('fcfs', 'sjf', 'priority' o 'round_robin')
            process_manager: Instancia del gestor de procesos
            resources: Instancia de los recursos del sistema
            quantum: Valor del quantum para Round Robin

        Returns:
            Una instancia del planificador solicitado
        """
        algorithm = algorithm.lower()

        if algorithm == 'fcfs':
            return FCFSScheduler(process_manager, resources)
        elif algorithm == 'sjf':
            return SJFScheduler(process_manager, resources)
        elif algorithm == 'priority':
            return PriorityScheduler(process_manager, resources)
        elif algorithm == 'round_robin':
            return RoundRobinScheduler(process_manager, resources, quantum)
        else:
            raise ValueError(f"Algoritmo desconocido: {algorithm}")