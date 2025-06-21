"""
Widget de Dashboard moderno para o Race Telemetry Analyzer.
Fornece controles principais e informações em tempo real.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QSplitter, QFrame, QGroupBox, QGridLayout,
    QScrollArea, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QProgressBar,
    QSpacerItem, QSizePolicy, QSpinBox, QCheckBox, QTextEdit
)
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QTimer

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional


class ModernCard(QFrame):
    """Card moderno com sombra e bordas arredondadas."""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("""
            ModernCard {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 12px;
                margin: 4px;
            }
            ModernCard:hover {
                border-color: #0078d4;
                background-color: #323232;
            }
        """)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)
        
        # Título do card
        if title:
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 600;
                    color: #ffffff;
                    margin-bottom: 8px;
                }
            """)
            self.main_layout.addWidget(self.title_label)
    
    def add_content(self, widget):
        """Adiciona conteúdo ao card."""
        self.main_layout.addWidget(widget)


class ModernButton(QPushButton):
    """Botão moderno com estilo personalizado."""
    
    def __init__(self, text: str, button_type: str = "primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self._setup_style()
    
    def _setup_style(self):
        """Configura o estilo do botão."""
        base_style = """
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                min-height: 20px;
            }
            QPushButton:hover {
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                transform: translateY(0px);
            }
            QPushButton:disabled {
                opacity: 0.5;
            }
        """
        
        if self.button_type == "primary":
            style = base_style + """
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
            """
        elif self.button_type == "secondary":
            style = base_style + """
                QPushButton {
                    background-color: #404040;
                    color: white;
                    border: 1px solid #606060;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                    border-color: #0078d4;
                }
                QPushButton:pressed {
                    background-color: #363636;
                }
            """
        elif self.button_type == "danger":
            style = base_style + """
                QPushButton {
                    background-color: #d13438;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #b92b2f;
                }
                QPushButton:pressed {
                    background-color: #a12328;
                }
            """
        else:
            style = base_style
        
        self.setStyleSheet(style)


class StatusIndicator(QLabel):
    def __init__(self, label: str, color: str = "#6c63ff", parent=None):
        super().__init__(parent)
        self.setText(label)
        self.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 15px;")


class ModernProgressBar(QProgressBar):
    """Barra de progresso moderna."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #404040;
                text-align: center;
                color: white;
                font-size: 12px;
                height: 16px;
            }
            QProgressBar::chunk {
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078d4, stop:1 #106ebe);
            }
        """)


