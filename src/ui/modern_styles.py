"""
Stylesheet moderno com design elegante para o Race Telemetry Analyzer.
Design minimalista com cores suaves e excelente usabilidade.
"""

def get_modern_stylesheet():
    """Retorna um stylesheet moderno com design elegante."""
    
    return """
    /* ===== RESET E CONFIGURAÇÃO GERAL ===== */
    * {
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        font-size: 10pt;
        color: #2c3e50;
    }
    
    QWidget {
        background-color: #f8f9fa;
        color: #2c3e50;
    }
    
    /* ===== JANELA PRINCIPAL ===== */
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                   stop:0 #f8f9fa, stop:1 #e9ecef);
        border: none;
    }
    
    /* ===== BARRA DE STATUS ===== */
    QStatusBar {
        background-color: #ffffff;
        color: #495057;
        border-top: 2px solid #e9ecef;
        padding: 8px;
        font-weight: 500;
    }
    
    QStatusBar QLabel {
        color: #495057;
        font-weight: 500;
        padding: 4px 8px;
        background-color: #f8f9fa;
        border-radius: 4px;
        border: 1px solid #dee2e6;
    }
    
    QProgressBar {
        border: 2px solid #dee2e6;
        border-radius: 10px;
        background-color: #ffffff;
        text-align: center;
        color: #495057;
        font-weight: 600;
        height: 20px;
    }
    
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #6c5ce7, stop:1 #a29bfe);
        border-radius: 8px;
    }
    
    /* ===== BOTÕES PRINCIPAIS ===== */
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #6c5ce7, stop:1 #5f3dc4);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 11pt;
        min-height: 24px;
        min-width: 80px;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #5f3dc4, stop:1 #4c3aa3);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(108, 92, 231, 0.3);
    }
    
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #4c3aa3, stop:1 #3d2f8a);
        transform: translateY(0px);
    }
    
    QPushButton:disabled {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #adb5bd, stop:1 #6c757d);
        color: #e9ecef;
    }
    
    /* Botões secundários */
    QPushButton[class="secondary"] {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #74b9ff, stop:1 #0984e3);
    }
    
    QPushButton[class="secondary"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #0984e3, stop:1 #0652DD);
    }
    
    /* Botões de sucesso */
    QPushButton[class="success"] {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #00b894, stop:1 #00a085);
    }
    
    QPushButton[class="success"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #00a085, stop:1 #008f7a);
    }
    
    /* Botões de perigo */
    QPushButton[class="danger"] {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #fd79a8, stop:1 #e84393);
    }
    
    QPushButton[class="danger"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #e84393, stop:1 #d63384);
    }
    
    /* Botões pequenos */
    QPushButton[class="small"] {
        padding: 6px 12px;
        font-size: 9pt;
        min-height: 18px;
        min-width: 60px;
    }
    
    /* ===== LABELS E TEXTOS ===== */
    QLabel {
        color: #2c3e50;
        font-weight: 500;
        padding: 4px;
    }
    
    QLabel[class="title"] {
        font-size: 18pt;
        font-weight: 800;
        color: #2c3e50;
        padding: 15px 0px;
    }
    
    QLabel[class="subtitle"] {
        font-size: 14pt;
        font-weight: 700;
        color: #34495e;
        padding: 8px 0px;
    }
    
    QLabel[class="metric"] {
        font-size: 16pt;
        font-weight: 800;
        color: #6c5ce7;
        padding: 12px;
        background-color: #ffffff;
        border-radius: 12px;
        border: 2px solid #e9ecef;
    }
    
    QLabel[class="metric"]:hover {
        border-color: #6c5ce7;
    }
    
    QLabel[class="status"] {
        font-size: 10pt;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 8px;
        border: 2px solid;
    }
    
    QLabel[class="status-success"] {
        background-color: #d4edda;
        color: #155724;
        border-color: #c3e6cb;
    }
    
    QLabel[class="status-warning"] {
        background-color: #fff3cd;
        color: #856404;
        border-color: #ffeaa7;
    }
    
    QLabel[class="status-error"] {
        background-color: #f8d7da;
        color: #721c24;
        border-color: #f5c6cb;
    }
    
    QLabel[class="status-neutral"] {
        background-color: #e9ecef;
        color: #495057;
        border-color: #dee2e6;
    }
    
    /* ===== CAMPOS DE ENTRADA ===== */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 10px;
        padding: 12px 16px;
        color: #2c3e50;
        font-size: 10pt;
        font-weight: 500;
        selection-background-color: #6c5ce7;
        selection-color: white;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #6c5ce7;
        background-color: #ffffff;
    }
    
    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {
        border-color: #adb5bd;
        background-color: #ffffff;
    }
    
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
        background-color: #f8f9fa;
        color: #6c757d;
        border-color: #e9ecef;
    }
    
    /* ===== COMBOBOX ===== */
    QComboBox {
        background-color: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 10px;
        padding: 10px 16px;
        color: #2c3e50;
        font-size: 10pt;
        font-weight: 500;
        min-height: 24px;
    }
    
    QComboBox:hover {
        border-color: #6c5ce7;
        background-color: #ffffff;
    }
    
    QComboBox:focus {
        border-color: #6c5ce7;
        background-color: #ffffff;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 30px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 6px solid #6c5ce7;
        margin-right: 8px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        border: 2px solid #6c5ce7;
        border-radius: 10px;
        selection-background-color: #6c5ce7;
        selection-color: white;
        outline: none;
    }
    
    QComboBox QAbstractItemView::item {
        padding: 10px 16px;
        color: #2c3e50;
        border-bottom: 1px solid #f8f9fa;
    }
    
    QComboBox QAbstractItemView::item:hover {
        background-color: #f8f9fa;
        color: #2c3e50;
    }
    
    QComboBox QAbstractItemView::item:selected {
        background-color: #6c5ce7;
        color: white;
    }
    
    /* ===== LISTAS E TABELAS ===== */
    QListWidget, QTreeWidget, QTableWidget {
        background-color: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 10px;
        color: #2c3e50;
        gridline-color: #e9ecef;
        selection-background-color: #6c5ce7;
        selection-color: white;
        outline: none;
    }
    
    QListWidget::item, QTreeWidget::item {
        padding: 10px;
        border-bottom: 1px solid #f8f9fa;
        border-radius: 6px;
        margin: 2px;
    }
    
    QListWidget::item:selected, QTreeWidget::item:selected {
        background-color: #6c5ce7;
        color: white;
        border-radius: 6px;
    }
    
    QListWidget::item:hover, QTreeWidget::item:hover {
        background-color: #f8f9fa;
        border-radius: 6px;
    }
    
    /* ===== SCROLLBARS ===== */
    QScrollBar:vertical {
        background-color: #f8f9fa;
        width: 14px;
        border-radius: 7px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #6c5ce7;
        border-radius: 7px;
        min-height: 30px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #5f3dc4;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        background-color: #f8f9fa;
        height: 14px;
        border-radius: 7px;
        margin: 0px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #6c5ce7;
        border-radius: 7px;
        min-width: 30px;
        margin: 2px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #5f3dc4;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    /* ===== GROUPBOX ===== */
    QGroupBox {
        font-weight: 700;
        font-size: 12pt;
        color: #2c3e50;
        border: 2px solid #dee2e6;
        border-radius: 12px;
        margin-top: 15px;
        padding-top: 15px;
        background-color: #ffffff;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 10px 0 10px;
        background-color: #ffffff;
        color: #6c5ce7;
        font-weight: 800;
    }
    
    /* ===== TAB WIDGET ===== */
    QTabWidget::pane {
        border: 2px solid #dee2e6;
        border-radius: 12px;
        background-color: #ffffff;
        margin-top: -2px;
    }
    
    QTabBar::tab {
        background-color: #f8f9fa;
        color: #495057;
        padding: 12px 24px;
        margin-right: 3px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        font-weight: 600;
        font-size: 11pt;
        min-width: 100px;
    }
    
    QTabBar::tab:selected {
        background-color: #6c5ce7;
        color: white;
        border-bottom: 3px solid #6c5ce7;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #e9ecef;
        color: #2c3e50;
    }
    
    /* ===== FRAME E CONTAINERS ===== */
    QFrame {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 10px;
    }
    
    QFrame[class="card"] {
        background-color: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 20px;
        margin: 8px;
    }
    
    QFrame[class="card"]:hover {
        border-color: #6c5ce7;
    }
    
    QFrame[class="highlight"] {
        background-color: #f8f9fa;
        border: 2px solid #6c5ce7;
        border-radius: 12px;
    }
    
    /* ===== GRÁFICOS ===== */
    QGraphicsView {
        background-color: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 10px;
    }
    
    /* ===== MENU ===== */
    QMenuBar {
        background-color: #ffffff;
        color: #2c3e50;
        border-bottom: 2px solid #dee2e6;
        font-weight: 600;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 10px 15px;
        border-radius: 6px;
        margin: 2px;
    }
    
    QMenuBar::item:selected {
        background-color: #6c5ce7;
        color: white;
    }
    
    QMenu {
        background-color: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 10px;
        padding: 8px;
    }
    
    QMenu::item {
        padding: 10px 20px;
        border-radius: 6px;
        margin: 2px;
    }
    
    QMenu::item:selected {
        background-color: #6c5ce7;
        color: white;
    }
    
    /* ===== TOOLBAR ===== */
    QToolBar {
        background-color: #ffffff;
        border-bottom: 2px solid #dee2e6;
        spacing: 8px;
        padding: 8px;
    }
    
    QToolButton {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 8px;
        margin: 2px;
    }
    
    QToolButton:hover {
        background-color: #f8f9fa;
        border-color: #6c5ce7;
    }
    
    QToolButton:pressed {
        background-color: #e9ecef;
    }
    
    /* ===== DOCK WIDGET ===== */
    QDockWidget {
        titlebar-close-icon: url(close.png);
        titlebar-normal-icon: url(undock.png);
    }
    
    QDockWidget::title {
        background-color: #6c5ce7;
        color: white;
        padding: 10px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        font-weight: 700;
    }
    
    /* ===== SPLITTER ===== */
    QSplitter::handle {
        background-color: #6c5ce7;
        border: none;
    }
    
    QSplitter::handle:horizontal {
        width: 3px;
    }
    
    QSplitter::handle:vertical {
        height: 3px;
    }
    
    QSplitter::handle:hover {
        background-color: #5f3dc4;
    }
    
    /* ===== MESSAGE BOX ===== */
    QMessageBox {
        background-color: #ffffff;
    }
    
    QMessageBox QPushButton {
        min-width: 100px;
        min-height: 30px;
    }
    
    /* ===== FILE DIALOG ===== */
    QFileDialog {
        background-color: #ffffff;
    }
    
    QFileDialog QListView, QFileDialog QTreeView {
        background-color: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 8px;
    }
    
    /* ===== CUSTOM WIDGETS ===== */
    QWidget[class="dashboard"] {
        background-color: #f8f9fa;
        border: none;
    }
    
    QWidget[class="telemetry"] {
        background-color: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 15px;
    }
    
    QWidget[class="analysis"] {
        background-color: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 15px;
    }
    
    QWidget[class="comparison"] {
        background-color: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 15px;
    }
    
    /* ===== RESPONSIVE DESIGN ===== */
    @media (max-width: 800px) {
        QPushButton {
            padding: 8px 16px;
            font-size: 9pt;
            min-height: 20px;
        }
        
        QLabel[class="title"] {
            font-size: 14pt;
        }
        
        QLabel[class="subtitle"] {
            font-size: 11pt;
        }
        
        QLabel[class="metric"] {
            font-size: 12pt;
            padding: 8px;
        }
    }
    """

def get_color_palette():
    """Retorna a paleta de cores do sistema."""
    return {
        'primary': '#6c5ce7',
        'primary_dark': '#5f3dc4',
        'secondary': '#74b9ff',
        'success': '#00b894',
        'warning': '#fdcb6e',
        'danger': '#fd79a8',
        'light': '#f8f9fa',
        'dark': '#2c3e50',
        'white': '#ffffff',
        'gray_100': '#f8f9fa',
        'gray_200': '#e9ecef',
        'gray_300': '#dee2e6',
        'gray_400': '#ced4da',
        'gray_500': '#adb5bd',
        'gray_600': '#6c757d',
        'gray_700': '#495057',
        'gray_800': '#343a40',
        'gray_900': '#212529'
    } 