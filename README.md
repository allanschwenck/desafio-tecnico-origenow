DESAFIO TÉCNICO - MONITORAMENTO DE MARKETPLACES (TOP 30)

Este projeto é uma solução full-stack para remoção e visualização de dados de e-commerce (Mercado Livre e Amazon). O sistema realiza scraping automatizado, processa os dados e apresenta um dashboard interativo.

FUNCIONALIDADES

Scraping Robusto: Utiliza Playwright para navegar como um usuário real, contornando bloqueios básicos. Front-end Moderno: Interface Dark Mode (Identidade Origenow), com feedback em tempo real e tooltips de imagem. Dados: Gera Excel (resultado.xlsx) e JSON (resultado.json). Resiliência: Sistema de novas tentativas, timeouts ajustados e User-Agents rotativos.

TECNOLOGIAS

Backend: Python 3, Flask, Pandas, Playwright. Frontend: HTML5, CSS3, JavaScript (Fetch API).

PRÉ-REQUISITOS

Python 3.8 ou superior. Navegadores instalados (via Playwright).

MANUAL DE INSTRUÇÕES E RESOLUÇÃO DE PROBLEMAS (USANDO VS CODE, MAS PODE-SE USAR QUALQUER OUTRO EDITOR)

Siga este guia para rodar o projeto utilizando o terminal do VS Code.
Comandos alternativos são sugeridos por conta de problemas de PATH (Windows não sabe onde o Python está instalado), isso acontece quando aquela caixinha "Add Python to PATH" não é marcada na instalação.

PASSO 1: ABRIR O TERMINAL NO VS CODE

Como fazer: Abra a pasta do projeto no VS Code. Olhe para a barra de menu no topo, clique em "Terminal" e depois selecione "New Terminal" (Novo Terminal). Um painel abrirá na parte inferior.

PASSO 2: INSTALAR AS BIBLIOTECAS (COMANDOS BLINDADOS)

Nesta etapa, usaremos um comando que invoca o instalador diretamente pelo Python, evitando erros de caminho não encontrado.

Comando Principal (Windows): python -m pip install -r requirements.txt

Comando Alternativo (Windows - se o de cima falhar): py -m pip install -r requirements.txt

Comando (Mac): python3 -m pip install -r requirements.txt

O que esse comando faz: O trecho "-m pip" diz ao computador: "Não procure pelo programa pip solto no sistema, use o pip que está dentro deste Python que estou rodando agora". Isso garante que as bibliotecas sejam instaladas no lugar certo e funciona mesmo se o atalho do pip estiver quebrado.

Erros possíveis e solução definitiva: Se aparecer "python não é reconhecido" ou nada acontecer: Significa que o Python não está nas Variáveis de Ambiente. A solução única é reinstalar o Python. Baixe o instalador novamente no site python.org, execute-o e OBRIGATORIAMENTE marque a caixa "Add Python to PATH" na primeira tela antes de clicar em Install. Reinicie o VS Code após isso.

PASSO 3: INSTALAR O NAVEGADOR DE AUTOMAÇÃO

Comando (Windows): python -m playwright install chromium

Comando Alternativo (Windows - se o de cima falhar): py -m playwright install chromium

Comando (Mac): python3 -m playwright install chromium

O que esse comando faz: Baixa especificamente o navegador Chromium adaptado para automação. Usamos "python -m" novamente para garantir que o comando seja executado corretamente pela biblioteca que acabamos de instalar.

Erros possíveis:

Erro de conexão: Por que ocorre: Internet instável ou bloqueio de rede corporativa (firewall) impedindo o download. Tente usar uma rede pessoal (4G/Wi-Fi de casa).

PASSO 4: RODAR A APLICAÇÃO

Comando (Windows): python app.py

Comando Alternativo (Windows - se o de cima falhar): py app.py

Comando (Mac): python3 app.py

O que esse comando faz: Inicia o servidor Flask. Ele cria uma ponte entre a interface visual (HTML) e o script de automação em Python.

Sobre o aviso "WARNING: This is a development server...": Você verá esta mensagem em vermelho. Não se preocupe. Ela indica que o servidor subiu corretamente para testes locais e não deve ser usado em grandes servidores de produção.

Erros possíveis:

Erro: "ModuleNotFoundError". Por que ocorre: O Passo 2 falhou. Tente rodar novamente o Passo 2 e leia atentamente se aparece "Successfully installed" no final.

Erro: "Address already in use". Por que ocorre: Você já tem outro terminal rodando o projeto. Encerre os outros terminais clicando no ícone de lixeira do painel do terminal.

PASSO FINAL: ACESSAR O DASHBOARD

No navegador: Abra o Chrome ou Safari e digite o seguinte endereço na barra de endereços:

http://127.0.0.1:5000

DECISÕES DE PROJETO

Playwright vs Requests: Optei pelo Playwright para garantir a renderização de elementos dinâmicos (JavaScript) e evitar bloqueios de bot (erro 403), simulando um comportamento humano. Flask: Utilizado para criar uma ponte simples entre a interface web e o script de automação.

ORDENAÇÃO

Amazon: Parâmetro de URL para "Mais Vendidos". Mercado Livre: Busca padrão "Mais Relevantes" (proxy para vendas conforme documentação).

LIMITAÇÕES CONHECIDAS

O processo é síncrono; a interface aguarda o fim do scraping para exibir resultados (tempo médio: 20 a 40 segundos dependendo da internet). Depende da estrutura HTML dos marketplaces; mudanças drásticas no layout dos sites podem exigir atualização dos seletores CSS no código.

Desenvolvido como parte do teste técnico para Originenow.
