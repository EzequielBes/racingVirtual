"""
Gerenciador de dados de telemetria em tempo real.
Responsável por iniciar e parar coletores de dados e distribuir telemetria.
"""

import logging
from typing import Dict, Any, Callable, Optional

from realtime.acc_collector import ACCDataCollector
from realtime.lmu_collector import LMUDataCollector

logger = logging.getLogger(__name__)

class RealtimeTelemetryManager:
    """Gerencia a coleta e distribuição de telemetria em tempo real."""
    
    def __init__(self):
        self.acc_collector: Optional[ACCDataCollector] = None
        self.lmu_collector: Optional[LMUDataCollector] = None
        self.data_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self.current_game: Optional[str] = None
        
    def start_collector(self, game: str, data_callback: Callable[[Dict[str, Any]], None]):
        """Inicia o coletor de dados para o jogo especificado."""
        self.stop_all_collectors() # Garante que apenas um coletor esteja ativo
        
        self.data_callback = data_callback
        self.current_game = game.lower()
        
        if self.current_game == "acc":
            self.acc_collector = ACCDataCollector()
            self.acc_collector.start(self._process_realtime_data)
            logger.info("Coletor ACC iniciado.")
        elif self.current_game == "lmu":
            self.lmu_collector = LMUDataCollector()
            self.lmu_collector.start(self._process_realtime_data)
            logger.info("Coletor LMU iniciado.")
        else:
            logger.warning(f"Jogo \'{game}\' não suportado para telemetria em tempo real.")
            
    def stop_all_collectors(self):
        """Para todos os coletores de dados ativos."""
        if self.acc_collector and self.acc_collector.running:
            self.acc_collector.stop()
            self.acc_collector = None
            logger.info("Coletor ACC parado.")
            
        if self.lmu_collector and self.lmu_collector.running:
            self.lmu_collector.stop()
            self.lmu_collector = None
            logger.info("Coletor LMU parado.")
            
        self.current_game = None
        
    def _process_realtime_data(self, data: Dict[str, Any]):
        """Processa e distribui os dados de telemetria recebidos."""
        # Aqui você pode adicionar lógica para normalizar dados entre jogos
        # ou para enriquecer os dados antes de passá-los para a UI/análise.
        
        if self.data_callback:
            self.data_callback(data)
            
    def get_last_data(self) -> Optional[Dict[str, Any]]:
        """Retorna o último pacote de dados do coletor ativo."""
        if self.current_game == "acc" and self.acc_collector:
            return self.acc_collector.get_last_telemetry_data()
        elif self.current_game == "lmu" and self.lmu_collector:
            return self.lmu_collector.get_last_telemetry_data()
        return None

# Exemplo de uso (para testes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def handle_telemetry(data):
        if "speed" in data:
            print(f"[Realtime] Speed: {data["speed"]:.2f} km/h, RPM: {data["rpm"]:.0f}, Gear: {data["gear"]}")
            
    manager = RealtimeTelemetryManager()
    
    print("\n--- Testando ACC ---")
    manager.start_collector("acc", handle_telemetry)
    time.sleep(5) # Simula tempo de execução
    manager.stop_all_collectors()
    
    print("\n--- Testando LMU ---")
    manager.start_collector("lmu", handle_telemetry)
    time.sleep(5) # Simula tempo de execução
    manager.stop_all_collectors()
    
    print("\n--- Teste Concluído ---")


