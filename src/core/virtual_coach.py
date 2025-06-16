"""
Core component for the Virtual Coach, interacting with a local LLM (Ollama).
"""

import logging
import ollama
from typing import Optional, Dict, Any, List

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)

# Default model to use (ensure it's pulled in Ollama: `ollama pull llama3` or similar)
DEFAULT_OLLAMA_MODEL = "llama3:latest" 

# --- Prompt Engineering --- 
# Base system prompt to guide the LLM's behavior as a racing coach
BASE_SYSTEM_PROMPT = """
You are a professional sim racing coach. Your role is to analyze telemetry data and user questions 
to provide concise, actionable advice to help the driver improve their lap times and consistency. 
Focus on specific aspects like braking points, racing lines, throttle/brake application, and setup adjustments. 
Be encouraging but direct. Use the provided context data about the current session/lap.
Avoid overly long explanations. Keep responses focused on the user's query and the data.
"""

def format_context_for_llm(telemetry_data: Optional[Dict[str, Any]], current_lap_id: Optional[str] = None) -> str:
    """Formats relevant telemetry data into a string for the LLM prompt context."""
    if not telemetry_data:
        return "No session data loaded."
    
    context_parts = []
    metadata = telemetry_data.get("metadata", {})
    details = telemetry_data.get("details", {})
    beacons = telemetry_data.get("beacons", [])
    
    context_parts.append("**Session Context:**")
    if metadata.get("track"): context_parts.append(f"- Track: {metadata["track"]}")
    if metadata.get("vehicle"): context_parts.append(f"- Vehicle: {metadata["vehicle"]}")
    if details.get("Total Laps"): context_parts.append(f"- Total Laps in Session: {details["Total Laps"]}")
    if details.get("Fastest Lap") and details.get("Fastest Time"):
        context_parts.append(f"- Fastest Lap: {details["Fastest Lap"]} ({details["Fastest Time"]:.3f}s)")
        
    # Add info about the currently selected/analyzed lap if available
    # TODO: Enhance this with more specific lap data (sector times, key events)
    if current_lap_id and beacons:
        try:
            # Assuming lap_id corresponds to index + 1 for beacons
            lap_idx = int(current_lap_id) - 1 
            if 0 <= lap_idx < len(beacons) - 1:
                start_beacon = beacons[lap_idx]
                end_beacon = beacons[lap_idx + 1]
                lap_time = end_beacon["time"] - start_beacon["time"]
                context_parts.append(f"\n**Current Lap Focus (Lap {current_lap_id}):**")
                context_parts.append(f"- Lap Time: {lap_time:.3f}s")
                # Add more data here: sector times, max/min speed, etc.
            else:
                 context_parts.append(f"\n**Current Lap Focus:** Lap {current_lap_id} (Data not fully available)")
        except (ValueError, IndexError):
             context_parts.append(f"\n**Current Lap Focus:** Lap {current_lap_id} (Error retrieving data)")
             
    return "\n".join(context_parts)

