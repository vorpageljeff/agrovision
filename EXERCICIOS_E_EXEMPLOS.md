# Exemplos Práticos e Exercícios - Chat AgroVision

## Parte 1: Exemplos de Código

### Exemplo 1: Entender o Pattern Matching

```python
# Pergunta do usuário
user_question = "qual foi a maior confiança dos registros de hoje?"

# Converter para minúsculas (facilita comparação)
question = user_question.lower().strip()
# Resultado: "qual foi a maior confiança dos registros de hoje?"

# Verificar palavras-chave
if "confiança" in question:
    print("✓ Pergunta é sobre confiança!")
    
    if "maior" in question or "máxima" in question:
        print("✓ Usuário quer a MAIOR confiança")
    elif "menor" in question:
        print("✓ Usuário quer a MENOR confiança")
    elif "média" in question:
        print("✓ Usuário quer a MÉDIA de confiança")
```

### Exemplo 2: Calcular Estatísticas

```python
# Lista de eventos com confiança
events = [
    {"confidence": 0.95, "label": "person"},
    {"confidence": 0.87, "label": "car"},
    {"confidence": 0.92, "label": "person"},
    {"confidence": 0.78, "label": "truck"},
    {"confidence": 0.89, "label": "person"},
]

# Extrair apenas confiança
confidences = [evt["confidence"] for evt in events]
# Resultado: [0.95, 0.87, 0.92, 0.78, 0.89]

# Calcular máximo
max_conf = max(confidences)
# Resultado: 0.95

# Calcular mínimo
min_conf = min(confidences)
# Resultado: 0.78

# Calcular média
avg_conf = sum(confidences) / len(confidences)
# Resultado: 0.882

# Formatar resultado
print(f"Confiança - Máx: {max_conf:.2f}, Mín: {min_conf:.2f}, Média: {avg_conf:.2f}")
# Output: Confiança - Máx: 0.95, Mín: 0.78, Média: 0.88
```

### Exemplo 3: Usar Counter para Contar

```python
from collections import Counter

events = [
    {"label": "person"},
    {"label": "person"},
    {"label": "car"},
    {"label": "person"},
    {"label": "truck"},
]

# Contar cada tipo de objeto
labels = [evt["label"] for evt in events]
labels_counter = Counter(labels)
# Resultado: Counter({'person': 3, 'car': 1, 'truck': 1})

# Acessar contagem específica
person_count = labels_counter.get("person", 0)
# Resultado: 3

# Encontrar o mais comum
most_common = labels_counter.most_common(1)
# Resultado: [('person', 3)]

# Desempacotar resultado
label, count = most_common[0]
print(f"Mais detectado: {label} ({count} vezes)")
# Output: Mais detectado: person (3 vezes)
```

### Exemplo 4: Buscar Evento Específico

```python
events = [
    {"confidence": 0.95, "label": "person", "event_time": "10:30:45"},
    {"confidence": 0.87, "label": "car", "event_time": "10:25:20"},
    {"confidence": 0.92, "label": "person", "event_time": "10:15:00"},
]

# Encontrar evento com maior confiança
max_conf = max([e["confidence"] for e in events])
event_max = next(e for e in events if e["confidence"] == max_conf)

print(f"Maior confiança: {event_max['confidence']:.2f}")
print(f"Objeto: {event_max['label']}")
print(f"Horário: {event_max['event_time']}")
```

---

## Parte 2: Exercícios Práticos

### Exercício 1: Adicionar Suporte a Perguntas sobre Hora

**Objetivo**: Fazer o chat responder "que horas foram os eventos?"

**Seu código aqui**:
```python
def ask_about_last_event(user_question: str) -> str:
    events = get_recent_events(limit=50)
    question = user_question.lower().strip()
    
    # TODO: Adicione lógica para detectar "que horas"
    # Dica: Use a estrutura de data/hora em event_time
    
    if "que horas" in question:
        # Sua implementação aqui
        pass
```

