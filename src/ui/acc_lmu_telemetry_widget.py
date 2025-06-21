"""
Widget especializado para análise de telemetria de ACC e LMU.
Focado em ajudar pilotos virtuais a melhorar sua performance.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QGridLayout, QSizePolicy, QTextEdit, QListWidget, 
    QListWidgetItem, QSlider, QSpinBox, QPushButton, QComboBox,
    QProgressBar, QFrame, QSplitter
)
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QTimer
from typing import Dict, List, Any, Optional
import pyqtgraph as pg
import numpy as np

from src.ui.modern_dashboard_widget import ModernCard
from src.analysis.track_detection import TrackAnalyzer

import logging

logger = logging.getLogger(__name__)

class RealTimeDataWidget(QWidget):
    """Widget para exibir dados de telemetria em tempo real."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """Configura a interface para dados em tempo real."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("Telemetria em Tempo Real")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #0078d4;
                padding: 8px;
                border-bottom: 2px solid #0078d4;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(header)
        
        # Grid de métricas em tempo real
        metrics_grid = QGridLayout()
        
        # Velocidade
        self.speed_card = self.create_metric_card("Velocidade", "0", "km/h", "#10b981")
        metrics_grid.addWidget(self.speed_card, 0, 0)
        
        # RPM
        self.rpm_card = self.create_metric_card("RPM", "0", "rpm", "#f59e0b")
        metrics_grid.addWidget(self.rpm_card, 0, 1)
        
        # Marcha
        self.gear_card = self.create_metric_card("Marcha", "N", "", "#8b5cf6")
        metrics_grid.addWidget(self.gear_card, 0, 2)
        
        # Acelerador
        self.throttle_card = self.create_metric_card("Acelerador", "0", "%", "#ef4444")
        metrics_grid.addWidget(self.throttle_card, 1, 0)
        
        # Freio
        self.brake_card = self.create_metric_card("Freio", "0", "%", "#dc2626")
        metrics_grid.addWidget(self.brake_card, 1, 1)
        
        # Direção
        self.steering_card = self.create_metric_card("Direção", "0", "°", "#06b6d4")
        metrics_grid.addWidget(self.steering_card, 1, 2)
        
        # G-Force Lateral
        self.g_lat_card = self.create_metric_card("G Lateral", "0.0", "g", "#84cc16")
        metrics_grid.addWidget(self.g_lat_card, 2, 0)
        
        # G-Force Longitudinal
        self.g_long_card = self.create_metric_card("G Longitudinal", "0.0", "g", "#f97316")
        metrics_grid.addWidget(self.g_long_card, 2, 1)
        
        # Tempo de Volta Atual
        self.lap_time_card = self.create_metric_card("Tempo de Volta", "00:00.000", "", "#3b82f6")
        metrics_grid.addWidget(self.lap_time_card, 2, 2)
        
        layout.addLayout(metrics_grid)
        
        # Gráfico de G-Force em tempo real
        self.g_force_plot = pg.PlotWidget(title="Forças G em Tempo Real")
        self.g_force_plot.setLabel('left', 'G-Force')
        self.g_force_plot.setLabel('bottom', 'Tempo (s)')
        self.g_force_plot.setMinimumHeight(200)
        
        # Curvas para G lateral e longitudinal
        self.g_lat_curve = self.g_force_plot.plot(pen=pg.mkPen(color='#84cc16', width=2), name='G Lateral')
        self.g_long_curve = self.g_force_plot.plot(pen=pg.mkPen(color='#f97316', width=2), name='G Longitudinal')
        
        # Dados para os gráficos
        self.g_lat_data = []
        self.g_long_data = []
        self.time_data = []
        self.max_points = 300  # 5 minutos a 60Hz
        
        layout.addWidget(self.g_force_plot)
        
    def create_metric_card(self, title: str, value: str, unit: str, color: str) -> QWidget:
        """Cria um card para exibir uma métrica."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 8px;
            }}
            QFrame:hover {{
                border-color: {color};
                background-color: #363636;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setObjectName("value_label")
        
        unit_label = QLabel(unit)
        unit_label.setStyleSheet("color: #cccccc; font-size: 10px;")
        unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(unit_label)
        
        return card
        
    def setup_timer(self):
        """Configura o timer para atualização dos dados."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plots)
        self.update_timer.start(50)  # 20Hz
        
    def update_metric_card(self, card: QWidget, value: str):
        """Atualiza o valor de um card de métrica."""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)
            
    @pyqtSlot(dict)
    def update_realtime_data(self, data: Dict[str, Any]):
        """Atualiza os dados em tempo real."""
        # Atualiza cards de métricas
        self.update_metric_card(self.speed_card, f"{data.get('speed', 0):.0f}")
        self.update_metric_card(self.rpm_card, f"{data.get('rpm', 0):.0f}")
        self.update_metric_card(self.gear_card, str(data.get('gear', 'N')))
        self.update_metric_card(self.throttle_card, f"{data.get('throttle', 0):.0f}")
        self.update_metric_card(self.brake_card, f"{data.get('brake', 0):.0f}")
        self.update_metric_card(self.steering_card, f"{data.get('steering', 0):.1f}")
        self.update_metric_card(self.g_lat_card, f"{data.get('g_lat', 0):.2f}")
        self.update_metric_card(self.g_long_card, f"{data.get('g_long', 0):.2f}")
        
        # Formatar tempo de volta
        lap_time = data.get('lap_time', 0)
        if lap_time > 0:
            minutes = int(lap_time // 60)
            seconds = lap_time % 60
            lap_time_str = f"{minutes:02d}:{seconds:06.3f}"
        else:
            lap_time_str = "00:00.000"
        self.update_metric_card(self.lap_time_card, lap_time_str)
        
        # Atualiza dados dos gráficos
        current_time = data.get('time', 0)
        self.time_data.append(current_time)
        self.g_lat_data.append(data.get('g_lat', 0))
        self.g_long_data.append(data.get('g_long', 0))
        
        # Limita o número de pontos
        if len(self.time_data) > self.max_points:
            self.time_data.pop(0)
            self.g_lat_data.pop(0)
            self.g_long_data.pop(0)
            
    def update_plots(self):
        """Atualiza os gráficos."""
        if len(self.time_data) > 1:
            self.g_lat_curve.setData(self.time_data, self.g_lat_data)
            self.g_long_curve.setData(self.time_data, self.g_long_data)

class DriverCoachWidget(QWidget):
    """Widget de coaching para pilotos virtuais."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do coach virtual."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("Coach Virtual")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #10b981;
                padding: 8px;
                border-bottom: 2px solid #10b981;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(header)
        
        # Tabs para diferentes tipos de coaching
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #363636;
                border: 1px solid #404040;
                border-bottom-color: #404040;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 8ex;
                padding: 6px 12px;
                color: #cccccc;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: #2b2b2b;
                border-color: #10b981;
                border-bottom-color: #2b2b2b;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background: #404040;
            }
        """)
        
        # Aba de Dicas em Tempo Real
        self.realtime_tips_tab = QWidget()
        self.setup_realtime_tips_tab()
        self.tab_widget.addTab(self.realtime_tips_tab, "Dicas em Tempo Real")
        
        # Aba de Análise de Setor
        self.sector_analysis_tab = QWidget()
        self.setup_sector_analysis_tab()
        self.tab_widget.addTab(self.sector_analysis_tab, "Análise de Setor")
        
        # Aba de Comparação com Referência
        self.reference_comparison_tab = QWidget()
        self.setup_reference_comparison_tab()
        self.tab_widget.addTab(self.reference_comparison_tab, "Comparação")
        
        layout.addWidget(self.tab_widget)
        
    def setup_realtime_tips_tab(self):
        """Configura a aba de dicas em tempo real."""
        layout = QVBoxLayout(self.realtime_tips_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Lista de dicas ativas
        self.tips_list = QListWidget()
        self.tips_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 8px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:hover {
                background-color: #363636;
            }
        """)
        layout.addWidget(self.tips_list)
        
        # Adiciona algumas dicas de exemplo
        self.add_tip("🏁 Mantenha uma linha consistente", "info")
        self.add_tip("⚠️ Frenagem muito agressiva detectada", "warning")
        self.add_tip("✅ Boa saída de curva!", "success")
        
    def setup_sector_analysis_tab(self):
        """Configura a aba de análise de setor."""
        layout = QVBoxLayout(self.sector_analysis_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Seletor de setor
        sector_layout = QHBoxLayout()
        sector_layout.addWidget(QLabel("Setor:"))
        
        self.sector_combo = QComboBox()
        self.sector_combo.addItems(["Setor 1", "Setor 2", "Setor 3"])
        self.sector_combo.setStyleSheet("""
            QComboBox {
                background-color: #363636;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #cccccc;
            }
        """)
        sector_layout.addWidget(self.sector_combo)
        sector_layout.addStretch()
        
        layout.addLayout(sector_layout)
        
        # Gráfico de comparação de setor
        self.sector_plot = pg.PlotWidget(title="Análise de Setor")
        self.sector_plot.setLabel('left', 'Velocidade (km/h)')
        self.sector_plot.setLabel('bottom', 'Distância (m)')
        self.sector_plot.setMinimumHeight(200)
        
        layout.addWidget(self.sector_plot)
        
        # Métricas do setor
        metrics_layout = QGridLayout()
        
        self.sector_time_label = QLabel("Tempo: --:---.---")
        self.sector_time_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        metrics_layout.addWidget(self.sector_time_label, 0, 0)
        
        self.sector_speed_label = QLabel("Vel. Média: --- km/h")
        self.sector_speed_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        metrics_layout.addWidget(self.sector_speed_label, 0, 1)
        
        self.sector_delta_label = QLabel("Delta: +-.---")
        self.sector_delta_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        metrics_layout.addWidget(self.sector_delta_label, 1, 0)
        
        layout.addLayout(metrics_layout)
        
    def setup_reference_comparison_tab(self):
        """Configura a aba de comparação com referência."""
        layout = QVBoxLayout(self.reference_comparison_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Seletor de volta de referência
        ref_layout = QHBoxLayout()
        ref_layout.addWidget(QLabel("Volta de Referência:"))
        
        self.reference_combo = QComboBox()
        self.reference_combo.addItems(["Melhor Volta", "Volta Anterior", "Volta Personalizada"])
        self.reference_combo.setStyleSheet("""
            QComboBox {
                background-color: #363636;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
            }
        """)
        ref_layout.addWidget(self.reference_combo)
        ref_layout.addStretch()
        
        layout.addLayout(ref_layout)
        
        # Gráfico de comparação
        self.comparison_plot = pg.PlotWidget(title="Comparação de Voltas")
        self.comparison_plot.setLabel('left', 'Delta (s)')
        self.comparison_plot.setLabel('bottom', 'Distância (%)')
        self.comparison_plot.setMinimumHeight(200)
        
        # Linha de referência (delta = 0)
        self.comparison_plot.addLine(y=0, pen=pg.mkPen(color='#666666', style=Qt.PenStyle.DashLine))
        
        layout.addWidget(self.comparison_plot)
        
        # Resumo da comparação
        summary_layout = QGridLayout()
        
        self.delta_total_label = QLabel("Delta Total: +-.---")
        self.delta_total_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        summary_layout.addWidget(self.delta_total_label, 0, 0, 1, 2)
        
        self.delta_s1_label = QLabel("S1: +-.---")
        self.delta_s1_label.setStyleSheet("color: #cccccc;")
        summary_layout.addWidget(self.delta_s1_label, 1, 0)
        
        self.delta_s2_label = QLabel("S2: +-.---")
        self.delta_s2_label.setStyleSheet("color: #cccccc;")
        summary_layout.addWidget(self.delta_s2_label, 1, 1)
        
        self.delta_s3_label = QLabel("S3: +-.---")
        self.delta_s3_label.setStyleSheet("color: #cccccc;")
        summary_layout.addWidget(self.delta_s3_label, 2, 0)
        
        layout.addLayout(summary_layout)
        
    def add_tip(self, message: str, tip_type: str = "info"):
        """Adiciona uma dica à lista."""
        item = QListWidgetItem(message)
        
        if tip_type == "warning":
            item.setBackground(QColor("#fbbf24"))
            item.setForeground(QColor("#000000"))
        elif tip_type == "success":
            item.setBackground(QColor("#10b981"))
            item.setForeground(QColor("#000000"))
        else:  # info
            item.setBackground(QColor("#3b82f6"))
            item.setForeground(QColor("#ffffff"))
            
        self.tips_list.insertItem(0, item)
        
        # Limita a 10 dicas
        if self.tips_list.count() > 10:
            self.tips_list.takeItem(self.tips_list.count() - 1)

class TrackMapWidget(QWidget):
    """Widget para exibir o mapa da pista com posição do carro."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.track_analyzer = TrackAnalyzer()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do mapa da pista."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("Mapa da Pista")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #8b5cf6;
                padding: 8px;
                border-bottom: 2px solid #8b5cf6;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(header)
        
        # Widget de plotagem para o mapa
        self.track_plot = pg.PlotWidget()
        self.track_plot.setAspectLocked(True)
        self.track_plot.setLabel('left', 'Y (m)')
        self.track_plot.setLabel('bottom', 'X (m)')
        self.track_plot.setMinimumHeight(300)
        
        # Remove os eixos para um visual mais limpo
        self.track_plot.hideAxis('left')
        self.track_plot.hideAxis('bottom')
        self.track_plot.setBackground('#1e1e1e')
        
        layout.addWidget(self.track_plot)
        
        # Controles
        controls_layout = QHBoxLayout()
        
        self.zoom_fit_btn = QPushButton("Ajustar Zoom")
        self.zoom_fit_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
            QPushButton:pressed {
                background-color: #6d28d9;
            }
        """)
        self.zoom_fit_btn.clicked.connect(self.fit_track_view)
        controls_layout.addWidget(self.zoom_fit_btn)
        
        self.show_sectors_btn = QPushButton("Mostrar Setores")
        self.show_sectors_btn.setCheckable(True)
        self.show_sectors_btn.setStyleSheet("""
            QPushButton {
                background-color: #363636;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
            }
            QPushButton:checked {
                background-color: #8b5cf6;
                border-color: #8b5cf6;
            }
            QPushButton:hover {
                background-color: #404040;
            }
        """)
        controls_layout.addWidget(self.show_sectors_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Inicializa elementos do mapa
        self.track_line = None
        self.car_position = None
        self.sector_lines = []
        
    def load_track_data(self, telemetry_data: Dict[str, Any]):
        """Carrega dados da pista a partir da telemetria."""
        try:
            track_data = self.track_analyzer.extract_track_layout(telemetry_data)
            
            if track_data and track_data.get('coordinates'):
                coords = track_data['coordinates']
                x_coords = [point['x'] for point in coords]
                y_coords = [point['y'] for point in coords]
                
                # Desenha a linha da pista
                if self.track_line:
                    self.track_plot.removeItem(self.track_line)
                    
                self.track_line = self.track_plot.plot(
                    x_coords, y_coords,
                    pen=pg.mkPen(color='#ffffff', width=3),
                    name='Pista'
                )
                
                # Adiciona marcadores de setor se disponíveis
                if track_data.get('sectors'):
                    self.add_sector_markers(track_data['sectors'])
                    
                self.fit_track_view()
                
        except Exception as e:
            logger.error(f"Erro ao carregar dados da pista: {e}")
            
    def add_sector_markers(self, sectors: List[Dict[str, Any]]):
        """Adiciona marcadores de setor ao mapa."""
        colors = ['#ef4444', '#f59e0b', '#10b981']  # Vermelho, Amarelo, Verde
        
        for i, sector in enumerate(sectors):
            if 'start_point' in sector:
                point = sector['start_point']
                color = colors[i % len(colors)]
                
                marker = pg.ScatterPlotItem(
                    [point['x']], [point['y']],
                    pen=pg.mkPen(color=color, width=2),
                    brush=pg.mkBrush(color=color),
                    size=10,
                    symbol='o'
                )
                self.track_plot.addItem(marker)
                self.sector_lines.append(marker)
                
    def update_car_position(self, x: float, y: float):
        """Atualiza a posição do carro no mapa."""
        if self.car_position:
            self.track_plot.removeItem(self.car_position)
            
        self.car_position = pg.ScatterPlotItem(
            [x], [y],
            pen=pg.mkPen(color='#0078d4', width=3),
            brush=pg.mkBrush(color='#0078d4'),
            size=15,
            symbol='t'  # Triângulo para representar o carro
        )
        self.track_plot.addItem(self.car_position)
        
    def fit_track_view(self):
        """Ajusta a visualização para mostrar toda a pista."""
        if self.track_line:
            self.track_plot.autoRange()

class ACCLMUTelemetryWidget(QWidget):
    """Widget principal especializado para ACC e LMU."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface principal."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Painel esquerdo - Dados em tempo real e coach
        left_panel = QSplitter(Qt.Orientation.Vertical)
        
        self.realtime_widget = RealTimeDataWidget()
        self.coach_widget = DriverCoachWidget()
        
        left_panel.addWidget(self.realtime_widget)
        left_panel.addWidget(self.coach_widget)
        left_panel.setSizes([300, 400])
        
        # Painel direito - Mapa da pista
        self.track_map_widget = TrackMapWidget()
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(self.track_map_widget)
        main_splitter.setSizes([600, 400])
        
        layout.addWidget(main_splitter)
        
    @pyqtSlot(dict)
    def update_telemetry_data(self, data: Dict[str, Any]):
        """Atualiza todos os widgets com novos dados de telemetria."""
        # Atualiza dados em tempo real
        self.realtime_widget.update_realtime_data(data)
        
        # Atualiza posição no mapa se disponível
        if 'x' in data and 'y' in data:
            self.track_map_widget.update_car_position(data['x'], data['y'])
            
        # Adiciona dicas do coach baseadas nos dados
        self.update_coaching_tips(data)
        
    def update_coaching_tips(self, data: Dict[str, Any]):
        """Atualiza dicas do coach baseadas nos dados atuais."""
        # Exemplo de lógica de coaching
        speed = data.get('speed', 0)
        throttle = data.get('throttle', 0)
        brake = data.get('brake', 0)
        g_lat = abs(data.get('g_lat', 0))
        
        # Dica sobre aceleração
        if throttle > 90 and speed < 50:
            self.coach_widget.add_tip("⚠️ Cuidado com tração na saída!", "warning")
            
        # Dica sobre frenagem
        if brake > 95:
            self.coach_widget.add_tip("🔴 Frenagem no limite - risco de travamento", "warning")
            
        # Dica sobre força G
        if g_lat > 1.5:
            self.coach_widget.add_tip("🏎️ Excelente força G lateral!", "success")
            
    def load_track_data(self, telemetry_data: Dict[str, Any]):
        """Carrega dados da pista."""
        self.track_map_widget.load_track_data(telemetry_data)

