"""
Widget de gerenciamento de setups para o Race Telemetry Analyzer.
Permite gerenciar, comparar, importar, exportar e obter assistência para setups de carros.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSplitter, QFrame, QGroupBox, QGridLayout,
    QScrollArea, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QSlider, QFileDialog, QMessageBox, QDialog, QFormLayout,
    QDialogButtonBox, QRadioButton, QButtonGroup, QStackedWidget
)
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from typing import Dict, List, Any, Optional

import os
import json
import shutil
import logging
from datetime import datetime
import uuid # Para IDs únicos de setup

# Configuração de logging
logger = logging.getLogger("race_telemetry_api.setup")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

# --- Setup Card --- (Mantido como antes, com pequenas melhorias)
class SetupCard(QFrame):
    """Widget de card para exibir um setup."""
    setup_selected = pyqtSignal(dict)
    setup_exported = pyqtSignal(dict, str)
    setup_edited = pyqtSignal(dict)
    setup_deleted = pyqtSignal(str) # Emite o ID do setup a ser deletado

    def __init__(self, setup_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumHeight(150)
        self.setMinimumWidth(250)
        self.setup_data = setup_data

        layout = QVBoxLayout(self)
        self.car_label = QLabel(setup_data.get("car", "Desconhecido"))
        self.car_label.setObjectName("card-title")
        font = self.car_label.font()
        font.setBold(True)
        self.car_label.setFont(font)
        layout.addWidget(self.car_label)

        self.track_label = QLabel(f"Pista: {setup_data.get('track', 'Desconhecida')}")
        self.author_label = QLabel(f"Autor: {setup_data.get('author', 'Desconhecido')}")
        self.date_label = QLabel(f"Data: {self._format_date(setup_data.get('date'))}")
        layout.addWidget(self.track_label)
        layout.addWidget(self.author_label)
        layout.addWidget(self.date_label)

        buttons_layout = QHBoxLayout()
        self.view_button = QPushButton("Ver")
        self.edit_button = QPushButton("Editar")
        self.export_button = QPushButton("Exportar")
        self.delete_button = QPushButton("Excluir")
        self.delete_button.setStyleSheet("color: red;")
        buttons_layout.addWidget(self.view_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.delete_button)
        layout.addLayout(buttons_layout)

        self.view_button.clicked.connect(self._on_view_clicked)
        self.edit_button.clicked.connect(self._on_edit_clicked)
        self.export_button.clicked.connect(self._on_export_clicked)
        self.delete_button.clicked.connect(self._on_delete_clicked)

    def _format_date(self, date_str: Optional[str]) -> str:
        if not date_str:
            return "--"
        try:
            return datetime.fromisoformat(date_str).strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return date_str

    def _on_view_clicked(self):
        self.setup_selected.emit(self.setup_data)

    def _on_edit_clicked(self):
        dialog = SetupEditDialog(self.setup_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_setup_data()
            self.setup_data = updated_data
            self._update_display()
            self.setup_edited.emit(updated_data)
            logger.info(f"Setup editado: {updated_data.get('id')}")

    def _update_display(self):
        self.car_label.setText(self.setup_data.get("car", "Desconhecido"))
        self.track_label.setText(f"Pista: {self.setup_data.get('track', 'Desconhecida')}")
        self.author_label.setText(f"Autor: {self.setup_data.get('author', 'Desconhecido')}")
        self.date_label.setText(f"Data: {self._format_date(self.setup_data.get('date'))}")

    def _on_export_clicked(self):
        file_dialog = QFileDialog()
        default_filename = f"{self.setup_data.get('car', 'setup').replace(' ', '_')}_{self.setup_data.get('track', 'track').replace(' ', '_')}_{self.setup_data.get('id', '')[:8]}.json"
        setups_dir = os.path.join(os.path.expanduser("~"), "RaceTelemetryAnalyzer", "setups")
        default_path = os.path.join(setups_dir, default_filename)
        file_path, _ = file_dialog.getSaveFileName(self, "Exportar Setup", default_path, "Arquivos JSON (*.json);;Todos os Arquivos (*)")
        if file_path:
            self.setup_exported.emit(self.setup_data, file_path)

    def _on_delete_clicked(self):
        reply = QMessageBox.question(self, "Confirmar Exclusão",
                                     f"Tem certeza que deseja excluir o setup para {self.setup_data.get('car')} em {self.setup_data.get('track')}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            setup_id = self.setup_data.get("id")
            if setup_id:
                self.setup_deleted.emit(setup_id)
            else:
                 logger.error("Não foi possível excluir setup: ID não encontrado.")

# --- Setup Detail Panel --- (Mantido como antes)
class SetupDetailPanel(QFrame):
    """Painel para exibir detalhes de um setup."""
    export_requested = pyqtSignal(dict, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        layout = QVBoxLayout(self)
        self.title_label = QLabel("Detalhes do Setup")
        self.title_label.setObjectName("section-title")
        layout.addWidget(self.title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content = QWidget()
        self.detail_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        buttons_layout = QHBoxLayout()
        self.apply_button = QPushButton("Aplicar Setup (Manual)")
        self.export_button = QPushButton("Exportar Setup")
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.export_button)
        layout.addLayout(buttons_layout)

        self.export_button.clicked.connect(self._on_export_clicked)
        self.apply_button.clicked.connect(self._on_apply_clicked)

        self.current_setup = None

    def update_setup_details(self, setup_data: Optional[Dict[str, Any]]):
        self.current_setup = setup_data
        # Limpa layout anterior
        while self.detail_layout.count():
            item = self.detail_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        if not setup_data:
            self.title_label.setText("Nenhum setup selecionado")
            self.detail_layout.addWidget(QLabel("Selecione um setup na lista para ver os detalhes."))
            self.detail_layout.addStretch()
            self.apply_button.setEnabled(False)
            self.export_button.setEnabled(False)
            return

        car = setup_data.get("car", "Desconhecido")
        track = setup_data.get("track", "Desconhecida")
        self.title_label.setText(f"Setup: {car} - {track}")
        self.apply_button.setEnabled(True)
        self.export_button.setEnabled(True)

        # Adiciona grupos de informações
        self._add_detail_group("Informações Básicas", {
            "Carro": setup_data.get("car", "--"),
            "Pista": setup_data.get("track", "--"),
            "Autor": setup_data.get("author", "--"),
            "Data": self._format_date(setup_data.get("date"))
        })

        # Adiciona detalhes específicos (simplificado)
        for group_key in ["tyres", "suspension", "aero", "transmission", "alignment", "brakes", "electronics"]:
            if group_key in setup_data:
                self._add_detail_group(group_key.capitalize(), setup_data[group_key])

        if "notes" in setup_data and setup_data["notes"]:
            notes_group = QGroupBox("Notas")
            notes_layout = QVBoxLayout(notes_group)
            notes_text = QTextEdit(setup_data["notes"])
            notes_text.setReadOnly(True)
            notes_layout.addWidget(notes_text)
            self.detail_layout.addWidget(notes_group)

        self.detail_layout.addStretch()

    def _add_detail_group(self, title: str, data: Dict):
        if not data or not isinstance(data, dict):
            return
        group = QGroupBox(title)
        layout = QGridLayout(group)
        row = 0
        for key, value in data.items():
            # Transforma chave em label legível (ex: tyrePressureFL -> Tyre Pressure FL)
            label_text = key.replace("_", " ").title()
            layout.addWidget(QLabel(f"{label_text}:"), row, 0)
            layout.addWidget(QLabel(str(value)), row, 1)
            row += 1
        self.detail_layout.addWidget(group)

    def _format_date(self, date_str: Optional[str]) -> str:
        if not date_str:
            return "--"
        try:
            return datetime.fromisoformat(date_str).strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return date_str

    def _on_export_clicked(self):
        if not self.current_setup:
            return
        file_dialog = QFileDialog()
        default_filename = f"{self.current_setup.get('car', 'setup').replace(' ', '_')}_{self.current_setup.get('track', 'track').replace(' ', '_')}_{self.current_setup.get('id', '')[:8]}.json"
        setups_dir = os.path.join(os.path.expanduser("~"), "RaceTelemetryAnalyzer", "setups")
        default_path = os.path.join(setups_dir, default_filename)
        file_path, _ = file_dialog.getSaveFileName(self, "Exportar Setup", default_path, "Arquivos JSON (*.json);;Todos os Arquivos (*)")
        if file_path:
            self.export_requested.emit(self.current_setup, file_path)

    def _on_apply_clicked(self):
        QMessageBox.information(self, "Aplicar Setup", "A aplicação automática de setups ainda não está implementada.\n\nPor favor, ajuste manualmente os valores no simulador.")

# --- Setup Edit Dialog --- (Adicionando mais campos)
class SetupEditDialog(QDialog):
    """Diálogo para edição/criação de setup."""
    def __init__(self, setup_data: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.is_new_setup = setup_data is None
        self.setup_data = setup_data.copy() if setup_data else {}
        self.setWindowTitle("Novo Setup" if self.is_new_setup else "Editar Setup")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Dicionários para guardar referências aos campos de input
        self.fields = {
            "basic": {},
            "tyres": {},
            "suspension": {},
            "aero": {},
            "alignment": {},
            "notes": None
        }

        self._create_basic_tab()
        self._create_tyres_tab()
        self._create_suspension_tab()
        self._create_aero_tab()
        self._create_alignment_tab()
        self._create_notes_tab()

        # Botões
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _create_tab(self, name: str) -> QFormLayout:
        tab = QWidget()
        layout = QFormLayout(tab)
        self.tabs.addTab(tab, name)
        return layout

    def _add_field(self, layout: QFormLayout, category: str, key: str, label: str, field_type: type = QLineEdit, default_value: Any = ""):
        current_value = self.setup_data.get(category, {}).get(key, default_value)
        if field_type == QLineEdit:
            field = QLineEdit(str(current_value))
        elif field_type == QSpinBox:
            field = QSpinBox()
            field.setRange(-1000, 1000) # Exemplo de range
            field.setValue(int(current_value) if isinstance(current_value, (int, float, str)) and str(current_value).isdigit() else 0)
        elif field_type == QDoubleSpinBox:
            field = QDoubleSpinBox()
            field.setRange(-1000.0, 1000.0) # Exemplo de range
            field.setDecimals(2)
            field.setValue(float(current_value) if isinstance(current_value, (int, float, str)) and str(current_value).replace(".", "", 1).isdigit() else 0.0)
        else:
            field = QLineEdit(str(current_value)) # Fallback

        layout.addRow(label, field)
        if category not in self.fields: self.fields[category] = {}
        self.fields[category][key] = field
        return field

    def _create_basic_tab(self):
        layout = self._create_tab("Informações Básicas")
        self.fields["basic"]["car"] = self._add_field(layout, "basic", "car", "Carro (*):", QLineEdit, self.setup_data.get("car", ""))
        self.fields["basic"]["track"] = self._add_field(layout, "basic", "track", "Pista (*):", QLineEdit, self.setup_data.get("track", ""))
        self.fields["basic"]["author"] = self._add_field(layout, "basic", "author", "Autor:", QLineEdit, self.setup_data.get("author", ""))

    def _create_tyres_tab(self):
        layout = self._create_tab("Pneus")
        for pos in ["FL", "FR", "RL", "RR"]:
            self._add_field(layout, "tyres", f"pressure{pos}", f"Pressão {pos} (psi):", QDoubleSpinBox, 26.0)
            self._add_field(layout, "tyres", f"toe{pos}", f"Convergência {pos} (deg):", QDoubleSpinBox, 0.0)
            self._add_field(layout, "tyres", f"camber{pos}", f"Cambagem {pos} (deg):", QDoubleSpinBox, -2.0)

    def _create_suspension_tab(self):
        layout = self._create_tab("Suspensão")
        for pos in ["F", "R"]:
            self._add_field(layout, "suspension", f"rideHeight{pos}", f"Altura {pos} (mm):", QSpinBox, 50)
            self._add_field(layout, "suspension", f"antiRollBar{pos}", f"Barra Estabilizadora {pos}:", QSpinBox, 5)
            self._add_field(layout, "suspension", f"springRate{pos}", f"Mola {pos} (N/mm):", QSpinBox, 100)
            self._add_field(layout, "suspension", f"bumpStopRate{pos}", f"Batente Bump {pos}:", QSpinBox, 10)
            self._add_field(layout, "suspension", f"reboundStopRate{pos}", f"Batente Rebound {pos}:", QSpinBox, 10)

    def _create_aero_tab(self):
        layout = self._create_tab("Aerodinâmica")
        self._add_field(layout, "aero", "frontWing", "Asa Dianteira:", QSpinBox, 5)
        self._add_field(layout, "aero", "rearWing", "Asa Traseira:", QSpinBox, 10)
        self._add_field(layout, "aero", "brakeDucts", "Dutos de Freio:", QSpinBox, 3)

    def _create_alignment_tab(self):
        layout = self._create_tab("Alinhamento")
        self._add_field(layout, "alignment", "casterL", "Caster Esq:", QDoubleSpinBox, 5.0)
        self._add_field(layout, "alignment", "casterR", "Caster Dir:", QDoubleSpinBox, 5.0)
        self._add_field(layout, "alignment", "steerRatio", "Relação Direção:", QDoubleSpinBox, 14.0)

    def _create_notes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Notas Adicionais:"))
        self.fields["notes"] = QTextEdit(self.setup_data.get("notes", ""))
        layout.addWidget(self.fields["notes"])
        self.tabs.addTab(tab, "Notas")

    def accept(self):
        # Validação básica
        if not self.fields["basic"]["car"].text() or not self.fields["basic"]["track"].text():
            QMessageBox.warning(self, "Campos Obrigatórios", "Os campos 'Carro' e 'Pista' são obrigatórios.")
            return

        # Coleta dados
        for category, cat_fields in self.fields.items():
            if category == "notes":
                self.setup_data["notes"] = cat_fields.toPlainText() if cat_fields else ""
            elif isinstance(cat_fields, dict):
                if category not in self.setup_data: self.setup_data[category] = {}
                for key, field in cat_fields.items():
                    if isinstance(field, QLineEdit): self.setup_data[category][key] = field.text()
                    elif isinstance(field, QTextEdit): self.setup_data[category][key] = field.toPlainText()
                    elif isinstance(field, QSpinBox): self.setup_data[category][key] = field.value()
                    elif isinstance(field, QDoubleSpinBox): self.setup_data[category][key] = field.value()

        # Atualiza data e ID
        self.setup_data["date"] = datetime.now().isoformat()
        if self.is_new_setup:
            self.setup_data["id"] = f"setup_{uuid.uuid4().hex[:12]}"

        super().accept()

    def get_setup_data(self) -> Dict[str, Any]:
        return self.setup_data

# --- Setup Assistant Dialog --- (Nova funcionalidade)
class SetupAssistantDialog(QDialog):
    """Diálogo guiado para ajudar a ajustar ou criar setups."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Assistente de Setup")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Páginas do assistente
        self._create_problem_page()
        self._create_suggestion_page()

        # Botões de navegação
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("< Anterior")
        self.next_button = QPushButton("Próximo >")
        self.finish_button = QPushButton("Concluir")
        self.finish_button.setVisible(False)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.finish_button)
        layout.addLayout(nav_layout)

        self.prev_button.clicked.connect(self._go_prev)
        self.next_button.clicked.connect(self._go_next)
        self.finish_button.clicked.connect(self.accept)

        self.prev_button.setEnabled(False)
        self.stacked_widget.setCurrentIndex(0)

    def _create_problem_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Qual problema você está enfrentando ou o que deseja melhorar?"))

        self.problem_group = QButtonGroup(self)
        problems = [
            ("oversteer_entry", "Saída de traseira na entrada da curva (Oversteer)"),
            ("oversteer_mid", "Saída de traseira no meio da curva (Oversteer)"),
            ("oversteer_exit", "Saída de traseira na saída da curva (Oversteer)"),
            ("understeer_entry", "Saída de frente na entrada da curva (Understeer)"),
            ("understeer_mid", "Saída de frente no meio da curva (Understeer)"),
            ("understeer_exit", "Saída de frente na saída da curva (Understeer)"),
            ("braking_instability", "Instabilidade na frenagem"),
            ("poor_traction", "Pouca tração na aceleração"),
            ("slow_response", "Carro lento para responder/mudar de direção"),
            ("bumpy_ride", "Carro muito instável em zebras/ondulações")
        ]

        for key, text in problems:
            radio = QRadioButton(text)
            radio.setProperty("problem_key", key) # Armazena a chave do problema
            layout.addWidget(radio)
            self.problem_group.addButton(radio)

        layout.addStretch()
        self.stacked_widget.addWidget(page)

    def _create_suggestion_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Sugestões de Ajuste:"))
        self.suggestion_label = QLabel("Selecione um problema na página anterior.")
        self.suggestion_label.setWordWrap(True)
        layout.addWidget(self.suggestion_label)
        layout.addStretch()
        self.stacked_widget.addWidget(page)

    def _go_prev(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.stacked_widget.setCurrentIndex(current_index - 1)
            self._update_nav_buttons()

    def _go_next(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0: # Saindo da página de problemas
            selected_button = self.problem_group.checkedButton()
            if not selected_button:
                QMessageBox.warning(self, "Seleção Necessária", "Por favor, selecione um problema.")
                return
            problem_key = selected_button.property("problem_key")
            self._update_suggestions(problem_key)

        if current_index < self.stacked_widget.count() - 1:
            self.stacked_widget.setCurrentIndex(current_index + 1)
            self._update_nav_buttons()

    def _update_nav_buttons(self):
        current_index = self.stacked_widget.currentIndex()
        self.prev_button.setEnabled(current_index > 0)
        self.next_button.setVisible(current_index < self.stacked_widget.count() - 1)
        self.finish_button.setVisible(current_index == self.stacked_widget.count() - 1)

    def _update_suggestions(self, problem_key: str):
        # Lógica simplificada de sugestões (deve ser expandida)
        suggestions = {
            "oversteer_entry": "- Aumentar asa dianteira\n- Diminuir barra estabilizadora dianteira\n- Aumentar pressão pneus dianteiros",
            "oversteer_mid": "- Aumentar altura traseira\n- Amaciar molas traseiras\n- Aumentar cambagem negativa traseira",
            "oversteer_exit": "- Aumentar asa traseira\n- Endurecer barra estabilizadora traseira\n- Diminuir diferencial (aceleração)",
            "understeer_entry": "- Diminuir asa dianteira\n- Endurecer barra estabilizadora dianteira\n- Diminuir pressão pneus dianteiros",
            "understeer_mid": "- Diminuir altura traseira\n- Endurecer molas traseiras\n- Diminuir cambagem negativa traseira",
            "understeer_exit": "- Diminuir asa traseira\n- Amaciar barra estabilizadora traseira\n- Aumentar diferencial (aceleração)",
            "braking_instability": "- Aumentar dutos de freio\n- Mover balanço de freio para frente\n- Endurecer molas dianteiras",
            "poor_traction": "- Aumentar asa traseira\n- Amaciar molas traseiras\n- Diminuir pressão pneus traseiros",
            "slow_response": "- Endurecer barras estabilizadoras (F/R)\n- Diminuir altura do carro\n- Aumentar pressão dos pneus",
            "bumpy_ride": "- Amaciar molas (F/R)\n- Amaciar amortecedores (bump/rebound)\n- Aumentar altura do carro"
        }
        suggestion_text = suggestions.get(problem_key, "Nenhuma sugestão disponível para este problema.")
        self.suggestion_label.setText(suggestion_text)

# --- Setup Widget Principal --- (Integrando tudo)
class SetupWidget(QWidget):
    """Widget principal para gerenciamento de setups."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setups_dir = os.path.join(os.path.expanduser("~"), "RaceTelemetryAnalyzer", "setups")
        os.makedirs(self.setups_dir, exist_ok=True)
        self.all_setups: Dict[str, Dict[str, Any]] = {}

        layout = QVBoxLayout(self)

        # Barra de Ferramentas
        toolbar_layout = QHBoxLayout()
        self.new_setup_button = QPushButton("Novo Setup")
        self.import_setup_button = QPushButton("Importar Setup(s)")
        self.assistant_button = QPushButton("Assistente de Setup") # Novo botão
        toolbar_layout.addWidget(self.new_setup_button)
        toolbar_layout.addWidget(self.import_setup_button)
        toolbar_layout.addWidget(self.assistant_button)
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # Splitter Principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Painel Esquerdo (Lista/Cards)
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMinimumWidth(350)
        left_panel.setMaximumWidth(500)

        # Filtros (Placeholder)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtros:")) # Placeholder
        filter_layout.addStretch()
        left_layout.addLayout(filter_layout)

        # Área de scroll para os cards
        scroll_area_cards = QScrollArea()
        scroll_area_cards.setWidgetResizable(True)
        scroll_area_cards.setFrameShape(QFrame.Shape.NoFrame)
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area_cards.setWidget(self.cards_widget)
        left_layout.addWidget(scroll_area_cards)

        # Painel Direito (Detalhes)
        self.detail_panel = SetupDetailPanel()

        splitter.addWidget(left_panel)
        splitter.addWidget(self.detail_panel)
        splitter.setStretchFactor(1, 1) # Dar mais espaço para detalhes

        # Conectar sinais
        self.new_setup_button.clicked.connect(self._create_new_setup)
        self.import_setup_button.clicked.connect(self._import_setups)
        self.assistant_button.clicked.connect(self._open_assistant)
        self.detail_panel.export_requested.connect(self._export_setup) # Conecta sinal do painel

        # Carregar setups iniciais
        self.load_setups()

    def load_setups(self):
        """Carrega todos os arquivos .json do diretório de setups."""
        logger.info(f"Carregando setups de: {self.setups_dir}")
        self.all_setups = {}
        try:
            for filename in os.listdir(self.setups_dir):
                if filename.lower().endswith(".json"):
                    file_path = os.path.join(self.setups_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            setup_data = json.load(f)
                            # Garante que o setup tenha um ID
                            if "id" not in setup_data or not setup_data["id"]:
                                setup_data["id"] = f"setup_{uuid.uuid4().hex[:12]}"
                                # Salva o arquivo com o novo ID
                                self._save_setup_to_file(setup_data, file_path)

                            if setup_data["id"] in self.all_setups:
                                logger.warning(f"ID de setup duplicado encontrado: {setup_data['id']}. Ignorando {filename}")
                            else:
                                self.all_setups[setup_data["id"]] = setup_data
                    except json.JSONDecodeError:
                        logger.error(f"Erro ao decodificar JSON: {filename}")
                    except Exception as e:
                        logger.error(f"Erro ao carregar setup {filename}: {e}")
        except FileNotFoundError:
            logger.warning(f"Diretório de setups não encontrado: {self.setups_dir}")
        except Exception as e:
            logger.error(f"Erro ao listar diretório de setups: {e}")

        self._update_cards_display()
        self.detail_panel.update_setup_details(None) # Limpa detalhes

    def _update_cards_display(self):
        """Atualiza a exibição dos cards na lista."""
        # Limpa layout anterior
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        if not self.all_setups:
            self.cards_layout.addWidget(QLabel("Nenhum setup encontrado."))

        # Ordena setups (ex: por data, carro, pista)
        sorted_setups = sorted(self.all_setups.values(), key=lambda s: s.get("date", ""), reverse=True)

        for setup_data in sorted_setups:
            card = SetupCard(setup_data)
            card.setup_selected.connect(self.detail_panel.update_setup_details)
            card.setup_edited.connect(self._save_edited_setup)
            card.setup_exported.connect(self._export_setup)
            card.setup_deleted.connect(self._delete_setup)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch() # Empurra cards para cima

    def _create_new_setup(self):
        dialog = SetupEditDialog(None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_setup_data = dialog.get_setup_data()
            setup_id = new_setup_data.get("id")
            if setup_id:
                self.all_setups[setup_id] = new_setup_data
                file_path = os.path.join(self.setups_dir, f"{setup_id}.json")
                if self._save_setup_to_file(new_setup_data, file_path):
                    logger.info(f"Novo setup salvo: {setup_id}")
                    self._update_cards_display()
                    self.detail_panel.update_setup_details(new_setup_data) # Exibe o novo setup
                else:
                    # Remove da memória se não conseguiu salvar
                    del self.all_setups[setup_id]
            else:
                 logger.error("Falha ao criar novo setup: ID não gerado.")

    def _save_edited_setup(self, updated_data: Dict[str, Any]):
        setup_id = updated_data.get("id")
        if setup_id and setup_id in self.all_setups:
            self.all_setups[setup_id] = updated_data
            file_path = os.path.join(self.setups_dir, f"{setup_id}.json")
            if self._save_setup_to_file(updated_data, file_path):
                logger.info(f"Setup atualizado: {setup_id}")
                # Atualiza o painel de detalhes se este setup estiver selecionado
                if self.detail_panel.current_setup and self.detail_panel.current_setup.get("id") == setup_id:
                    self.detail_panel.update_setup_details(updated_data)
            else:
                # Reverter? Recarregar do arquivo?
                logger.error(f"Falha ao salvar alterações para o setup {setup_id}")
                QMessageBox.critical(self, "Erro ao Salvar", f"Não foi possível salvar as alterações no arquivo para o setup {setup_id}.")
                self.load_setups() # Recarrega tudo para garantir consistência
        else:
            logger.error(f"Falha ao salvar setup editado: ID inválido ou não encontrado ({setup_id})")

    def _import_setups(self):
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            self,
            "Importar Setup(s)",
            os.path.expanduser("~"), # Diretório inicial
            "Arquivos JSON (*.json);;Todos os Arquivos (*)"
        )

        imported_count = 0
        error_count = 0
        for file_path in file_paths:
            try:
                # Tenta ler o JSON para validar e obter ID (ou gerar um)
                with open(file_path, 'r', encoding='utf-8') as f:
                    setup_data = json.load(f)
                    setup_id = setup_data.get("id")
                    if not setup_id:
                        setup_id = f"setup_{uuid.uuid4().hex[:12]}"
                        # Não salva o ID no arquivo original importado

                # Define o nome do arquivo de destino usando o ID
                dest_filename = f"{setup_id}.json"
                dest_path = os.path.join(self.setups_dir, dest_filename)

                if os.path.exists(dest_path):
                     # Pergunta se deseja sobrescrever
                     reply = QMessageBox.question(self, "Setup Existente",
                                                  f"Um setup com ID '{setup_id}' já existe ({dest_filename}). Deseja sobrescrevê-lo com o arquivo importado '{os.path.basename(file_path)}'?",
                                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                                                  QMessageBox.StandardButton.No)
                     if reply == QMessageBox.StandardButton.Cancel:
                         error_count += (len(file_paths) - imported_count) # Cancela o resto
                         break
                     elif reply == QMessageBox.StandardButton.No:
                         logger.info(f"Importação pulada (setup existente): {os.path.basename(file_path)}")
                         continue # Pula este arquivo

                # Copia o arquivo para o diretório de setups
                shutil.copy2(file_path, dest_path)
                logger.info(f"Setup importado: {os.path.basename(file_path)} -> {dest_filename}")
                imported_count += 1
            except json.JSONDecodeError:
                logger.error(f"Erro ao importar: Arquivo JSON inválido - {os.path.basename(file_path)}")
                error_count += 1
            except Exception as e:
                logger.error(f"Erro ao importar {os.path.basename(file_path)}: {e}")
                error_count += 1

        if imported_count > 0:
            QMessageBox.information(self, "Importação Concluída", f"{imported_count} setup(s) importado(s) com sucesso.")
            self.load_setups() # Recarrega a lista
        elif error_count > 0:
             QMessageBox.warning(self, "Erro na Importação", f"Falha ao importar {error_count} arquivo(s). Verifique os logs para detalhes.")
        # else: Nenhum arquivo selecionado

    def _export_setup(self, setup_data: Dict[str, Any], file_path: str):
        """Salva os dados do setup no caminho especificado."""
        if self._save_setup_to_file(setup_data, file_path):
            logger.info(f"Setup exportado para: {file_path}")
            QMessageBox.information(self, "Exportação Concluída", f"Setup exportado com sucesso para:\n{file_path}")

    def _save_setup_to_file(self, setup_data: Dict[str, Any], file_path: str) -> bool:
        """Função auxiliar para salvar dados de setup em um arquivo JSON."""
        try:
            # Garante que o diretório de destino exista
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(setup_data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar setup no arquivo {file_path}: {e}")
            QMessageBox.critical(self, "Erro ao Salvar", f"Não foi possível salvar o setup em:\n{file_path}\n\nErro: {e}")
            return False

    def _delete_setup(self, setup_id: str):
        """Exclui o setup da memória e o arquivo correspondente."""
        if setup_id in self.all_setups:
            file_path = os.path.join(self.setups_dir, f"{setup_id}.json")
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Arquivo de setup excluído: {file_path}")
                else:
                    logger.warning(f"Arquivo para setup {setup_id} não encontrado para exclusão.")

                # Remove da memória
                del self.all_setups[setup_id]
                # Atualiza a exibição
                self._update_cards_display()
                # Limpa detalhes se o setup excluído estava selecionado
                if self.detail_panel.current_setup and self.detail_panel.current_setup.get("id") == setup_id:
                    self.detail_panel.update_setup_details(None)

            except Exception as e:
                logger.error(f"Erro ao excluir setup {setup_id}: {e}")
                QMessageBox.critical(self, "Erro ao Excluir", f"Não foi possível excluir o setup {setup_id}. Erro: {e}")
        else:
            logger.error(f"Tentativa de excluir setup não encontrado: {setup_id}")

    def _open_assistant(self):
        """Abre o diálogo do assistente de setup."""
        dialog = SetupAssistantDialog(self)
        # O diálogo é apenas informativo por enquanto, não retorna dados para aplicar
        dialog.exec()

# Exemplo de uso (em main.py ou similar)
# app = QApplication(sys.argv)
# main_window = QMainWindow()
# setup_view = SetupWidget()
# main_window.setCentralWidget(setup_view)
# main_window.show()
# sys.exit(app.exec())

