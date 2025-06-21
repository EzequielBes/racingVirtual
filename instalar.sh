#!/bin/bash

# Race Telemetry Analyzer - Instalador para Linux/Mac
# Script de instalação automática

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🏁 RACE TELEMETRY ANALYZER 🏁              ║"
echo "║                                                              ║"
echo "║              Sistema de Análise de Telemetria Avançado       ║"
echo "║                                                              ║"
echo "║  🚀 Instalação Automática para Linux/Mac                    ║"
echo "║  📊 Análise em Tempo Real                                   ║"
echo "║  🎨 Interface Moderna e Intuitiva                           ║"
echo "║  📈 Gráficos Interativos                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 Iniciando processo de instalação..."
echo "=================================================="

# Verifica se o Python está instalado
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "   Por favor, instale o Python 3.8 ou superior:"
    echo "   Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "   macOS: brew install python3"
    echo "   Ou baixe em: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION encontrado"

# Verifica se o pip está instalado
echo "📦 Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "📥 Instalando pip..."
    python3 -m ensurepip --upgrade
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao instalar pip"
        exit 1
    fi
fi
echo "✅ pip instalado"

# Atualiza pip
echo "🔄 Atualizando pip..."
python3 -m pip install --upgrade pip --quiet

# Instala dependências
echo "📦 Instalando dependências..."
dependencies=(
    "PyQt6>=6.4.0"
    "pyqtgraph>=0.13.0"
    "numpy>=1.21.0"
    "pandas>=1.3.0"
    "matplotlib>=3.5.0"
    "scipy>=1.7.0"
    "requests>=2.25.0"
)

for dep in "${dependencies[@]}"; do
    echo "   📥 Instalando $dep..."
    python3 -m pip install "$dep" --quiet
    if [ $? -ne 0 ]; then
        echo "   ❌ Erro ao instalar $dep"
        exit 1
    fi
    echo "   ✅ $dep instalado"
done

echo "✅ Todas as dependências instaladas com sucesso!"

# Cria diretórios necessários
echo "📁 Criando diretórios..."
directories=("logs" "output" "temp" "config")

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    echo "   ✅ Diretório $dir criado"
done

# Cria script de execução
echo "🚀 Criando script de execução..."
cat > "iniciar_analisador.sh" << 'EOF'
#!/bin/bash
echo "Iniciando Race Telemetry Analyzer..."
python3 run.py
EOF

chmod +x "iniciar_analisador.sh"
echo "✅ Script de execução criado"

# Cria atalho no desktop (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🖥️ Criando atalho no desktop..."
    DESKTOP="$HOME/Desktop"
    if [ -d "$DESKTOP" ]; then
        cat > "$DESKTOP/Race Telemetry Analyzer.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Race Telemetry Analyzer
Comment=Sistema de Análise de Telemetria Avançado
Exec=$(pwd)/iniciar_analisador.sh
Icon=applications-games
Terminal=false
Categories=Game;Sports;
EOF
        chmod +x "$DESKTOP/Race Telemetry Analyzer.desktop"
        echo "✅ Atalho no desktop criado"
    fi
fi

echo ""
echo "=================================================="
echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=================================================="
echo ""
echo "O Race Telemetry Analyzer foi instalado com sucesso!"
echo ""
echo "Para executar o sistema:"
echo "✅ Execute: ./iniciar_analisador.sh"
echo "✅ Ou execute: python3 run.py"
echo "✅ Ou use o atalho no desktop (Linux)"
echo ""

# Pergunta se quer executar agora
read -p "🚀 Deseja executar o Race Telemetry Analyzer agora? (s/n): " response
response=$(echo "$response" | tr '[:upper:]' '[:lower:]')

if [[ "$response" == "s" || "$response" == "sim" || "$response" == "y" || "$response" == "yes" ]]; then
    echo "🚀 Iniciando Race Telemetry Analyzer..."
    echo "=================================================="
    python3 run.py
else
    echo "👋 Instalação concluída!"
    echo "O sistema está pronto para uso!"
fi

echo ""
read -p "Pressione Enter para sair..." 