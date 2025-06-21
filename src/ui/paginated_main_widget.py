"""
Widget principal com sistema de paginação por contextos.
Organiza a interface em páginas temáticas para melhor usabilidade.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QFrame, QScrollArea, QSplitter, QGroupBox,
    QGridLayout, QStackedWidget, QListWidget, QListWidgetItem,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QSize

import os
from typing import Dict, List, Any, Optional


class ContextPage(QWidget):
    """Página base para diferentes contextos de análise."""
    
    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface básica da página."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Cabeçalho da página
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        header_layout = QVBoxLayout(header)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 8px;
            }
        """)
        header_layout.addWidget(title_label)
        
        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #cccccc;
                    line-height: 1.4;
                }
            """)
            desc_label.setWordWrap(True)
            header_layout.addWidget(desc_label)
        
        layout.addWidget(header)
        
        # Área de conteúdo (será sobrescrita pelas subclasses)
        self.content_area = QFrame()
        self.content_area.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        layout.addWidget(self.content_area)
        
        # Spacer para empurrar conteúdo para cima
        layout.addStretch()


class PaginatedMainWidget(QWidget):
    """Widget principal com sistema de paginação por contextos."""
    
    # Sinais para comunicação com a janela principal
    context_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_context = "overview"
        self.contexts = {}
        self.setup_ui()
        self.setup_contexts()
        
    def setup_ui(self):
        """Configura a interface principal."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Barra lateral de navegação
        self.nav_sidebar = self.create_navigation_sidebar()
        layout.addWidget(self.nav_sidebar)
        
        # Área de conteúdo principal
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #1a1a1a;
                border: none;
            }
        """)
        layout.addWidget(self.content_stack)
        
        # Configura proporções (sidebar: 280px, content: flexível)
        layout.setStretch(0, 0)  # Sidebar não estica
        layout.setStretch(1, 1)  # Content estica
        
    def create_navigation_sidebar(self):
        """Cria a barra lateral de navegação."""
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-right: 1px solid #404040;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Header
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background-color: #0078d4;
                border-bottom: 1px solid #404040;
            }
        """)
        header_layout = QVBoxLayout(header)
        
        logo_label = QLabel("🏁 Race Telemetry")
        logo_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 700;
                color: white;
                padding: 20px;
            }
        """)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo_label)
        
        layout.addWidget(header)
        
        # Lista de contextos
        self.context_list = QListWidget()
        self.context_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                font-size: 14px;
                padding: 8px;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 12px 16px;
                margin: 2px 8px;
                border-radius: 8px;
                color: #cccccc;
            }
            QListWidget::item:hover {
                background-color: #323232;
                color: white;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        self.context_list.currentRowChanged.connect(self.on_context_changed)
        layout.addWidget(self.context_list)
        
        return sidebar
    
    def setup_contexts(self):
        """Configura os diferentes contextos/páginas."""
        contexts_data = [
            {
                "id": "overview",
                "title": "Visão Geral",
                "description": "Dashboard principal com controles e métricas essenciais",
                "icon": "📊",
                "widget_class": "DashboardWidget"
            },
            {
                "id": "telemetry",
                "title": "📊 Telemetria",
                "description": "Visualização avançada de telemetria com gráficos interativos e análise detalhada",
                "icon": "📊",
                "widget_class": "ModernTelemetryWidget"
            },
            {
                "id": "analysis",
                "title": "Análise Avançada",
                "description": "Análises profundas e insights sobre performance",
                "icon": "🔍",
                "widget_class": "AdvancedAnalysisWidget"
            },
            {
                "id": "comparison",
                "title": "Comparação",
                "description": "Compare voltas, sessões e setups diferentes",
                "icon": "⚖️",
                "widget_class": "ComparisonWidget"
            },
            {
                "id": "setup",
                "title": "Gerenciador de Setups",
                "description": "Gerencie e compare diferentes configurações de carro",
                "icon": "🔧",
                "widget_class": "SetupWidget"
            },
            {
                "id": "realtime",
                "title": "Tempo Real",
                "description": "Monitoramento em tempo real de ACC/LMU",
                "icon": "⚡",
                "widget_class": "ACCLMUTelemetryWidget"
            },
            {
                "id": "coach",
                "title": "Coach Virtual",
                "description": "Feedback e dicas personalizadas para melhorar performance",
                "icon": "🎯",
                "widget_class": "CoachWidget"
            }
        ]
        
        for context_data in contexts_data:
            self.add_context(context_data)
    
    def add_context(self, context_data: Dict[str, Any]):
        """Adiciona um novo contexto à navegação."""
        context_id = context_data["id"]
        
        # Cria item na lista de navegação
        item = QListWidgetItem(f"{context_data['icon']} {context_data['title']}")
        item.setData(Qt.ItemDataRole.UserRole, context_id)
        self.context_list.addItem(item)
        
        # Cria a página do contexto
        page = ContextPage(context_data["title"], context_data["description"])
        
        # Adiciona o widget específico do contexto
        try:
            widget_class_name = context_data["widget_class"]
            if widget_class_name == "DashboardWidget":
                from src.ui.modern_dashboard_widget import DashboardWidget
                widget = DashboardWidget(self.parent())
            elif widget_class_name == "ModernTelemetryWidget":
                from src.ui.modern_telemetry_widget import ModernTelemetryWidget
                widget = ModernTelemetryWidget()
            elif widget_class_name == "AdvancedAnalysisWidget":
                from src.ui.advanced_analysis_widget import AdvancedAnalysisWidget
                widget = AdvancedAnalysisWidget()
            elif widget_class_name == "ComparisonWidget":
                from src.ui.comparison_widget import ComparisonWidget
                widget = ComparisonWidget()
            elif widget_class_name == "SetupWidget":
                from src.ui.setup_widget import SetupWidget
                widget = SetupWidget()
            elif widget_class_name == "ACCLMUTelemetryWidget":
                from src.ui.acc_lmu_telemetry_widget import ACCLMUTelemetryWidget
                widget = ACCLMUTelemetryWidget()
            elif widget_class_name == "CoachWidget":
                # Placeholder para o coach virtual
                widget = QLabel("Coach Virtual - Em desenvolvimento")
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                widget.setStyleSheet("color: #cccccc; font-size: 16px;")
            else:
                widget = QLabel(f"Widget {widget_class_name} não encontrado")
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                widget.setStyleSheet("color: #cccccc; font-size: 16px;")
            
            # Adiciona o widget à página
            page_layout = page.content_area.layout()
            if page_layout is None:
                page_layout = QVBoxLayout(page.content_area)
                page_layout.setContentsMargins(20, 20, 20, 20)
                page_layout.setSpacing(16)
            
            page_layout.addWidget(widget)
            
        except ImportError as e:
            # Widget não disponível, cria placeholder
            placeholder = QLabel(f"Widget {context_data['widget_class']} não disponível")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: #cccccc; font-size: 16px;")
            
            page_layout = page.content_area.layout()
            if page_layout is None:
                page_layout = QVBoxLayout(page.content_area)
                page_layout.setContentsMargins(20, 20, 20, 20)
                page_layout.setSpacing(16)
            
            page_layout.addWidget(placeholder)
        
        # Adiciona a página ao stack
        self.content_stack.addWidget(page)
        self.contexts[context_id] = {
            "data": context_data,
            "page": page,
            "widget": widget if 'widget' in locals() else None
        }
    
    def on_context_changed(self, index: int):
        """Chamado quando o contexto é alterado."""
        if index >= 0 and index < self.context_list.count():
            item = self.context_list.item(index)
            if item is not None:
                context_id = item.data(Qt.ItemDataRole.UserRole)
                self.current_context = context_id
                
                # Muda para a página correspondente
                self.content_stack.setCurrentIndex(index)
                
                # Emite sinal de mudança de contexto
                self.context_changed.emit(context_id)
    
    def get_current_context(self) -> str:
        """Retorna o contexto atual."""
        return self.current_context
    
    def get_context_widget(self, context_id: str):
        """Retorna o widget de um contexto específico."""
        if context_id in self.contexts:
            return self.contexts[context_id].get("widget")
        return None
    
    def switch_to_context(self, context_id: str):
        """Muda para um contexto específico."""
        for i in range(self.context_list.count()):
            item = self.context_list.item(i)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == context_id:
                self.context_list.setCurrentRow(i)
                break 