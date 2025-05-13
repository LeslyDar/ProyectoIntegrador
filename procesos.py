class Process:
    def __init__(self, pid: int, priority: int, memory: int, burst_time: int):
        self.pid = pid                      # Identificador único
        self.state = "ready"                # Estados: ready, running, waiting, terminated
        self.priority = priority            # Número entero (ej: 1-5)
        self.memory = memory                # MB requeridos
        self.burst_time = burst_time        # Tiempo de CPU necesario
        self.resources = []                 # Lista de recursos asignados (ej: ["CPU", "memoria_256MB"])
        self.arrival_time = 0               # Para FCFS/Round Robin (Semana 2)

class ProcessManager:
    def __init__(self):
        self.processes = []                 # Lista de todos los procesos
        self.ready_queue = []               # Cola de procesos listos

    def create_process(self, priority: int, memory: int, burst_time: int) -> Process:
        pid = len(self.processes) + 1       # Generar PID único
        new_process = Process(pid, priority, memory, burst_time)
        self.processes.append(new_process)
        self.ready_queue.append(new_process)
        return new_process

    def list_processes(self) -> list[Process]:
        return self.processes