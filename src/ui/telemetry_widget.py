"""
Widget de telemetria moderno e funcional com layout clean e minimalista.
Exibe gráficos interativos, métricas em tempo real e análise detalhada.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QFrame, QScrollArea, QSplitter, QGroupBox,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QComboBox, QSlider, QProgressBar, QCheckBox,
    QSpinBox, QDoubleSpinBox, QListWidget, QListWidgetItem,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QPixmap, QPainter, QPen
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QRectF
import pyqtgraph as pg
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ModernTelemetryGraph(pg.PlotWidget):
    """Widget de gráfico moderno para telemetria."""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setBackground('#FFFFFF')
        self.setTitle(title, color="#2C3E50", size="16pt")
        self.showGrid(x=True, y=True, alpha=0.2)
        self.setLabel('left', 'Valor', color="#2C3E50", size="12pt")
        self.setLabel('bottom', 'Tempo (s)', color="#2C3E50", size="12pt")
        
        # Configurações modernas
        self.getAxis('left').setTextPen('#2C3E50')
        self.getAxis('bottom').setTextPen('#2C3E50')
        self.getAxis('left').setPen('#E9ECEF')
        self.getAxis('bottom').setPen('#E9ECEF')
        
        # Remove bordas desnecessárias
        self.setMouseEnabled(x=True, y=True)
        self.setMenuEnabled(False)
        
        # Define range do eixo Y para 0-100%
        self.setYRange(0, 100)
        
        # Adiciona legendas
        self.addLegend(offset=(10, 10))

class ModernTrackMap(pg.PlotWidget):
    """Widget para exibir o mapa de traçado moderno."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground('#FFFFFF')
        self.setTitle("Mapa da Pista", color="#2C3E50", size="16pt")
        self.setLabel('left', 'Latitude / Y', color="#2C3E50", size="12pt")
        self.setLabel('bottom', 'Longitude / X', color="#2C3E50", size="12pt")
        
        # Configurações modernas
        self.getAxis('left').setTextPen('#2C3E50')
        self.getAxis('bottom').setTextPen('#2C3E50')
        self.getAxis('left').setPen('#E9ECEF')
        self.getAxis('bottom').setPen('#E9ECEF')
        
        # Remove grid para melhor visualização do traçado
        self.showGrid(x=False, y=False)
        
        # Adiciona legendas
        self.addLegend(offset=(10, 10))

