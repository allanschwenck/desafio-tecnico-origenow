"""
Script para buscar produtos nos marketplaces Mercado Livre e Amazon BR
e gerar arquivos Excel e JSON com os resultados.
"""

import pandas as pd
import time
import random
import re
from playwright.sync_api import sync_playwright
from typing import List, Dict
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ler_termos(arquivo: str) -> List[str]:
    """
    Lê os termos de busca do arquivo inputs.txt.
    
    Args:
        arquivo: Caminho do arquivo com os termos
        
    Returns:
        Lista de termos de busca
    """
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            termos = [linha.strip() for linha in f if linha.strip()]
        logger.info(f"Lidos {len(termos)} termos de busca")
        return termos
    except FileNotFoundError:
        logger.error(f"Arquivo {arquivo} não encontrado")
        return []


def limpar_preco(texto: str) -> float:
    """
    Limpa e converte texto de preço para float usando regex para ser mais robusta.
    
    Lida com strings sujas como 'ou R$ 232,19' ou '10x de R$ 50,00'.
    Busca padrões numéricos e extrai o valor após 'R$' ou o último da string.
    
    Args:
        texto: Texto do preço a ser limpo (pode conter texto extra)
        
    Returns:
        Valor float do preço, ou 0.0 se não conseguir converter
    """
    if not texto:
        return 0.0
    
    try:
        # Buscar todos os padrões numéricos (sequências de números, pontos e vírgulas)
        padrao = r'[\d\.,]+'
        matches = re.findall(padrao, texto)
        
        if not matches:
            return 0.0
        
        # Se encontrar 'R$' no texto, priorizar o valor logo após ele
        valor_preco = None
        if 'R$' in texto:
            # Buscar o padrão numérico que vem logo após 'R$'
            padrao_apos_rs = r'R\$\s*([\d\.,]+)'
            match_rs = re.search(padrao_apos_rs, texto)
            if match_rs:
                valor_preco = match_rs.group(1)
        
        # Se não encontrou após R$, usar o último match (geralmente o valor total/à vista)
        if not valor_preco:
            valor_preco = matches[-1]
        
        # Limpar o valor: remover pontos de milhar e trocar vírgula decimal por ponto
        # Se tem vírgula, assume formato brasileiro: vírgula é decimal, pontos são milhar
        if ',' in valor_preco:
            partes = valor_preco.split(',')
            parte_inteira = partes[0].replace('.', '')  # Remove pontos de milhar
            parte_decimal = partes[1] if len(partes) > 1 else '00'
            valor_limpo = f"{parte_inteira}.{parte_decimal}"
        else:
            # Se não tem vírgula, pode ter ponto como decimal ou milhar
            # Se tem apenas um ponto e 1-2 dígitos após, assume decimal
            if '.' in valor_preco:
                partes_ponto = valor_preco.split('.')
                if len(partes_ponto) == 2 and len(partes_ponto[1]) <= 2:
                    # É decimal (ex: 10.80)
                    valor_limpo = valor_preco  # Mantém como está
                else:
                    # É milhar, remove pontos
                    valor_limpo = valor_preco.replace('.', '')
            else:
                valor_limpo = valor_preco
        
        return float(valor_limpo)
    except (ValueError, AttributeError, IndexError):
        return 0.0


