"""
Widget para visualização do replay da pista e comparação de traçados (Ghost Replay).
Utiliza PyQtGraph para desenho 2D, com coloração de segmentos baseada em dados reais (velocidade, freio, acelerador) e playback.
"""

import logging
from typing import List, Dict, Tuple, Optional, Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSlider, QGridLayout
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtGui import QColor, QPen

logger = logging.getLogger(__name__)

# --- Cores da Paleta do Usuário (Adaptadas para PyQtGraph/QColor) ---
# bg-100:#1A1A1A
# bg-200:#292929
# bg-300:#404040
# text-100:#FFFFFF
# text-200:#e0e0e0
# primary-100:#FF5733 (Laranja avermelhado)
# primary-200:#ff8a5f
# primary-300:#fff3bf
# accent-100:#33FF57 (Verde brilhante)
# accent-200:#009700 (Verde escuro)

COLOR_BG = QColor("#1A1A1A")
COLOR_FG = QColor("#E0E0E0")
COLOR_GRID = QColor(80, 80, 80, 150) # --bg-300 com alpha
COLOR_TRACK_OUTLINE = QColor(150, 150, 150, 150)

# Cores para Segmentos Baseadas em Ações
COLOR_BRAKING = QColor(255, 87, 51, 220)    # Vermelho/Laranja (--primary-100 com alpha)
COLOR_ACCELERATING = QColor(51, 255, 87, 200) # Verde Brilhante (--accent-100 com alpha)
COLOR_COASTING = QColor(100, 100, 200, 180) # Azulado claro (para diferenciar)
COLOR_NEUTRAL_SPEED = QColor(200, 200, 200, 180) # Cinza para velocidade média/constante

# Cores base para voltas (se não houver dados para coloração avançada)
LAP_BASE_COLORS = [
    QColor(255, 0, 0, 200),    # Red
    QColor(0, 0, 255, 200),    # Blue
    QColor(0, 255, 0, 200),    # Green
    QColor(255, 255, 0, 200),  # Yellow
    QColor(255, 0, 255, 200),  # Magenta
    QColor(0, 255, 255, 200),  # Cyan
    QColor(255, 165, 0, 200), # Orange
    QColor(128, 0, 128, 200), # Purple
]

# Limiares para coloração
BRAKE_THRESHOLD = 0.10 # 10% de pressão de freio
THROTTLE_THRESHOLD = 0.80 # 80% de acelerador

