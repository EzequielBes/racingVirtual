#!/usr/bin/env python3
"""
Script para gerar executável do Race Telemetry Analyzer usando PyInstaller.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def install_pyinstaller():
    """Instala o PyInstaller se necessário."""
    print("📦 Verificando PyInstaller...")
    
    try:
        import PyInstaller
        print("✅ PyInstaller já está instalado")
        return True
    except ImportError:
        print("📥 Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller instalado com sucesso")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar PyInstaller")
            return False

def create_spec_file():
    """Cria o arquivo .spec para o PyInstaller."""
    print("📝 Criando arquivo de especificação...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ui/styles.qss', 'src/ui'),
        ('src/ui/modern_styles.py', 'src/ui'),
        ('exemplos', 'exemplos'),
        ('docs', 'docs'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'pyqtgraph',
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'requests',
        'src.main',
        'src.ui.modern_dashboard_widget',
        'src.ui.modern_telemetry_widget',
        'src.ui.comparison_widget',
        'src.ui.setup_widget',
        'src.ui.advanced_analysis_widget',
        'src.ui.paginated_main_widget',
        'src.core.realtime_analyzer',
        'src.parsers.csv_parser',
        'src.parsers.ld_parser_wrapper',
        'src.parsers.ldx_xml_parser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Race Telemetry Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open("RaceTelemetryAnalyzer.spec", "w") as f:
        f.write(spec_content)
    
    print("✅ Arquivo .spec criado!")

def build_executable():
    """Constrói o executável."""
    print("🔨 Construindo executável...")
    
    try:
        # Usa o arquivo .spec criado
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "RaceTelemetryAnalyzer.spec"
        ])
        
        print("✅ Executável construído com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao construir executável: {e}")
        return False

def create_installer_script():
    """Cria um script de instalação simples."""
    print("📝 Criando script de instalação...")
    
    if platform.system() == "Windows":
        installer_content = """@echo off
title Race Telemetry Analyzer - Instalador
echo.
echo ========================================
echo    RACE TELEMETRY ANALYZER
echo ========================================
echo.
echo Instalador Automático
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python não encontrado. Baixando e instalando...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile 'python_installer.exe'"
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
    echo Python instalado!
)

echo.
echo Instalando dependências...
python -m pip install --upgrade pip
python -m pip install PyQt6 pyqtgraph numpy pandas matplotlib scipy requests

echo.
echo Criando diretórios...
mkdir logs 2>nul
mkdir output 2>nul
mkdir temp 2>nul
mkdir config 2>nul

echo.
echo ========================================
echo Instalação concluída!
echo ========================================
echo.
echo Para executar o sistema:
echo - Execute: python run.py
echo - Ou use o instalador automático
echo.
pause
"""
        installer_file = "Instalar.bat"
    else:
        installer_content = """#!/bin/bash
echo "========================================"
echo "   RACE TELEMETRY ANALYZER"
echo "========================================"
echo ""
echo "Instalador Automático"
echo ""

echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python não encontrado. Por favor, instale o Python 3.8+"
    exit 1
fi

echo ""
echo "Instalando dependências..."
python3 -m pip install --upgrade pip
python3 -m pip install PyQt6 pyqtgraph numpy pandas matplotlib scipy requests

echo ""
echo "Criando diretórios..."
mkdir -p logs output temp config

echo ""
echo "========================================"
echo "Instalação concluída!"
echo "========================================"
echo ""
echo "Para executar o sistema:"
echo "- Execute: python3 run.py"
echo "- Ou use o instalador automático"
echo ""
read -p "Pressione Enter para continuar..."
"""
        installer_file = "instalar.sh"
        os.chmod(installer_file, 0o755)
    
    with open(installer_file, "w", encoding="utf-8") as f:
        f.write(installer_content)
    
    print(f"✅ Script de instalação criado: {installer_file}")

def create_readme():
    """Cria um README com instruções."""
    print("📖 Criando README...")
    
    readme_content = """# 🏁 Race Telemetry Analyzer

Sistema avançado de análise de telemetria para simuladores de corrida.

## 🚀 Instalação Rápida

### Windows
1. Execute `Instalar.bat` como administrador
2. Ou execute `setup_windows.py`
3. Ou use o instalador automático: `install_and_run.py`

### Linux/Mac
1. Execute `./instalar.sh`
2. Ou execute `python3 install_and_run.py`

## 📦 Instalação Manual

1. Instale Python 3.8 ou superior
2. Execute: `pip install -r requirements.txt`
3. Execute: `python run.py`

## 🎯 Como Usar

1. **Carregar Dados**: Clique em "Carregar Arquivo" e selecione arquivos .csv, .ld ou .ldx
2. **Análise**: Clique em "Iniciar Análise" para processar os dados
3. **Visualização**: Explore os gráficos e métricas na interface
4. **Tempo Real**: Conecte-se a simuladores para análise em tempo real

## 📊 Recursos

- ✅ Análise de arquivos CSV, LD e LDX
- ✅ Interface moderna e intuitiva
- ✅ Gráficos interativos
- ✅ Análise em tempo real
- ✅ Comparação de voltas
- ✅ Métricas avançadas
- ✅ Exportação de dados

## 🛠️ Desenvolvimento

Para gerar um executável:
```bash
python build_executable.py
```

## 📁 Estrutura

```
racingVirtual/
├── src/                    # Código fonte
├── ui/                     # Interface gráfica
├── parsers/               # Parsers de dados
├── core/                  # Lógica principal
├── exemplos/              # Arquivos de exemplo
├── docs/                  # Documentação
└── output/                # Saídas geradas
```

## 🆘 Suporte

Em caso de problemas:
1. Verifique se o Python 3.8+ está instalado
2. Execute o instalador automático
3. Consulte os logs em `logs/`

---
Desenvolvido com ❤️ para a comunidade de simracing
"""
    
    with open("README_INSTALACAO.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ README criado!")

def main():
    """Função principal."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🏁 RACE TELEMETRY ANALYZER 🏁              ║
║                                                              ║
║              Gerador de Executável                           ║
║                                                              ║
║  🔨 Constrói executável standalone                          ║
║  📦 Inclui todas as dependências                            ║
║  🚀 Pronto para distribuição                                ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("🎯 Iniciando processo de construção...")
    print("=" * 60)
    
    # Instala PyInstaller
    if not install_pyinstaller():
        print("❌ Falha na instalação do PyInstaller")
        input("Pressione Enter para sair...")
        return
    
    # Cria arquivo .spec
    create_spec_file()
    
    # Constrói executável
    if not build_executable():
        print("❌ Falha na construção do executável")
        input("Pressione Enter para sair...")
        return
    
    # Cria scripts de instalação
    create_installer_script()
    create_readme()
    
    print("=" * 60)
    print("🎉 CONSTRUÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print()
    print("Arquivos gerados:")
    print("✅ dist/Race Telemetry Analyzer.exe (Windows)")
    print("✅ Instalar.bat (Script de instalação Windows)")
    print("✅ instalar.sh (Script de instalação Linux/Mac)")
    print("✅ README_INSTALACAO.md (Instruções)")
    print()
    print("Para distribuir:")
    print("1. Compacte a pasta 'dist'")
    print("2. Inclua os scripts de instalação")
    print("3. Compartilhe com os usuários")
    print()
    
    input("Pressione Enter para sair...")

if __name__ == "__main__":
    main() 