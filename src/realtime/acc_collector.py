"""
Coletor de dados de telemetria em tempo real para Assetto Corsa Competizione (ACC).
Utiliza o protocolo UDP para receber dados do jogo.
"""

import socket
import struct
import json
import threading
import time
import logging
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)

class ACCDataCollector:
    """Coleta dados de telemetria do ACC via UDP."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9000, buffer_size: int = 4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.socket = None
        self.running = False
        self.thread = None
        self.data_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self.last_telemetry_data: Dict[str, Any] = {}
        
    def start(self, data_callback: Callable[[Dict[str, Any]], None]):
        """Inicia o coletor de dados."""
        if self.running:
            logger.warning("Coletor já está rodando.")
            return
        
        self.data_callback = data_callback
        self.running = True
        self.thread = threading.Thread(target=self._run_collector)
        self.thread.daemon = True  # Permite que o programa principal saia mesmo com a thread rodando
        self.thread.start()
        logger.info(f"Coletor ACC iniciado no {self.host}:{self.port}")
        
    def stop(self):
        """Para o coletor de dados."""
        if not self.running:
            logger.warning("Coletor não está rodando.")
            return
        
        self.running = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join(timeout=1) # Espera a thread terminar
        logger.info("Coletor ACC parado.")
        
    def _run_collector(self):
        """Loop principal de coleta de dados."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.host, self.port))
            self.socket.settimeout(1.0) # Timeout para não bloquear indefinidamente
            logger.info(f"Aguardando dados UDP do ACC em {self.host}:{self.port}...")
            
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(self.buffer_size)
                    telemetry = self._parse_acc_udp_data(data)
                    if telemetry:
                        self.last_telemetry_data = telemetry
                        if self.data_callback:
                            self.data_callback(telemetry)
                except socket.timeout:
                    # logger.debug("Aguardando dados UDP...")
                    pass # Sem dados recebidos no timeout
                except Exception as e:
                    logger.error(f"Erro ao receber/processar dados UDP do ACC: {e}")
                    time.sleep(0.1) # Pequena pausa para evitar loop de erro
        except Exception as e:
            logger.critical(f"Erro fatal ao iniciar socket UDP para ACC: {e}")
        finally:
            if self.socket:
                self.socket.close()
            self.running = False

    def _parse_acc_udp_data(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Parses the raw UDP data from ACC.
        
        This is a simplified parser. A full implementation would require
        understanding the exact ACC UDP protocol structure, which is complex
        and involves multiple message types (graphics, physics, static info).
        
        For demonstration, we'll assume a basic structure or try to extract
        some common values if they are present in a simple format.
        
        Real ACC UDP data is usually structured with headers and specific
        offsets for different data types (floats, ints, strings).
        """
        telemetry = {}
        
        # ACC UDP Protocol is complex. This is a placeholder for actual parsing.
        # A common approach is to use a library or a detailed spec.
        # Example: https://www.assettocorsa.net/forum/index.php?threads/acc-shared-memory-and-api-documentation.54823/
        # Or look for existing Python implementations for ACC UDP.
        
        # Try to extract some basic values if the data is simple enough
        # This part is highly dependent on the actual UDP packet structure.
        
        # For now, let's assume we can decode some basic float values
        # This is a *very* naive attempt and will likely fail with real ACC data
        # without proper protocol understanding.
        try:
            # Attempt to unpack some floats, assuming common channels like speed, RPM
            # This is a guess; actual offsets and types vary.
            if len(data) >= 4 * 5: # At least 5 floats
                # Example: speed, rpm, throttle, brake, gear
                # This is NOT the actual ACC UDP structure.
                values = struct.unpack("<fffff", data[:4*5])
                telemetry["speed"] = values[0] * 3.6 # m/s to km/h
                telemetry["rpm"] = values[1]
                telemetry["throttle"] = values[2]
                telemetry["brake"] = values[3]
                telemetry["gear"] = int(values[4])
                
                # Add some dummy G-forces for testing track map
                telemetry["G_LAT"] = (telemetry["speed"] / 100) * 0.5 # Dummy lateral G
                telemetry["G_LONG"] = (telemetry["throttle"] - telemetry["brake"]) / 100 * 0.8 # Dummy longitudinal G
                
                # Dummy position data for track map visualization
                # In a real scenario, ACC provides X, Y, Z coordinates.
                # For now, we'll simulate movement for testing.
                # This requires a more sophisticated state machine or actual game data.
                # For a simple test, let's just make them change slightly.
                telemetry["POS_X"] = time.time() * 0.1 % 1000 # Dummy X
                telemetry["POS_Y"] = time.time() * 0.05 % 1000 # Dummy Y
                
                # Add dummy lap data for testing
                telemetry["lap_number"] = 1
                telemetry["lap_time"] = time.time() % 100 # Dummy lap time
                telemetry["distance_travelled"] = time.time() * 50 # Dummy distance
                
                # Add dummy metadata
                telemetry["track"] = "monza"
                telemetry["car"] = "Ferrari 488 GT3"
                
                return telemetry
        except struct.error as se:
            logger.debug(f"Erro ao desempacotar dados UDP do ACC (formato inesperado): {se}")
        except Exception as e:
            logger.error(f"Erro genérico ao parsear dados UDP do ACC: {e}")
            
        return None

    def get_last_telemetry_data(self) -> Dict[str, Any]:
        """Retorna o último pacote de telemetria recebido."""
        return self.last_telemetry_data

# Exemplo de uso (para testes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def print_telemetry(data):
        # print(f"Dados recebidos: {data}")
        if "speed" in data:
            print(f"Speed: {data['speed']:.2f} km/h, RPM: {data['rpm']:.0f}, Gear: {data['gear']}")
            
    collector = ACCDataCollector()
    try:
        collector.start(print_telemetry)
        # Para simular dados, você precisaria de um ACC rodando e enviando UDP
        # Ou um script que envia pacotes UDP para a porta 9000
        print("Aguardando dados do ACC. Certifique-se de que o ACC está enviando telemetria UDP para 127.0.0.1:9000.")
        print("Pressione Ctrl+C para parar.")
        while True:
            time.sleep(1) # Mantém o programa rodando
    except KeyboardInterrupt:
        print("Parando coletor...")
    finally:
        collector.stop()