class TrackReplayWidget(QWidget):
    """Widget que exibe o mapa da pista, traçados com coloração e playback."""
    
    replay_time_changed = pyqtSignal(float) 
    playback_state_changed = pyqtSignal(bool) # True if playing, False if paused/stopped

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Initializing TrackReplayWidget...")
        
        self.track_data: Optional[Dict[str, np.ndarray]] = None
        self.lap_data: Dict[str, Dict[str, Any]] = {}
        self.current_replay_time: float = 0.0
        self.max_replay_time: float = 0.0
        self.is_playing: bool = False
        
        self.playback_timer = QTimer(self)
        self.playback_timer.setInterval(33) # ~30 FPS update interval
        self.playback_timer.timeout.connect(self._advance_replay)
        
        self._setup_ui()
        logger.info("TrackReplayWidget initialized.")

    def _setup_ui(self):
        """Configura a interface do widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Plot Widget --- 
        pg.setConfigOption("background", COLOR_BG)
        pg.setConfigOption("foreground", COLOR_FG)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.showGrid(x=True, y=True, pen=pg.mkPen(COLOR_GRID))
        self.plot_item = self.plot_widget.getPlotItem()
        # Remover eixos para visualização mais limpa do mapa
        self.plot_item.hideAxis(	"bottom"	)
        self.plot_item.hideAxis(	"left"	)
        main_layout.addWidget(self.plot_widget, 1)

        # --- Controle de Replay --- 
        control_widget = QWidget()
        control_layout = QGridLayout(control_widget)
        
        self.play_pause_button = QPushButton("▶ Play")
        self.play_pause_button.setCheckable(True)
        self.play_pause_button.toggled.connect(self._toggle_play)
        self.play_pause_button.setObjectName("accentButton") # Usa cor de destaque do QSS
        self.play_pause_button.setFixedWidth(80)
        
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.clicked.connect(self.stop_replay)
        self.stop_button.setFixedWidth(80)

        self.replay_slider = QSlider(Qt.Orientation.Horizontal)
        self.replay_slider.setMinimum(0)
        self.replay_slider.setMaximum(1000) 
        self.replay_slider.valueChanged.connect(self._on_slider_change)
        self.playback_state_changed.connect(lambda playing: self.replay_slider.setEnabled(not playing))

        self.time_label = QLabel("Tempo: 0.00s")
        self.time_label.setFixedWidth(100)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        control_layout.addWidget(self.play_pause_button, 0, 0)
        control_layout.addWidget(self.stop_button, 0, 1)
        control_layout.addWidget(self.replay_slider, 0, 2)
        control_layout.addWidget(self.time_label, 0, 3)
        control_layout.setColumnStretch(2, 1) # Slider expande
        
        main_layout.addWidget(control_widget)

    def load_track_outline(self, x_coords: List[float], y_coords: List[float]):
        """Carrega e desenha o contorno da pista."""
        logger.info(f"Loading track outline with {len(x_coords)} points.")
        if not x_coords or not y_coords:
            logger.warning("Empty track outline data provided.")
            return
            
        self.track_data = {
            "outline_x": np.array(x_coords),
            "outline_y": np.array(y_coords)
        }
        self.plot_item.clearPlots()
        self.lap_data = {}
        
        track_pen = pg.mkPen(color=COLOR_TRACK_OUTLINE, width=2)
        self.plot_item.plot(self.track_data["outline_x"], self.track_data["outline_y"], pen=track_pen, name="Track Outline")
        logger.info("Track outline drawn.")
        self.plot_item.autoRange()

    def _calculate_segment_colors(self, speed: Optional[np.ndarray], brake: Optional[np.ndarray], throttle: Optional[np.ndarray], num_segments: int, base_color: QColor) -> List[QColor]:
        """Calcula as cores dos segmentos com base nos dados de telemetria."""
        colors = [base_color] * num_segments # Cor base padrão

        # Se tiver dados de freio e acelerador, usa coloração avançada
        if brake is not None and throttle is not None and len(brake) > 1 and len(throttle) > 1:
            # Calcula valores médios por segmento
            avg_brake = (brake[:-1] + brake[1:]) / 2
            avg_throttle = (throttle[:-1] + throttle[1:]) / 2
            
            colors = []
            for i in range(num_segments):
                if avg_brake[i] > BRAKE_THRESHOLD:
                    colors.append(COLOR_BRAKING)
                elif avg_throttle[i] > THROTTLE_THRESHOLD:
                    colors.append(COLOR_ACCELERATING)
                elif avg_brake[i] < 0.01 and avg_throttle[i] < 0.05: # Quase sem input
                    colors.append(COLOR_COASTING)
                else:
                    # Poderia adicionar lógica baseada em velocidade aqui se desejado
                    colors.append(COLOR_NEUTRAL_SPEED) # Cor neutra para outros casos
                    
        # Fallback para coloração por velocidade se freio/acelerador não disponíveis
        elif speed is not None and len(speed) > 1:
            logger.debug("Coloring segments based on speed (fallback).")
            avg_speeds = (speed[:-1] + speed[1:]) / 2
            # Usar percentis para definir limiares dinâmicos
            try:
                speed_threshold_low = np.percentile(speed, 33)
                speed_threshold_high = np.percentile(speed, 66)
            except IndexError: # Acontece se houver poucos pontos
                speed_threshold_low = np.min(speed) if len(speed) > 0 else 0
                speed_threshold_high = np.max(speed) if len(speed) > 0 else 1
                
            colors = []
            for s in avg_speeds:
                if s < speed_threshold_low:
                    colors.append(COLOR_COASTING) # Reutiliza cor de coasting para baixa velocidade
                elif s > speed_threshold_high:
                    colors.append(COLOR_ACCELERATING) # Reutiliza cor de aceleração para alta velocidade
                else:
                    colors.append(COLOR_NEUTRAL_SPEED)
        else:
             logger.debug("No sufficient data for advanced segment coloring. Using base lap color.")
             # Mantém a cor base se nenhum dado relevante estiver disponível
             pass 

        return colors

    def add_lap(self, lap_id: str, lap_data: Dict[str, np.ndarray]):
        """Adiciona os dados de uma volta, com coloração baseada em telemetria.
        
        Args:
            lap_id: Identificador único da volta.
            lap_data: Dicionário contendo arrays numpy para canais como 
                      'Pos X', 'Pos Y', 'Time', e opcionalmente 'Ground Speed', 
                      'Brake Pos', 'Throttle Pos'.
        """
        required_channels = ["Pos X", "Pos Y", "Time"]
        if not all(k in lap_data for k in required_channels):
            logger.error(f"Missing required channels ({required_channels}) for lap 	'{lap_id}	'. Cannot add lap.")
            return

        x = lap_data["Pos X"]
        y = lap_data["Pos Y"]
        t = lap_data["Time"]
        speed = lap_data.get("Ground Speed")
        brake = lap_data.get("Brake Pos")
        throttle = lap_data.get("Throttle Pos")

        if not (len(x) > 1 and len(y) > 1 and len(t) > 1):
            logger.warning(f"Attempted to add lap 	'{lap_id}	' with insufficient data points.")
            return
            
        # Validação de comprimento (todos os arrays devem ter o mesmo tamanho)
        base_len = len(x)
        for key, arr in lap_data.items():
            if len(arr) != base_len:
                logger.error(f"Data length mismatch for lap 	'{lap_id}	'. Channel 	'{key}	' has length {len(arr)}, expected {base_len}. Cannot add lap.")
                return

        logger.info(f"Adding lap 	'{lap_id}	' with {base_len} points.")
        
        lap_index = len(self.lap_data)
        base_color = LAP_BASE_COLORS[lap_index % len(LAP_BASE_COLORS)]
        
        # --- Desenho do Traçado com Coloração por Segmento --- 
        points = np.vstack([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        num_segments = len(segments)
        
        # Calcula cores dos segmentos
        segment_colors = self._calculate_segment_colors(speed, brake, throttle, num_segments, base_color)
            
        # Cria o PlotDataItem com segmentos coloridos
        colored_trace = pg.PlotDataItem(connect="pairs", pen=None)
        colored_trace.setData(pos=segments.reshape(-1, 2), color=segment_colors, pxMode=False)
        colored_trace.setPen(pg.mkPen(width=3)) # Aplica largura, cor é por segmento
        self.plot_item.addItem(colored_trace)

        # Cria o marcador (Ghost)
        marker_color_tuple = base_color.getRgb() # Converte QColor para tupla para ScatterPlotItem
        marker = pg.ScatterPlotItem(size=12, brush=pg.mkBrush(marker_color_tuple), pen=pg.mkPen(color=(255,255,255), width=1))
        self.plot_item.addItem(marker)
        marker.setData(pos=np.array([[x[0], y[0]]])) # Posição inicial
        
        # Armazena os dados brutos e itens do plot
        self.lap_data[lap_id] = {
            "data": lap_data, # Armazena todos os dados recebidos
            "color": base_color,
            "plot_item": colored_trace,
            "marker": marker
        }
        
        # Atualiza o tempo máximo e o range do slider
        self.max_replay_time = max([self.max_replay_time] + [lap["data"]["Time"].max() for lap in self.lap_data.values()])
        self.replay_slider.setMaximum(int(self.max_replay_time * 100)) 
        logger.info(f"Lap 	'{lap_id}	' added. Max time: {self.max_replay_time:.2f}s. Slider max: {self.replay_slider.maximum()}")
        self.plot_item.autoRange() # Ajusta o zoom após adicionar a volta

    def remove_lap(self, lap_id: str):
        """Remove uma volta da visualização."""
        if lap_id in self.lap_data:
            logger.info(f"Removing lap 	'{lap_id}	'.")
            lap_info = self.lap_data.pop(lap_id)
            self.plot_item.removeItem(lap_info["plot_item"])
            self.plot_item.removeItem(lap_info["marker"])
            # Recalcula max_time e atualiza slider
            self.max_replay_time = max([0.0] + [lap["data"]["Time"].max() for lap in self.lap_data.values()])
            self.replay_slider.setMaximum(int(self.max_replay_time * 100))
        else:
            logger.warning(f"Attempted to remove non-existent lap 	'{lap_id}	'.")

    def clear_laps(self):
        """Remove todas as voltas da visualização."""
        logger.info("Clearing all laps.")
        lap_ids = list(self.lap_data.keys())
        for lap_id in lap_ids:
            self.remove_lap(lap_id)
        self.stop_replay()

    @pyqtSlot(int)
    def _on_slider_change(self, value):
        """Atualiza a posição dos marcadores quando o slider muda manualmente."""
        if not self.is_playing:
            target_time = value / 100.0 
            self.set_replay_time(target_time)
        
    def set_replay_time(self, target_time: float):
        """Define o tempo atual do replay e atualiza os marcadores."""
        target_time = min(max(target_time, 0.0), self.max_replay_time)
        self.current_replay_time = target_time
        self.time_label.setText(f"Tempo: {target_time:.2f}s")
        
        if not self.replay_slider.isSliderDown() and not self.is_playing:
             slider_value = int(target_time * 100)
             if self.replay_slider.value() != slider_value:
                 self.replay_slider.setValue(slider_value)

        for lap_id, lap_info in self.lap_data.items():
            time_array = lap_info["data"]["Time"]
            # Encontra o índice mais próximo do tempo alvo
            index = np.searchsorted(time_array, target_time, side="left")
            
            # Ajusta o índice para o ponto mais próximo (antes ou depois)
            if index >= len(time_array):
                index = len(time_array) - 1
            elif index > 0 and abs(time_array[index-1] - target_time) < abs(time_array[index] - target_time):
                 index = index - 1
                 
            if index < 0: index = 0

            x_pos = lap_info["data"]["Pos X"][index]
            y_pos = lap_info["data"]["Pos Y"][index]
            lap_info["marker"].setData(pos=np.array([[x_pos, y_pos]]))
            
        self.replay_time_changed.emit(target_time)

    @pyqtSlot(bool)
    def _toggle_play(self, checked):
        """Inicia ou pausa o playback."""
        if checked:
            if self.current_replay_time >= self.max_replay_time:
                self.current_replay_time = 0 # Reinicia se chegou ao fim
            self.is_playing = True
            self.playback_timer.start()
            self.play_pause_button.setText("❚❚ Pause")
            logger.info("Playback started.")
        else:
            self.is_playing = False
            self.playback_timer.stop()
            self.play_pause_button.setText("▶ Play")
            logger.info("Playback paused.")
        self.playback_state_changed.emit(self.is_playing)

    def stop_replay(self):
        """Para o playback e reseta o tempo."""
        if self.is_playing:
            self.play_pause_button.setChecked(False)
        self.set_replay_time(0.0)
        self.replay_slider.setValue(0)
        logger.info("Playback stopped and reset.")

    def _advance_replay(self):
        """Avança o tempo do replay em um passo."""
        if not self.is_playing: return
        
        increment = self.playback_timer.interval() / 1000.0
        new_time = self.current_replay_time + increment
        
        if new_time >= self.max_replay_time:
            self.set_replay_time(self.max_replay_time)
            self.play_pause_button.setChecked(False)
        else:
            self.set_replay_time(new_time)
            # Atualiza o slider visualmente
            self.replay_slider.setValue(int(new_time * 100))

    def closeEvent(self, event):
        """Garante que o timer pare ao fechar."""
        self.playback_timer.stop()
        super().closeEvent(event)

# Exemplo de uso (para teste)
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    logging.basicConfig(level=logging.DEBUG)
    
    app = QApplication(sys.argv)
    # Aplicar estilo QSS aqui se necessário para teste visual
    app.setStyleSheet("""
        QWidget { background-color: #1A1A1A; color: #E0E0E0; font-size: 10pt; }
        QPushButton { background-color: #404040; border: 1px solid #505050; padding: 5px 10px; min-height: 20px; }
        QPushButton:hover { background-color: #505050; }
        QPushButton:pressed { background-color: #303030; }
        QPushButton#accentButton { background-color: #009700; color: white; }
        QPushButton#accentButton:hover { background-color: #33FF57; }
        QPushButton#accentButton:pressed { background-color: #007700; }
        QSlider::groove:horizontal { height: 8px; background: #404040; border-radius: 4px; }
        QSlider::handle:horizontal { background: #E0E0E0; border: 1px solid #B0B0B0; width: 16px; margin: -4px 0; border-radius: 8px; }
        QSlider::sub-page:horizontal { background: #33FF57; border-radius: 4px; }
        QLabel { color: #E0E0E0; }
    """)
    
    window = QWidget()
    layout = QVBoxLayout(window)
    replay_widget = TrackReplayWidget()
    layout.addWidget(replay_widget)
    
    # --- Dados de Exemplo --- 
    # Simula contorno simples
    track_x = [0, 100, 100, 50, 0, 0]
    track_y = [0, 0, 100, 150, 100, 0]
    replay_widget.load_track_outline(track_x, track_y)
    
    # Volta 1 (com dados de telemetria)
    lap1_n = 200
    lap1_t = np.linspace(0, 10, lap1_n)
    lap1_x = 50 + 40 * np.cos(lap1_t * np.pi / 5) 
    lap1_y = 75 + 60 * np.sin(lap1_t * np.pi / 5)
    lap1_s = 150 + 50 * np.sin(lap1_t * np.pi / 2.5) # Velocidade
    lap1_b = np.zeros(lap1_n)
    lap1_b[50:70] = np.linspace(0, 1, 20)**0.5 # Zona de frenagem
    lap1_b[150:170] = np.linspace(0, 0.8, 20)**0.5 # Outra frenagem
    lap1_th = np.zeros(lap1_n)
    lap1_th[80:110] = np.linspace(0.5, 1, 30) # Aceleração
    lap1_th[180:] = np.linspace(0.2, 1, lap1_n - 180) # Aceleração final
    
    lap1_data = {
        "Pos X": lap1_x,
        "Pos Y": lap1_y,
        "Time": lap1_t,
        "Ground Speed": lap1_s,
        "Brake Pos": lap1_b,
        "Throttle Pos": lap1_th
    }
    replay_widget.add_lap("Lap 1", lap1_data)

    # Volta 2 (simulada, talvez sem dados de freio/acelerador para testar fallback)
    lap2_n = 240
    lap2_t = np.linspace(0, 12, lap2_n) # Volta mais lenta
    lap2_x = 50 + 45 * np.cos(lap2_t * np.pi / 6 + 0.1) # Traçado ligeiramente diferente
    lap2_y = 75 + 65 * np.sin(lap2_t * np.pi / 6 + 0.1)
    lap2_s = 130 + 40 * np.sin(lap2_t * np.pi / 3) # Velocidade diferente
    
    lap2_data = {
        "Pos X": lap2_x,
        "Pos Y": lap2_y,
        "Time": lap2_t,
        "Ground Speed": lap2_s
        # Sem Brake Pos e Throttle Pos para testar fallback de coloração
    }
    replay_widget.add_lap("Lap 2", lap2_data)
    
    window.setWindowTitle("Track Replay - Advanced Coloring")
    window.setGeometry(100, 100, 800, 700)
    window.show()
    sys.exit(app.exec())

