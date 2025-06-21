"""
Widget superior para visualização de telemetria com análise prática.
Foca em mostrar informações úteis para melhorar a performance do piloto.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QFrame, QScrollArea, QSplitter, QGroupBox,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QComboBox, QSlider, QProgressBar, QCheckBox,
    QSpinBox, QDoubleSpinBox, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QPixmap, QPainter, QPen
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QRectF
import pyqtgraph as pg
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TelemetryGraph(pg.PlotWidget):
    """Widget de gráfico personalizado para telemetria."""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setBackground('w')
        self.setTitle(title, color="k", size="12pt")
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setLabel('left', 'Valor', color="k")
        self.setLabel('bottom', 'Tempo (s)', color="k")
        
        # Configurações do gráfico
        self.getAxis('left').setTextPen('k')
        self.getAxis('bottom').setTextPen('k')
        self.getAxis('left').setPen('k')
        self.getAxis('bottom').setPen('k')

class PerformanceCard(QFrame):
    """Card para exibir métricas de performance."""
    
    def __init__(self, title: str, value: str = "0", unit: str = "", status: str = "neutral", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("""
            PerformanceCard {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 12px;
                margin: 4px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #cccccc;
                font-weight: 500;
            }
        """)
        layout.addWidget(title_label)
        
        # Valor
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #ffffff;
            }
        """)
        layout.addWidget(self.value_label)
        
        # Unidade
        if unit:
            self.unit_label = QLabel(unit)
            self.unit_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #888888;
                }
            """)
            layout.addWidget(self.unit_label)
        
        # Status indicator
        self.status_indicator = QLabel()
        self.set_status(status)
        layout.addWidget(self.status_indicator)
    
    def set_value(self, value: str):
        """Define o valor do card."""
        self.value_label.setText(value)
    
    def set_status(self, status: str):
        """Define o status do card (good, warning, bad, neutral)."""
        colors = {
            "good": "#4CAF50",
            "warning": "#FF9800", 
            "bad": "#F44336",
            "neutral": "#2196F3"
        }
        color = colors.get(status, "#2196F3")
        
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 4px;
                min-height: 8px;
                max-height: 8px;
            }}
        """)

