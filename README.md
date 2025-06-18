# Manipulador de Imagens MoovSec

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)

Projeto para manipulação e organização de imagens e vídeos recebidos do software moovsec.

---

## 📦 Funcionalidades

- 🗂️ Organização de arquivos de imagens e vídeos por data e origem.
- 🔄 Consumo de mensagens via Kafka.
- 🏷️ Geração de logs estruturados.
- 📤 Processamento e movimentação de arquivos entre diretórios.

---

## 🚀 Tecnologias Utilizadas

- Python 3.10+
- Kafka
- OpenCV
- Pillow
- Logging
- OS, shutil (nativos)

---



## 🔧 Configuração

1. Clone o repositório:

```bash
git clone https://github.com/dg-marins/ManipuladorImagensMoovSec.git

cd ManipuladorImagensMoovSec
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```
3. Configure o arquivo `config/config.py` com as informações necessárias.
```bash
editor config/config.py
```

4. Execute o programa:
```bash
python3 app.py
```