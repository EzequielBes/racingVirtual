"""
Widget para interação com o Coach Virtual baseado em LLM local (Ollama).
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel, 
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPalette, QColor

logger = logging.getLogger(__name__)

class CoachWidget(QWidget):
    """Interface de chat para interagir com o Coach Virtual."""
    # Sinal emitido quando o usuário envia uma mensagem
    user_message_sent = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Initializing CoachWidget...")
        self._setup_ui()
        logger.info("CoachWidget initialized.")

    def _setup_ui(self):
        """Configura a interface do widget de chat."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # --- Área de Exibição do Chat --- 
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setObjectName("chatDisplay") # Para estilização QSS
        # Estilo básico para diferenciar do fundo
        # palette = self.chat_display.palette()
        # palette.setColor(QPalette.ColorRole.Base, QColor("#292929")) # --bg-200
        # self.chat_display.setPalette(palette)
        layout.addWidget(self.chat_display, 1) # Expande

        # --- Área de Input --- 
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Pergunte ao Coach Virtual...")
        self.input_field.returnPressed.connect(self._send_message) # Envia com Enter
        input_layout.addWidget(self.input_field, 1)

        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self._send_message)
        self.send_button.setObjectName("accentButton")
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

    @pyqtSlot()
    def _send_message(self):
        """Pega o texto do input, emite o sinal e limpa o campo."""
        user_text = self.input_field.text().strip()
        if user_text:
            logger.debug(f"User message sent: {user_text}")
            self.add_message("Piloto", user_text)
            self.user_message_sent.emit(user_text)
            self.input_field.clear()
        else:
            logger.debug("Empty message submitted.")

    @pyqtSlot(str, str)
    def add_message(self, sender: str, message: str):
        """Adiciona uma mensagem formatada à área de exibição."""
        # Formatação simples (pode ser melhorada com HTML)
        formatted_message = f"<b>{sender}:</b> {message.replace(	"\n", "<br>")}"
        self.chat_display.append(formatted_message)
        # Auto-scroll para o fim
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())
        logger.debug(f"Message added to chat display: [{sender}] {message[:50]}...")

    @pyqtSlot()
    def clear_chat(self):
        """Limpa o histórico do chat."""
        self.chat_display.clear()
        logger.info("Chat display cleared.")

    @pyqtSlot(bool)
    def set_input_enabled(self, enabled: bool):
        """Habilita ou desabilita a área de input."""
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        if not enabled:
            self.input_field.setPlaceholderText("Aguardando resposta do Coach...")
        else:
            self.input_field.setPlaceholderText("Pergunte ao Coach Virtual...")

# Exemplo de uso (para teste)
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # Aplica um estilo básico para teste
    app.setStyleSheet("""
        QWidget { 
            background-color: #1A1A1A; 
            color: #E0E0E0; 
            font-size: 10pt;
        }
        QTextEdit#chatDisplay { 
            background-color: #292929; 
            border: 1px solid #404040;
        }
        QLineEdit { 
            background-color: #292929; 
            border: 1px solid #404040; 
            padding: 5px;
        }
        QPushButton { 
            background-color: #404040; 
            border: 1px solid #505050; 
            padding: 5px 10px;
            min-height: 20px;
        }
        QPushButton:hover { background-color: #505050; }
        QPushButton:pressed { background-color: #303030; }
        QPushButton#accentButton { background-color: #009700; color: white; }
        QPushButton#accentButton:hover { background-color: #33FF57; }
        QPushButton#accentButton:pressed { background-color: #007700; }
    """)
    
    window = CoachWidget()
    window.setWindowTitle("Coach Widget Test")
    window.setGeometry(200, 200, 400, 500)
    
    # Simula recebimento de mensagem
    def simulate_coach_response():
        window.add_message("Coach", "Olá! Analisei sua última volta. Notei que você freou um pouco tarde na curva 3. Tente frear 5 metros antes na próxima vez.")
        window.set_input_enabled(True)

    # Conecta o sinal de envio para simular resposta após um tempo
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(simulate_coach_response)
    
    def handle_user_message(msg):
        window.set_input_enabled(False)
        timer.start(2000) # Simula espera de 2 segundos
        
    window.user_message_sent.connect(handle_user_message)
    
    window.show()
    sys.exit(app.exec())

