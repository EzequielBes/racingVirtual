import logging
import time
from typing import Dict, List, Any

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)

# --- Simple Rule Examples --- 
# These would ideally be more complex and potentially loaded from config
# For now, just check lap times against a threshold.
LAP_TIME_THRESHOLD_SLOW = 115.0 # Example: 1:55.000
LAP_TIME_THRESHOLD_FAST = 108.0 # Example: 1:48.000

class RealTimeAnalyzerWorker(QObject):
    """Worker object to perform analysis in a separate thread."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    feedback_detected = pyqtSignal(str) # Signal for feedback messages
    progress_update = pyqtSignal(int, int) # Current step, total steps

    def __init__(self, telemetry_data: Dict[str, Any]):
        super().__init__()
        self.telemetry_data = telemetry_data
        self._running = True
        self._paused = False

    def run(self):
        """Processes the loaded telemetry data."""
        logger.info("RealTimeAnalyzerWorker thread started.")
        try:
            beacons = self.telemetry_data.get("beacons", [])
            if not beacons or len(beacons) < 2:
                logger.warning("Not enough beacon data for lap time analysis.")
                self.error.emit("Dados de beacon insuficientes para análise.")
                self.finished.emit()
                return

            total_laps = len(beacons) -1 # Number of full laps
            self.progress_update.emit(0, total_laps)

            for i in range(total_laps):
                if not self._running: break
                while self._paused:
                    if not self._running: break
                    time.sleep(0.1) # Sleep while paused
                
                start_beacon = beacons[i]
                end_beacon = beacons[i+1]
                lap_number = i + 1 # Laps are usually 1-indexed for users
                
                lap_time = end_beacon["time"] - start_beacon["time"]
                lap_time_str = f"{lap_time:.3f}s"
                logger.info(f"Analyzing Lap {lap_number}: Time = {lap_time_str}")

                # --- Apply Simple Rules --- 
                if lap_time > LAP_TIME_THRESHOLD_SLOW:
                    feedback = f"Volta {lap_number} foi lenta ({lap_time_str}). Verifique os setores."
                    logger.info(f"Feedback generated: {feedback}")
                    self.feedback_detected.emit(feedback)
                    time.sleep(0.5) # Add a small delay after feedback
                    
                elif lap_time < LAP_TIME_THRESHOLD_FAST:
                    feedback = f"Volta {lap_number} excepcional! ({lap_time_str}). Ótimo ritmo!"
                    logger.info(f"Feedback generated: {feedback}")
                    self.feedback_detected.emit(feedback)
                    time.sleep(0.5)
                
                # TODO: Add more rules based on other data (requires parsing .ld file)
                # e.g., check speed at apex, throttle application, braking points

                self.progress_update.emit(lap_number, total_laps)
                time.sleep(1) # Simulate processing time or playback speed

        except Exception as e:
            logger.error(f"Error during telemetry analysis: {e}", exc_info=True)
            self.error.emit(f"Erro na análise: {e}")
        finally:
            logger.info("RealTimeAnalyzerWorker thread finished.")
            self.finished.emit()

    def stop(self):
        logger.info("Stopping RealTimeAnalyzerWorker...")
        self._running = False
        self._paused = False # Ensure it's not stuck paused

    def pause(self):
        logger.info("Pausing RealTimeAnalyzerWorker...")
        self._paused = True

    def resume(self):
        logger.info("Resuming RealTimeAnalyzerWorker...")
        self._paused = False

class RealTimeAnalyzer(QObject):
    """Manages the telemetry analysis worker thread."""
    analysis_error = pyqtSignal(str)
    analysis_feedback = pyqtSignal(str)
    analysis_progress = pyqtSignal(int, int)
    analysis_finished = pyqtSignal()
    analysis_started = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread: Optional[QThread] = None
        self.worker: Optional[RealTimeAnalyzerWorker] = None
        self.is_running = False

    def start_analysis(self, telemetry_data: Dict[str, Any]):
        """Starts the analysis in a new thread."""
        if self.is_running:
            logger.warning("Analysis is already running.")
            self.analysis_error.emit("Análise já em andamento.")
            return
            
        if not telemetry_data or not telemetry_data.get("beacons"):
             logger.error("No telemetry data provided or data is invalid.")
             self.analysis_error.emit("Dados de telemetria inválidos ou ausentes.")
             return

        self.thread = QThread()
        self.worker = RealTimeAnalyzerWorker(telemetry_data)
        self.worker.moveToThread(self.thread)

        # Connect worker signals
        self.worker.finished.connect(self._on_analysis_finished)
        self.worker.error.connect(self.analysis_error)
        self.worker.feedback_detected.connect(self.analysis_feedback)
        self.worker.progress_update.connect(self.analysis_progress)
        
        # Connect thread signals
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
        self.is_running = True
        self.analysis_started.emit()
        logger.info("RealTimeAnalyzer thread started.")

    def _on_analysis_finished(self):
        logger.info("Analysis finished signal received.")
        self.is_running = False
        if self.thread:
            self.thread.quit()
            # self.thread.wait(500) # Optional wait
        self.analysis_finished.emit()
        self.thread = None # Clean up
        self.worker = None

    def stop_analysis(self):
        """Requests the analysis thread to stop."""
        if self.worker and self.is_running:
            logger.info("Requesting RealTimeAnalyzer thread stop...")
            self.worker.stop()
        else:
            logger.info("Analysis not running or worker not available.")
            
    def pause_analysis(self):
        if self.worker and self.is_running:
             self.worker.pause()
             
    def resume_analysis(self):
         if self.worker and self.is_running:
             self.worker.resume()

    def __del__(self):
        # Ensure thread is stopped on deletion
        self.stop_analysis()

# Example Usage (for testing within this module)
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QTextEdit, QProgressBar, QLabel

    logging.basicConfig(level=logging.DEBUG)

    # Dummy data similar to parsed LDX
    dummy_data = {
        "beacons": [
            {"time": 0.1, "name": "0, id=99", "lap_index": 0},
            {"time": 110.5, "name": "1, id=99", "lap_index": 1}, # Lap 1: 110.4s (OK)
            {"time": 228.0, "name": "2, id=99", "lap_index": 2}, # Lap 2: 117.5s (Slow)
            {"time": 335.2, "name": "3, id=99", "lap_index": 3}, # Lap 3: 107.2s (Fast)
            {"time": 446.1, "name": "4, id=99", "lap_index": 4}  # Lap 4: 110.9s (OK)
        ],
        "details": {"Total Laps": 5, "Fastest Lap": 3, "Fastest Time": 107.2},
        "metadata": {"format": "ldx_xml"}
    }

    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    
    log_view = QTextEdit()
    log_view.setReadOnly(True)
    progress_bar = QProgressBar()
    start_button = QPushButton("Start Analysis")
    pause_button = QPushButton("Pause Analysis")
    resume_button = QPushButton("Resume Analysis")
    stop_button = QPushButton("Stop Analysis")

    layout.addWidget(QLabel("Analysis Log & Feedback:"))
    layout.addWidget(log_view)
    layout.addWidget(progress_bar)
    layout.addWidget(start_button)
    layout.addWidget(pause_button)
    layout.addWidget(resume_button)
    layout.addWidget(stop_button)

    analyzer = RealTimeAnalyzer()
    synthesizer = VoiceSynthesizer() # Also test voice output

    def log_message(msg):
        log_view.append(f"[ANALYSIS] {msg}")
        synthesizer.speak(msg) # Speak the feedback

    def log_error(msg):
        log_view.append(f"[ERROR] {msg}")
        
    def update_progress(current, total):
        log_view.append(f"[PROGRESS] Lap {current}/{total}")
        progress_bar.setMaximum(total)
        progress_bar.setValue(current)
        
    def on_finish():
        log_view.append("[INFO] Analysis Finished.")
        progress_bar.setValue(progress_bar.maximum())
        start_button.setEnabled(True)
        pause_button.setEnabled(False)
        resume_button.setEnabled(False)
        stop_button.setEnabled(False)
        
    def on_start():
        log_view.append("[INFO] Analysis Started.")
        start_button.setEnabled(False)
        pause_button.setEnabled(True)
        resume_button.setEnabled(False)
        stop_button.setEnabled(True)
        progress_bar.setValue(0)

    analyzer.analysis_feedback.connect(log_message)
    analyzer.analysis_error.connect(log_error)
    analyzer.analysis_progress.connect(update_progress)
    analyzer.analysis_finished.connect(on_finish)
    analyzer.analysis_started.connect(on_start)

    start_button.clicked.connect(lambda: analyzer.start_analysis(dummy_data))
    stop_button.clicked.connect(analyzer.stop_analysis)
    pause_button.clicked.connect(lambda: (analyzer.pause_analysis(), pause_button.setEnabled(False), resume_button.setEnabled(True)))
    resume_button.clicked.connect(lambda: (analyzer.resume_analysis(), pause_button.setEnabled(True), resume_button.setEnabled(False)))

    # Initial state
    pause_button.setEnabled(False)
    resume_button.setEnabled(False)
    stop_button.setEnabled(False)

    window.setWindowTitle("RealTime Analyzer Test")
    window.setGeometry(100, 100, 500, 400)
    window.show()

    # Ensure threads stop when app quits
    app.aboutToQuit.connect(analyzer.stop_analysis)
    app.aboutToQuit.connect(synthesizer.stop)

    sys.exit(app.exec())