class MetricCard(QFrame):
    """Card moderno para exibir métricas."""
    
    def __init__(self, title: str, value: str = "0", unit: str = "", color: str = "#3498DB", parent=None):
        super().__init__(parent)
        self.setObjectName("metric-card")
        self.setFixedSize(200, 120)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Título
        title_label = QLabel(title)
        title_label.setObjectName("metric-title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Valor
        self.value_label = QLabel(value)
        self.value_label.setObjectName("metric-value")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Unidade
        unit_label = QLabel(unit)
        unit_label.setObjectName("metric-unit")
        unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(unit_label)
        
        # Aplica cor de fundo
        self.setStyleSheet(f"""
            QFrame#metric-card {{
                background-color: {color}15;
                border: 2px solid {color}30;
                border-radius: 16px;
                padding: 16px;
            }}
            
            QFrame#metric-card:hover {{
                background-color: {color}25;
                border-color: {color}50;
            }}
            
            QLabel#metric-title {{
                color: #2C3E50;
                font-size: 14px;
                font-weight: 600;
                background-color: transparent;
                border: none;
            }}
            
            QLabel#metric-value {{
                color: {color};
                font-size: 24px;
                font-weight: 700;
                background-color: transparent;
                border: none;
            }}
            
            QLabel#metric-unit {{
                color: #7F8C8D;
                font-size: 12px;
                font-weight: 500;
                background-color: transparent;
                border: none;
            }}
        """)
    
    def update_value(self, value: str):
        """Atualiza o valor da métrica."""
        self.value_label.setText(value)

class ModernTelemetryWidget(QWidget):
    """Widget principal de telemetria moderno e funcional."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Telemetria Avançada")
        self.setMinimumSize(1600, 1000)
        
        # Configura o layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        
        # Configura o estilo moderno
        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA;
                color: #2C3E50;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            
            QFrame#header {
                background-color: #FFFFFF;
                border: 2px solid #E9ECEF;
                border-radius: 20px;
                padding: 20px;
            }
            
            QFrame#metrics-section {
                background-color: #FFFFFF;
                border: 2px solid #E9ECEF;
                border-radius: 20px;
                padding: 20px;
            }
            
            QFrame#graphs-section {
                background-color: #FFFFFF;
                border: 2px solid #E9ECEF;
                border-radius: 20px;
                padding: 20px;
            }
            
            QFrame#analysis-section {
                background-color: #FFFFFF;
                border: 2px solid #E9ECEF;
                border-radius: 20px;
                padding: 20px;
            }
            
            QLabel#title {
                font-size: 28px;
                font-weight: 700;
                color: #2C3E50;
                background-color: transparent;
                border: none;
                padding: 8px;
            }
            
            QLabel#subtitle {
                font-size: 16px;
                font-weight: 500;
                color: #7F8C8D;
                background-color: transparent;
                border: none;
                padding: 4px;
            }
            
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }
            
            QPushButton:hover {
                background-color: #2980B9;
            }
            
            QPushButton:pressed {
                background-color: #21618C;
            }
            
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
            
            QTabWidget::pane {
                border: 2px solid #E9ECEF;
                border-radius: 16px;
                background-color: #FFFFFF;
            }
            
            QTabBar::tab {
                background-color: #F8F9FA;
                color: #2C3E50;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                font-weight: 600;
            }
            
            QTabBar::tab:selected {
                background-color: #3498DB;
                color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #2980B9;
                color: white;
            }
        """)
        
        self._setup_header()
        self._setup_metrics()
        self._setup_graphs()
        self._setup_analysis()
        
        # Dados de telemetria
        self.telemetry_data = None
        self.current_lap = 0
        
        logger.info("ModernTelemetryWidget inicializado com sucesso")
        
    def _setup_header(self):
        """Configura o cabeçalho moderno."""
        header_frame = QFrame()
        header_frame.setObjectName("header")
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(20)
        
        # Título e subtítulo
        title_layout = QVBoxLayout()
        title_label = QLabel("📊 Análise de Telemetria Avançada")
        title_label.setObjectName("title")
        
        subtitle_label = QLabel("Visualização em tempo real e análise detalhada")
        subtitle_label.setObjectName("subtitle")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Status
        self.status_label = QLabel("Pronto para análise")
        self.status_label.setObjectName("subtitle")
        
        # Botões de controle
        self.play_button = QPushButton("▶️ Reproduzir")
        self.play_button.clicked.connect(self.play_telemetry)
        
        self.pause_button = QPushButton("⏸️ Pausar")
        self.pause_button.clicked.connect(self.pause_telemetry)
        self.pause_button.setEnabled(False)
        
        self.stop_button = QPushButton("⏹️ Parar")
        self.stop_button.clicked.connect(self.stop_telemetry)
        self.stop_button.setEnabled(False)
        
        # Adiciona widgets ao layout
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        header_layout.addWidget(self.play_button)
        header_layout.addWidget(self.pause_button)
        header_layout.addWidget(self.stop_button)
        
        self.main_layout.addWidget(header_frame)

    def _setup_metrics(self):
        """Configura a seção de métricas modernas."""
        metrics_frame = QFrame()
        metrics_frame.setObjectName("metrics-section")
        
        metrics_layout = QVBoxLayout(metrics_frame)
        
        # Título da seção
        section_title = QLabel("📈 Métricas em Tempo Real")
        section_title.setObjectName("title")
        metrics_layout.addWidget(section_title)
        
        # Grid de métricas
        metrics_grid = QHBoxLayout()
        metrics_grid.setSpacing(16)
        
        # Cria cards de métricas
        self.speed_card = MetricCard("Velocidade", "0.0", "km/h", "#E74C3C")
        self.rpm_card = MetricCard("RPM", "0", "rpm", "#F39C12")
        self.gear_card = MetricCard("Marcha", "N", "", "#3498DB")
        self.best_lap_card = MetricCard("Melhor Volta", "0.000", "s", "#27AE60")
        self.current_lap_card = MetricCard("Volta Atual", "0.000", "s", "#9B59B6")
        self.throttle_card = MetricCard("Acelerador", "0", "%", "#E67E22")
        self.brake_card = MetricCard("Freio", "0", "%", "#C0392B")
        self.clutch_card = MetricCard("Embreagem", "0", "%", "#8E44AD")
        
        # Adiciona cards ao grid
        metrics_grid.addWidget(self.speed_card)
        metrics_grid.addWidget(self.rpm_card)
        metrics_grid.addWidget(self.gear_card)
        metrics_grid.addWidget(self.best_lap_card)
        metrics_grid.addWidget(self.current_lap_card)
        metrics_grid.addWidget(self.throttle_card)
        metrics_grid.addWidget(self.brake_card)
        metrics_grid.addWidget(self.clutch_card)
        
        metrics_layout.addLayout(metrics_grid)
        self.main_layout.addWidget(metrics_frame)

    def _setup_graphs(self):
        """Configura os gráficos modernos."""
        graphs_frame = QFrame()
        graphs_frame.setObjectName("graphs-section")
        
        graphs_layout = QVBoxLayout(graphs_frame)
        
        # Título da seção
        section_title = QLabel("📊 Gráficos de Telemetria")
        section_title.setObjectName("title")
        graphs_layout.addWidget(section_title)
        
        # Configura cores dos gráficos
        self.graph_colors = {
            'throttle': '#E74C3C',      # Vermelho vibrante
            'brake': '#3498DB',         # Azul vibrante  
            'clutch': '#F39C12',        # Laranja vibrante
            'speed': '#27AE60',         # Verde vibrante
            'rpm': '#9B59B6',           # Roxo vibrante
            'actual_line': '#E74C3C',   # Linha atual
            'ideal_line': '#27AE60',    # Linha ideal
            'current_line': '#3498DB'   # Linha atual
        }
        
        # Cria os gráficos de controle
        self.throttle_plot = ModernTelemetryGraph("Acelerador")
        self.brake_plot = ModernTelemetryGraph("Freio")
        self.clutch_plot = ModernTelemetryGraph("Embreagem")
        self.speed_plot = ModernTelemetryGraph("Velocidade")
        
        # Layout horizontal para os gráficos de controle
        control_graphs_layout = QHBoxLayout()
        control_graphs_layout.addWidget(self.throttle_plot)
        control_graphs_layout.addWidget(self.brake_plot)
        control_graphs_layout.addWidget(self.clutch_plot)
        control_graphs_layout.addWidget(self.speed_plot)
        
        # Cria o mapa da pista
        self.track_map = ModernTrackMap()
        
        # Layout para gráficos e mapa
        graphs_and_map_layout = QHBoxLayout()
        graphs_and_map_layout.addLayout(control_graphs_layout, 3)  # 3/4 do espaço
        graphs_and_map_layout.addWidget(self.track_map, 1)         # 1/4 do espaço
        
        graphs_layout.addLayout(graphs_and_map_layout)
        self.main_layout.addWidget(graphs_frame)

    def _setup_analysis(self):
        """Configura a seção de análise."""
        analysis_frame = QFrame()
        analysis_frame.setObjectName("analysis-section")
        
        analysis_layout = QVBoxLayout(analysis_frame)
        
        # Título da seção
        section_title = QLabel("🔍 Análise Detalhada")
        section_title.setObjectName("title")
        analysis_layout.addWidget(section_title)
        
        # Tabs para diferentes análises
        self.analysis_tabs = QTabWidget()
        
        # Tab de análise de setores
        sectors_widget = QWidget()
        sectors_layout = QVBoxLayout(sectors_widget)
        self.sectors_text = QTextEdit()
        self.sectors_text.setReadOnly(True)
        self.sectors_text.setMaximumHeight(200)
        sectors_layout.addWidget(self.sectors_text)
        
        # Tab de análise de frenagem
        braking_widget = QWidget()
        braking_layout = QVBoxLayout(braking_widget)
        self.braking_text = QTextEdit()
        self.braking_text.setReadOnly(True)
        self.braking_text.setMaximumHeight(200)
        braking_layout.addWidget(self.braking_text)
        
        # Tab de análise de aceleração
        acceleration_widget = QWidget()
        acceleration_layout = QVBoxLayout(acceleration_widget)
        self.acceleration_text = QTextEdit()
        self.acceleration_text.setReadOnly(True)
        self.acceleration_text.setMaximumHeight(200)
        acceleration_layout.addWidget(self.acceleration_text)
        
        # Tab de análise de curvas
        cornering_widget = QWidget()
        cornering_layout = QVBoxLayout(cornering_widget)
        self.cornering_text = QTextEdit()
        self.cornering_text.setReadOnly(True)
        self.cornering_text.setMaximumHeight(200)
        cornering_layout.addWidget(self.cornering_text)
        
        # Adiciona tabs
        self.analysis_tabs.addTab(sectors_widget, "Setores")
        self.analysis_tabs.addTab(braking_widget, "Frenagem")
        self.analysis_tabs.addTab(acceleration_widget, "Aceleração")
        self.analysis_tabs.addTab(cornering_widget, "Curvas")
        
        analysis_layout.addWidget(self.analysis_tabs)
        self.main_layout.addWidget(analysis_frame)

    def load_telemetry_data(self, data: Dict[str, Any]):
        """Carrega dados de telemetria no widget."""
        logger.info("Carregando dados de telemetria...")
        
        try:
            self.telemetry_data = data
            
            if not data:
                logger.warning("Dados de telemetria vazios")
                self.status_label.setText("Nenhum dado carregado")
                return
            
            # Converte dados do parser CSV para DataFrame se necessário
            if 'data_points' in data and data['data_points'] and 'data' not in data:
                import pandas as pd
                df = pd.DataFrame(data['data_points'])
                data['data'] = df
                logger.info(f"Convertido {len(data['data_points'])} pontos de dados para DataFrame")
            
            # Atualiza a interface
            self.update_ui()
            
            # Atualiza métricas se houver dados
            if 'beacons' in data and data['beacons']:
                self._update_metrics_from_beacons(data['beacons'])
            elif 'data' in data and isinstance(data['data'], pd.DataFrame):
                self._update_metrics_from_dataframe(data['data'])
            elif 'data_points' in data and data['data_points']:
                # Usa os data_points diretamente se não houver DataFrame
                self._update_metrics_from_data_points(data['data_points'])
            
            # Atualiza gráficos
            self.update_control_graphs()
            
            # Atualiza mapa
            self.update_track_map()
            
            logger.info("Dados de telemetria carregados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados de telemetria: {e}")
            self.status_label.setText("Erro ao carregar dados")

    def _update_metrics_from_data_points(self, data_points: List[Dict[str, Any]]):
        """Atualiza métricas a partir dos data_points."""
        if not data_points:
            return
            
        try:
            # Pega o último ponto para dados atuais
            latest = data_points[-1]
            
            # Atualiza valores
            if 'SPEED' in latest:
                speed = latest['SPEED']
                self.speed_card.update_value(f"{speed:.1f}")
            
            if 'RPMS' in latest:
                rpm = latest['RPMS']
                self.rpm_card.update_value(f"{rpm:.0f}")
            
            if 'GEAR' in latest:
                gear = latest['GEAR']
                gear_text = str(int(gear)) if gear > 0 else "N" if gear == 0 else "R"
                self.gear_card.update_value(gear_text)
            
            if 'THROTTLE' in latest:
                throttle = latest['THROTTLE']
                self.throttle_card.update_value(f"{throttle:.0f}")
            
            if 'BRAKE' in latest:
                brake = latest['BRAKE']
                self.brake_card.update_value(f"{brake:.0f}")
            
            if 'CLUTCH' in latest:
                clutch = latest['CLUTCH']
                self.clutch_card.update_value(f"{clutch:.0f}")
            
            # Calcula melhor tempo se houver dados de voltas
            if hasattr(self, 'telemetry_data') and self.telemetry_data:
                laps = self.telemetry_data.get('laps', [])
                if laps:
                    times = [lap.get('lap_time', 0) for lap in laps if lap.get('lap_time', 0) > 0]
                    if times:
                        best_time = min(times)
                        self.best_lap_card.update_value(f"{best_time:.3f}")
            
            logger.info("Métricas atualizadas a partir dos data_points")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar métricas dos data_points: {e}")

    def update_control_graphs(self):
        """Atualiza os gráficos de controle com dados reais."""
        if not self.telemetry_data:
            return
            
        try:
            # Limpa gráficos existentes
            self.throttle_plot.clear()
            self.brake_plot.clear()
            self.clutch_plot.clear()
            self.speed_plot.clear()
            
            # Obtém dados
            df = None
            if 'data' in self.telemetry_data and isinstance(self.telemetry_data['data'], pd.DataFrame):
                df = self.telemetry_data['data']
            elif 'data_points' in self.telemetry_data and self.telemetry_data['data_points']:
                # Converte data_points para DataFrame
                df = pd.DataFrame(self.telemetry_data['data_points'])
            
            if df is None or df.empty:
                logger.warning("Nenhum dado disponível para gráficos")
                return
            
            # Verifica se temos colunas de tempo
            time_col = None
            for col in ['Time', 'time', 'TIME']:
                if col in df.columns:
                    time_col = col
                    break
            
            if time_col is None:
                # Cria um array de tempo baseado no índice
                time_data = np.arange(len(df))
            else:
                time_data = df[time_col].values
            
            # Plota throttle
            throttle_col = None
            for col in ['THROTTLE', 'Throttle', 'throttle']:
                if col in df.columns:
                    throttle_col = col
                    break
            
            if throttle_col:
                throttle_data = df[throttle_col].values
                valid_mask = ~pd.isna(throttle_data)
                if np.any(valid_mask):
                    valid_time = time_data[valid_mask]
                    valid_throttle = throttle_data[valid_mask]
                    self.throttle_plot.plot(valid_time, valid_throttle, 
                                          pen=pg.mkPen(color=self.graph_colors['throttle'], width=3),
                                          name='Acelerador')
            
            # Plota brake
            brake_col = None
            for col in ['BRAKE', 'Brake', 'brake']:
                if col in df.columns:
                    brake_col = col
                    break
            
            if brake_col:
                brake_data = df[brake_col].values
                valid_mask = ~pd.isna(brake_data)
                if np.any(valid_mask):
                    valid_time = time_data[valid_mask]
                    valid_brake = brake_data[valid_mask]
                    self.brake_plot.plot(valid_time, valid_brake, 
                                       pen=pg.mkPen(color=self.graph_colors['brake'], width=3),
                                       name='Freio')
            
            # Plota clutch
            clutch_col = None
            for col in ['CLUTCH', 'Clutch', 'clutch']:
                if col in df.columns:
                    clutch_col = col
                    break
            
            if clutch_col:
                clutch_data = df[clutch_col].values
                valid_mask = ~pd.isna(clutch_data)
                if np.any(valid_mask):
                    valid_time = time_data[valid_mask]
                    valid_clutch = clutch_data[valid_mask]
                    self.clutch_plot.plot(valid_time, valid_clutch, 
                                        pen=pg.mkPen(color=self.graph_colors['clutch'], width=3),
                                        name='Embreagem')
            
            # Plota speed
            speed_col = None
            for col in ['SPEED', 'Speed', 'speed']:
                if col in df.columns:
                    speed_col = col
                    break
            
            if speed_col:
                speed_data = df[speed_col].values
                valid_mask = ~pd.isna(speed_data)
                if np.any(valid_mask):
                    valid_time = time_data[valid_mask]
                    valid_speed = speed_data[valid_mask]
                    self.speed_plot.plot(valid_time, valid_speed, 
                                       pen=pg.mkPen(color=self.graph_colors['speed'], width=3),
                                       name='Velocidade')
            
            logger.info("Gráficos de controle atualizados")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar gráficos de controle: {e}")

    def update_track_map(self):
        """Atualiza o mapa da pista."""
        if not self.telemetry_data:
            return
            
        try:
            # Limpa mapa existente
            self.track_map.clear()
            
            # Obtém dados de posição
            df = None
            if 'data' in self.telemetry_data and isinstance(self.telemetry_data['data'], pd.DataFrame):
                df = self.telemetry_data['data']
            elif 'data_points' in self.telemetry_data and self.telemetry_data['data_points']:
                df = pd.DataFrame(self.telemetry_data['data_points'])
            
            if df is None or df.empty:
                return
            
            # Procura colunas de posição - para telemetria de simulação, pode usar G_LAT e G_LON
            x_col = None
            y_col = None
            
            # Primeiro tenta coordenadas GPS
            for col in ['X', 'x', 'Longitude', 'longitude', 'G_LON']:
                if col in df.columns:
                    x_col = col
                    break
            
            for col in ['Y', 'y', 'Latitude', 'latitude', 'G_LAT']:
                if col in df.columns:
                    y_col = col
                    break
            
            if x_col and y_col:
                x_data = df[x_col].values
                y_data = df[y_col].values
                
                # Remove valores NaN
                valid_mask = ~(np.isnan(x_data) | np.isnan(y_data))
                if np.any(valid_mask):
                    x_valid = x_data[valid_mask]
                    y_valid = y_data[valid_mask]
                    
                    # Plota o traçado
                    self.track_map.plot(x_valid, y_valid, 
                                      pen=pg.mkPen(color=self.graph_colors['actual_line'], width=4),
                                      name='Traçado Atual')
                    
                    logger.info("Mapa da pista atualizado")
                
        except Exception as e:
            logger.error(f"Erro ao atualizar mapa da pista: {e}")

    def update_ui(self):
        """Atualiza a interface com os dados carregados."""
        if not self.telemetry_data:
            return
            
        try:
            # Atualiza informações básicas
            metadata = self.telemetry_data.get('metadata', {})
            filename = metadata.get('filename', 'Arquivo desconhecido')
            
            # Atualiza status
            self.status_label.setText(f"Arquivo carregado: {filename}")
            
            # Atualiza gráficos
            self.update_control_graphs()
            
            # Atualiza mapa
            self.update_track_map()
            
            # Atualiza análises
            self.update_analysis()
            
            logger.info("UI atualizada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar UI: {e}")
            self.status_label.setText("Erro ao atualizar interface")
        
    def update_analysis(self):
        """Atualiza as análises com dados reais."""
        if not self.telemetry_data:
            return
            
        try:
            # Análise de setores (baseada em dados reais)
            laps = self.telemetry_data.get('laps', [])
            if laps:
                total_laps = len(laps)
                times = [lap.get('lap_time', 0) for lap in laps if lap.get('lap_time', 0) > 0]
                if times:
                    avg_time = sum(times) / len(times)
                    best_time = min(times)
                    worst_time = max(times)
                    
                    sectors_analysis = f"""
                    📊 Análise de Setores:
                    
                    • Total de voltas: {total_laps}
                    • Melhor volta: {best_time:.3f}s
                    • Pior volta: {worst_time:.3f}s
                    • Tempo médio: {avg_time:.3f}s
                    • Consistência: {((best_time/avg_time)*100):.1f}%
                    
                    🎯 Foco: Melhorar consistência entre voltas
                    """
                else:
                    sectors_analysis = "📊 Análise de Setores:\n\nNenhum tempo de volta válido encontrado."
            else:
                sectors_analysis = "📊 Análise de Setores:\n\nNenhuma volta identificada nos dados."
            
            self.sectors_text.setText(sectors_analysis)
            
            # Análise de frenagem (baseada em dados reais)
            df = None
            if 'data' in self.telemetry_data and isinstance(self.telemetry_data['data'], pd.DataFrame):
                df = self.telemetry_data['data']
            elif 'data_points' in self.telemetry_data and self.telemetry_data['data_points']:
                df = pd.DataFrame(self.telemetry_data['data_points'])
            
            if df is not None and not df.empty:
                brake_col = None
                for col in ['BRAKE', 'Brake', 'brake']:
                    if col in df.columns:
                        brake_col = col
                        break
                
                if brake_col:
                    brake_data = df[brake_col].dropna()
                    if not brake_data.empty:
                        avg_brake = brake_data.mean()
                        max_brake = brake_data.max()
                        brake_usage = (brake_data > 10).sum() / len(brake_data) * 100
                        
                        braking_analysis = f"""
                        🛑 Análise de Frenagem:
                        
                        • Frenagem média: {avg_brake:.1f}%
                        • Frenagem máxima: {max_brake:.1f}%
                        • Uso de freio: {brake_usage:.1f}% do tempo
                        • Pontos de frenagem: {(brake_data > 50).sum()}
                        
                        💡 Dica: {'Reduzir frenagem excessiva' if avg_brake > 60 else 'Frenagem adequada'}
                        """
                    else:
                        braking_analysis = "🛑 Análise de Frenagem:\n\nNenhum dado de frenagem válido."
                else:
                    braking_analysis = "🛑 Análise de Frenagem:\n\nDados de frenagem não encontrados."
            else:
                braking_analysis = "🛑 Análise de Frenagem:\n\nNenhum dado disponível."
            
            self.braking_text.setText(braking_analysis)
            
            # Análise de aceleração
            if df is not None and not df.empty:
                throttle_col = None
                for col in ['THROTTLE', 'Throttle', 'throttle']:
                    if col in df.columns:
                        throttle_col = col
                        break
                
                if throttle_col:
                    throttle_data = df[throttle_col].dropna()
                    if not throttle_data.empty:
                        avg_throttle = throttle_data.mean()
                        max_throttle = throttle_data.max()
                        throttle_usage = (throttle_data > 10).sum() / len(throttle_data) * 100
                        
                        acceleration_analysis = f"""
                        🚀 Análise de Aceleração:
                        
                        • Aceleração média: {avg_throttle:.1f}%
                        • Aceleração máxima: {max_throttle:.1f}%
                        • Uso do acelerador: {throttle_usage:.1f}% do tempo
                        • Pontos de aceleração: {(throttle_data > 80).sum()}
                        
                        💡 Dica: {'Ser mais agressivo na saída das curvas' if avg_throttle < 50 else 'Aceleração adequada'}
                        """
                    else:
                        acceleration_analysis = "🚀 Análise de Aceleração:\n\nNenhum dado de aceleração válido."
                else:
                    acceleration_analysis = "🚀 Análise de Aceleração:\n\nDados de aceleração não encontrados."
            else:
                acceleration_analysis = "🚀 Análise de Aceleração:\n\nNenhum dado disponível."
            
            self.acceleration_text.setText(acceleration_analysis)
            
            # Análise de curva
            if df is not None and not df.empty:
                speed_col = None
                for col in ['SPEED', 'Speed', 'speed']:
                    if col in df.columns:
                        speed_col = col
                        break
                
                if speed_col:
                    speed_data = df[speed_col].dropna()
                    if not speed_data.empty:
                        avg_speed = speed_data.mean()
                        max_speed = speed_data.max()
                        min_speed = speed_data.min()
                        
                        cornering_analysis = f"""
                        🏁 Análise de Curvas:
                        
                        • Velocidade média: {avg_speed:.1f} km/h
                        • Velocidade máxima: {max_speed:.1f} km/h
                        • Velocidade mínima: {min_speed:.1f} km/h
                        • Variação de velocidade: {max_speed - min_speed:.1f} km/h
                        
                        💡 Dica: {'Melhorar linha de corrida' if (max_speed - min_speed) > 100 else 'Linha de corrida adequada'}
                        """
                    else:
                        cornering_analysis = "🏁 Análise de Curvas:\n\nNenhum dado de velocidade válido."
                else:
                    cornering_analysis = "🏁 Análise de Curvas:\n\nDados de velocidade não encontrados."
            else:
                cornering_analysis = "🏁 Análise de Curvas:\n\nNenhum dado disponível."
            
            self.cornering_text.setText(cornering_analysis)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar análises: {e}")
    
    def update_realtime_telemetry(self, data: Dict[str, Any]):
        """Atualiza com dados de telemetria em tempo real."""
        # Implementar quando necessário
        pass

    def play_telemetry(self):
        """Implementa a lógica para reproduzir a telemetria."""
        # Implementar quando necessário
        pass

    def pause_telemetry(self):
        """Implementa a lógica para pausar a telemetria."""
        # Implementar quando necessário
        pass

    def stop_telemetry(self):
        """Implementa a lógica para parar a telemetria."""
        # Implementar quando necessário
        pass
