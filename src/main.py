"""
Módulo principal do Race Telemetry Analyzer.
Inicializa a aplicação e a interface gráfica com layout baseado em DockWidgets,
integrando o analisador em tempo real.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional # Added Optional

# --- Configuração de Logging --- 
log_dir = os.path.join(os.path.expanduser("~"), "RaceTelemetryAnalyzer", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"rta_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler() # Mantém o log no console também
    ]
)
logger = logging.getLogger("race_telemetry_main")

# Adiciona o diretório pai ao path para permitir imports absolutos
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QMessageBox, QDockWidget, 
        QLabel, QVBoxLayout, QSplitter, QPushButton, QStatusBar, QProgressBar, # Added QPushButton, QStatusBar, QProgressBar
        QFileDialog # Added QFileDialog
    )
    from PyQt6.QtGui import QIcon, QFont, QPalette, QColor
    from PyQt6.QtCore import Qt, QSize, pyqtSlot # Added pyqtSlot
    
    # Imports dos widgets da UI
    from src.ui.modern_dashboard_widget import DashboardWidget
    from src.ui.modern_telemetry_widget import ModernTelemetryWidget # Widget de telemetria moderno
    from src.ui.comparison_widget import ComparisonWidget
    from src.ui.setup_widget import SetupWidget
    from src.ui.modern_styles import get_modern_stylesheet
    from src.ui.advanced_analysis_widget import AdvancedAnalysisWidget
    from src.ui.paginated_main_widget import PaginatedMainWidget
    # Import do parser LDX XML
    from src.parsers.ldx_xml_parser import parse_ldx_xml
    # Import do parser LD
    from src.parsers.ld_parser_wrapper import parse_ld_telemetry
    # Import Core components
    from src.core.realtime_analyzer import RealTimeAnalyzer
    from src.realtime.realtime_manager import RealtimeTelemetryManager # Importa o gerenciador de telemetria em tempo real
    
except ImportError as e:
    logger.critical(f"Erro fatal ao importar dependências PyQt, UI ou Core: {str(e)}", exc_info=True)
    print(f"Erro fatal ao importar dependências PyQt, UI ou Core: {str(e)}")
    print("Certifique-se de que PyQt6 e os módulos da UI/Core estão instalados e acessíveis.")
    try:
        app = QApplication([])
        QMessageBox.critical(None, "Erro Crítico", f"Não foi possível carregar componentes essenciais: {e}. Verifique a instalação e os logs.")
    except Exception:
        pass 
    sys.exit(1)


class MainWindow(QMainWindow):
    """Janela principal do Race Telemetry Analyzer com layout de Docks e análise integrada."""
    
    def __init__(self):
        super().__init__()
        logger.info("Inicializando MainWindow com Sistema de Paginação...")
        self.current_telemetry_data: Optional[Dict[str, Any]] = None
        
        self.setWindowTitle("Race Telemetry Analyzer - Professional")
        self.setMinimumSize(1400, 900)
        
        # Carrega e aplica o stylesheet moderno
        self.setStyleSheet(get_modern_stylesheet())
        
        # Inicializa Core Components
        self.analyzer = RealTimeAnalyzer(self)
        self.realtime_manager = RealtimeTelemetryManager() # Instancia o gerenciador de telemetria em tempo real
        
        self._setup_paginated_interface()
        self._setup_statusbar()
        self._connect_signals()
        
        self._center_window()
        logger.info("MainWindow inicializada com sucesso.")

    def _apply_stylesheet(self, filepath):
        """Carrega e aplica um arquivo QSS."""
        try:
            with open(filepath, "r") as f:
                style = f.read()
                self.setStyleSheet(style)
                logger.info(f"Stylesheet 	'{filepath}	' aplicado com sucesso.")
        except FileNotFoundError:
            logger.error(f"Arquivo de estilo não encontrado: {filepath}")
            self._setup_basic_dark_theme()
        except Exception as e:
            logger.error(f"Erro ao aplicar stylesheet: {e}", exc_info=True)
            self._setup_basic_dark_theme()

    def _setup_basic_dark_theme(self):
        """Define um tema escuro básico caso o QSS falhe."""
        logger.warning("Aplicando tema escuro básico como fallback.")
        # (Código do tema básico - sem alterações)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(palette)

    def _create_dock(self, title: str, widget: QWidget, area: Qt.DockWidgetArea) -> QDockWidget:
        """Cria e configura um QDockWidget."""
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.addDockWidget(area, dock)
        return dock

    def _setup_paginated_interface(self):
        """Configura a interface com sistema de paginação."""
        logger.info("Configurando Interface com Paginação...")
        
        # Cria o widget principal com paginação
        self.paginated_widget = PaginatedMainWidget(self)
        self.setCentralWidget(self.paginated_widget)
        
        # Obtém referências para os widgets principais
        self.dashboard_widget = self.paginated_widget.get_context_widget("overview")
        self.telemetry_visualizer = self.paginated_widget.get_context_widget("telemetry")
        self.comparison_widget = self.paginated_widget.get_context_widget("comparison")
        self.setup_widget = self.paginated_widget.get_context_widget("setup")
        self.advanced_analysis_widget = self.paginated_widget.get_context_widget("analysis")
        self.acc_lmu_widget = self.paginated_widget.get_context_widget("realtime")
        
        logger.info("Interface com paginação configurada.")

    def _setup_statusbar(self):
        """Configura a barra de status com widgets permanentes."""
        self.status_label = QLabel("Pronto")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False) # Hide initially
        
        statusbar = self.statusBar()
        if statusbar:
            statusbar.addWidget(self.status_label, 1) # Stretch factor 1
            statusbar.addPermanentWidget(self.progress_bar)

    def _connect_signals(self):
        """Conecta os sinais dos componentes core à UI."""
        logger.info("Conectando sinais...")
        # Analyzer Signals
        self.analyzer.analysis_started.connect(self.on_analysis_started)
        self.analyzer.analysis_finished.connect(self.on_analysis_finished)
        self.analyzer.analysis_error.connect(self.on_analysis_error)
        self.analyzer.analysis_feedback.connect(self.on_analysis_feedback)
        self.analyzer.analysis_progress.connect(self.on_analysis_progress)
        
        # Conecta o sinal de análise finalizada ao AdvancedAnalysisWidget
        if isinstance(self.advanced_analysis_widget, AdvancedAnalysisWidget):
            self.analyzer.analysis_finished.connect(self.advanced_analysis_widget.update_analysis_results)
            logger.info("Sinal de análise finalizada conectado ao AdvancedAnalysisWidget.")
        
        # Connect Dashboard actions (assuming DashboardWidget has these signals)
        if isinstance(self.dashboard_widget, DashboardWidget):
            try:
                self.dashboard_widget.load_file_requested.connect(self.load_telemetry_file)
                self.dashboard_widget.start_analysis_requested.connect(self.start_analysis)
                self.dashboard_widget.pause_analysis_requested.connect(self.analyzer.pause_analysis)
                self.dashboard_widget.resume_analysis_requested.connect(self.analyzer.resume_analysis)
                self.dashboard_widget.stop_analysis_requested.connect(self.analyzer.stop_analysis)
                self.dashboard_widget.start_realtime_requested.connect(self.on_start_realtime) # Conecta sinal de iniciar RT
                self.dashboard_widget.stop_realtime_requested.connect(self.on_stop_realtime)   # Conecta sinal de parar RT
                logger.info("Sinais do DashboardWidget conectados.")
            except AttributeError as e:
                 logger.warning(f"DashboardWidget não possui os sinais esperados para controle da análise: {e}")
        else:
            logger.warning("DashboardWidget não é da classe esperada, controles de análise não conectados.")
            
        logger.info("Sinais conectados.")

    # --- Slots for Core Component Signals --- 
    @pyqtSlot()
    def on_analysis_started(self):
        logger.info("Slot: Análise iniciada.")
        self.status_label.setText("Análise em andamento...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        # Update button states in dashboard (needs reference or signal)
        if isinstance(self.dashboard_widget, DashboardWidget):
            self.dashboard_widget.update_analysis_buttons(is_running=True, is_paused=False)

    @pyqtSlot()
    def on_analysis_finished(self):
        logger.info("Slot: Análise finalizada.")
        self.status_label.setText("Análise concluída.")
        self.progress_bar.setVisible(False)
        if isinstance(self.dashboard_widget, DashboardWidget):
            self.dashboard_widget.update_analysis_buttons(is_running=False, is_paused=False)

    @pyqtSlot(str)
    def on_analysis_error(self, message):
        logger.error(f"Slot: Erro na análise: {message}")
        self.status_label.setText(f"Erro na análise: {message}")
        self.progress_bar.setVisible(False)
        QMessageBox.warning(self, "Erro de Análise", message)
        if isinstance(self.dashboard_widget, DashboardWidget):
            self.dashboard_widget.update_analysis_buttons(is_running=False, is_paused=False)

    @pyqtSlot(str)
    def on_analysis_feedback(self, message):
        logger.info(f"Slot: Feedback recebido: {message}")
        self.status_label.setText(f"Feedback: {message}") 
        # TODO: Display feedback more prominently? (e.g., temporary overlay, log panel)

    @pyqtSlot(int, int)
    def on_analysis_progress(self, current_step, total_steps):
        # logger.debug(f"Slot: Progresso {current_step}/{total_steps}")
        self.progress_bar.setMaximum(total_steps)
        self.progress_bar.setValue(current_step)
        self.status_label.setText(f"Analisando Volta {current_step}/{total_steps}...")
        # Atualiza progresso no dashboard se o método existir
        if isinstance(self.dashboard_widget, DashboardWidget) and hasattr(self.dashboard_widget, 'update_progress'):
            try:
                self.dashboard_widget.update_progress(current_step, total_steps)
            except AttributeError:
                pass  # Método não existe, ignora

    # --- Action Slots --- 
    @pyqtSlot()
    def load_telemetry_file(self):
        logger.info("Slot: Carregar arquivo de telemetria solicitado.")
        # TODO: Support both .ldx (XML) and potentially .ld (binary) later
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir Arquivo de Telemetria",
            "", # Start directory
            "Arquivos LDX (*.ldx);;Arquivos LD (*.ld);;Arquivos CSV (*.csv);;Todos os Arquivos (*)"
        )
        if filepath:
            logger.info(f"Arquivo selecionado: {filepath}")
            try:
                if filepath.lower().endswith(".ldx"):
                    self.current_telemetry_data = parse_ldx_xml(filepath)
                    logger.info("Arquivo LDX XML parseado com sucesso.")
                elif filepath.lower().endswith(".ld"):
                    self.current_telemetry_data = parse_ld_telemetry(filepath)
                    logger.info("Arquivo LD parseado com sucesso.")
                elif filepath.lower().endswith(".csv"):
                    from src.parsers.csv_parser import parse_csv_telemetry
                    self.current_telemetry_data = parse_csv_telemetry(filepath)
                    logger.info("Arquivo CSV parseado com sucesso.")
                else:
                    raise ValueError("Formato de arquivo não suportado (apenas .ldx XML, .ld e .csv por enquanto).")
                    
                self.status_label.setText(f"Arquivo carregado: {os.path.basename(filepath)}")
                # Enable analysis start button
                if isinstance(self.dashboard_widget, DashboardWidget):
                     self.dashboard_widget.update_analysis_buttons(file_loaded=True, is_running=False)
                     # Atualiza informações do arquivo no dashboard
                     self.dashboard_widget.update_file_info(filepath, self.current_telemetry_data.get('metadata', {}))
                     # Atualiza métricas da sessão
                     self.dashboard_widget.update_session_metrics(self.current_telemetry_data.get('laps', []))
                     
                # Carrega dados no visualizador de telemetria
                if isinstance(self.telemetry_visualizer, ModernTelemetryWidget):
                    self.telemetry_visualizer.load_telemetry_data(self.current_telemetry_data)
                    # TODO: Load data into relevant widgets (Comparison, Visualizer)
                    if isinstance(self.comparison_widget, ComparisonWidget):
                        # Basic example: needs proper data structure adaptation
                        session_name = os.path.basename(filepath)
                        basic_lap_data = [{"lap_number": i+1, "lap_time": b["time"]} for i, b in enumerate(self.current_telemetry_data.get("beacons", []))]
                        # comparison_widget.load_telemetry_data({session_name: {"laps": basic_lap_data}})
                        logger.info("Dados básicos carregados no ComparisonWidget (exemplo).")
                        
            except Exception as e:
                logger.error(f"Erro ao carregar ou parsear arquivo {filepath}", exc_info=True)
                QMessageBox.critical(self, "Erro ao Carregar Arquivo", f"Não foi possível carregar ou ler o arquivo:\n{e}")
                self.current_telemetry_data = None
                if isinstance(self.dashboard_widget, DashboardWidget):
                     self.dashboard_widget.update_analysis_buttons(file_loaded=False, is_running=False)
        else:
            logger.info("Nenhum arquivo selecionado.")

    @pyqtSlot()
    def start_analysis(self):
        logger.info("Slot: Iniciar análise solicitado.")
        if self.current_telemetry_data:
            self.analyzer.start_analysis(self.current_telemetry_data)
        else:
            logger.warning("Tentativa de iniciar análise sem dados carregados.")
            QMessageBox.warning(self, "Nenhum Dado", "Carregue um arquivo de telemetria antes de iniciar a análise.")

    # --- Utility Methods --- 
    def _center_window(self):
        # (Código para centralizar - sem alterações)
        try:
            frame_geometry = self.frameGeometry()
            screen = QApplication.primaryScreen()
            if screen:
                 center_point = screen.availableGeometry().center()
                 frame_geometry.moveCenter(center_point)
                 self.move(frame_geometry.topLeft())
            else:
                 logger.warning("Não foi possível obter a tela primária para centralizar a janela.")
        except Exception as e:
             logger.error("Erro ao tentar centralizar a janela", exc_info=True)

    def closeEvent(self, event):
        """Sobrescreve o evento de fechamento para garantir limpeza."""
        logger.info("Fechando a aplicação...")
        
        try:
            # Para a análise de forma segura
            if hasattr(self, 'analyzer') and self.analyzer:
                self.analyzer.stop_analysis()
            
            # Para o gerenciador de tempo real
            if hasattr(self, 'realtime_manager') and self.realtime_manager:
                self.realtime_manager.stop_all_collectors()
            
            # Aguarda um pouco para as threads terminarem
            import time
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Erro durante o fechamento: {e}")
        
        super().closeEvent(event)

    @pyqtSlot(str)
    def on_start_realtime(self, game: str):
        logger.info(f"Slot: Iniciar telemetria em tempo real para {game} solicitado.")
        self.status_label.setText(f"Conectando ao {game}...")
        if isinstance(self.dashboard_widget, DashboardWidget) and hasattr(self.dashboard_widget, 'update_realtime_buttons'):
            self.dashboard_widget.update_realtime_buttons(is_running=True)
        self.realtime_manager.start_collector(game, self._handle_realtime_data)

    @pyqtSlot()
    def on_stop_realtime(self):
        logger.info("Slot: Parar telemetria em tempo real solicitado.")
        self.status_label.setText("Desconectando...")
        self.realtime_manager.stop_all_collectors()
        if isinstance(self.dashboard_widget, DashboardWidget) and hasattr(self.dashboard_widget, 'update_realtime_buttons'):
            self.dashboard_widget.update_realtime_buttons(is_running=False)
        self.status_label.setText("Pronto")

    def _handle_realtime_data(self, data: Dict[str, Any]):
        """Callback para processar dados de telemetria em tempo real."""
        # logger.debug(f"Dados RT recebidos: {data.get("speed", "N/A")} km/h")
        # Atualiza status da conexão no dashboard se os atributos existirem
        if isinstance(self.dashboard_widget, DashboardWidget):
            # Verifica se os atributos existem antes de tentar acessá-los
            if hasattr(self.dashboard_widget, 'connection_status') and hasattr(self.dashboard_widget.connection_status, 'set_status'):
                try:
                    self.dashboard_widget.connection_status.set_status("Ativa", "success")
                except AttributeError:
                    pass
                    
            if hasattr(self.dashboard_widget, 'simulator_status') and hasattr(self.dashboard_widget.simulator_status, 'set_status'):
                try:
                    self.dashboard_widget.simulator_status.set_status(data.get("game", "N/A"), "neutral")
                except AttributeError:
                    pass
                    
            if hasattr(self.dashboard_widget, 'track_status') and hasattr(self.dashboard_widget.track_status, 'set_status'):
                try:
                    self.dashboard_widget.track_status.set_status(data.get("track", "N/A"), "neutral")
                except AttributeError:
                    pass
                    
            if hasattr(self.dashboard_widget, 'car_status') and hasattr(self.dashboard_widget.car_status, 'set_status'):
                try:
                    self.dashboard_widget.car_status.set_status(data.get("car", "N/A"), "neutral")
                except AttributeError:
                    pass
            
            # Atualiza métricas rápidas se os métodos existirem
            if hasattr(self.dashboard_widget, 'total_laps') and hasattr(self.dashboard_widget.total_laps, 'set_status'):
                try:
                    self.dashboard_widget.total_laps.set_status(str(data.get("lap_number", 0)), "neutral")
                except AttributeError:
                    pass
                    
            if hasattr(self.dashboard_widget, 'best_lap') and hasattr(self.dashboard_widget.best_lap, 'set_status'):
                try:
                    self.dashboard_widget.best_lap.set_status(self.dashboard_widget.format_time(data.get("lap_time", 0)), "neutral")
                except AttributeError:
                    pass
                    
            if hasattr(self.dashboard_widget, 'avg_lap') and hasattr(self.dashboard_widget.avg_lap, 'set_status'):
                try:
                    self.dashboard_widget.avg_lap.set_status(self.dashboard_widget.format_time(data.get("lap_time", 0)), "neutral") # Placeholder
                except AttributeError:
                    pass
                    
            if hasattr(self.dashboard_widget, 'session_time') and hasattr(self.dashboard_widget.session_time, 'set_status'):
                try:
                    self.dashboard_widget.session_time.set_status(self.dashboard_widget.format_time(data.get("session_time", 0)), "neutral") # Placeholder
                except AttributeError:
                    pass

        # Passa os dados para o visualizador de telemetria
        if isinstance(self.telemetry_visualizer, ModernTelemetryWidget):
            # O TelemetryWidget precisa de um método para receber dados em tempo real
            # Vamos criar um método `update_realtime_telemetry` nele.
            self.telemetry_visualizer.update_realtime_telemetry(data)

        # TODO: Passar dados para o AdvancedAnalysisWidget para análise em tempo real
        # if isinstance(self.advanced_analysis_widget, AdvancedAnalysisWidget):
        #     self.advanced_analysis_widget.update_realtime_data(data)


def main():
    """Função principal com tratamento de exceção global."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical("Exceção não tratada capturada!", exc_info=(exc_type, exc_value, exc_traceback))
        try:
             app_instance = QApplication.instance()
             if app_instance:
                  error_message = f"Ocorreu um erro inesperado:\n\n{exc_value}\n\nConsulte o arquivo de log para detalhes:\n{log_file}"
                  QMessageBox.critical(None, "Erro Inesperado", error_message)
        except Exception as msg_err:
             logger.error(f"Erro ao exibir a caixa de diálogo de erro: {msg_err}")
        finally:
             sys.exit(1)

    sys.excepthook = handle_exception

    try:
        logger.info("Iniciando Race Telemetry Analyzer...")
        app = QApplication(sys.argv)
        app.setApplicationName("Race Telemetry Analyzer")
        
        window = MainWindow()
        window.show()
        
        logger.info("Aplicação iniciada, entrando no loop de eventos.")
        exit_code = app.exec()
        logger.info(f"Loop de eventos finalizado com código: {exit_code}")
        sys.exit(exit_code)
    
    except Exception as e:
        logger.critical(f"Erro crítico irrecuperável na inicialização da aplicação: {str(e)}", exc_info=True)
        print(f"Erro crítico irrecuperável na inicialização da aplicação: {str(e)}")
        try:
             app = QApplication([])
             QMessageBox.critical(None, "Erro Crítico", f"Erro irrecuperável na inicialização: {e}. Verifique os logs.")
        except Exception:
             pass
        sys.exit(1)

if __name__ == "__main__":
    # Adiciona o diretório core ao path se executando diretamente
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    main()


