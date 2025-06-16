# Plano de Aplicação da Nova Identidade Visual e UX

Este documento detalha o planejamento para a aplicação da nova identidade visual e melhorias de Experiência do Usuário (UX) no `racingAnalize`, conforme solicitado.

## 1. Estratégia para Paleta de Cores

**Abordagem:** Utilizar **Qt Stylesheets (QSS)** para aplicar a paleta de cores fornecida de forma consistente em toda a aplicação PyQt6.

**Paleta Definida:**

```qss
/* Paleta Principal */
--primary-100: #FF5733; /* Laranja Vibrante */
--primary-200: #ff8a5f; /* Laranja Claro */
--primary-300: #fff3bf; /* Amarelo Pálido (para destaques sutis) */

/* Cores de Destaque (Accent) */
--accent-100: #33FF57; /* Verde Vibrante */
--accent-200: #009700; /* Verde Escuro */

/* Cores de Texto */
--text-100: #FFFFFF; /* Branco Principal */
--text-200: #e0e0e0; /* Cinza Claro (texto secundário) */

/* Cores de Fundo (Background) */
--bg-100: #1A1A1A; /* Preto/Cinza Muito Escuro (fundo principal) */
--bg-200: #292929; /* Cinza Escuro (painéis, áreas secundárias) */
--bg-300: #404040; /* Cinza Médio (bordas, separadores, elementos interativos hover) */
```

**Implementação:**

*   Criar um arquivo `styles.qss` centralizado.
*   Definir estilos globais para `QWidget`, `QMainWindow`, `QFrame`, `QLabel`, `QPushButton`, `QTableWidget`, `QTabWidget`, etc., utilizando as variáveis de cor (embora QSS não suporte variáveis nativamente como CSS, podemos definir as cores diretamente ou usar um pré-processador simples se necessário).
*   Aplicar o stylesheet globalmente na aplicação (`app.setStyleSheet(...)`).
*   Utilizar seletores de objeto (`setObjectName`) para estilizar widgets específicos quando necessário (ex: botões de ação primária com `--primary-100`, alertas com `--accent-100` ou `--accent-200`).
*   Garantir contraste adequado entre texto e fundo (`--text-100` sobre `--bg-100`/`--bg-200`).
*   Usar `--primary-100` e `--accent-100` para elementos interativos importantes e feedback visual.

## 2. Avaliação de Bibliotecas para Layout e Painéis Acopláveis

**Requisito:** Layout baseado em grid com painéis que o usuário possa mover, redimensionar e acoplar/desacoplar.

**Opções Avaliadas:**

1.  **PyQt6 Nativo (`QDockWidget`, `QGridLayout`, `QSplitter`):**
    *   **Prós:** Já faz parte do framework, sem dependências extras, boa integração, flexível.
    *   **Contras:** Pode exigir mais código manual para gerenciar layouts complexos e salvar/restaurar estados.
2.  **PyQtGraph:**
    *   **Prós:** Excelente para gráficos científicos/engenharia, inclui um sistema de docking robusto (`pyqtgraph.dockarea`).
    *   **Contras:** Adiciona uma dependência considerável. O sistema de docking é bom, mas pode ser um exagero se não precisarmos intensivamente dos recursos gráficos avançados da biblioteca em *todos* os painéis.
3.  **DearPyGui:**
    *   **Prós:** Framework moderno com foco em performance e UI para ferramentas, bom sistema de janelas/painéis.
    *   **Contras:** É um framework *diferente*. Exigiria reescrever toda a UI, abandonando PyQt6. Inviável no contexto atual.
4.  **Tkinter + ttkbootstrap:**
    *   **Prós:** ttkbootstrap oferece temas modernos (incluindo escuros) para Tkinter.
    *   **Contras:** Framework diferente, exigiria reescrita completa. Tkinter tem limitações em comparação com PyQt para UIs complexas e personalizadas.

**Decisão:** Utilizar as **funcionalidades nativas do PyQt6**, primariamente `QMainWindow` com `QDockWidget` para os painéis principais e `QGridLayout` ou `QSplitter` para organizar o conteúdo *dentro* dos painéis ou da área central. Esta abordagem minimiza dependências e aproveita o conhecimento existente do framework.

## 3. Esboço do Novo Layout da Interface Principal

**Conceito:** Uma `QMainWindow` com uma área central e múltiplos `QDockWidget` que podem ser movidos, redimensionados, agrupados em abas ou desacoplados.

**Painéis Principais (como QDockWidgets):**

1.  **Seleção de Sessão/Voltas:** (Pode ser um painel lateral esquerdo) Lista de sessões e voltas carregadas, permitindo seleção para análise e comparação.
2.  **Resultados da Comparação/Métricas:** (Pode ser um painel lateral esquerdo ou inferior) Exibe tabelas com tempos de volta, deltas por setor, métricas avançadas, sugestões de melhoria.
3.  **Visualização Principal (Área Central ou Dock):**
    *   **Replay Visual/Mapa:** Exibição 2D da pista com traçados (real, ideal, ghost), sincronizada com a timeline.
    *   **Gráficos de Telemetria:** Gráficos dinâmicos (velocidade, pedais, volante, etc.) com zoom, scroll e cursor sincronizado. Provavelmente organizados em abas (`QTabWidget`) dentro deste painel.
4.  **Gerenciador de Setups:** (Pode ser um painel lateral direito) Lista, visualização, edição e assistente de setups.
5.  **Coach Virtual (Chat):** (Pode ser um painel inferior ou lateral direito) Interface de chat para interação com o LLM local.
6.  **Feedback em Tempo Real:** (Pode ser um painel discreto ou notificações) Área para exibir alertas e mensagens do sistema de feedback.

**Organização Inicial Sugerida:**

*   **Esquerda:** Painel de Seleção de Voltas e Painel de Resultados/Métricas (possivelmente em abas).
*   **Centro:** Área principal com o Replay Visual/Mapa e os Gráficos de Telemetria (em abas).
*   **Direita:** Painel de Gerenciamento de Setups e Painel do Coach Virtual (possivelmente em abas).
*   **Inferior/StatusBar:** Área para Feedback em Tempo Real ou status geral.

**Flexibilidade:** O uso de `QDockWidget` permitirá ao usuário reorganizar os painéis conforme sua preferência, salvando e restaurando o layout.

