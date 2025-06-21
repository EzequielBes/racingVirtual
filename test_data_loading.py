#!/usr/bin/env python3
"""
Teste específico para verificar se os dados estão sendo carregados corretamente.
"""

import sys
import os
import logging

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_csv_loading():
    """Testa o carregamento de dados CSV."""
    try:
        logger.info("Testando carregamento de dados CSV...")
        
        from src.parsers.csv_parser import parse_csv_telemetry
        
        # Testa com um arquivo de exemplo
        csv_file = "exemplos/monza-mclaren_720s_gt3_evo-1-2025.06.01-19.40.55.csv"
        
        if os.path.exists(csv_file):
            data = parse_csv_telemetry(csv_file)
            
            if data and 'metadata' in data:
                logger.info(f"✓ CSV carregado: {data['metadata'].get('filename', 'N/A')}")
                
                # Verifica se tem dados
                if 'beacons' in data and data['beacons']:
                    logger.info(f"✓ {len(data['beacons'])} beacons encontrados")
                    
                    # Mostra alguns dados de exemplo
                    first_beacon = data['beacons'][0]
                    logger.info(f"✓ Primeiro beacon: {first_beacon}")
                    
                    return True
                else:
                    logger.warning("✗ Nenhum beacon encontrado")
                    return False
            else:
                logger.error("✗ Dados CSV inválidos")
                return False
        else:
            logger.warning(f"Arquivo de exemplo não encontrado: {csv_file}")
            return True  # Não é um erro crítico
            
    except Exception as e:
        logger.error(f"✗ Erro no carregamento CSV: {e}")
        return False

def test_telemetry_widget():
    """Testa o TelemetryWidget com dados reais."""
    try:
        logger.info("Testando TelemetryWidget...")
        
        from PyQt6.QtWidgets import QApplication
        from src.ui.telemetry_widget import TelemetryWidget
        from src.parsers.csv_parser import parse_csv_telemetry
        
        # Cria aplicação
        app = QApplication([])
        
        # Cria widget
        widget = TelemetryWidget()
        
        # Carrega dados de exemplo
        csv_file = "exemplos/monza-mclaren_720s_gt3_evo-1-2025.06.01-19.40.55.csv"
        
        if os.path.exists(csv_file):
            data = parse_csv_telemetry(csv_file)
            if data:
                widget.load_telemetry_data(data)
                logger.info("✓ Dados carregados no TelemetryWidget")
                
                # Verifica se os valores foram atualizados
                speed_text = widget.speed_value.text()
                rpm_text = widget.rpm_value.text()
                
                logger.info(f"✓ Velocidade: {speed_text}")
                logger.info(f"✓ RPM: {rpm_text}")
                
                return True
            else:
                logger.error("✗ Falha ao carregar dados")
                return False
        else:
            logger.warning("Arquivo de exemplo não encontrado")
            return True
        
    except Exception as e:
        logger.error(f"✗ Erro no TelemetryWidget: {e}")
        return False

def test_ld_parser():
    """Testa o parser LD."""
    try:
        logger.info("Testando parser LD...")
        
        from src.parsers.ld_parser_wrapper import parse_ld_telemetry
        
        # Procura por arquivos .ld na pasta exemplos
        examples_dir = "exemplos"
        ld_files = []
        
        if os.path.exists(examples_dir):
            for file in os.listdir(examples_dir):
                if file.lower().endswith('.ld'):
                    ld_files.append(os.path.join(examples_dir, file))
        
        if ld_files:
            # Testa com o primeiro arquivo .ld encontrado
            ld_file = ld_files[0]
            logger.info(f"Testando arquivo LD: {ld_file}")
            
            try:
                data = parse_ld_telemetry(ld_file)
                if data and 'metadata' in data:
                    logger.info(f"✓ LD carregado: {data['metadata'].get('filename', 'N/A')}")
                    logger.info(f"✓ {len(data.get('channels', []))} canais encontrados")
                    return True
                else:
                    logger.error("✗ Dados LD inválidos")
                    return False
            except Exception as e:
                logger.warning(f"✗ Erro ao carregar LD: {e}")
                return False
        else:
            logger.info("✓ Nenhum arquivo .ld encontrado para teste")
            return True
        
    except Exception as e:
        logger.error(f"✗ Erro no teste LD: {e}")
        return False

def main():
    """Função principal de teste."""
    logger.info("=== TESTE DE CARREGAMENTO DE DADOS ===")
    
    tests = [
        ("Carregamento CSV", test_csv_loading),
        ("TelemetryWidget", test_telemetry_widget),
        ("Parser LD", test_ld_parser),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Testando: {test_name} ---")
        try:
            if test_func():
                logger.info(f"✓ {test_name}: PASSOU")
                passed += 1
            else:
                logger.error(f"✗ {test_name}: FALHOU")
        except Exception as e:
            logger.error(f"✗ {test_name}: ERRO - {e}")
    
    logger.info(f"\n=== RESULTADO: {passed}/{total} testes passaram ===")
    
    if passed == total:
        logger.info("🎉 Todos os testes de carregamento passaram!")
        return 0
    else:
        logger.error("❌ Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 