**Solução** (veja ao final):
```python
if "que horas" in question or "horário" in question:
    times = [evt["event_time"] for evt in events]
    return f"Horários dos eventos: {', '.join(times[:5])}"
```

---

### Exercício 2: Implementar Filtro por Objeto

**Objetivo**: Responder "quantas pessoas foram detectadas entre 10h e 11h?"

**Seu código aqui**:
```python
def ask_about_last_event(user_question: str) -> str:
    events = get_recent_events(limit=50)
    question = user_question.lower().strip()
    
    # TODO: Detectar intervalo de tempo e filtrar eventos
    # Dica: Use slicing de strings para extrair horas
    
    if "entre" in question and "e" in question:
        # Sua implementação aqui
        pass
```

---

### Exercício 3: Criar Alertas Automáticos

**Objetivo**: Avisar se houve mais de N detecções de um tipo

**Seu código aqui**:
```python
def check_alerts(events, thresholds):
    """
    Verifica se há alertas baseado em limiares
    
    Parâmetros:
    - events: lista de eventos
    - thresholds: dict como {"person": 5, "car": 10}
    
    Retorna:
    - lista de alertas
    """
    from collections import Counter
    
    labels_counter = Counter(evt["label"] for evt in events)
    alerts = []
    
    # TODO: Comparar contagens com thresholds
    # Se exceder, adicionar à lista de alertas
    
    return alerts

# Usar a função
alerts = check_alerts(events, {"person": 3, "car": 2})
# Se tiver mais de 3 pessoas, gerar alerta
```

---

### Exercício 4: Analisar Confiança por Tipo de Objeto

**Objetivo**: Retornar "Qual é a confiança média de pessoas?"

**Seu código aqui**:
```python
def get_confidence_by_label(events, label):
    """Calcula confiança média para um tipo de objeto específico"""
    
    # TODO: Filtrar eventos do tipo label
    # Calcular média de confiança
    # Retornar resultado formatado
    
    pass

# Exemplo de uso
avg_confidence = get_confidence_by_label(events, "person")
print(f"Confiança média de pessoas: {avg_confidence:.2f}")
```

---

## Parte 3: Desafios Avançados

### Desafio 1: Detector de Anomalias

```python
def detect_anomalies(events):
    """
    Detecta eventos com confiança anormalmente baixa ou alta
    
    Anomalia: confiança > média + 2*desvio_padrão
    OU confiança < média - 2*desvio_padrão
    """
    import statistics
    
    confidences = [e["confidence"] for e in events]
    
    # Calcular média e desvio padrão
    media = statistics.mean(confidences)
    desvio = statistics.stdev(confidences)
    
    # Encontrar anomalias
    anomalies = []
    for event in events:
        conf = event["confidence"]
        if conf > media + 2 * desvio or conf < media - 2 * desvio:
            anomalies.append(event)
    
    return anomalies
```

**Sua tarefa**: Integrar isso no chat para responder "teve alguma anomalia?"

---

### Desafio 2: Padrão Temporal

```python
def analyze_temporal_pattern(events):
    """
    Analisa padrão de atividade ao longo do tempo
    (Exemplo: mais detecções entre 9h-12h?)
    """
    from collections import defaultdict
    from datetime import datetime
    
    # Agrupar por hora
    by_hour = defaultdict(int)
    
    for event in events:
        # Extrair hora de event_time (formato: "2026-03-10 19:09:20")
        time_str = event["event_time"].split(" ")[1]  # "19:09:20"
        hour = time_str.split(":")[0]  # "19"
        
        by_hour[hour] += 1
    
    # Encontrar hora com mais atividade
    most_active_hour = max(by_hour, key=by_hour.get)
    
    return f"Hora com mais atividade: {most_active_hour}h ({by_hour[most_active_hour]} eventos)"
```

---

## Parte 4: Testes Unitários

### Exemplo de Teste

