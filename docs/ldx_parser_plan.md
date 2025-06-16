# Análise e Decisão sobre Parser .LDX

## Objetivo
Implementar um parser performático para arquivos `.ldx` do MoTeC i2, integrando-o ao projeto `racingAnalize`.

## Pesquisa e Alternativas

1.  **`gotzl/ldparser` (Python):** Analisado anteriormente. Suporta apenas `.ld`, não `.ldx`. Descartado para `.ldx`.
2.  **Desenvolvimento Próprio (Python Puro):** Exigiria engenharia reversa complexa do formato binário `.ldx`. Provavelmente resultaria em performance inferior comparado a soluções compiladas.
3.  **Bindings C/C++ (ctypes/cffi):** Exigiria encontrar ou desenvolver uma biblioteca C/C++ para `.ldx` e criar os bindings. Potencialmente performático, mas pode ser complexo de manter.
4.  **IronPython + .NET:** Dependeria da existência de uma biblioteca .NET para `.ldx`. Adiciona complexidade de interoperabilidade e restringe a execução ao IronPython.
5.  **`afonso360/motec-i2` (Rust) + PyO3 Bindings:**
    *   **Biblioteca Existente:** `motec-i2` é uma biblioteca Rust que declara explicitamente suporte à leitura e escrita de arquivos `.ld` e `.ldx`.
    *   **Performance:** Rust compilado tende a oferecer performance significativamente superior ao Python puro para tarefas de I/O e parsing binário.
    *   **Integração:** PyO3 é o padrão de mercado para criar bindings Python para Rust, permitindo chamar código Rust de forma eficiente a partir do Python.
    *   **Manutenção:** Código Rust é conhecido pela segurança e manutenibilidade. A biblioteca parece estruturada.
    *   **Viabilidade:** A biblioteca existe, está sob licença MIT e a tecnologia de bindings (PyO3) é madura.

## Decisão

A abordagem escolhida é utilizar a biblioteca Rust **`afonso360/motec-i2`** e criar bindings Python para ela usando **PyO3**. Esta opção oferece o melhor equilíbrio entre performance, reutilização de código existente e viabilidade de integração com o projeto Python atual.

## Próximos Passos (Implementação)

1.  **Configurar Ambiente:** Instalar Rust, Cargo e Maturin (ferramenta para construir e publicar pacotes Python escritos em Rust).
2.  **Clonar `motec-i2`:** Obter o código-fonte da biblioteca Rust.
3.  **Criar Bindings PyO3:**
    *   Adicionar `pyo3` como dependência no `Cargo.toml`.
    *   Criar um módulo de bindings (`#[pymodule]`) que exponha funções Rust para Python (`#[pyfunction]`).
    *   A função principal exposta deverá receber o caminho de um arquivo `.ldx` e retornar os dados parseados em um formato utilizável por Python (provavelmente um dicionário ou uma estrutura de classes Python definidas via `#[pyclass]`).
4.  **Compilar Módulo Python:** Usar `maturin build` ou `maturin develop` para compilar a biblioteca Rust como uma extensão Python (`.so`/`.pyd`).
5.  **Integrar ao `racingAnalize`:**
    *   Copiar o módulo compilado para a estrutura do projeto (ex: `src/parsers/motec_parser_rust.so`).
    *   Modificar `src/telemetry_import.py` para detectar arquivos `.ldx` e chamar a função do módulo Rust compilado para realizar o parsing.
    *   Adaptar o restante do código para consumir a estrutura de dados retornada pelo parser Rust.
6.  **Testar:** Validar o parsing com diversos arquivos `.ldx` de diferentes fontes (ACC, LMU, etc.) e comparar a estrutura de dados com a esperada.

