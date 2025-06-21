"""
Coletor de dados de telemetria em tempo real para Le Mans Ultimate (LMU).
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

class LMUDataCollector:
    """Coleta dados de telemetria do LMU via UDP."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 5000, buffer_size: int = 4096):
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
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Coletor LMU iniciado no {self.host}:{self.port}")
        
    def stop(self):
        """Para o coletor de dados."""
        if not self.running:
            logger.warning("Coletor não está rodando.")
            return
        
        self.running = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join(timeout=1)
        logger.info("Coletor LMU parado.")
        
    def _run_collector(self):
        """Loop principal de coleta de dados."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.host, self.port))
            self.socket.settimeout(1.0)
            logger.info(f"Aguardando dados UDP do LMU em {self.host}:{self.port}...")
            
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(self.buffer_size)
                    telemetry = self._parse_lmu_udp_data(data)
                    if telemetry:
                        self.last_telemetry_data = telemetry
                        if self.data_callback:
                            self.data_callback(telemetry)
                except socket.timeout:
                    pass
                except Exception as e:
                    logger.error(f"Erro ao receber/processar dados UDP do LMU: {e}")
                    time.sleep(0.1)
        except Exception as e:
            logger.critical(f"Erro fatal ao iniciar socket UDP para LMU: {e}")
        finally:
            if self.socket:
                self.socket.close()
            self.running = False

    def _parse_lmu_udp_data(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Parses the raw UDP data from LMU.
        
        LMU uses a more structured UDP telemetry. This is a simplified example
        based on common sim racing telemetry structures. A full implementation
        would require the exact LMU UDP protocol specification.
        
        For demonstration, we will assume a basic structure for key channels.
        """
        telemetry = {}
        
        # LMU UDP protocol details are needed for accurate parsing.
        # This is a placeholder, assuming a fixed-size packet with some common values.
        # Example: https://www.studio-397.com/developers-corner/ (rFactor 2 shares similar UDP)
        
        try:
            # Assuming a structure like: speed, rpm, throttle, brake, gear, pos_x, pos_y
            # This is a guess; actual offsets and types vary.
            if len(data) >= 4 * 7: # At least 7 floats
                values = struct.unpack("<fffffff", data[:4*7])
                telemetry["speed"] = values[0] * 3.6 # m/s to km/h
                telemetry["rpm"] = values[1]
                telemetry["throttle"] = values[2]
                telemetry["brake"] = values[3]
                telemetry["gear"] = int(values[4])
                telemetry["POS_X"] = values[5]
                telemetry["POS_Y"] = values[6]
                
                # Add some dummy G-forces for testing track map
                telemetry["G_LAT"] = (telemetry["speed"] / 100) * 0.6 # Dummy lateral G
                telemetry["G_LONG"] = (telemetry["throttle"] - telemetry["brake"]) / 100 * 0.9 # Dummy longitudinal G
                
                # Add dummy lap data for testing
                telemetry["lap_number"] = 1
                telemetry["lap_time"] = time.time() % 100 # Dummy lap time
                telemetry["distance_travelled"] = time.time() * 60 # Dummy distance
                
                # Add dummy metadata
                telemetry["track"] = "spa"
                telemetry["car"] = "Porsche 963"
                
                return telemetry
        except struct.error as se:
            logger.debug(f"Erro ao desempacotar dados UDP do LMU (formato inesperado): {se}")
        except Exception as e:
            logger.error(f"Erro genérico ao parsear dados UDP do LMU: {e}")
            
        return None

    def get_last_telemetry_data(self) -> Dict[str, Any]:
        """Retorna o último pacote de telemetria recebido."""
        return self.last_telemetry_data

# Exemplo de uso (para testes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def print_telemetry(data):
        if "speed" in data:
            print(f"Speed: {data["speed"]:.2f} km/h, RPM: {data["rpm"]:.0f}, Gear: {data["gear"]}")
            
    collector = LMUDataCollector()
    try:
        collector.start(print_telemetry)
        print("Aguardando dados do LMU. Certifique-se de que o LMU está enviando telemetria UDP para 127.0.0.1:5000.")
        print("Pressione Ctrl+C para parar.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Parando coletor...")
    finally:
        collector.stop()