class CoachWorker(QObject):
    """Worker to handle Ollama communication in a separate thread."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    response_ready = pyqtSignal(str) # Signal with the LLM's response
    
    # Takes the user message and the formatted context
    def __init__(self, user_message: str, context: str, model: str = DEFAULT_OLLAMA_MODEL):
        super().__init__()
        self.user_message = user_message
        self.context = context
        self.model = model
        self._running = True

    def run(self):
        """Sends the request to Ollama and emits the response."""
        logger.info(f"CoachWorker started for model {self.model}.")
        try:
            # Construct messages for Ollama API
            messages = [
                {"role": "system", "content": BASE_SYSTEM_PROMPT},
                {"role": "user", "content": f"## Session Context\n{self.context}\n\n## My Question\n{self.user_message}"}
            ]
            
            logger.debug("Sending request to Ollama...")
            # Use ollama.chat for conversational context
            response = ollama.chat(
                model=self.model,
                messages=messages,
                # stream=False # Get full response at once
            )
            
            llm_response = response["message"]["content"]
            logger.info("Ollama response received.")
            logger.debug(f"LLM Response: {llm_response[:100]}...")
            self.response_ready.emit(llm_response)
            
        except ollama.ResponseError as e:
            logger.error(f"Ollama API Response Error: {e.error}", exc_info=True)
            self.error.emit(f"Erro na API Ollama: {e.error} (Verifique se o modelo 	'{self.model}	' está disponível e Ollama está rodando)")
        except Exception as e:
            logger.error(f"Error during Ollama communication: {e}", exc_info=True)
            self.error.emit(f"Erro de comunicação com Ollama: {e}")
        finally:
            logger.info("CoachWorker finished.")
            self.finished.emit()

    def stop(self):
        # Ollama client doesn't have an explicit stop for non-streaming requests
        logger.info("CoachWorker stopping (no explicit action needed for Ollama client).")
        self._running = False # In case run loop is added later

class VirtualCoach(QObject):
    """Manages interaction with the Ollama LLM via a worker thread."""
    coach_response = pyqtSignal(str)
    coach_error = pyqtSignal(str)
    coach_busy = pyqtSignal(bool) # True when processing, False when idle

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread: Optional[QThread] = None
        self.worker: Optional[CoachWorker] = None
        self.current_telemetry_data: Optional[Dict[str, Any]] = None
        self.current_lap_id: Optional[str] = None # Track which lap is in focus
        self.is_busy = False

    @pyqtSlot(dict)
    def update_telemetry_context(self, telemetry_data: Dict[str, Any]):
        """Updates the telemetry data used for context."""
        logger.info("Updating coach telemetry context.")
        self.current_telemetry_data = telemetry_data
        # Reset current lap focus when new data comes in?
        self.current_lap_id = None 

    @pyqtSlot(str)
    def update_lap_focus(self, lap_id: str):
        """Sets the currently focused lap for context."""
        logger.info(f"Updating coach lap focus to: {lap_id}")
        self.current_lap_id = lap_id

    @pyqtSlot(str)
    def process_user_message(self, user_message: str):
        """Processes a user message by querying the LLM in a thread."""
        if self.is_busy:
            logger.warning("Coach is already processing a request.")
            self.coach_error.emit("Coach ainda está processando a última pergunta.")
            return
            
        logger.info(f"Processing user message: {user_message[:50]}...")
        self.is_busy = True
        self.coach_busy.emit(True)
        
        # Format context based on current data
        context_str = format_context_for_llm(self.current_telemetry_data, self.current_lap_id)
        
        # Create worker and thread
        self.thread = QThread()
        self.worker = CoachWorker(user_message, context_str)
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.worker.response_ready.connect(self.coach_response)
        self.worker.error.connect(self.coach_error)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def _on_worker_finished(self):
        """Cleans up after the worker thread finishes."""
        logger.info("Coach worker finished signal received.")
        self.is_busy = False
        self.coach_busy.emit(False)
        if self.thread:
            self.thread.quit()
            # self.thread.wait(100) # Optional short wait
        self.worker = None
        self.thread = None

    def stop(self):
        """Stops any ongoing worker thread."""
        if self.worker and self.thread and self.thread.isRunning():
            logger.info("Requesting CoachWorker stop...")
            # Worker stop doesn't do much here, but good practice
            self.worker.stop() 
            self.thread.quit()
            # Force quit if it doesn't stop?
            # if not self.thread.wait(500):
            #     logger.warning("Coach thread did not stop gracefully. Terminating.")
            #     self.thread.terminate()
        self.is_busy = False
        self.coach_busy.emit(False)

    def __del__(self):
        self.stop()

# Example Usage (for testing within this module)
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    logging.basicConfig(level=logging.DEBUG)
    
    # Dummy data for context
    dummy_data = {
        "metadata": {"track": "Barcelona", "vehicle": "Porsche 992 GT3 R"},
        "details": {"Total Laps": 5, "Fastest Lap": 3, "Fastest Time": 107.2},
        "beacons": [
            {"time": 0.1, "name": "0, id=99", "lap_index": 0},
            {"time": 110.5, "name": "1, id=99", "lap_index": 1},
            {"time": 228.0, "name": "2, id=99", "lap_index": 2},
            {"time": 335.2, "name": "3, id=99", "lap_index": 3},
            {"time": 446.1, "name": "4, id=99", "lap_index": 4}
        ]
    }

    app = QApplication(sys.argv)
    
    # Create a simple test widget (or just use console output)
    test_widget = QWidget() 
    coach = VirtualCoach(test_widget) # Parent ensures cleanup?
    coach.update_telemetry_context(dummy_data)
    coach.update_lap_focus("2") # Focus on lap 2 (the slow one)

    @pyqtSlot(str)
    def handle_response(response):
        print(f"\n--- Coach Response ---\n{response}\n----------------------")
        # Quit after first response for simple test
        # app.quit()

    @pyqtSlot(str)
    def handle_error(error):
        print(f"\n--- Coach Error ---\n{error}\n-------------------")
        # Quit on error
        app.quit()
        
    @pyqtSlot(bool)
    def handle_busy(busy):
        print(f"[Coach Busy: {busy}]")

    coach.coach_response.connect(handle_response)
    coach.coach_error.connect(handle_error)
    coach.coach_busy.connect(handle_busy)

    # Send a test message
    print("Sending test message to coach...")
    coach.process_user_message("My lap 2 was slow, what happened?")
    
    print("Starting app event loop (waiting for response)...")
    # Keep app running until response or error
    # sys.exit(app.exec()) # Use this if you have a UI window
    app.exec() # Run event loop to allow thread communication
    print("App loop finished.")