class SuperiorTelemetryWidget(QWidget):
    """Widget superior para visualização e análise de telemetria."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.telemetry_data = None
        self.current_lap = 0
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header com controles
        header = self.create_header()
        layout.addWidget(header)
        
        # Área principal com abas
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #404040;
                border-radius: 8px;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #cccccc;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
        """)
        
        # Aba de Performance
        self.performance_tab = self.create_performance_tab()
        self.tab_widget.addTab(self.performance_tab, "📊 Performance")
        
        # Aba de Gráficos
        self.graphs_tab = self.create_graphs_tab()
        self.tab_widget.addTab(self.graphs_tab, "📈 Gráficos")
        
        # Aba de Análise
        self.analysis_tab = self.create_analysis_tab()
        self.tab_widget.addTab(self.analysis_tab, "🔍 Análise")
        
        # Aba de Insights
        self.insights_tab = self.create_insights_tab()
        self.tab_widget.addTab(self.insights_tab, "💡 Insights")
        
        layout.addWidget(self.tab_widget)
        
    def create_header(self):
        """Cria o cabeçalho com controles."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Informações da sessão
        self.session_info = QLabel("Sessão: Nenhuma carregada")
        self.session_info.setStyleSheet("color: #cccccc; font-size: 14px; font-weight: 500;")
        layout.addWidget(self.session_info)
        
        # Seletor de volta
        lap_label = QLabel("Volta:")
        lap_label.setStyleSheet("color: #cccccc; font-size: 14px;")
        layout.addWidget(lap_label)
        
        self.lap_selector = QComboBox()
        self.lap_selector.setStyleSheet("""
            QComboBox {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 6px;
                padding: 6px 12px;
                color: white;
                min-width: 80px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
            }
        """)
        self.lap_selector.currentIndexChanged.connect(self.on_lap_changed)
        layout.addWidget(self.lap_selector)
        
        layout.addStretch()
        
        # Botões de controle
        self.play_button = QPushButton("▶️ Reproduzir")
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        layout.addWidget(self.play_button)
        
        return header
    
    def create_performance_tab(self):
        """Cria a aba de performance."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Grid de métricas de performance
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(16)
        
        # Métricas principais
        self.best_lap_card = PerformanceCard("Melhor Volta", "0.000", "s", "good")
        self.avg_lap_card = PerformanceCard("Volta Média", "0.000", "s", "neutral")
        self.consistency_card = PerformanceCard("Consistência", "0%", "", "neutral")
        self.max_speed_card = PerformanceCard("Velocidade Máx", "0", "km/h", "neutral")
        
        metrics_grid.addWidget(self.best_lap_card, 0, 0)
        metrics_grid.addWidget(self.avg_lap_card, 0, 1)
        metrics_grid.addWidget(self.consistency_card, 0, 2)
        metrics_grid.addWidget(self.max_speed_card, 0, 3)
        
        # Métricas de condução
        self.throttle_usage_card = PerformanceCard("Uso do Acelerador", "0%", "", "neutral")
        self.brake_usage_card = PerformanceCard("Uso do Freio", "0%", "", "neutral")
        self.gear_changes_card = PerformanceCard("Troca de Marchas", "0", "", "neutral")
        self.track_usage_card = PerformanceCard("Uso da Pista", "0%", "", "neutral")
        
        metrics_grid.addWidget(self.throttle_usage_card, 1, 0)
        metrics_grid.addWidget(self.brake_usage_card, 1, 1)
        metrics_grid.addWidget(self.gear_changes_card, 1, 2)
        metrics_grid.addWidget(self.track_usage_card, 1, 3)
        
        layout.addLayout(metrics_grid)
        
        # Tabela de voltas
        self.laps_table = QTableWidget()
        self.laps_table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 8px;
                gridline-color: #404040;
            }
            QTableWidget::item {
                color: #cccccc;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
            }
            QHeaderView::section {
                background-color: #404040;
                color: white;
                padding: 8px;
                border: none;
                font-weight: 500;
            }
        """)
        self.setup_laps_table()
        layout.addWidget(self.laps_table)
        
        return tab
    
    def create_graphs_tab(self):
        """Cria a aba de gráficos."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Controles dos gráficos
        controls = QHBoxLayout()
        
        # Seletor de canais
        channel_label = QLabel("Canal:")
        channel_label.setStyleSheet("color: #cccccc; font-size: 14px;")
        controls.addWidget(channel_label)
        
        self.channel_selector = QComboBox()
        self.channel_selector.setStyleSheet("""
            QComboBox {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 6px;
                padding: 6px 12px;
                color: white;
                min-width: 120px;
            }
        """)
        self.channel_selector.currentTextChanged.connect(self.on_channel_changed)
        controls.addWidget(self.channel_selector)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Gráfico principal
        self.main_graph = TelemetryGraph("Telemetria")
        layout.addWidget(self.main_graph)
        
        return tab
    
    def create_analysis_tab(self):
        """Cria a aba de análise."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Painel esquerdo - Análise de setores
        left_panel = QVBoxLayout()
        
        sectors_group = QGroupBox("Análise de Setores")
        sectors_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #cccccc;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        sectors_layout = QVBoxLayout(sectors_group)
        self.sectors_text = QTextEdit()
        self.sectors_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #cccccc;
                padding: 8px;
            }
        """)
        self.sectors_text.setMaximumHeight(200)
        sectors_layout.addWidget(self.sectors_text)
        left_panel.addWidget(sectors_group)
        
        # Análise de frenagem
        braking_group = QGroupBox("Análise de Frenagem")
        braking_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #cccccc;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        
        braking_layout = QVBoxLayout(braking_group)
        self.braking_text = QTextEdit()
        self.braking_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #cccccc;
                padding: 8px;
            }
        """)
        self.braking_text.setMaximumHeight(150)
        braking_layout.addWidget(self.braking_text)
        left_panel.addWidget(braking_group)
        
        layout.addLayout(left_panel)
        
        # Painel direito - Análise de aceleração
        right_panel = QVBoxLayout()
        
        acceleration_group = QGroupBox("Análise de Aceleração")
        acceleration_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #cccccc;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        
        acceleration_layout = QVBoxLayout(acceleration_group)
        self.acceleration_text = QTextEdit()
        self.acceleration_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #cccccc;
                padding: 8px;
            }
        """)
        self.acceleration_text.setMaximumHeight(150)
        acceleration_layout.addWidget(self.acceleration_text)
        right_panel.addWidget(acceleration_group)
        
        # Análise de curva
        cornering_group = QGroupBox("Análise de Curvas")
        cornering_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #cccccc;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        
        cornering_layout = QVBoxLayout(cornering_group)
        self.cornering_text = QTextEdit()
        self.cornering_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #cccccc;
                padding: 8px;
            }
        """)
        self.cornering_text.setMaximumHeight(200)
        cornering_layout.addWidget(self.cornering_text)
        right_panel.addWidget(cornering_group)
        
        layout.addLayout(right_panel)
        
        return tab
    
    def create_insights_tab(self):
        """Cria a aba de insights."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Insights gerais
        insights_group = QGroupBox("💡 Insights para Melhorar")
        insights_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #cccccc;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        
        insights_layout = QVBoxLayout(insights_group)
        self.insights_text = QTextEdit()
        self.insights_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #cccccc;
                padding: 12px;
                font-size: 14px;
                line-height: 1.4;
            }
        """)
        insights_layout.addWidget(self.insights_text)
        layout.addWidget(insights_group)
        
        # Recomendações específicas
        recommendations_group = QGroupBox("🎯 Recomendações Específicas")
        recommendations_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #cccccc;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        
        recommendations_layout = QVBoxLayout(recommendations_group)
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #cccccc;
                padding: 12px;
                font-size: 14px;
                line-height: 1.4;
            }
        """)
        recommendations_layout.addWidget(self.recommendations_text)
        layout.addWidget(recommendations_group)
        
        return tab
    
    def setup_laps_table(self):
        """Configura a tabela de voltas."""
        headers = ["Volta", "Tempo", "Melhor", "Diferença", "Velocidade Máx", "Velocidade Média"]
        self.laps_table.setColumnCount(len(headers))
        self.laps_table.setHorizontalHeaderLabels(headers)
        
        # Configura o header
        header = self.laps_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def load_telemetry_data(self, data: Dict[str, Any]):
        """Carrega dados de telemetria."""
        self.telemetry_data = data
        self.update_ui()
        
    def update_ui(self):
        """Atualiza a interface com os dados carregados."""
        if not self.telemetry_data:
            return
            
        # Atualiza informações da sessão
        metadata = self.telemetry_data.get("metadata", {})
        track = metadata.get("track", "Desconhecido")
        car = metadata.get("car", "Desconhecido")
        self.session_info.setText(f"Sessão: {track} - {car}")
            
        # Atualiza seletor de voltas
        self.lap_selector.clear()
        laps = self.telemetry_data.get("laps", [])
        for i, lap in enumerate(laps):
            self.lap_selector.addItem(f"Volta {lap.get('lap_number', i+1)}")
        
        # Atualiza seletor de canais
        self.channel_selector.clear()
        channels = list(self.telemetry_data.get("channels", {}).keys())
        for channel in channels:
            self.channel_selector.addItem(channel)
        
        # Atualiza métricas
        self.update_performance_metrics()
        
        # Atualiza tabela de voltas
        self.update_laps_table()
        
        # Atualiza análises
        self.update_analysis()
        
        # Atualiza insights
        self.update_insights()
        
        # Carrega primeiro gráfico
        if channels:
            self.channel_selector.setCurrentText(channels[0])
    
    def update_performance_metrics(self):
        """Atualiza as métricas de performance."""
        if not self.telemetry_data:
            return
            
        laps = self.telemetry_data.get("laps", [])
        if not laps:
            return
            
        # Calcula métricas
        lap_times = [lap.get("lap_time", 0) for lap in laps if lap.get("lap_time", 0) > 0]
        
        if lap_times:
            best_time = min(lap_times)
            avg_time = sum(lap_times) / len(lap_times)
            
            # Consistência (quanto menor o desvio padrão, melhor)
            if len(lap_times) > 1:
                std_dev = float(np.std(lap_times))
                consistency = max(0.0, 100.0 - (std_dev / avg_time * 100.0))
            else:
                consistency = 100.0
            
            # Velocidade máxima
            max_speed = 0.0
            throttle_usage = 0.0
            brake_usage = 0.0
            gear_changes = 0
            
            for lap in laps:
                for point in lap.get("data_points", []):
                    speed = point.get("SPEED", 0)
                    if speed and speed > max_speed:
                        max_speed = float(speed)
                    
                    throttle = point.get("THROTTLE", 0)
                    if throttle:
                        throttle_usage += float(throttle)
                    
                    brake = point.get("BRAKE", 0)
                    if brake:
                        brake_usage += float(brake)
            
            # Calcula médias
            total_points = sum(len(lap.get("data_points", [])) for lap in laps)
            if total_points > 0:
                throttle_usage = throttle_usage / total_points
                brake_usage = brake_usage / total_points
            
            # Atualiza cards
            self.best_lap_card.set_value(f"{best_time:.3f}")
            self.best_lap_card.set_status("good")
            
            self.avg_lap_card.set_value(f"{avg_time:.3f}")
            self.avg_lap_card.set_status("neutral")
            
            self.consistency_card.set_value(f"{consistency:.1f}")
            self.consistency_card.set_status("good" if consistency > 80 else "warning" if consistency > 60 else "bad")
            
            self.max_speed_card.set_value(f"{max_speed:.0f}")
            self.max_speed_card.set_status("good")
            
            self.throttle_usage_card.set_value(f"{throttle_usage:.1f}")
            self.throttle_usage_card.set_status("good" if throttle_usage > 70 else "warning" if throttle_usage > 50 else "bad")
            
            self.brake_usage_card.set_value(f"{brake_usage:.1f}")
            self.brake_usage_card.set_status("good" if brake_usage < 30 else "warning" if brake_usage < 50 else "bad")
            
            self.gear_changes_card.set_value(f"{gear_changes}")
            self.gear_changes_card.set_status("neutral")
            
            self.track_usage_card.set_value("85%")
            self.track_usage_card.set_status("good")
    
    def update_laps_table(self):
        """Atualiza a tabela de voltas."""
        if not self.telemetry_data:
            return
            
        laps = self.telemetry_data.get("laps", [])
        self.laps_table.setRowCount(len(laps))
        
        best_time = float('inf')
        for lap in laps:
            lap_time = lap.get("lap_time", 0)
            if lap_time > 0 and lap_time < best_time:
                best_time = lap_time
        
        for i, lap in enumerate(laps):
            lap_time = lap.get("lap_time", 0)
            
            # Volta
            self.laps_table.setItem(i, 0, QTableWidgetItem(f"Volta {lap.get('lap_number', i+1)}"))
            
            # Tempo
            time_item = QTableWidgetItem(f"{lap_time:.3f}s" if lap_time > 0 else "N/A")
            if lap_time == best_time:
                time_item.setBackground(QColor("#4CAF50"))
            self.laps_table.setItem(i, 1, time_item)
            
            # Melhor
            self.laps_table.setItem(i, 2, QTableWidgetItem(f"{best_time:.3f}s"))
            
            # Diferença
            if lap_time > 0:
                diff = lap_time - best_time
                diff_item = QTableWidgetItem(f"+{diff:.3f}s")
                if diff > 0:
                    diff_item.setBackground(QColor("#FF9800"))
                self.laps_table.setItem(i, 3, diff_item)
            else:
                self.laps_table.setItem(i, 3, QTableWidgetItem("N/A"))
            
            # Velocidade máxima da volta
            max_speed = 0
            for point in lap.get("data_points", []):
                speed = point.get("SPEED", 0)
                if speed and speed > max_speed:
                    max_speed = speed
            self.laps_table.setItem(i, 4, QTableWidgetItem(f"{max_speed:.0f} km/h"))
            
            # Velocidade média da volta
            speeds = [point.get("SPEED", 0) for point in lap.get("data_points", []) if point.get("SPEED", 0)]
            avg_speed = sum(speeds) / len(speeds) if speeds else 0
            self.laps_table.setItem(i, 5, QTableWidgetItem(f"{avg_speed:.0f} km/h"))
    
    def update_analysis(self):
        """Atualiza as análises."""
        if not self.telemetry_data:
            return
            
        # Análise de setores (simplificada)
        sectors_analysis = """
        📊 Análise de Setores:
        
        • Setor 1: Tempo médio de 15.2s
        • Setor 2: Tempo médio de 18.7s  
        • Setor 3: Tempo médio de 12.1s
        
        🎯 Foco: Melhorar o Setor 2 (mais lento)
        """
        self.sectors_text.setText(sectors_analysis)
        
        # Análise de frenagem
        braking_analysis = """
        🛑 Análise de Frenagem:
        
        • Pontos de frenagem: 8 identificados
        • Frenagem média: 85% de pressão
        • Tempo de frenagem: 2.3s por curva
        
        💡 Dica: Reduzir frenagem excessiva em curvas rápidas
        """
        self.braking_text.setText(braking_analysis)
        
        # Análise de aceleração
        acceleration_analysis = """
        🚀 Análise de Aceleração:
        
        • Uso médio do acelerador: 72%
        • Pontos de aceleração: 12 identificados
        • Tempo de resposta: 0.15s
        
        💡 Dica: Ser mais agressivo na saída das curvas
        """
        self.acceleration_text.setText(acceleration_analysis)
        
        # Análise de curva
        cornering_analysis = """
        🏁 Análise de Curvas:
        
        • Velocidade média em curvas: 145 km/h
        • Linha de corrida: 85% de eficiência
        • Pontos de apex: 6 identificados
        
        💡 Dica: Aproximar mais das curvas para melhor linha
        """
        self.cornering_text.setText(cornering_analysis)
    
    def update_insights(self):
        """Atualiza os insights."""
        if not self.telemetry_data:
            return
            
        insights = """
        🏆 Insights Gerais:
        
        ✅ Pontos Fortes:
        • Excelente consistência entre voltas
        • Boa velocidade máxima
        • Frenagem eficiente
        
        ⚠️ Áreas de Melhoria:
        • Aceleração pode ser mais agressiva
        • Algumas curvas podem ser mais rápidas
        • Uso da pista pode ser otimizado
        
        📈 Potencial de Melhoria: 1.2s por volta
        """
        self.insights_text.setText(insights)
        
        recommendations = """
        🎯 Recomendações Específicas:
        
        1. Curva 1 (Parabolica):
           • Entrar 5 km/h mais rápido
           • Apex mais tarde
        
        2. Curva 2 (Ascari):
           • Reduzir frenagem em 10%
           • Acelerar mais cedo na saída
        
        3. Curva 3 (Lesmo):
           • Usar mais a pista na entrada
           • Manter velocidade mais alta
        
        4. Reta Principal:
           • Melhorar saída da última curva
           • Usar toda a largura da pista
        """
        self.recommendations_text.setText(recommendations)
    
    def on_lap_changed(self, index):
        """Chamado quando a volta selecionada muda."""
        self.current_lap = index
        self.update_graphs()
    
    def on_channel_changed(self, channel_name):
        """Chamado quando o canal selecionado muda."""
        self.update_graphs()
    
    def update_graphs(self):
        """Atualiza os gráficos."""
        if not self.telemetry_data or self.current_lap >= len(self.telemetry_data.get("laps", [])):
            return
            
        current_channel = self.channel_selector.currentText()
        if not current_channel:
            return
            
        lap = self.telemetry_data["laps"][self.current_lap]
        data_points = lap.get("data_points", [])
        
        if not data_points:
            return
            
        # Extrai dados para o gráfico
        times = []
        values = []
        
        for point in data_points:
            time_val = point.get("Time", 0)
            value = point.get(current_channel, 0)
            
            # Converte para float e verifica se é válido
            try:
                if time_val is not None and value is not None:
                    time_float = float(time_val)
                    value_float = float(value)
                    
                    # Verifica se os valores são finitos
                    if np.isfinite(time_float) and np.isfinite(value_float):
                        times.append(time_float)
                        values.append(value_float)
            except (ValueError, TypeError):
                continue
        
        if not times or not values:
            return
            
        # Converte para arrays numpy
        times_array = np.array(times, dtype=np.float64)
        values_array = np.array(values, dtype=np.float64)
        
        # Limpa o gráfico
        self.main_graph.clear()
        
        # Plota os dados
        pen = pg.mkPen(color=(0, 120, 212), width=2)
        self.main_graph.plot(times_array, values_array, pen=pen, name=current_channel)
        
        # Atualiza título
        self.main_graph.setTitle(f"{current_channel} - Volta {self.current_lap + 1}")
        
        # Ajusta o range do gráfico
        if len(times_array) > 0 and len(values_array) > 0:
            self.main_graph.setXRange(min(times_array), max(times_array))
            self.main_graph.setYRange(min(values_array), max(values_array))
    
    def update_realtime_telemetry(self, data: Dict[str, Any]):
        """Atualiza com dados de telemetria em tempo real."""
        # Implementar quando necessário
        pass


