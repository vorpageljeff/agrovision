# FAQ - Perguntas Frequentes

## Geral

### P: Por que não usar OpenAI/IA?
**R**: 
- ❌ Caro (API chargada por tokens)
- ❌ Limite de requisições
- ❌ Requer conexão internet
- ✅ Python puro = grátis, rápido, local

### P: Posso adicionar mais perguntas facilmente?
**R**: Sim! Adicione um simples `if` em `chat_service.py`. Veja exercício 1 em `EXERCICIOS_E_EXEMPLOS.md`

### P: Isso funciona em produção?
**R**: Sim! Inclusive com melhor performance que IA em nuvem.

---

## Instalação

### P: Qual versão de Python preciso?
**R**: Python 3.10+. Verifique com:
```bash
python --version
```

### P: Preciso de GPU?
**R**: Não! O chat roda em CPU. Só precisa de GPU se for usar YOLO em temps real.

### P: Quanto espaço em disco?
**R**: ~2GB (principalmente pelas dependências e modelo YOLO)

### P: Funciona em Mac/Linux?
**R**: Sim! Tudo é Python puro. Só mude os comandos PowerShell para bash.

---

## Uso

### P: Como faço testes sem câmera?
**R**: 
```bash
# Populate banco manualmente
python -c "
from app import save_event
save_event('person', 0.95, 'static/captures/test.jpg')
save_event('car', 0.87, 'static/captures/test2.jpg')
save_event('person', 0.92, 'static/captures/test3.jpg')
"
```

### P: Posso usar banco de dados remoto?
**R**: Sim. Mude `DB_PATH` em `chat_service.py` para apontar para arquivo remoto ou use PostgreSQL:

```python
# SQLite remoto
import sqlite3
conn = sqlite3.connect('/net/servidor/banco.db')

# Ou PostgreSQL
import psycopg2
conn = psycopg2.connect("dbname=agrovision user=admin")
```

### P: O chat entende português mal?
**R**: É por design - usamos pattern matching simples. Para melhorar:
- [ ] Use biblioteca `unidecode` para acentos
- [ ] Implemente com spaCy/NLP

```python
from unidecode import unidecode

def normalize_question(q):
    return unidecode(q.lower())

# Uso
normalized = normalize_question("qual foi o maior índice?")
# Resultado: "qual foi o maior indice?"
```

### P: Posso customizar o intervalo de busca?
**R**: Sim! Em `chat_service.py`, mude o limit:

```python
# De 50 para 100 eventos
events = get_recent_events(limit=100)
```

---

## Performance

### P: Qual é a latência média de resposta?
**R**: ~7ms (ver benchmark em QUICKSTART.md)

### P: Funciona com 10.000 eventos?
**R**: Sim, mas vai ficar mais lento. Optimize com índices no SQLite:

```sql
CREATE INDEX idx_event_time ON events(event_time);
CREATE INDEX idx_label ON events(label);
CREATE INDEX idx_confidence ON events(confidence);
```

### P: Posso cachear respostas?
**R**: Sim! Adicione cache:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def ask_about_last_event(user_question: str) -> str:
    # ... seu código
```

---

## Desenvolvimento

### P: Como debugar o chat?
**R**: Adicione prints:

```python
def ask_about_last_event(user_question: str) -> str:
    print(f"DEBUG: Pergunta recebida: {user_question}")
    
    question = user_question.lower().strip()
    print(f"DEBUG: Pergunta normalizada: {question}")
    
    if "confiança" in question:
        print("DEBUG: Detectada pergunta sobre confiança")
        # ...
```

### P: Como fazer testes unitários?
**R**: Veja exemplo em `EXERCICIOS_E_EXEMPLOS.md` ou use pytest:

```bash
pip install pytest
pytest test_chat.py -v
```

### P: Como contribuir melhorias?
**R**:
1. Fork o repo
2. Faça suas mudanças
3. Testes passando
4. Pull request com descrição

### P: Posso usar em outro projeto?
**R**: Sim! Basta copiar `services/chat_service.py` e adaptar:

```python
# Em outro projeto
from agrovision.services.chat_service import ask_about_last_event

resposta = ask_about_last_event("quantas pessoas?")
print(resposta)
```

---

## Extensões

### P: Como integrar com Discord?
**R**: Use discord.py:

```bash
pip install discord.py
```

```python
import discord
from chat_service import ask_about_last_event

