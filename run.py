#!/usr/bin/env python3
"""
Script principal para executar o Race Telemetry Analyzer.
Inclui verificações de dependências e tratamento de erros melhorado.
"""

import sys
import os
import subprocess
import importlib

def check_dependencies():
    """Verifica se todas as dependências necessárias estão instaladas."""
    required_packages = [
        'PyQt6',
        'pyqtgraph', 
        'numpy',
        'pandas',
        'matplotlib',
        'scipy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} - FALTANDO")
    
    if missing_packages:
        print(f"\nDependências faltando: {', '.join(missing_packages)}")
        print("Instalando dependências faltantes...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '--user', *missing_packages
            ])
            print("Dependências instaladas com sucesso!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erro ao instalar dependências: {e}")
            return False
    
    return True

def main():
    """Função principal."""
    print("Race Telemetry Analyzer - Inicializando...")
    print("=" * 50)
    
    # Verifica dependências
    if not check_dependencies():
        print("Erro: Não foi possível instalar todas as dependências.")
        sys.exit(1)
    
    print("\nIniciando aplicação...")
    
    try:
        # Adiciona o diretório src ao path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        sys.path.insert(0, src_path)
        
        # Importa e executa o main
        from main import main as run_app
        run_app()
        
    except ImportError as e:
        print(f"Erro de importação: {e}")
        print("Verifique se todos os módulos estão presentes.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
