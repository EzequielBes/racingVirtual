"""
Widget de Comparação de Voltas com design minimalista e moderno.
"""

from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QComboBox, QPushButton, QTextEdit, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class ComparisonCard(QWidget):
    """Card para exibir uma comparação específica."""
    
    def __init__(self, title: str, value: str = "--", delta: str = "", color: str = "#6c63ff", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #868e96; font-size: 14px; font-weight: 500;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        if delta:
            delta_label = QLabel(delta)
            delta_color = "#51cf66" if delta.startswith("+") else "#ff6b6b"
            delta_label.setStyleSheet(f"color: {delta_color}; font-size: 12px; font-weight: 500;")
            delta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(delta_label)
        
        self.setLayout(layout)

class ComparisonWidget(QWidget):
    """Widget de comparação de voltas com design minimalista."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.telemetry_data = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do widget."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # Área de scroll para conteúdo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # Card: Seleção de Voltas
        selection_card = QGroupBox("🏁 Seleção de Voltas")
        selection_layout = QHBoxLayout()
        
        self.reference_lap_combo = QComboBox()
        self.reference_lap_combo.addItem("Selecione a volta de referência")
        self.reference_lap_combo.currentTextChanged.connect(self.on_reference_changed)
        
        self.comparison_lap_combo = QComboBox()
        self.comparison_lap_combo.addItem("Selecione a volta para comparar")
        self.comparison_lap_combo.currentTextChanged.connect(self.on_comparison_changed)
        
        self.compare_button = QPushButton("🔄 Comparar Voltas")
        self.compare_button.clicked.connect(self.compare_laps)
        self.compare_button.setEnabled(False)
        
        selection_layout.addWidget(QLabel("Referência:"))
        selection_layout.addWidget(self.reference_lap_combo)
        selection_layout.addWidget(QLabel("Comparar:"))
        selection_layout.addWidget(self.comparison_lap_combo)
        selection_layout.addWidget(self.compare_button)
        
        selection_card.setLayout(selection_layout)
        content_layout.addWidget(selection_card)
        
        # Card: Resumo da Comparação
        summary_card = QGroupBox("📊 Resumo da Comparação")
        summary_layout = QHBoxLayout()
        
        self.reference_time_card = ComparisonCard("Tempo Referência", "--", "", "#6c63ff")
        self.comparison_time_card = ComparisonCard("Tempo Comparação", "--", "", "#8ec5fc")
        self.delta_time_card = ComparisonCard("Diferença", "--", "", "#ffd43b")
        self.improvement_card = ComparisonCard("Melhoria", "--", "", "#51cf66")
        
        summary_layout.addWidget(self.reference_time_card)
        summary_layout.addWidget(self.comparison_time_card)
        summary_layout.addWidget(self.delta_time_card)
        summary_layout.addWidget(self.improvement_card)
        
        summary_card.setLayout(summary_layout)
        content_layout.addWidget(summary_card)
        
        # Card: Análise por Setores
        sectors_card = QGroupBox("🎯 Análise por Setores")
        sectors_layout = QVBoxLayout()
        
        self.sectors_text = QTextEdit()
        self.sectors_text.setReadOnly(True)
        self.sectors_text.setMaximumHeight(120)
        self.sectors_text.setPlaceholderText("Análise por setores aparecerá aqui após a comparação.")
        self.sectors_text.setStyleSheet("""
            QTextEdit {
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
                color: #2d3748;
            }
        """)
        
        sectors_layout.addWidget(self.sectors_text)
        sectors_card.setLayout(sectors_layout)
        content_layout.addWidget(sectors_card)
        
        # Card: Pontos de Ganho/Perda
        points_card = QGroupBox("💡 Pontos de Ganho/Perda")
        points_layout = QVBoxLayout()
        
        self.points_text = QTextEdit()
        self.points_text.setReadOnly(True)
        self.points_text.setMaximumHeight(120)
        self.points_text.setPlaceholderText("Pontos onde você ganhou ou perdeu tempo aparecerão aqui.")
        self.points_text.setStyleSheet("""
            QTextEdit {
                background: #f0fff4;
                border: 1px solid #c6f6d5;
                border-radius: 8px;
                padding: 8px;
                color: #22543d;
            }
        """)
        
        points_layout.addWidget(self.points_text)
        points_card.setLayout(points_layout)
        content_layout.addWidget(points_card)
        
        # Card: Insights e Recomendações
        insights_card = QGroupBox("🧠 Insights e Recomendações")
        insights_layout = QVBoxLayout()
        
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setPlaceholderText("Insights e recomendações personalizadas aparecerão aqui.")
        self.insights_text.setStyleSheet("""
            QTextEdit {
                background: #fff5f5;
                border: 1px solid #fed7d7;
                border-radius: 8px;
                padding: 8px;
                color: #c53030;
            }
        """)
        
        insights_layout.addWidget(self.insights_text)
        insights_card.setLayout(insights_layout)
        content_layout.addWidget(insights_card)
        
        # Botões de ação
        actions_layout = QHBoxLayout()
        
        self.export_comparison_button = QPushButton("📄 Exportar Comparação")
        self.export_comparison_button.setEnabled(False)
        self.export_comparison_button.clicked.connect(self.export_comparison)
        
        self.clear_comparison_button = QPushButton("🗑️ Limpar Comparação")
        self.clear_comparison_button.clicked.connect(self.clear_comparison)
        
        actions_layout.addWidget(self.export_comparison_button)
        actions_layout.addWidget(self.clear_comparison_button)
        actions_layout.addStretch()
        
        content_layout.addLayout(actions_layout)
        content_widget.setLayout(content_layout)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
        
    def load_telemetry_data(self, data: Dict[str, Any]):
        """Carrega dados de telemetria para comparação."""
        self.telemetry_data = data
        self.update_lap_selection()
        
    def update_lap_selection(self):
        """Atualiza as opções de seleção de voltas."""
        self.reference_lap_combo.clear()
        self.comparison_lap_combo.clear()
        
        self.reference_lap_combo.addItem("Selecione a volta de referência")
        self.comparison_lap_combo.addItem("Selecione a volta para comparar")
        
        if self.telemetry_data and 'laps' in self.telemetry_data:
            for i, lap in enumerate(self.telemetry_data['laps']):
                lap_number = lap.get('lap_number', i + 1)
                lap_time = lap.get('lap_time', 0)
                lap_text = f"Volta {lap_number} ({self.format_time(lap_time)})"
                
                self.reference_lap_combo.addItem(lap_text, i)
                self.comparison_lap_combo.addItem(lap_text, i)
                
    def on_reference_changed(self, text: str):
        """Callback quando a volta de referência muda."""
        self.update_compare_button()
        
    def on_comparison_changed(self, text: str):
        """Callback quando a volta de comparação muda."""
        self.update_compare_button()
        
    def update_compare_button(self):
        """Atualiza o estado do botão de comparação."""
        ref_index = self.reference_lap_combo.currentIndex()
        comp_index = self.comparison_lap_combo.currentIndex()
        
        can_compare = (ref_index > 0 and comp_index > 0 and ref_index != comp_index)
        self.compare_button.setEnabled(can_compare)
        
    def compare_laps(self):
        """Executa a comparação entre as voltas selecionadas."""
        if not self.telemetry_data:
            return
            
        ref_index = self.reference_lap_combo.currentData()
        comp_index = self.comparison_lap_combo.currentData()
        
        if ref_index is None or comp_index is None:
            return
            
        laps = self.telemetry_data['laps']
        if ref_index >= len(laps) or comp_index >= len(laps):
            return
            
        reference_lap = laps[ref_index]
        comparison_lap = laps[comp_index]
        
        # Atualiza cards de resumo
        ref_time = reference_lap.get('lap_time', 0)
        comp_time = comparison_lap.get('lap_time', 0)
        delta_time = comp_time - ref_time
        
        self.reference_time_card.findChild(QLabel, "").setText(self.format_time(ref_time))
        self.comparison_time_card.findChild(QLabel, "").setText(self.format_time(comp_time))
        
        delta_text = f"{delta_time:+.3f}s"
        delta_color = "#51cf66" if delta_time < 0 else "#ff6b6b"
        self.delta_time_card.findChild(QLabel, "").setText(delta_text)
        self.delta_time_card.findChild(QLabel, "").setStyleSheet(f"color: {delta_color}; font-size: 20px; font-weight: bold;")
        
        # Calcula melhoria percentual
        if ref_time > 0:
            improvement = ((ref_time - comp_time) / ref_time) * 100
            improvement_text = f"{improvement:+.1f}%"
            self.improvement_card.findChild(QLabel, "").setText(improvement_text)
        
        # Atualiza análise por setores
        self.update_sectors_analysis(reference_lap, comparison_lap)
        
        # Atualiza pontos de ganho/perda
        self.update_points_analysis(reference_lap, comparison_lap)
        
        # Atualiza insights
        self.update_insights(reference_lap, comparison_lap, delta_time)
        
        # Habilita botão de exportar
        self.export_comparison_button.setEnabled(True)
        
    def update_sectors_analysis(self, ref_lap: Dict[str, Any], comp_lap: Dict[str, Any]):
        """Atualiza a análise por setores."""
        ref_sectors = ref_lap.get('sectors', [])
        comp_sectors = comp_lap.get('sectors', [])
        
        sectors_text = "🎯 ANÁLISE POR SETORES\n\n"
        
        for i in range(min(len(ref_sectors), len(comp_sectors))):
            ref_time = ref_sectors[i].get('time', 0)
            comp_time = comp_sectors[i].get('time', 0)
            delta = comp_time - ref_time
            
            sectors_text += f"Setor {i+1}:\n"
            sectors_text += f"  Referência: {self.format_time(ref_time)}\n"
            sectors_text += f"  Comparação: {self.format_time(comp_time)}\n"
            sectors_text += f"  Diferença: {delta:+.3f}s\n\n"
            
        self.sectors_text.setText(sectors_text)
        
    def update_points_analysis(self, ref_lap: Dict[str, Any], comp_lap: Dict[str, Any]):
        """Atualiza os pontos de ganho/perda."""
        points_text = "💡 PONTOS DE GANHO/PERDA\n\n"
        
        # Análise simplificada baseada em velocidade média
        ref_avg_speed = self.calculate_average_speed(ref_lap)
        comp_avg_speed = self.calculate_average_speed(comp_lap)
        
        if comp_avg_speed > ref_avg_speed:
            points_text += "✅ Velocidade média melhor na volta de comparação\n"
        else:
            points_text += "❌ Velocidade média menor na volta de comparação\n"
            
        # Análise de uso dos pedais
        ref_throttle = self.calculate_throttle_usage(ref_lap)
        comp_throttle = self.calculate_throttle_usage(comp_lap)
        
        if comp_throttle > ref_throttle:
            points_text += "✅ Melhor uso do acelerador na volta de comparação\n"
        else:
            points_text += "❌ Uso do acelerador pode ser melhorado\n"
            
        self.points_text.setText(points_text)
        
    def update_insights(self, ref_lap: Dict[str, Any], comp_lap: Dict[str, Any], delta_time: float):
        """Atualiza os insights e recomendações."""
        insights_text = "🧠 INSIGHTS E RECOMENDAÇÕES\n\n"
        
        if delta_time < 0:
            insights_text += "🎉 A volta de comparação foi mais rápida!\n"
            insights_text += "   Continue praticando esse ritmo.\n\n"
        else:
            insights_text += "📈 A volta de referência foi mais rápida.\n"
            insights_text += "   Analise onde você pode melhorar.\n\n"
            
        # Recomendações baseadas na diferença
        abs_delta = abs(delta_time)
        if abs_delta < 0.5:
            insights_text += "🎯 Voltas muito próximas! Trabalhe na consistência.\n"
        elif abs_delta < 2.0:
            insights_text += "📊 Diferença moderada. Foque nos setores mais lentos.\n"
        else:
            insights_text += "🚀 Diferença significativa. Revise sua abordagem geral.\n"
            
        self.insights_text.setText(insights_text)
        
    def calculate_average_speed(self, lap: Dict[str, Any]) -> float:
        """Calcula a velocidade média de uma volta."""
        data_points = lap.get('data_points', [])
        if not data_points:
            return 0.0
            
        speeds = [point.get('speed', 0) for point in data_points]
        return sum(speeds) / len(speeds) if speeds else 0.0
        
    def calculate_throttle_usage(self, lap: Dict[str, Any]) -> float:
        """Calcula o uso médio do acelerador."""
        data_points = lap.get('data_points', [])
        if not data_points:
            return 0.0
            
        throttles = [point.get('throttle', 0) for point in data_points]
        return sum(throttles) / len(throttles) if throttles else 0.0
        
    def format_time(self, seconds: float) -> str:
        """Formata tempo em segundos."""
        if seconds <= 0:
            return "--"
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"
        
    def export_comparison(self):
        """Exporta a comparação."""
        # TODO: Implementar exportação
        print("Funcionalidade de exportação será implementada em breve!")
        
    def clear_comparison(self):
        """Limpa a comparação atual."""
        self.reference_time_card.findChild(QLabel, "").setText("--")
        self.comparison_time_card.findChild(QLabel, "").setText("--")
        self.delta_time_card.findChild(QLabel, "").setText("--")
        self.improvement_card.findChild(QLabel, "").setText("--")
        
        self.sectors_text.clear()
        self.points_text.clear()
        self.insights_text.clear()
        
        self.export_comparison_button.setEnabled(False)