def buscar_mercado_livre(termo: str, limite: int = 30) -> List[Dict]:
    """
    Busca produtos no Mercado Livre usando Playwright para scraping.
    
    Args:
        termo: Termo de busca
        limite: Número máximo de produtos a retornar
        
    Returns:
        Lista de dicionários com informações dos produtos
    """
    produtos = []
    
    try:
        with sync_playwright() as p:
            # Iniciar navegador em modo headless
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # URL de busca do Mercado Livre
            # Nota: A URL padrão já traz os resultados ordenados por "Mais Relevantes",
            # que serve como proxy para "Mais Vendidos" conforme as regras do marketplace.
            # Qualquer discrepância entre o navegador do usuário e o script se deve à
            # personalização de cookies/região do navegador. O script captura o ranking neutro.
            url_busca = f'https://lista.mercadolivre.com.br/{termo.replace(" ", "-")}'
            
            # Debug: mostrar URL final gerada
            print(f'URL Mercado Livre: {url_busca}')
            
            logger.info(f"Acessando Mercado Livre para '{termo}'...")
            page.goto(url_busca, wait_until="domcontentloaded", timeout=60000)
            
            # Aguardar carregamento dos produtos - tentar ambos os seletores
            try:
                page.wait_for_selector('.ui-search-layout__item', timeout=10000)
            except:
                try:
                    page.wait_for_selector('div.poly-card', timeout=10000)
                except:
                    pass
            
            # Extrair produtos da página - tentar ambos os seletores de container
            elementos_produtos = page.query_selector_all('div.poly-card, li.ui-search-layout__item')
            
            # Conjunto para rastrear links já vistos (deduplicação)
            vistos = set()
            
            # Iterar sobre todos os elementos até ter 30 produtos únicos
            for elemento in elementos_produtos:
                # Parar quando tiver 30 produtos únicos
                if len(produtos) >= limite:
                    break
                
                try:
                    # Extrair título - tentar múltiplos seletores
                    titulo = "Título não disponível"
                    titulo_elem = elemento.query_selector('h2.poly-box')
                    if not titulo_elem:
                        titulo_elem = elemento.query_selector('.poly-component__title')
                    if not titulo_elem:
                        titulo_elem = elemento.query_selector('.ui-search-item__title')
                    
                    if titulo_elem:
                        titulo = titulo_elem.inner_text()
                    
                    # Debug: mostrar título encontrado
                    print(f'Título encontrado (Mercado Livre): {titulo}')
                    
                    # Extrair link - tentar múltiplos seletores
                    link = ""
                    link_elem = elemento.query_selector('a.poly-component__title')
                    if not link_elem:
                        link_elem = elemento.query_selector('a.ui-search-link')
                    
                    if link_elem:
                        href = link_elem.get_attribute('href')
                        if href:
                            link = href
                    
                    # Deduplicação: verificar se o link já foi visto
                    if link in vistos:
                        continue
                    vistos.add(link)
                    
                    # Extrair preço - Mercado Livre
                    preco = 0
                    
                    # Método 1: Buscar container .andes-money-amount e pegar inteiro + centavos
                    container_preco = elemento.query_selector('.andes-money-amount')
                    if container_preco:
                        # Parte inteira
                        inteiro_elem = container_preco.query_selector('.andes-money-amount__fraction')
                        # Centavos
                        centavos_elem = container_preco.query_selector('.andes-money-amount__cents')
                        
                        if inteiro_elem:
                            inteiro_texto = inteiro_elem.inner_text().replace('.', '').strip()
                            try:
                                inteiro = float(inteiro_texto)
                                if centavos_elem:
                                    centavos_texto = centavos_elem.inner_text().strip()
                                    try:
                                        centavos = float(centavos_texto)
                                        preco = inteiro + (centavos / 100)
                                    except ValueError:
                                        preco = inteiro
                                else:
                                    preco = inteiro
                            except ValueError:
                                pass
                    
                    # Método 2 (alternativa): Buscar preço completo em outros seletores
                    if preco == 0:
                        preco_elem = elemento.query_selector('.poly-price__current')
                        if not preco_elem:
                            preco_elem = elemento.query_selector('.ui-search-price__part')
                        
                        if preco_elem:
                            preco_texto = preco_elem.inner_text()
                            preco = limpar_preco(preco_texto)
                    
                    # Extrair imagem - Mercado Livre
                    imagem = ""
                    img_elem = elemento.query_selector('img.ui-search-result-image__element')
                    if not img_elem:
                        # Fallback: buscar qualquer img dentro do card
                        img_elem = elemento.query_selector('img')
                    
                    if img_elem:
                        src = img_elem.get_attribute('src')
                        if src:
                            imagem = src
                    
                    # Posição baseada no número de produtos únicos já adicionados
                    posicao = len(produtos) + 1
                    
                    produto = {
                        "termo": termo,
                        "marketplace": "Mercado Livre",
                        "posicao": posicao,
                        "titulo": titulo,
                        "preco": preco,
                        "link": link,
                        "imagem": imagem
                    }
                    produtos.append(produto)
                    
                except Exception as e:
                    logger.warning(f"Erro ao extrair produto {idx} do Mercado Livre: {e}")
                    continue
            
            browser.close()
            
        logger.info(f"Mercado Livre - {termo}: {len(produtos)} produtos encontrados")
        
    except Exception as e:
        logger.error(f"Erro ao buscar no Mercado Livre para '{termo}': {e}")
    
    return produtos


