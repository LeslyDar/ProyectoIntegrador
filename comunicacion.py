import queue
import threading
import time


class MessageQueue:
    """Sistema de mensajes entre procesos"""

    def __init__(self):
        self.process_queues = {}  # Diccionario de colas para cada proceso

    def create_queue(self, pid: int) -> None:
        """Crea una cola de mensajes para un proceso"""
        if pid not in self.process_queues:
            self.process_queues[pid] = queue.Queue()

    def send_message(self, sender_pid: int, receiver_pid: int, message: str) -> bool:
        """
        Envía un mensaje de un proceso a otro

        Args:
            sender_pid: PID del proceso emisor
            receiver_pid: PID del proceso receptor
            message: Contenido del mensaje

        Returns:
            True si el mensaje se envió correctamente, False en caso contrario
        """
        # Verificar si el proceso receptor existe
        if receiver_pid not in self.process_queues:
            return False

        # Crear el mensaje con metadatos
        formatted_message = {
            "sender": sender_pid,
            "content": message,
            "timestamp": time.time()
        }

        # Encolar el mensaje
        self.process_queues[receiver_pid].put(formatted_message)
        return True

    def receive_message(self, pid: int) -> dict:
        """
        Recibe un mensaje de la cola del proceso

        Args:
            pid: PID del proceso receptor

        Returns:
            El mensaje recibido o None si no hay mensajes
        """
        # Verificar si el proceso tiene una cola
        if pid not in self.process_queues:
            return None

        # Verificar si hay mensajes en la cola
        if self.process_queues[pid].empty():
            return None

        # Obtener el mensaje
        return self.process_queues[pid].get()

    def get_queue_size(self, pid: int) -> int:
        """Retorna el número de mensajes en la cola de un proceso"""
        if pid not in self.process_queues:
            return 0
        return self.process_queues[pid].qsize()


class Semaphore:
    """Implementación de semáforo para sincronización"""

    def __init__(self, initial_value: int = 1):
        self.value = initial_value
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def acquire(self) -> None:
        """Operación P (wait/down) - Decrementa el valor del semáforo"""
        with self.lock:
            while self.value <= 0:
                self.condition.wait()
            self.value -= 1

    def release(self) -> None:
        """Operación V (signal/up) - Incrementa el valor del semáforo"""
        with self.lock:
            self.value += 1
            self.condition.notify()


class ProducerConsumer:
    """Implementación del problema del productor-consumidor"""

    def __init__(self, buffer_size: int = 5):
        self.buffer_size = buffer_size
        self.buffer = []

        # Semáforos para la sincronización
        self.mutex = Semaphore(1)  # Exclusión mutua para acceder al buffer
        self.empty = Semaphore(buffer_size)  # Espacios vacíos
        self.full = Semaphore(0)  # Espacios llenos

        # Estados de los procesos
        self.producer_active = False
        self.consumer_active = False

        # Logs de actividad
        self.logs = []

    def produce(self, item: str) -> bool:
        """
        Produce un item y lo coloca en el buffer

        Args:
            item: El item a producir

        Returns:
            True si el item se produjo correctamente, False si el buffer está lleno
        """
        if len(self.buffer) >= self.buffer_size:
            return False

        # Simular la adquisición de semáforos
        if self.empty.value <= 0:
            self.logs.append("Productor bloqueado: buffer lleno")
            return False

        self.empty.value -= 1  # Reduce espacios vacíos
        self.mutex.value -= 1  # Adquiere exclusión mutua

        # Agrega el item al buffer
        self.buffer.append(item)
        self.logs.append(f"Productor: item '{item}' producido → buffer: {len(self.buffer)}/{self.buffer_size}")

        self.mutex.value += 1  # Libera exclusión mutua
        self.full.value += 1  # Incrementa espacios llenos

        return True

    def consume(self) -> str:
        """
        Consume un item del buffer

        Returns:
            El item consumido o None si el buffer está vacío
        """
        if len(self.buffer) <= 0:
            return None

        # Simular la adquisición de semáforos
        if self.full.value <= 0:
            self.logs.append("Consumidor bloqueado: buffer vacío")
            return None

        self.full.value -= 1  # Reduce espacios llenos
        self.mutex.value -= 1  # Adquiere exclusión mutua

        # Retira el item del buffer
        item = self.buffer.pop(0)
        self.logs.append(f"Consumidor: item '{item}' consumido → buffer: {len(self.buffer)}/{self.buffer_size}")

        self.mutex.value += 1  # Libera exclusión mutua
        self.empty.value += 1  # Incrementa espacios vacíos

        return item

    def get_buffer_status(self) -> dict:
        """Retorna el estado actual del buffer"""
        return {
            "buffer_size": self.buffer_size,
            "items_in_buffer": len(self.buffer),
            "buffer_content": self.buffer.copy(),
            "empty_slots": self.empty.value,
            "full_slots": self.full.value
        }

    def get_logs(self) -> list:
        """Retorna los logs de la simulación"""
        return self.logs


# Sistema de comunicación global
message_system = MessageQueue()
producer_consumer = ProducerConsumer()