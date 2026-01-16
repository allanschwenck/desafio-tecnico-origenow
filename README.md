# Desafio Técnico - Monitoramento de Marketplaces (Top 30)

Este projeto é uma solução full-stack para extração e visualização de dados de e-commerce (Mercado Livre e Amazon). O sistema realiza scraping automatizado, processa os dados e apresenta um dashboard interativo.

## 🚀 Funcionalidades

* **Scraping Robusto:** Utiliza Playwright para navegar como um usuário real, contornando bloqueios básicos.
* **Front-end Moderno:** Interface Dark Mode (Identidade Origenow), com feedback em tempo real e tooltips de imagem.
* **Dados:** Gera Excel (`resultado.xlsx`) e JSON (`resultado.json`).
* **Resiliência:** Sistema de retries, timeouts ajustados e User-Agents rotativos.

## 🛠️ Tecnologias

* **Backend:** Python 3, Flask, Pandas, Playwright.
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API).

## 📋 Pré-requisitos

* Python 3.8+
* Navegadores instalados (via Playwright)

## 🔧 Como rodar o projeto

1.  **Clone o repositório ou extraia o zip.**
2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Instale os navegadores do robô:**
    ```bash
    playwright install chromium
    ```
4.  **Execute o servidor:**
    ```bash
    python app.py
    ```
5.  **Acesse no navegador:**
    Abra `http://127.0.0.1:5000`

## ⚙️ Decisões de Projeto

* **Playwright vs Requests:** Optei pelo Playwright para garantir a renderização de elementos dinâmicos (JavaScript) e evitar bloqueios de bot (erro 403), simulando um comportamento humano.
* **Flask:** Utilizado para criar uma ponte simples entre a interface web e o script de automação.
* **Ordenação:** * *Amazon:* Parâmetro de URL para "Mais Vendidos".
    * *Mercado Livre:* Busca padrão "Mais Relevantes" (proxy para vendas conforme documentação).

## ⚠️ Limitações Conhecidas

* O processo é síncrono; a interface aguarda o fim do scraping para exibir resultados (tempo médio: 20-40s dependendo da internet).
* Depende da estrutura HTML dos marketplaces; mudanças drásticas no layout podem requerer atualização dos seletores CSS.

---
Desenvolvido como parte do teste técnico para Origenow.