class DashboardWidget(QWidget):
    """Widget principal do dashboard."""
    
    # Sinais para comunicação com a janela principal
    load_file_requested = pyqtSignal()
    start_analysis_requested = pyqtSignal()
    pause_analysis_requested = pyqtSignal()
    resume_analysis_requested = pyqtSignal()
    stop_analysis_requested = pyqtSignal()
    start_realtime_requested = pyqtSignal(str)
    stop_realtime_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """Configura a interface do dashboard."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(24)

        # Card: Arquivo
        file_card = QGroupBox("Arquivo de Telemetria")
        file_layout = QVBoxLayout()
        self.load_button = QPushButton("📂 Carregar Arquivo")
        self.load_button.clicked.connect(self.load_file_requested.emit)
        self.file_info_label = QLabel("Nenhum arquivo carregado")
        self.file_info_label.setStyleSheet("color: #868e96; font-style: italic;")
        file_layout.addWidget(self.load_button)
        file_layout.addWidget(self.file_info_label)
        file_card.setLayout(file_layout)
        layout.addWidget(file_card)

        # Card: Análise
        analysis_card = QGroupBox("Análise de Volta")
        analysis_layout = QHBoxLayout()
        self.start_analysis_button = QPushButton("▶️ Iniciar Análise")
        self.start_analysis_button.clicked.connect(self.start_analysis_requested.emit)
        self.start_analysis_button.setEnabled(False)
        self.pause_analysis_button = QPushButton("⏸️ Pausar")
        self.pause_analysis_button.clicked.connect(self.pause_analysis_requested.emit)
        self.pause_analysis_button.setEnabled(False)
        self.stop_analysis_button = QPushButton("⏹️ Parar")
        self.stop_analysis_button.clicked.connect(self.stop_analysis_requested.emit)
        self.stop_analysis_button.setEnabled(False)
        analysis_layout.addWidget(self.start_analysis_button)
        analysis_layout.addWidget(self.pause_analysis_button)
        analysis_layout.addWidget(self.stop_analysis_button)
        analysis_card.setLayout(analysis_layout)
        layout.addWidget(analysis_card)

        # Card: Tempo Real
        realtime_card = QGroupBox("Tempo Real")
        realtime_layout = QHBoxLayout()
        self.simulator_combo = QComboBox()
        self.simulator_combo.addItems(["Assetto Corsa Competizione", "Le Mans Ultimate", "Automobilista 2"])
        self.start_realtime_button = QPushButton("🔌 Conectar")
        self.start_realtime_button.clicked.connect(self._start_realtime)
        self.stop_realtime_button = QPushButton("❌ Desconectar")
        self.stop_realtime_button.clicked.connect(self.stop_realtime_requested.emit)
        self.stop_realtime_button.setEnabled(False)
        realtime_layout.addWidget(self.simulator_combo)
        realtime_layout.addWidget(self.start_realtime_button)
        realtime_layout.addWidget(self.stop_realtime_button)
        realtime_card.setLayout(realtime_layout)
        layout.addWidget(realtime_card)

        # Card: Métricas
        metrics_card = QGroupBox("Métricas da Sessão")
        metrics_layout = QHBoxLayout()
        self.total_laps = StatusIndicator("Voltas: --", "#6c63ff")
        self.best_lap = StatusIndicator("Melhor: --", "#51cf66")
        self.avg_lap = StatusIndicator("Média: --", "#ffd43b")
        self.session_time = StatusIndicator("Tempo: --", "#8ec5fc")
        metrics_layout.addWidget(self.total_laps)
        metrics_layout.addWidget(self.best_lap)
        metrics_layout.addWidget(self.avg_lap)
        metrics_layout.addWidget(self.session_time)
        metrics_card.setLayout(metrics_layout)
        layout.addWidget(metrics_card)

        # Card: Feedback/Sugestão
        feedback_card = QGroupBox("Sugestão do Coach Virtual")
        feedback_layout = QVBoxLayout()
        self.feedback_box = QTextEdit()
        self.feedback_box.setReadOnly(True)
        self.feedback_box.setPlaceholderText("Dicas e sugestões de pilotagem aparecerão aqui após a análise.")
        feedback_layout.addWidget(self.feedback_box)
        feedback_card.setLayout(feedback_layout)
        layout.addWidget(feedback_card)

        self.setLayout(layout)
        
    def setup_timer(self):
        """Configura timer para atualizações em tempo real."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_realtime_data)
        self.update_timer.start(100)  # Atualiza a cada 100ms
        
    def _start_realtime(self):
        """Inicia telemetria em tempo real."""
        simulator_map = {
            "Assetto Corsa Competizione": "acc",
            "Le Mans Ultimate": "lmu", 
            "Automobilista 2": "ams2"
        }
        
        selected_simulator = self.simulator_combo.currentText()
        simulator_code = simulator_map.get(selected_simulator, "acc")
        
        self.start_realtime_requested.emit(simulator_code)
        
    def _update_realtime_data(self):
        """Atualiza dados em tempo real (placeholder)."""
        # Esta função será chamada periodicamente para atualizar dados em tempo real
        pass
        
    def update_analysis_buttons(self, file_loaded: bool = False, is_running: bool = False, is_paused: bool = False):
        """Atualiza o estado dos botões de análise."""
        self.start_analysis_button.setEnabled(file_loaded and not is_running)
        self.pause_analysis_button.setEnabled(is_running and not is_paused)
        self.stop_analysis_button.setEnabled(is_running)
        
    def update_realtime_buttons(self, is_running: bool = False):
        """Atualiza o estado dos botões de tempo real."""
        self.start_realtime_button.setEnabled(not is_running)
        self.stop_realtime_button.setEnabled(is_running)
        self.simulator_combo.setEnabled(not is_running)
        
    def update_file_info(self, filepath: str, metadata: Dict[str, Any]):
        """Atualiza informações do arquivo carregado."""
        filename = os.path.basename(filepath)
        track = metadata.get('track', 'Desconhecida')
        car = metadata.get('car', 'Desconhecido')
        
        info_text = f"Arquivo: {filename}\nPista: {track}\nCarro: {car}"
        self.file_info_label.setText(info_text)
        self.file_info_label.setStyleSheet("color: #51cf66; font-weight: bold;")
        
    def update_session_metrics(self, laps: list):
        """Atualiza métricas da sessão."""
        if not laps:
            return
            
        total_laps = len(laps)
        lap_times = [lap.get('lap_time', 0) for lap in laps if lap.get('lap_time', 0) > 0]
        
        if lap_times:
            best_time = min(lap_times)
            avg_time = sum(lap_times) / len(lap_times)
            
            self.total_laps.setText(f"Voltas: {total_laps}")
            self.best_lap.setText(f"Melhor: {self.format_time(best_time)}")
            self.avg_lap.setText(f"Média: {self.format_time(avg_time)}")
        else:
            self.total_laps.setText(f"Voltas: {total_laps}")
            self.best_lap.setText("Melhor: --")
            self.avg_lap.setText("Média: --")
            
    def format_time(self, seconds: float) -> str:
        """Formata tempo em segundos para formato legível."""
        if seconds <= 0:
            return "--"
            
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"

    def show_feedback(self, text: str):
        self.feedback_box.setText(text)


