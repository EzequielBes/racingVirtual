#!/usr/bin/env python3
"""
Script de instalação e execução automática do Race Telemetry Analyzer.
Instala todas as dependências necessárias e executa o sistema.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_banner():
    """Exibe o banner do sistema."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🏁 RACE TELEMETRY ANALYZER 🏁              ║
║                                                              ║
║              Sistema de Análise de Telemetria Avançado       ║
║                                                              ║
║  🚀 Instalação e Configuração Automática                    ║
║  📊 Análise em Tempo Real                                   ║
║  🎨 Interface Moderna e Intuitiva                           ║
║  📈 Gráficos Interativos                                    ║
╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Verifica se a versão do Python é compatível."""
    print("🔍 Verificando versão do Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Erro: Python 3.8 ou superior é necessário!")
        print(f"   Versão atual: {sys.version}")
        print("   Por favor, atualize o Python e tente novamente.")
        input("Pressione Enter para sair...")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def install_pip():
    """Instala ou atualiza o pip."""
    print("📦 Verificando pip...")
    
    try:
        import pip
        print("✅ pip já está instalado")
        return True
    except ImportError:
        print("📥 Instalando pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
            print("✅ pip instalado com sucesso")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar pip")
            return False

def install_dependencies():
    """Instala todas as dependências necessárias."""
    print("📦 Instalando dependências...")
    
    dependencies = [
        "PyQt6>=6.4.0",
        "pyqtgraph>=0.13.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "scipy>=1.7.0",
        "requests>=2.25.0"
    ]
    
    for dep in dependencies:
        print(f"   📥 Instalando {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep, "--quiet"])
            print(f"   ✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"   ❌ Erro ao instalar {dep}")
            return False
    
    print("✅ Todas as dependências instaladas com sucesso!")
    return True

def create_directories():
    """Cria os diretórios necessários."""
    print("📁 Criando diretórios...")
    
    directories = [
        "logs",
        "output",
        "temp",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ Diretório {directory} criado")
    
    print("✅ Diretórios criados com sucesso!")

def create_requirements_file():
    """Cria o arquivo requirements.txt."""
    print("📝 Criando requirements.txt...")
    
    requirements_content = """# Race Telemetry Analyzer - Dependências
# Gerado automaticamente pelo instalador

PyQt6>=6.4.0
pyqtgraph>=0.13.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
scipy>=1.7.0
requests>=2.25.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    
    print("✅ requirements.txt criado!")

def create_launcher_script():
    """Cria um script de lançamento."""
    print("🚀 Criando script de lançamento...")
    
    if platform.system() == "Windows":
        launcher_content = """@echo off
echo Iniciando Race Telemetry Analyzer...
python run.py
pause
"""
        launcher_file = "iniciar_analisador.bat"
    else:
        launcher_content = """#!/bin/bash
echo "Iniciando Race Telemetry Analyzer..."
python3 run.py
"""
        launcher_file = "iniciar_analisador.sh"
        # Torna o script executável
        os.chmod(launcher_file, 0o755)
    
    with open(launcher_file, "w") as f:
        f.write(launcher_content)
    
    print(f"✅ Script de lançamento criado: {launcher_file}")

def create_desktop_shortcut():
    """Cria atalho na área de trabalho (Windows)."""
    if platform.system() == "Windows":
        print("🖥️ Criando atalho na área de trabalho...")
        
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop, "Race Telemetry Analyzer.lnk")
        
        try:
            import winshell
            from win32com.client import Dispatch
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{os.path.abspath("run.py")}"'
            shortcut.WorkingDirectory = os.path.abspath(".")
            shortcut.IconLocation = sys.executable
            shortcut.save()
            
            print("✅ Atalho na área de trabalho criado!")
        except ImportError:
            print("⚠️ Não foi possível criar atalho (winshell não disponível)")

def run_system():
    """Executa o sistema principal."""
    print("🚀 Iniciando Race Telemetry Analyzer...")
    print("=" * 60)
    
    try:
        # Importa e executa o sistema principal
        from src.main import main
        main()
    except KeyboardInterrupt:
        print("\n👋 Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar o sistema: {e}")
        print("💡 Verifique se todas as dependências foram instaladas corretamente")
        input("Pressione Enter para sair...")

def main():
    """Função principal do instalador."""
    print_banner()
    
    print("🎯 Iniciando processo de instalação e configuração...")
    print("=" * 60)
    
    # Verifica Python
    if not check_python_version():
        return
    
    # Instala pip
    if not install_pip():
        print("❌ Falha na instalação do pip")
        input("Pressione Enter para sair...")
        return
    
    # Instala dependências
    if not install_dependencies():
        print("❌ Falha na instalação das dependências")
        input("Pressione Enter para sair...")
        return
    
    # Cria diretórios
    create_directories()
    
    # Cria arquivos de configuração
    create_requirements_file()
    create_launcher_script()
    
    # Cria atalho (Windows)
    create_desktop_shortcut()
    
    print("=" * 60)
    print("🎉 Instalação concluída com sucesso!")
    print("=" * 60)
    
    # Pergunta se quer executar agora
    response = input("🚀 Deseja executar o Race Telemetry Analyzer agora? (s/n): ").lower()
    
    if response in ['s', 'sim', 'y', 'yes']:
        run_system()
    else:
        print("👋 Instalação concluída!")
        print("💡 Para executar o sistema, use:")
        if platform.system() == "Windows":
            print("   - Clique no atalho na área de trabalho")
            print("   - Ou execute: iniciar_analisador.bat")
        else:
            print("   - Execute: ./iniciar_analisador.sh")
        print("   - Ou execute: python run.py")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main() 