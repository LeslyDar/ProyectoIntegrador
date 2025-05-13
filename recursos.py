class SystemResources:
    def __init__(self):
        self.cpu_available = True           # Solo 1 CPU
        self.total_memory = 4096            # 4GB en MB
        self.available_memory = 4096

    def assign_memory(self, pid: int, memory: int) -> bool:
        if self.available_memory >= memory:
            self.available_memory -= memory
            return True
        return False  # No hay suficiente memoria

    def release_memory(self, pid: int, memory: int) -> None:
        self.available_memory += memory

    def get_resource_status(self) -> dict:
        return {
            "CPU": "Libre" if self.cpu_available else "Ocupada",
            "Memoria": f"{self.available_memory}/{self.total_memory} MB"
        }