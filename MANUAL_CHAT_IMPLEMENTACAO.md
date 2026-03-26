# Manual: Implementação do Chat de Interpretação de Eventos - AgroVision

## Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Passo a Passo da Implementação](#passo-a-passo-da-implementação)
4. [Código Explicado](#código-explicado)
5. [Como Usar](#como-usar)
6. [Melhorias Futuras](#melhorias-futuras)

---

## Visão Geral

O chat de interpretação de eventos é um componente que permite aos usuários fazer perguntas em linguagem natural sobre eventos detectados pelo sistema de visão computacional (YOLO). Em vez de apenas listar eventos, o chat **analisa dados e responde perguntas intelligentemente** sobre:

- Confiança de detecção
- Objetos mais detectados
- Padrões de atividade
- Estatísticas gerais

### Tecnologias Utilizadas
- **Backend**: FastAPI (Python)
- **Banco de Dados**: SQLite
- **Análise**: Python puro (sem dependências de IA)
- **Frontend**: HTML + JavaScript + Bootstrap

---

## Arquitetura

```
┌─────────────────────────────────────────┐
│         Frontend (HTML/JS)              │
│  - Formulário de perguntas              │
│  - Exibição de respostas                │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    FastAPI Backend (app.py)             │
│  - Endpoint POST /chat                  │
│  - Recebe pergunta do usuário           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Chat Service (chat_service.py)         │
│  - ask_about_last_event()               │
│  - Processa pergunta                    │
│  - Acessa banco de dados                │
│  - Retorna resposta analisada           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    Banco de Dados SQLite                │
│  - Tabela: events                       │
│  - Armazena detecções do YOLO           │
└─────────────────────────────────────────┘
```

---

## Passo a Passo da Implementação

### Etapa 1: Criar o Serviço de Chat

**Arquivo**: `services/chat_service.py`

O serviço é responsável por:
1. Buscar eventos do banco de dados
2. Processar a pergunta do usuário
3. Analisar os eventos com regras inteligentes
4. Retornar uma resposta formatada

**Criação do arquivo**:
```bash
# Criar arquivo vazio
New-Item -Path "services/chat_service.py" -ItemType File
```

### Etapa 2: Implementar Funções de Acesso ao Banco

```python
def get_recent_events(limit: int = 10):
    """Busca os últimos N eventos do banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, event_time, label, confidence, image_path
        FROM events
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    rows = cur.fetchall()
    conn.close()
    
    events = []
    for row in rows:
        events.append({
            "id": row[0],
            "event_time": row[1],
            "label": row[2],
            "confidence": float(row[3]),
            "image_path": row[4]
        })
    
    return events
```

**O que faz?**
- Conecta ao banco SQLite
- Executa consulta SQL para pegar eventos
- Converte resultados em dicionários Python
- Garante que `confidence` seja float

### Etapa 3: Implementar Lógica de Análise

A função principal `ask_about_last_event()` usa **pattern matching** para entender perguntas:

```python
def ask_about_last_event(user_question: str) -> str:
    events = get_recent_events(limit=50)
    
    if not events:
        return "Ainda não há eventos detectados."
    
    question = user_question.lower().strip()
    
    # ===== CONFIANÇA =====
    if "confiança" in question or "indice" in question:
        confidences = [evt["confidence"] for evt in events]
        max_conf = max(confidences)
        
        if "maior" in question or "máxima" in question:
            event_max = next(e for e in events if e["confidence"] == max_conf)
            return f"Maior confiança: {max_conf:.2f}"
```

**Estratégia de Pattern Matching**:
1. Converte pergunta para minúsculas
2. Verifica se contém palavras-chave
3. Executa lógica específica
4. Retorna resposta formatada

### Etapa 4: Integrar com FastAPI

**Arquivo**: `app.py`

```python
from services.chat_service import ask_about_last_event

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Endpoint do chat"""
    answer = ask_about_last_event(req.message)
    return ChatResponse(answer=answer)
```

**Modelos Pydantic**:
```python
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
```

### Etapa 5: Criar Frontend HTML

**Arquivo**: `templates/index.html`

```html
<section class="chat-section">
    <h2>Chat de interpretação de eventos</h2>
    <textarea id="chatInput" placeholder="Faça uma pergunta..."></textarea>
    <button onclick="sendMessage()">Enviar pergunta</button>
    <div id="response"></div>
</section>
```

**JavaScript**:
```javascript
async function sendMessage() {
    const question = document.getElementById('chatInput').value;
    
    const response = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: question})
    });
    
    const data = await response.json();
    document.getElementById('response').innerText = data.answer;
}
```

---

## Código Explicado

### Parte 1: Importações e Configuração

```python
import os
import sqlite3
from collections import Counter
from datetime import datetime

DB_PATH = "detections.db"
```

- `sqlite3`: Acessa banco de dados
- `Counter`: Conta ocorrências de objetos
- `DB_PATH`: Caminho do banco

### Parte 2: Buscar Eventos

```python
def get_recent_events(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, event_time, label, confidence, image_path
        FROM events
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
```

**Fluxo**:
1. Conecta ao banco
2. Cria cursor
3. Executa SQL (ORDER BY DESC = mais recentes primeiro)
4. Limita a N eventos

### Parte 3: Análise de Confiança

```python
if "confiança" in question or "indice" in question:
    confidences = [evt["confidence"] for evt in events]
    max_conf = max(confidences)
    min_conf = min(confidences)
    avg_conf = sum(confidences) / len(confidences)
```

**Operações**:
- `max()` e `min()`: Encontra valores extremos
- `sum() / len()`: Calcula média
- **List comprehension**: Extrai valores de forma elegante

### Parte 4: Contagem de Objetos

```python
if "quantos" in question or "quantidade" in question:
    labels_counter = Counter(evt["label"] for evt in events)
    
    if "pessoa" in question:
        count = labels_counter.get("person", 0)
        return f"Foram detectadas {count} pessoas..."
```

**Counter**:
- Conta automaticamente ocorrências
- `.get(chave, padrão)`: Retorna 0 se não encontra

### Parte 5: Padrão Mais Comum

```python
if "mais" in question and "detectado" in question:
    labels_counter = Counter(evt["label"] for evt in events)
    most_common = labels_counter.most_common(1)[0]
    # most_common = ("person", 45)
    return f"Objeto mais detectado: '{most_common[0]}' ({most_common[1]}x)"
```

**`most_common()`**: Retorna tuplas `(item, contagem)`

### Parte 6: Fallback (Resposta Padrão)

```python
# Se nenhuma palavra-chave for encontrada
labels_counter = Counter(evt["label"] for evt in events)
confidences = [evt["confidence"] for evt in events]
most_common = labels_counter.most_common(1)[0]

return (
    f"Análise dos últimos {len(events)} eventos:\n"
    f"- Mais detectado: {most_common[0]} ({most_common[1]}x)\n"
    f"- Confiança média: {sum(confidences)/len(confidences):.2f}\n"
    f"- Último evento: {events[0]['label']} às {events[0]['event_time']}"
)
```

Garante que sempre haja uma resposta útil.

---

## Como Usar

### 1. Iniciar o Servidor

```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Rodar servidor
python -m uvicorn app:app --reload
```

### 2. Acessar a Interface

Abra no navegador: `http://127.0.0.1:8000`

### 3. Fazer Perguntas

**Exemplos de perguntas que funcionam**:

| Pergunta | Resposta |
|----------|----------|
| "qual foi o maior indice de confiança?" | Retorna confiança máxima |
| "quantas pessoas foram detectadas?" | Conta "person" |
| "qual foi mais detectado?" | Objeto mais frequente |
| "quando foi o último evento?" | Hora do último evento |
| "resuma os eventos" | Resumo completo |

---

## Estrutura de Dados

### Tabela `events` no SQLite

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    event_time TEXT,          -- "2026-03-10 19:09:20"
    label TEXT,               -- "person", "car", "truck"
    confidence REAL,          -- 0.0 a 1.0
    image_path TEXT           -- caminho da imagem
)
```

### Exemplo de Evento

```python
{
    "id": 123,
    "event_time": "2026-03-10 19:09:20",
    "label": "person",
    "confidence": 0.89,
    "image_path": "static/captures/2026-03-10_190920.jpg"
}
```

---

## Fluxo Completo de uma Pergunta

```
1. Usuário digita: "qual foi a maior confiança?"
                        ↓
2. JavaScript envia POST /chat com {message: "qual foi..."}
                        ↓
3. FastAPI recebe em app.py na rota /chat
                        ↓
4. Chama ask_about_last_event("qual foi a maior confiança?")
                        ↓
5. Função busca 50 eventos de get_recent_events()
                        ↓
6. Converte pergunta: "qual foi a maior confiança?" → minúsculas
                        ↓
7. Detecta palavras-chave: "confiança" ✓, "maior" ✓
                        ↓
8. Calcula max(confidences) = 0.95
                        ↓
9. Busca evento com essa confiança
                        ↓
10. Retorna: "Maior confiança: 0.95 (person) em 2026-03-10 19:09:20"
                        ↓
11. FastAPI retorna JSON: {"answer": "Maior confiança: ..."}
                        ↓
12. JavaScript exibe a resposta na tela
```

---

## Vantagens da Implementação Atual

✅ **Sem dependências externas de IA** - Não usa OpenAI (gratuito)
✅ **Rápido** - Análise local em milissegundos
✅ **Sem limite de requisições** - Não cobra por tokens
✅ **Fácil de entender** - Usa Python puro
✅ **Fácil de estender** - Adicione novas perguntas facilmente

---

## Como Adicionar Novas Perguntas

Exemplo: Adicionar suporte a "Quais foram os animais detectados?"

**Passo 1**: Adicione no `chat_service.py`:

```python
# ===== NOVOS PADRÕES =====
if "animal" in question:
    labels_counter = Counter(evt["label"] for evt in events)
    # Assume que você tem uma classe "animal" no YOLO
    count = labels_counter.get("animal", 0)
    return f"Foram detectados {count} animais"
```

**Pronto!** Agora o chat responde a perguntas sobre animais.

---

## Melhorias Futuras

1. **Machine Learning Local** - Usar Ollama ao invés de OpenAI
2. **NLP Avançado** - Biblioteca spacy para processamento melhor
3. **Cache de Respostas** - Armazenar perguntas frequentes
4. **Histórico de Chat** - Guardar conversas completas
5. **Análise Temporal** - "Quantos eventos tivemos entre 9h e 10h?"
6. **Alertas Automáticos** - "Avise-me se tiver mais de 5 pessoas"
7. **Exportar Relatórios** - Gerar PDF com análises

---

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'fastapi'"

**Solução**:
```bash
pip install -r requirements.txt
```

### Erro: "No such file or directory: 'detections.db'"

**Solução**: O banco não existe ainda. Rode a aplicação uma vez para criar:
```bash
python -m uvicorn app:app --reload
```

### Chat retorna respostas genéricas sempre

**Motivo**: Suas perguntas não contêm as palavras-chave esperadas

**Solução**: Use as palavras-chave (veja tabela acima)

---

## Resumo de Implementação

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| Lógica de Chat | `services/chat_service.py` | Processar perguntas |
| Rota FastAPI | `app.py` | Receber requisições HTTP |
| Interface | `templates/index.html` | Exibir chat para usuário |
| Banco de Dados | `detections.db` | Armazenar eventos |

---

## Conclusão

Este chat demonstra como criar um sistema inteligente **sem IA externa**, usando apenas:
- ✅ Python puro
- ✅ Padrão matching
- ✅ Estatística básica
- ✅ Estruturas de dados eficientes

É uma solução **escalável, gratuita e fácil de manter** para fins educacionais e de produção!

---

**Autor**: Implementação e Manual
**Data**: Março 26, 2026
**Versão**: 1.0
