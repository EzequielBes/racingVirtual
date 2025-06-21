"""
Widget de Análise Avançada com design minimalista e moderno.
"""

from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QTextEdit, QPushButton, QProgressBar, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class MetricCard(QWidget):
    """Card para exibir uma métrica específica."""
    
    def __init__(self, title: str, value: str = "--", color: str = "#6c63ff", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #868e96; font-size: 14px; font-weight: 500;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        self.setLayout(layout)

class AdvancedAnalysisWidget(QWidget):
    """Widget de análise avançada com design minimalista."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analysis_data = None
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
        
        # Card: Resumo da Análise
        summary_card = QGroupBox("📊 Resumo da Análise")
        summary_layout = QHBoxLayout()
        
        self.total_laps_metric = MetricCard("Total de Voltas", "--", "#6c63ff")
        self.best_lap_metric = MetricCard("Melhor Volta", "--", "#51cf66")
        self.consistency_metric = MetricCard("Consistência", "--", "#ffd43b")
        self.avg_speed_metric = MetricCard("Velocidade Média", "--", "#8ec5fc")
        
        summary_layout.addWidget(self.total_laps_metric)
        summary_layout.addWidget(self.best_lap_metric)
        summary_layout.addWidget(self.consistency_metric)
        summary_layout.addWidget(self.avg_speed_metric)
        
        summary_card.setLayout(summary_layout)
        content_layout.addWidget(summary_card)
        
        # Card: Erros Detectados
        errors_card = QGroupBox("⚠️ Erros Detectados")
        errors_layout = QVBoxLayout()
        
        self.errors_text = QTextEdit()
        self.errors_text.setReadOnly(True)
        self.errors_text.setMaximumHeight(150)
        self.errors_text.setPlaceholderText("Nenhum erro detectado ainda. Carregue um arquivo e inicie a análise.")
        self.errors_text.setStyleSheet("""
            QTextEdit {
                background: #fff5f5;
                border: 1px solid #fed7d7;
                border-radius: 8px;
                padding: 8px;
                color: #c53030;
            }
        """)
        
        errors_layout.addWidget(self.errors_text)
        errors_card.setLayout(errors_layout)
        content_layout.addWidget(errors_card)
        
        # Card: Sugestões de Melhoria
        suggestions_card = QGroupBox("💡 Sugestões de Melhoria")
        suggestions_layout = QVBoxLayout()
        
        self.suggestions_text = QTextEdit()
        self.suggestions_text.setReadOnly(True)
        self.suggestions_text.setMaximumHeight(150)
        self.suggestions_text.setPlaceholderText("Sugestões personalizadas aparecerão aqui após a análise.")
        self.suggestions_text.setStyleSheet("""
            QTextEdit {
                background: #f0fff4;
                border: 1px solid #c6f6d5;
                border-radius: 8px;
                padding: 8px;
                color: #22543d;
            }
        """)
        
        suggestions_layout.addWidget(self.suggestions_text)
        suggestions_card.setLayout(suggestions_layout)
        content_layout.addWidget(suggestions_card)
        
        # Card: Análise Detalhada por Volta
        detailed_card = QGroupBox("📈 Análise Detalhada")
        detailed_layout = QVBoxLayout()
        
        self.detailed_text = QTextEdit()
        self.detailed_text.setReadOnly(True)
        self.detailed_text.setPlaceholderText("Análise detalhada de cada volta aparecerá aqui.")
        self.detailed_text.setStyleSheet("""
            QTextEdit {
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
                color: #2d3748;
            }
        """)
        
        detailed_layout.addWidget(self.detailed_text)
        detailed_card.setLayout(detailed_layout)
        content_layout.addWidget(detailed_card)
        
        # Botões de ação
        actions_layout = QHBoxLayout()
        
        self.export_button = QPushButton("📄 Exportar Relatório")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.export_report)
        
        self.clear_button = QPushButton("🗑️ Limpar Análise")
        self.clear_button.clicked.connect(self.clear_analysis)
        
        actions_layout.addWidget(self.export_button)
        actions_layout.addWidget(self.clear_button)
        actions_layout.addStretch()
        
        content_layout.addLayout(actions_layout)
        content_widget.setLayout(content_layout)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
        
    def update_analysis_results(self, results: Dict[str, Any]):
        """Atualiza os resultados da análise."""
        self.analysis_data = results
        
        # Atualiza métricas principais
        total_laps = results.get("total_laps", 0)
        analyzed_laps = results.get("laps_analyzed", 0)
        best_lap = results.get("best_lap")
        consistency = results.get("consistency_score", 0)
        
        self.total_laps_metric.findChild(QLabel, "").setText(str(analyzed_laps))
        
        if best_lap:
            best_time = best_lap.get("time", 0)
            self.best_lap_metric.findChild(QLabel, "").setText(self.format_time(best_time))
        else:
            self.best_lap_metric.findChild(QLabel, "").setText("--")
            
        self.consistency_metric.findChild(QLabel, "").setText(f"{consistency:.1f}%")
        
        # Calcula velocidade média
        avg_speed = self.calculate_average_speed(results)
        self.avg_speed_metric.findChild(QLabel, "").setText(f"{avg_speed:.0f} km/h")
        
        # Atualiza erros detectados
        self.update_errors_display(results)
        
        # Atualiza sugestões
        self.update_suggestions_display(results)
        
        # Atualiza análise detalhada
        self.update_detailed_analysis(results)
        
        # Habilita botão de exportar
        self.export_button.setEnabled(True)
        
    def update_errors_display(self, results: Dict[str, Any]):
        """Atualiza a exibição de erros detectados."""
        errors_text = ""
        lap_details = results.get("lap_details", [])
        
        for lap in lap_details:
            lap_number = lap.get("lap_number", 0)
            lap_time = lap.get("lap_time", 0)
            
            # Detecta erros básicos
            errors = []
            if lap_time > 120:  # Volta muito lenta
                errors.append("Volta muito lenta")
            
            avg_speed = lap.get("average_speed", 0)
            if avg_speed < 80:  # Velocidade muito baixa
                errors.append("Velocidade média muito baixa")
                
            if errors:
                errors_text += f"Volta {lap_number}:\n"
                for error in errors:
                    errors_text += f"  • {error}\n"
                errors_text += "\n"
        
        if not errors_text:
            errors_text = "✅ Nenhum erro significativo detectado!"
            
        self.errors_text.setText(errors_text)
        
    def update_suggestions_display(self, results: Dict[str, Any]):
        """Atualiza as sugestões de melhoria."""
        suggestions = []
        
        # Sugestões baseadas na consistência
        consistency = results.get("consistency_score", 0)
        if consistency < 60:
            suggestions.append("🎯 Trabalhe na consistência das voltas")
        elif consistency > 80:
            suggestions.append("🌟 Excelente consistência! Continue assim!")
            
        # Sugestões baseadas no tempo médio
        best_lap = results.get("best_lap")
        if best_lap:
            best_time = best_lap.get("time", 0)
            suggestions.append(f"🏆 Sua melhor volta foi {self.format_time(best_time)}")
            
        # Sugestões baseadas no número de voltas
        total_laps = results.get("total_laps", 0)
        if total_laps < 5:
            suggestions.append("📈 Faça mais voltas para uma análise mais precisa")
        else:
            suggestions.append(f"📊 Boa quantidade de dados: {total_laps} voltas analisadas")
            
        suggestions_text = "\n".join(suggestions)
        if not suggestions_text:
            suggestions_text = "Carregue dados para receber sugestões personalizadas."
            
        self.suggestions_text.setText(suggestions_text)
        
    def update_detailed_analysis(self, results: Dict[str, Any]):
        """Atualiza a análise detalhada."""
        detailed_text = "📊 ANÁLISE DETALHADA\n\n"
        
        lap_details = results.get("lap_details", [])
        for lap in lap_details:
            lap_number = lap.get("lap_number", 0)
            lap_time = lap.get("lap_time", 0)
            avg_speed = lap.get("average_speed", 0)
            max_speed = lap.get("max_speed", 0)
            throttle_usage = lap.get("throttle_usage", 0)
            brake_usage = lap.get("brake_usage", 0)
            
            detailed_text += f"🏁 VOLTA {lap_number}\n"
            detailed_text += f"   Tempo: {self.format_time(lap_time)}\n"
            detailed_text += f"   Velocidade Média: {avg_speed:.0f} km/h\n"
            detailed_text += f"   Velocidade Máxima: {max_speed:.0f} km/h\n"
            detailed_text += f"   Uso do Acelerador: {throttle_usage:.1f}%\n"
            detailed_text += f"   Uso do Freio: {brake_usage:.1f}%\n\n"
            
        self.detailed_text.setText(detailed_text)
        
    def calculate_average_speed(self, results: Dict[str, Any]) -> float:
        """Calcula a velocidade média geral."""
        lap_details = results.get("lap_details", [])
        if not lap_details:
            return 0.0
            
        total_speed = sum(lap.get("average_speed", 0) for lap in lap_details)
        return total_speed / len(lap_details)
        
    def format_time(self, seconds: float) -> str:
        """Formata tempo em segundos."""
        if seconds <= 0:
            return "--"
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"
        
    def export_report(self):
        """Exporta relatório da análise."""
        # TODO: Implementar exportação para PDF/CSV
        print("Funcionalidade de exportação será implementada em breve!")
        
    def clear_analysis(self):
        """Limpa a análise atual."""
        self.analysis_data = None
        self.total_laps_metric.findChild(QLabel, "").setText("--")
        self.best_lap_metric.findChild(QLabel, "").setText("--")
        self.consistency_metric.findChild(QLabel, "").setText("--")
        self.avg_speed_metric.findChild(QLabel, "").setText("--")
        
        self.errors_text.clear()
        self.suggestions_text.clear()
        self.detailed_text.clear()
        
        self.export_button.setEnabled(False)


