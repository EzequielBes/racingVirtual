"""
Widget de comparação de voltas para o Race Telemetry Analyzer.
Permite comparar múltiplas voltas e visualizar diferenças de desempenho.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QSplitter, QFrame, QGroupBox, QGridLayout,
    QScrollArea, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QDialog, QDialogButtonBox, QColorDialog, QSizePolicy
)
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QPainter, QPen, QBrush, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QRectF
from typing import Dict, List, Any, Optional, Tuple # Adicionado Tuple aqui

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from .track_view import TrackViewWidget
from .telemetry_widget import TelemetryChart
from ..telemetry_comparison import TelemetryComparison # Importar a classe de comparação

# Cores padrão para as voltas
DEFAULT_LAP_COLORS = [
    QColor("#1f77b4"), QColor("#ff7f0e"), QColor("#2ca02c"), QColor("#d62728"),
    QColor("#9467bd"), QColor("#8c564b"), QColor("#e377c2"), QColor("#7f7f7f"),
    QColor("#bcbd22"), QColor("#17becf")
]

class LapSelectionDialog(QDialog):
    """Diálogo para selecionar múltiplas voltas de diferentes sessões."""
    def __init__(self, sessions_data: Dict[str, List[Dict[str, Any]]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar Voltas para Comparação")
        self.setMinimumSize(600, 400)

        self.sessions_data = sessions_data
        self.selected_laps = [] # Lista de tuplas (session_id, lap_data)

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.list_widget)

        self.populate_list()

        # Botões OK e Cancelar
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def populate_list(self):
        self.list_widget.clear()
        for session_id, session_info in self.sessions_data.items():
            session_item = QListWidgetItem(f"Sessão: {session_info['metadata'].get('track', 'N/A')} - {session_info['metadata'].get('car', 'N/A')} ({session_info['metadata'].get('driver', 'N/A')})")
            session_item.setFlags(session_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            font = session_item.font()
            font.setBold(True)
            session_item.setFont(font)
            session_item.setBackground(QColor("#f0f0f0"))
            self.list_widget.addItem(session_item)

            for lap_data in session_info.get("laps", []):
                lap_num = lap_data.get("lap_number", "N/A")
                lap_time = lap_data.get("lap_time", 0)
                lap_text = f"  Volta {lap_num} - {self._format_time(lap_time)}"
                lap_item = QListWidgetItem(lap_text)
                lap_item.setData(Qt.ItemDataRole.UserRole, (session_id, lap_data)) # Armazena dados da volta
                self.list_widget.addItem(lap_item)

    def accept(self):
        self.selected_laps = []
        for item in self.list_widget.selectedItems():
            lap_data_tuple = item.data(Qt.ItemDataRole.UserRole)
            if lap_data_tuple:
                self.selected_laps.append(lap_data_tuple[1]) # Apenas os dados da volta
        super().accept()

    def get_selected_laps(self) -> List[Dict[str, Any]]:
        return self.selected_laps

    def _format_time(self, time_seconds: float) -> str:
        if time_seconds <= 0:
            return "00:00.000"
        minutes = int(time_seconds // 60)
        seconds = int(time_seconds % 60)
        milliseconds = int((time_seconds % 1) * 1000)
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

class SelectedLapsWidget(QWidget):
    """Widget para exibir e gerenciar as voltas selecionadas para comparação."""
    laps_updated = pyqtSignal(list) # Emite a lista de voltas selecionadas
    reference_changed = pyqtSignal(int) # Emite o índice da nova volta de referência

    def __init__(self, parent=None):
        super().__init__(parent)
        self.laps_data: List[Dict[str, Any]] = []
        self.lap_colors: List[QColor] = []
        self.reference_lap_index = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        title_label = QLabel("Voltas Selecionadas para Comparação")
        title_label.setObjectName("section-title")
        layout.addWidget(title_label)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._change_lap_color)
        layout.addWidget(self.list_widget)

        # Botão para definir como referência
        ref_button = QPushButton("Definir como Referência")
        ref_button.clicked.connect(self._set_reference_lap)
        layout.addWidget(ref_button)

    def update_laps(self, laps: List[Dict[str, Any]]):
        self.laps_data = laps
        self.lap_colors = DEFAULT_LAP_COLORS[:len(laps)] # Atribui cores padrão
        self.reference_lap_index = 0 # Define a primeira como referência por padrão
        self._populate_list()
        self.laps_updated.emit(self.laps_data)
        self.reference_changed.emit(self.reference_lap_index)

    def _populate_list(self):
        self.list_widget.clear()
        for i, lap in enumerate(self.laps_data):
            lap_num = lap.get("lap_number", "N/A")
            lap_time = lap.get("lap_time", 0)
            driver = lap.get("metadata", {}).get("driver", "N/A") # Assumindo que metadata está na volta
            track = lap.get("metadata", {}).get("track", "N/A")
            car = lap.get("metadata", {}).get("car", "N/A")

            item_text = f"Volta {lap_num} ({self._format_time(lap_time)}) - {driver} @ {track} ({car})"
            if i == self.reference_lap_index:
                item_text += " [REF]"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i) # Armazena o índice original

            # Adiciona ícone de cor
            pixmap = QPixmap(16, 16)
            pixmap.fill(self.lap_colors[i])
            item.setIcon(QIcon(pixmap))

            self.list_widget.addItem(item)

    def _set_reference_lap(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            new_ref_index = selected_items[0].data(Qt.ItemDataRole.UserRole)
            if new_ref_index != self.reference_lap_index:
                self.reference_lap_index = new_ref_index
                self._populate_list() # Atualiza a lista para mostrar [REF]
                self.reference_changed.emit(self.reference_lap_index)

    def _change_lap_color(self, item: QListWidgetItem):
        index = item.data(Qt.ItemDataRole.UserRole)
        current_color = self.lap_colors[index]
        new_color = QColorDialog.getColor(current_color, self, "Escolher Cor da Volta")
        if new_color.isValid():
            self.lap_colors[index] = new_color
            self._populate_list() # Atualiza a lista com a nova cor
            # Emitir sinal se necessário para atualizar gráficos
            self.laps_updated.emit(self.laps_data) # Re-emite para forçar atualização de cor nos gráficos

    def get_laps_and_colors(self) -> Tuple[List[Dict[str, Any]], List[QColor]]:
        return self.laps_data, self.lap_colors

    def get_reference_lap_index(self) -> int:
        return self.reference_lap_index

    def _format_time(self, time_seconds: float) -> str:
        if time_seconds <= 0:
            return "00:00.000"
        minutes = int(time_seconds // 60)
        seconds = int(time_seconds % 60)
        milliseconds = int((time_seconds % 1) * 1000)
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

class ComparisonResultsPanel(QFrame):
    """Painel para exibir resultados da comparação entre múltiplas voltas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        layout = QVBoxLayout(self)

        title = QLabel("Resultados da Comparação (vs Referência)")
        title.setObjectName("section-title")
        layout.addWidget(title)

        self.results_tabs = QTabWidget()
        layout.addWidget(self.results_tabs)

    def update_comparison_results(self, comparison_results_list: List[Dict[str, Any]], reference_lap: Dict[str, Any], lap_colors: List[QColor]):
        self.results_tabs.clear()

        ref_lap_num = reference_lap.get("lap_number", "REF")
        ref_lap_time_str = self._format_time(reference_lap.get("lap_time", 0))

        for i, result in enumerate(comparison_results_list):
            comp_lap_num = result.get("comparison_lap", f"Comp{i+1}")
            comp_lap_time = result.get("comparison_lap_time", 0)
            comp_lap_time_str = self._format_time(comp_lap_time)

            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)

            if "error" in result:
                error_label = QLabel(f"Erro na comparação: {result['error']}")
                error_label.setStyleSheet("color: red;")
                tab_layout.addWidget(error_label)
                self.results_tabs.addTab(tab_widget, f"Erro Lap {comp_lap_num}")
                continue

            # --- Resumo da Comparação --- 
            summary_group = QGroupBox("Resumo")
            summary_layout = QGridLayout(summary_group)
            summary_layout.addWidget(QLabel("Referência:"), 0, 0)
            summary_layout.addWidget(QLabel(f"Lap {ref_lap_num} ({ref_lap_time_str})"), 0, 1)
            summary_layout.addWidget(QLabel("Comparação:"), 1, 0)
            summary_layout.addWidget(QLabel(f"Lap {comp_lap_num} ({comp_lap_time_str})"), 1, 1)
            summary_layout.addWidget(QLabel("Delta Total:"), 2, 0)
            time_delta_total = result.get("time_delta_total", 0)
            sign = "+" if time_delta_total > 0 else ""
            delta_label = QLabel(f"{sign}{time_delta_total:.3f}s")
            delta_label.setStyleSheet(f"color: {	'red	' if time_delta_total > 0 else 	'green	' if time_delta_total < 0 else 	'black	'};")
            summary_layout.addWidget(delta_label, 2, 1)
            summary_layout.setColumnStretch(1, 1)
            tab_layout.addWidget(summary_group)

            # --- Tabela de Setores --- 
            sectors_group = QGroupBox("Setores")
            sectors_layout = QVBoxLayout(sectors_group)
            sectors_table = QTableWidget()
            sectors_table.setColumnCount(4)
            sectors_table.setHorizontalHeaderLabels(["Setor", "Referência", "Comparação", "Diferença"])
            sectors_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            sectors_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            sectors_table.setAlternatingRowColors(True)
            header = sectors_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            sectors_layout.addWidget(sectors_table)
            tab_layout.addWidget(sectors_group)

            sectors = result.get("sectors", [])
            sectors_table.setRowCount(len(sectors))
            for row, sector in enumerate(sectors):
                sectors_table.setItem(row, 0, QTableWidgetItem(f"{sector.get(	'sector	', row+1)}"))
                sectors_table.setItem(row, 1, QTableWidgetItem(self._format_time(sector.get('ref_time', 0))))
                sectors_table.setItem(row, 2, QTableWidgetItem(self._format_time(sector.get('comp_time', 0))))
                delta = sector.get('delta', 0)
                sign_s = "+" if delta > 0 else ""
                delta_item = QTableWidgetItem(f"{sign_s}{delta:.3f}s")
                delta_item.setForeground(QColor("red") if delta > 0 else QColor("green") if delta < 0 else QColor("black"))
                sectors_table.setItem(row, 3, delta_item)

            # --- Sugestões (Placeholder) --- 
            suggestions = result.get("improvement_suggestions", [])
            if suggestions:
                suggestions_group = QGroupBox("Sugestões")
                suggestions_layout = QVBoxLayout(suggestions_group)
                for sug in suggestions:
                    suggestions_layout.addWidget(QLabel(sug))
                tab_layout.addWidget(suggestions_group)

            tab_layout.addStretch()
            self.results_tabs.addTab(tab_widget, f"vs Lap {comp_lap_num}")

            # Define a cor da aba (se possível, dependendo do estilo)
            # A cor da volta de comparação pode ser usada aqui
            # comp_lap_original_index = -1
            # for idx, lap_d in enumerate(all_laps_data):
            #     if lap_d.get("lap_number") == comp_lap_num: # Precisa de um ID único talvez
            #         comp_lap_original_index = idx
            #         break
            # if comp_lap_original_index != -1 and comp_lap_original_index < len(lap_colors):
            #     self.results_tabs.tabBar().setTabTextColor(i, lap_colors[comp_lap_original_index])
            #     # Ou definir a cor de fundo, etc.

    def _format_time(self, time_seconds: Optional[float]) -> str:
        if time_seconds is None or time_seconds <= 0:
            return "--:--.---"
        minutes = int(time_seconds // 60)
        seconds = int(time_seconds % 60)
        milliseconds = int((time_seconds % 1) * 1000)
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

class ComparisonWidget(QWidget):
    """Widget principal de comparação de múltiplas voltas."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.telemetry_data: Dict[str, List[Dict[str, Any]]] = {} # {session_id: [lap_data...]}
        self.comparer = TelemetryComparison()

        # Layout principal
        main_layout = QHBoxLayout(self)

        # --- Painel Esquerdo: Seleção e Resultados --- 
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(400) # Limita a largura do painel esquerdo

        # Botão para selecionar voltas
        self.select_laps_button = QPushButton("Selecionar Voltas...")
        self.select_laps_button.clicked.connect(self._open_lap_selection_dialog)
        left_layout.addWidget(self.select_laps_button)

        # Widget de voltas selecionadas
        self.selected_laps_widget = SelectedLapsWidget()
        left_layout.addWidget(self.selected_laps_widget)

        # Botão de comparação
        self.compare_button = QPushButton("Comparar Voltas Selecionadas")
        self.compare_button.clicked.connect(self._run_comparison)
        left_layout.addWidget(self.compare_button)

        # Painel de resultados
        self.results_panel = ComparisonResultsPanel()
        left_layout.addWidget(self.results_panel)
        left_layout.addStretch()

        # --- Painel Direito: Visualizações --- 
        right_panel = QSplitter(Qt.Orientation.Vertical)

        # Visualização da pista
        self.track_view = TrackViewWidget()
        # Placeholder para mapa
        map_placeholder = QLabel("Visualização do Mapa da Pista (TrackViewWidget)")
        map_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_placeholder.setFrameShape(QFrame.Shape.Box)
        map_placeholder.setMinimumHeight(200)
        right_panel.addWidget(map_placeholder) # Substituir por self.track_view quando pronto

        # Gráficos de comparação (Tabs)
        self.charts_widget = QTabWidget()
        right_panel.addWidget(self.charts_widget)

        # Adicionar tabs de gráficos (inicialmente vazias ou com placeholders)
        self._setup_chart_tabs()

        # --- Montagem Final --- 
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(1, 1) # Dá mais espaço para o painel direito

        main_layout.addWidget(main_splitter)

        # Conectar sinais
        self.selected_laps_widget.laps_updated.connect(self._update_visualizations)
        self.selected_laps_widget.reference_changed.connect(self._update_visualizations) # Re-executar comparação se ref mudar?

    def load_telemetry_data(self, all_data: Dict[str, Dict[str, Any]]):
        """Carrega todos os dados de telemetria importados."""
        # Simplificando: Assume que all_data é {session_id: {metadata: {}, laps: [...]}}
        self.telemetry_data = all_data
        # Limpa seleções anteriores
        self.selected_laps_widget.update_laps([])
        self.results_panel.results_tabs.clear()
        self._clear_charts()
        # Habilita o botão de seleção
        self.select_laps_button.setEnabled(bool(self.telemetry_data))

    def _open_lap_selection_dialog(self):
        dialog = LapSelectionDialog(self.telemetry_data, self)
        if dialog.exec():
            selected_laps = dialog.get_selected_laps()
            if len(selected_laps) >= 2:
                self.selected_laps_widget.update_laps(selected_laps)
            else:
                # Informar usuário que precisa selecionar pelo menos 2 voltas
                pass # Usar QMessageBox

    def _run_comparison(self):
        laps, colors = self.selected_laps_widget.get_laps_and_colors()
        ref_index = self.selected_laps_widget.get_reference_lap_index()

        if len(laps) < 2:
            print("Selecione pelo menos duas voltas para comparar.") # Usar QMessageBox
            return

        try:
            comparison_results = self.comparer.compare_multiple_laps(laps, ref_index, method="distance")
            self.results_panel.update_comparison_results(comparison_results, laps[ref_index], colors)
            self._update_visualizations() # Atualiza gráficos com os novos resultados

        except Exception as e:
            print(f"Erro ao executar comparação: {e}") # Usar QMessageBox
            # Limpar resultados?
            self.results_panel.results_tabs.clear()

    def _setup_chart_tabs(self):
        self.charts = {}
        chart_configs = {
            "Delta Tempo": ["delta_time"],
            "Velocidade": ["speed"],
            "Pedais": ["throttle", "brake"],
            "Volante": ["steering"],
            "Marchas": ["gear"]
        }

        for tab_name, channels in chart_configs.items():
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            chart = TelemetryChart()
            self.charts[tab_name] = chart
            tab_layout.addWidget(chart)
            self.charts_widget.addTab(tab_widget, tab_name)

    def _update_visualizations(self):
        laps, colors = self.selected_laps_widget.get_laps_and_colors()
        ref_index = self.selected_laps_widget.get_reference_lap_index()

        if not laps:
            self._clear_charts()
            # Limpar mapa também
            return

        # Atualizar Gráficos
        for tab_name, chart in self.charts.items():
            chart.clear_plot()
            if tab_name == "Delta Tempo":
                # Plotar delta_time dos resultados da comparação
                # Precisa acessar os resultados armazenados ou re-executar comparação?
                # Por simplicidade, vamos assumir que os resultados estão disponíveis
                # após _run_comparison ter sido chamado.
                # A lógica aqui precisaria ser mais robusta para buscar os dados corretos.
                pass # Implementar plot de delta
            else:
                # Plotar canais normais de telemetria para as voltas selecionadas
                channels_to_plot = []
                if tab_name == "Velocidade": channels_to_plot = ["speed"]
                elif tab_name == "Pedais": channels_to_plot = ["throttle", "brake"]
                elif tab_name == "Volante": channels_to_plot = ["steering"]
                elif tab_name == "Marchas": channels_to_plot = ["gear"]

                if channels_to_plot:
                    plot_data = []
                    for i, lap_data in enumerate(laps):
                        lap_label = f"Lap {lap_data.get('lap_number', i)}"
                        if i == ref_index: lap_label += " [REF]"
                        # Extrair dados para os canais necessários
                        x_data = np.array([p.get("distance", 0) for p in lap_data.get("data_points", [])])
                        y_datas = {}
                        for channel in channels_to_plot:
                             y_datas[channel] = np.array([p.get(channel, np.nan) for p in lap_data.get("data_points", [])])

                        plot_data.append({
                            "label": lap_label,
                            "color": colors[i].name(),
                            "x": x_data,
                            "y": y_datas # Dicionário de canais para este lap
                        })
                    chart.plot_multiple_laps(plot_data, channels_to_plot)

        # Atualizar Mapa (TrackViewWidget)
        # self.track_view.update_laps(laps, colors, ref_index)
        # Precisa implementar a lógica em TrackViewWidget para desenhar múltiplas linhas

    def _clear_charts(self):
        for chart in self.charts.values():
            chart.clear_plot()

# Exemplo de como usar (em main.py ou similar)
# app = QApplication(sys.argv)
# main_window = QMainWindow()
# telemetry_data = load_all_your_telemetry_files() # Carrega dados
# comparison_view = ComparisonWidget()
# comparison_view.load_telemetry_data(telemetry_data)
# main_window.setCentralWidget(comparison_view)
# main_window.show()
# sys.exit(app.exec())

