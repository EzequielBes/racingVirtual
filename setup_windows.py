#!/usr/bin/env python3
"""
Script de instalação para Windows do Race Telemetry Analyzer.
Pode ser convertido para .exe usando PyInstaller.
"""

import os
import sys
import subprocess
import platform
import ctypes
from pathlib import Path

def is_admin():
    """Verifica se o script está sendo executado como administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Executa o script como administrador."""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def show_welcome():
    """Exibe a tela de boas-vindas."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🏁 RACE TELEMETRY ANALYZER 🏁              ║
║                                                              ║
║              Sistema de Análise de Telemetria Avançado       ║
║                                                              ║
║  🚀 Instalação Automática para Windows                      ║
║  📊 Análise em Tempo Real                                   ║
║  🎨 Interface Moderna e Intuitiva                           ║
║  📈 Gráficos Interativos                                    ║
╚══════════════════════════════════════════════════════════════╝

Este instalador irá:
✅ Verificar e instalar Python (se necessário)
✅ Instalar todas as dependências
✅ Configurar o ambiente
✅ Criar atalhos na área de trabalho
✅ Configurar para execução fácil

Pressione Enter para continuar...
    """)
    input()

def check_python():
    """Verifica se o Python está instalado."""
    print("🔍 Verificando Python...")
    
    try:
        version = sys.version_info
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} encontrado")
        return True
    except:
        print("❌ Python não encontrado")
        return False

def install_python():
    """Instala o Python se necessário."""
    print("📥 Instalando Python...")
    
    # URL do Python para download
    python_url = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
    
    print("📥 Baixando Python...")
    try:
        import urllib.request
        urllib.request.urlretrieve(python_url, "python_installer.exe")
        
        print("🔧 Executando instalador do Python...")
        subprocess.run(["python_installer.exe", "/quiet", "InstallAllUsers=1", "PrependPath=1"], check=True)
        
        # Remove o instalador
        os.remove("python_installer.exe")
        
        print("✅ Python instalado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao instalar Python: {e}")
        return False

def install_dependencies():
    """Instala as dependências."""
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
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"   ✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"   ❌ Erro ao instalar {dep}")
            return False
    
    print("✅ Todas as dependências instaladas!")
    return True

def create_shortcuts():
    """Cria atalhos na área de trabalho e menu iniciar."""
    print("🖥️ Criando atalhos...")
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        # Área de trabalho
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "Race Telemetry Analyzer.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{os.path.abspath("run.py")}"'
        shortcut.WorkingDirectory = os.path.abspath(".")
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        # Menu iniciar
        start_menu = winshell.start_menu()
        programs_path = os.path.join(start_menu, "Programs", "Race Telemetry Analyzer")
        os.makedirs(programs_path, exist_ok=True)
        
        start_shortcut_path = os.path.join(programs_path, "Race Telemetry Analyzer.lnk")
        start_shortcut = shell.CreateShortCut(start_shortcut_path)
        start_shortcut.Targetpath = sys.executable
        start_shortcut.Arguments = f'"{os.path.abspath("run.py")}"'
        start_shortcut.WorkingDirectory = os.path.abspath(".")
        start_shortcut.IconLocation = sys.executable
        start_shortcut.save()
        
        print("✅ Atalhos criados com sucesso!")
        return True
    except ImportError:
        print("⚠️ Não foi possível criar atalhos (winshell não disponível)")
        return False

def create_batch_file():
    """Cria arquivo .bat para execução fácil."""
    print("📝 Criando arquivo de execução...")
    
    batch_content = """@echo off
title Race Telemetry Analyzer
echo.
echo ========================================
echo    RACE TELEMETRY ANALYZER
echo ========================================
echo.
echo Iniciando sistema...
echo.

cd /d "%~dp0"
python run.py

echo.
echo Sistema finalizado.
pause
"""
    
    with open("Iniciar Analisador.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print("✅ Arquivo de execução criado!")

def create_directories():
    """Cria diretórios necessários."""
    print("📁 Criando diretórios...")
    
    directories = ["logs", "output", "temp", "config"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ {directory}")
    
    print("✅ Diretórios criados!")

def main():
    """Função principal."""
    # Verifica se é Windows
    if platform.system() != "Windows":
        print("❌ Este instalador é apenas para Windows!")
        input("Pressione Enter para sair...")
        return
    
    # Executa como administrador se necessário
    if not is_admin():
        print("🔐 Este instalador precisa de privilégios de administrador.")
        print("O Windows irá solicitar permissão...")
        run_as_admin()
        return
    
    show_welcome()
    
    # Verifica Python
    if not check_python():
        if not install_python():
            print("❌ Falha na instalação do Python")
            input("Pressione Enter para sair...")
            return
    
    # Instala dependências
    if not install_dependencies():
        print("❌ Falha na instalação das dependências")
        input("Pressione Enter para sair...")
        return
    
    # Cria diretórios
    create_directories()
    
    # Cria atalhos
    create_shortcuts()
    
    # Cria arquivo .bat
    create_batch_file()
    
    print("=" * 60)
    print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print()
    print("O Race Telemetry Analyzer foi instalado com sucesso!")
    print()
    print("Para executar o sistema:")
    print("✅ Clique no atalho na área de trabalho")
    print("✅ Ou execute 'Iniciar Analisador.bat'")
    print("✅ Ou use o menu Iniciar > Race Telemetry Analyzer")
    print()
    
    response = input("🚀 Deseja executar o sistema agora? (s/n): ").lower()
    
    if response in ['s', 'sim', 'y', 'yes']:
        print("🚀 Iniciando Race Telemetry Analyzer...")
        try:
            from src.main import main
            main()
        except Exception as e:
            print(f"❌ Erro ao executar: {e}")
            input("Pressione Enter para sair...")
    else:
        print("👋 Instalação concluída!")
        print("O sistema está pronto para uso!")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main() 