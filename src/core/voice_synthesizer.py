import pyttsx3
import logging
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
import queue
import time

logger = logging.getLogger(__name__)

class VoiceWorker(QObject):
    """Worker object to handle pyttsx3 engine in a separate thread."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    speaking_started = pyqtSignal(str)
    speaking_finished = pyqtSignal(str)

    def __init__(self, text_queue: queue.Queue):
        super().__init__()
        self.text_queue = text_queue
        self._running = True
        self.engine = None

    def run(self):
        """Initialize engine and process queue."""
        try:
            logger.info("Initializing pyttsx3 engine...")
            self.engine = pyttsx3.init()
            # Optional: Configure voice, rate, volume
            # voices = self.engine.getProperty("voices")
            # self.engine.setProperty("voice", voices[0].id) # Example: first voice
            self.engine.setProperty("rate", 180) # Adjust speed
            logger.info("pyttsx3 engine initialized.")
            
            # Connect engine signals if needed (can be complex with threading)
            # self.engine.connect("started-utterance", self.on_start)
            # self.engine.connect("finished-utterance", self.on_end)

        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 engine: {e}", exc_info=True)
            self.error.emit(f"Failed to initialize TTS engine: {e}")
            self.finished.emit()
            return

        while self._running:
            try:
                text_to_speak = self.text_queue.get(timeout=0.5) # Wait briefly for text
                if text_to_speak is None: # Sentinel value to stop
                    self._running = False
                    continue
                
                logger.info(f"Speaking: {text_to_speak}")
                self.speaking_started.emit(text_to_speak)
                self.engine.say(text_to_speak)
                self.engine.runAndWait() # Blocks this thread until speech is done
                self.speaking_finished.emit(text_to_speak)
                self.text_queue.task_done()
                
            except queue.Empty:
                continue # No text, loop again
            except Exception as e:
                logger.error(f"Error during text-to-speech processing: {e}", exc_info=True)
                self.error.emit(f"TTS Error: {e}")
                # Decide if we should stop or continue
                # self._running = False 

        logger.info("VoiceWorker thread finished.")
        self.finished.emit()

    # --- Engine signal handlers (Example - might need adjustments for threading) ---
    # def on_start(self, name):
    #     logger.debug(f"TTS started: {name}")
    #     # self.speaking_started.emit(name) # Be careful with signal emission from engine callbacks

    # def on_end(self, name, completed):
    #     logger.debug(f"TTS finished: {name}, Completed: {completed}")
    #     # self.speaking_finished.emit(name) # Be careful with signal emission from engine callbacks

    def stop(self):
        logger.info("Stopping VoiceWorker...")
        self._running = False
        self.text_queue.put(None) # Send sentinel to unblock queue.get()

class VoiceSynthesizer(QObject):
    """Manages the text-to-speech worker thread."""
    error_occurred = pyqtSignal(str)
    speech_started = pyqtSignal(str)
    speech_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_queue = queue.Queue()
        self.thread = QThread()
        self.worker = VoiceWorker(self.text_queue)

        self.worker.moveToThread(self.thread)

        # Connect worker signals to synthesizer signals or slots
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.error_occurred)
        self.worker.speaking_started.connect(self.speech_started)
        self.worker.speaking_finished.connect(self.speech_finished)

        # Start the thread event loop
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        logger.info("VoiceSynthesizer thread started.")

    @pyqtSlot(str)
    def speak(self, text: str):
        """Adds text to the speech queue."""
        if self.thread.isRunning():
            logger.debug(f"Adding to speech queue: {text}")
            self.text_queue.put(text)
        else:
            logger.warning("VoiceSynthesizer thread is not running. Cannot speak.")
            self.error_occurred.emit("TTS thread not running.")

    def stop(self):
        """Para a síntese de voz e limpa recursos."""
        logger.info("Requesting VoiceSynthesizer thread stop...")
        self._running = False
        self._stop_requested = True
        
        # Para o worker se existir
        if hasattr(self, 'worker') and self.worker:
            self.worker.stop()
        
        # Aguarda um pouco para a thread terminar naturalmente
        if hasattr(self, 'thread') and self.thread and self.thread.isRunning():
            self.thread.quit()
            if not self.thread.wait(1000):  # Aguarda até 1 segundo
                logger.warning("VoiceSynthesizer thread não terminou em tempo hábil")
                self.thread.terminate()
                self.thread.wait(1000)  # Aguarda mais um pouco
        
        # Limpa a engine
        if hasattr(self, 'engine') and self.engine:
            try:
                self.engine.stop()
            except Exception as e:
                logger.warning(f"Erro ao parar engine TTS: {e}")
        
        logger.info("VoiceSynthesizer stopped.")

    def __del__(self):
        """Destrutor para garantir limpeza adequada."""
        try:
            self.stop()
        except:
            pass  # Ignora erros no destrutor

# Example Usage (for testing within this module)
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QTextEdit

    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    text_edit = QTextEdit()
    text_edit.setPlaceholderText("Enter text to speak")
    button = QPushButton("Speak")
    log_view = QTextEdit()
    log_view.setReadOnly(True)
    layout.addWidget(QLabel("Text to Speak:"))
    layout.addWidget(text_edit)
    layout.addWidget(button)
    layout.addWidget(QLabel("Log:"))
    layout.addWidget(log_view)

    synthesizer = VoiceSynthesizer()

    def on_speak_click():
        text = text_edit.toPlainText()
        if text:
            synthesizer.speak(text)
            log_view.append(f"[UI] Queued: {text}")

    def log_error(msg):
        log_view.append(f"[ERROR] {msg}")
        
    def log_start(text):
        log_view.append(f"[TTS] Started: {text}")
        
    def log_finish(text):
        log_view.append(f"[TTS] Finished: {text}")

    button.clicked.connect(on_speak_click)
    synthesizer.error_occurred.connect(log_error)
    synthesizer.speech_started.connect(log_start)
    synthesizer.speech_finished.connect(log_finish)

    window.setWindowTitle("Voice Synthesizer Test")
    window.setGeometry(100, 100, 400, 300)
    window.show()

    # Ensure synthesizer stops when app quits
    app.aboutToQuit.connect(synthesizer.stop)

    sys.exit(app.exec())