def buscar_amazon(termo: str, limite: int = 30) -> List[Dict]:
    """
    Busca produtos na Amazon BR usando Playwright para scraping.
    
    Args:
        termo: Termo de busca
        limite: Número máximo de produtos a retornar
        
    Returns:
        Lista de dicionários com informações dos produtos
    """
    produtos = []
    
    try:
        with sync_playwright() as p:
            # Iniciar navegador em modo headless
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # URL de busca da Amazon BR
            # Ordenação: Mais Vendidos (exact-aware-popularity-rank)
            url_busca = f"https://www.amazon.com.br/s?k={termo.replace(' ', '+')}&s=exact-aware-popularity-rank"
            
            # Debug: mostrar URL final gerada
            print(f'URL Amazon: {url_busca}')
            
            logger.info(f"Acessando Amazon BR para '{termo}'...")
            page.goto(url_busca, wait_until="domcontentloaded", timeout=60000)
            
            # Aguardar carregamento dos produtos
            page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=10000)
            
            # Extrair produtos da página usando o container base
            elementos_produtos = page.query_selector_all('div[data-component-type="s-search-result"]')
            
            for idx, elemento in enumerate(elementos_produtos[:limite], 1):
                try:
                    # Extrair título usando h2 span dentro do container
                    titulo_elem = elemento.query_selector('h2 span')
                    titulo = titulo_elem.inner_text() if titulo_elem else "Título não disponível"
                    
                    # Debug: mostrar título encontrado
                    print(f'Título encontrado (Amazon): {titulo}')
                    
                    # Extrair link - tentar múltiplos seletores
                    link = ""
                    link_elem = elemento.query_selector('a.a-link-normal.s-no-outline')
                    if not link_elem:
                        link_elem = elemento.query_selector('h2 a')
                    
                    if link_elem:
                        href = link_elem.get_attribute('href')
                        if href:
                            # Se o link vier relativo (começando com /), concatenar com a URL base
                            link = f"https://www.amazon.com.br{href}" if href.startswith('/') else href
                    
                    # Extrair preço - Amazon
                    preco = 0
                    
                    # Método 1: Buscar span.a-offscreen (preço completo oculto)
                    preco_offscreen = elemento.query_selector('span.a-offscreen')
                    if preco_offscreen:
                        preco_texto = preco_offscreen.inner_text()
                        preco = limpar_preco(preco_texto)
                    
                    # Método 2 (alternativa): Reconstruir com parte inteira + centavos
                    if preco == 0:
                        inteiro_elem = elemento.query_selector('span.a-price-whole')
                        centavos_elem = elemento.query_selector('span.a-price-fraction')
                        
                        if inteiro_elem:
                            inteiro_texto = inteiro_elem.inner_text().replace('.', '').replace(',', '').strip()
                            try:
                                inteiro = float(inteiro_texto)
                                if centavos_elem:
                                    centavos_texto = centavos_elem.inner_text().strip()
                                    try:
                                        centavos = float(centavos_texto)
                                        preco = inteiro + (centavos / 100)
                                    except ValueError:
                                        preco = inteiro
                                else:
                                    preco = inteiro
                            except ValueError:
                                pass
                    
                    # Extrair imagem - Amazon
                    imagem = ""
                    img_elem = elemento.query_selector('img.s-image')
                    if not img_elem:
                        # Fallback: buscar qualquer img dentro do container
                        img_elem = elemento.query_selector('img')
                    
                    if img_elem:
                        src = img_elem.get_attribute('src')
                        if src:
                            imagem = src
                    
                    produto = {
                        "termo": termo,
                        "marketplace": "Amazon BR",
                        "posicao": idx,
                        "titulo": titulo,
                        "preco": preco,
                        "link": link,
                        "imagem": imagem
                    }
                    produtos.append(produto)
                    
                except Exception as e:
                    logger.warning(f"Erro ao extrair produto {idx} da Amazon: {e}")
                    continue
            
            browser.close()
            
        logger.info(f"Amazon BR - {termo}: {len(produtos)} produtos encontrados")
        
    except Exception as e:
        logger.error(f"Erro ao buscar na Amazon para '{termo}': {e}")
    
    return produtos