@bot.event
async def on_message(message):
    if message.content.startswith("!chat "):
        question = message.content[6:]
        response = ask_about_last_event(question)
        await message.channel.send(response)

bot.run("TOKEN_DISCORD")
```

### P: Como gerar relatórios em PDF?
**R**: Use reportlab:

```bash
pip install reportlab
```

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_report(events, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "Relatório de Eventos")
    
    y = 700
    for event in events:
        text = f"{event['event_time']} - {event['label']} ({event['confidence']:.2f})"
        c.drawString(100, y, text)
        y -= 20
    
    c.save()
```

### P: Posso exportar dados em CSV?
**R**: Sim!

```python
import csv

def export_to_csv(events, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Data/Hora', 'Objeto', 'Confiança', 'Imagem'])
        
        for event in events:
            writer.writerow([
                event['id'],
                event['event_time'],
                event['label'],
                event['confidence'],
                event['image_path']
            ])
```

### P: Como adicionar gráficos?
**R**: Use matplotlib:

```bash
pip install matplotlib
```

```python
import matplotlib.pyplot as plt
from collections import Counter

def plot_detections(events):
    labels = [e['label'] for e in events]
    counter = Counter(labels)
    
    plt.bar(counter.keys(), counter.values())
    plt.xlabel('Objeto')
    plt.ylabel('Contagem')
    plt.title('Distribuição de Detecções')
    plt.show()
```

---

## Troubleshooting Avançado

### P: Chat fica lento com muitos eventos
**R**: Optimize:

```python
# Ao invés de 50, analise os últimos 20
events = get_recent_events(limit=20)

# Ou use paginação
def get_events_by_date_range(start_date, end_date):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM events
        WHERE event_time BETWEEN ? AND ?
        ORDER BY id DESC
    """, (start_date, end_date))
    
    return cur.fetchall()
```

### P: Erros de encoding (acentos)
**R**: Adicione ao início do arquivo Python:

```python
# -*- coding: utf-8 -*-
```

Ou normalize:
```python
import unicodedata

def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')
```

### P: SQLite locked
**R**: Erro de concorrência. Aumente timeout:

```python
conn = sqlite3.connect(DB_PATH, timeout=10.0)
```

### P: Memory leak com muitas requisições
**R**: Certifique-se de fechar conexões:

```python
def get_recent_events(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    try:
        # seu código
        pass
    finally:
        conn.close()  # ✅ Sempre fechar
```

---

## Extra

### P: Como profiling de performance?
**R**: Use cProfile:

```bash
python -m cProfile -s cumulative app.py
```

### P: Quali ferramenta recomenda para versionamento?
**R**: Git + GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### P: Posso dockerizar?
**R**: Sim! Crie Dockerfile:

```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0"]
```

```bash
# Build
docker build -t agrovision .

# Run
docker run -p 8000:8000 agrovision
```

### P: Como monitorar em produção?
**R**: Use Prometheus + Grafana:

```bash
pip install prometheus-client
```

```python
from prometheus_client import Counter, Histogram

chat_requests = Counter('chat_requests_total', 'Total chat requests')
chat_duration = Histogram('chat_duration_seconds', 'Chat response time')

@app.post("/chat")
async def chat(req: ChatRequest):
    with chat_duration.time():
        chat_requests.inc()
        # seu código
```

---

## Recursos Adicionais

### Documentação
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [SQLite Tutorial](https://www.sqlite.org/tutorial.html)
- [Python Docs](https://docs.python.org/3)

### Cursos Relacionados
- "FastAPI - Full Stack" (Udemy)
- "SQLite Masterclass" (Udemy)
- "Python for Data Science"

### Comunidades
- r/Python
- Stack Overflow
- GitHub Discussions

---

## Precisa de Mais Ajuda?

1. **Leia primeiro**: MANUAL_CHAT_IMPLEMENTACAO.md
2. **Veja exemplos**: EXERCICIOS_E_EXEMPLOS.md
3. **Quick start**: QUICKSTART.md
4. **FAQ**: Este arquivo

Se ainda tiver dúvidas, consulte:
- Documentação oficial das libs
- Stack Overflow
- GitHub Issues

---

**Versão do FAQ**: 1.0
**Última atualização**: Março 26, 2026

Boa sorte com seu projeto! 🚀