```python
import unittest

class TestChatService(unittest.TestCase):
    
    def setUp(self):
        """Preparar dados para cada teste"""
        self.events = [
            {"confidence": 0.95, "label": "person"},
            {"confidence": 0.87, "label": "car"},
            {"confidence": 0.92, "label": "person"},
        ]
    
    def test_max_confidence(self):
        """Testar se calcula corretamente a confiança máxima"""
        confidences = [e["confidence"] for e in self.events]
        max_conf = max(confidences)
        
        self.assertEqual(max_conf, 0.95)
    
    def test_count_persons(self):
        """Testar se conta corretamente pessoas"""
        from collections import Counter
        
        labels_counter = Counter(e["label"] for e in self.events)
        person_count = labels_counter.get("person", 0)
        
        self.assertEqual(person_count, 2)
    
    def test_most_common(self):
        """Testar se encontra objeto mais comum"""
        from collections import Counter
        
        labels_counter = Counter(e["label"] for e in self.events)
        most_common = labels_counter.most_common(1)[0][0]
        
        self.assertEqual(most_common, "person")

# Rodar testes
if __name__ == '__main__':
    unittest.main()
```

**Como rodar**:
```bash
python -m unittest seu_arquivo_teste.py
```

---

## Parte 5: Soluções dos Exercícios

### Solução do Exercício 1

```python
if "que horas" in question or "horário" in question or "horario" in question:
    # Pegar primeiros 5 horários únicos
    times = list(set([evt["event_time"] for evt in events]))[:5]
    time_list = ", ".join(times)
    return f"Horários dos eventos: {time_list}"
```

### Solução do Exercício 2

```python
if "entre" in question and "e" in question:
    # Exemplo: "entre 10 e 11"
    try:
        parts = question.split("entre")[1].split("e")
        start_hour = int(parts[0].strip().split()[0])
        end_hour = int(parts[1].strip().split()[0])
        
        # Filtrar eventos nesse intervalo
        filtered = []
        for evt in events:
            hour = int(evt["event_time"].split(":")[0])
            if start_hour <= hour <= end_hour:
                filtered.append(evt)
        
        return f"Encontrados {len(filtered)} eventos entre {start_hour}h e {end_hour}h"
    except:
        return "Não consegui processar o intervalo"
```

### Solução do Exercício 3

```python
def check_alerts(events, thresholds):
    from collections import Counter
    
    labels_counter = Counter(evt["label"] for evt in events)
    alerts = []
    
    for label, threshold in thresholds.items():
        count = labels_counter.get(label, 0)
        if count > threshold:
            alerts.append(f"⚠️ ALERTA: {count} detecções de {label} (limite: {threshold})")
    
    return alerts if alerts else ["✓ Nenhum alerta"]
```

### Solução do Exercício 4

```python
def get_confidence_by_label(events, label):
    # Filtrar apenas eventos do tipo label
    filtered = [e for e in events if e["label"] == label]
    
    if not filtered:
        return 0.0
    
    # Calcular média
    confidences = [e["confidence"] for e in filtered]
    avg = sum(confidences) / len(confidences)
    
    return avg

# Usar
avg_person = get_confidence_by_label(events, "person")
print(f"Confiança média de pessoas: {avg_person:.2f}")
```

---

## Resumo de Aprendizados

### Conceitos Importantes

1. **Pattern Matching**: Detectar palavras-chave em strings
2. **List Comprehension**: Extrair dados de listas elegantemente
3. **Counter**: Contar ocorrências eficientemente
4. **SQLite**: Armazenar e recuperar dados
5. **FastAPI**: Criar APIs HTTP
6. **HTML/JS**: Interface web

### Skills Desenvolvidos

✅ Python avançado
✅ Banco de dados
✅ Web development
✅ Problem solving
✅ System design

---

**Próximos Passos Sugeridos**:
1. Implementar todos os exercícios
2. Adicionar novos padrões de pergunta
3. Criar interface mais bonita
4. Integrar com Discord/Telegram bot
5. Machine learning com dados reais

Boa sorte! 🚀