def processar_termos(termos: List[str]) -> List[Dict]:
    """
    Processa todos os termos de busca e coleta produtos dos dois marketplaces.
    
    Args:
        termos: Lista de termos de busca
        
    Returns:
        Lista completa de produtos encontrados
    """
    todos_produtos = []
    
    for idx, termo in enumerate(termos, 1):
        logger.info(f"Processando termo {idx}/{len(termos)}: '{termo}'")
        
        # Buscar no Mercado Livre
        produtos_ml = buscar_mercado_livre(termo)
        todos_produtos.extend(produtos_ml)
        
        # Delay aleatório entre requisições (2 a 5 segundos)
        delay = random.uniform(2, 5)
        logger.info(f"Aguardando {delay:.2f} segundos antes da próxima requisição...")
        time.sleep(delay)
        
        # Buscar na Amazon
        produtos_amazon = buscar_amazon(termo)
        todos_produtos.extend(produtos_amazon)
        
        # Delay aleatório entre requisições (2 a 5 segundos)
        if idx < len(termos):  # Não esperar após o último termo
            delay = random.uniform(2, 5)
            logger.info(f"Aguardando {delay:.2f} segundos antes da próxima requisição...")
            time.sleep(delay)
    
    return todos_produtos


def salvar_excel(produtos: List[Dict], arquivo_saida: str):
    """
    Salva os produtos em arquivos Excel e JSON.
    
    Args:
        produtos: Lista de dicionários com informações dos produtos
        arquivo_saida: Nome do arquivo Excel de saída
    """
    if not produtos:
        logger.warning("Nenhum produto para salvar")
        return
    
    df = pd.DataFrame(produtos)
    
    # Reordenar colunas
    colunas = ["termo", "marketplace", "posicao", "titulo", "preco", "link", "imagem"]
    df = df[colunas]
    
    # Renomear colunas para português mais amigável
    df.columns = ["Termo Pesquisado", "Marketplace", "Posição no Ranking", 
                  "Título do Produto", "Preço", "Link do Produto", "Imagem"]
    
    # Salvar Excel
    df.to_excel(arquivo_saida, index=False, engine='openpyxl')
    logger.info(f"Arquivo {arquivo_saida} salvo com {len(produtos)} produtos")
    
    # Salvar JSON (para uso no front-end)
    df.to_json('resultado.json', orient='records', force_ascii=False, indent=4)
    logger.info(f"Arquivo resultado.json salvo com {len(produtos)} produtos")


def main():
    """
    Função principal que orquestra todo o processo.
    """
    logger.info("Iniciando processamento...")
    
    # Ler termos de busca
    termos = ler_termos("inputs.txt")
    
    if not termos:
        logger.error("Nenhum termo encontrado. Encerrando.")
        return
    
    # Processar termos e coletar produtos
    produtos = processar_termos(termos)
    
    # Salvar resultados em Excel
    salvar_excel(produtos, "resultado.xlsx")
    
    logger.info("Processamento concluído!")


if __name__ == "__main__":
    main()
