"""
Aplicação Flask para executar o script de busca de produtos
e fornecer os dados via API.
"""

from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import json
import os

app = Flask(__name__)


@app.route('/')
def index():
    """
    Rota principal que renderiza o template index.html.
    """
    return render_template('index.html')


@app.route('/executar', methods=['POST'])
def executar():
    """
    Rota para executar o script de busca de produtos.
    
    Recebe um JSON com a estrutura: { "keywords": "termo1, termo2" }
    Grava os termos no arquivo inputs.txt e executa o main.py
    """
    try:
        # Receber dados JSON
        data = request.get_json()
        
        if not data or 'keywords' not in data:
            return jsonify({'status': 'erro', 'mensagem': 'Campo "keywords" não encontrado'}), 400
        
        keywords = data['keywords']
        
        # Quebrar por vírgula e limpar espaços
        termos = [termo.strip() for termo in keywords.split(',') if termo.strip()]
        
        if not termos:
            return jsonify({'status': 'erro', 'mensagem': 'Nenhum termo válido fornecido'}), 400
        
        # Gravar termos no arquivo inputs.txt
        with open('inputs.txt', 'w', encoding='utf-8') as f:
            for termo in termos:
                f.write(f"{termo}\n")
        
        # Executar o script main.py
        try:
            result = subprocess.run(
                ['python', 'main.py'],
                capture_output=True,
                text=True,
                timeout=600  # Timeout de 10 minutos
            )
            
            if result.returncode != 0:
                return jsonify({
                    'status': 'erro',
                    'mensagem': 'Erro ao executar o script',
                    'detalhes': result.stderr
                }), 500
            
        except subprocess.TimeoutExpired:
            return jsonify({
                'status': 'erro',
                'mensagem': 'Timeout ao executar o script'
            }), 500
        except Exception as e:
            return jsonify({
                'status': 'erro',
                'mensagem': f'Erro ao executar: {str(e)}'
            }), 500
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        return jsonify({
            'status': 'erro',
            'mensagem': f'Erro interno: {str(e)}'
        }), 500


@app.route('/dados', methods=['GET'])
def dados():
    """
    Rota para retornar os dados do resultado.json.
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists('resultado.json'):
            return jsonify({
                'status': 'erro',
                'mensagem': 'Arquivo resultado.json não encontrado. Execute a busca primeiro.'
            }), 404
        
        # Ler e retornar o conteúdo do JSON
        with open('resultado.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        return jsonify(dados)
        
    except json.JSONDecodeError:
        return jsonify({
            'status': 'erro',
            'mensagem': 'Erro ao ler o arquivo JSON'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'erro',
            'mensagem': f'Erro interno: {str(e)}'
        }), 500


@app.route('/download', methods=['GET'])
def download():
    """
    Rota para fazer download do arquivo resultado.xlsx.
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists('resultado.xlsx'):
            return jsonify({
                'status': 'erro',
                'mensagem': 'Arquivo resultado.xlsx não encontrado. Execute a busca primeiro.'
            }), 404
        
        # Retornar o arquivo para download
        return send_file('resultado.xlsx', as_attachment=True)
        
    except Exception as e:
        return jsonify({
            'status': 'erro',
            'mensagem': f'Erro ao fazer download: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
