import os
import sqlite3
from collections import Counter
from datetime import datetime

DB_PATH = "detections.db"

def get_recent_events(limit: int = 10):
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

def get_last_event():
    events = get_recent_events(limit=1)
    return events[0] if events else None

def summarize_events(events):
    if not events:
        return "Não há eventos registrados."

    counter = Counter(event["label"] for event in events)
    parts = [f"{qty} {label}" for label, qty in counter.items()]
    return "Nos eventos recentes foram identificados: " + ", ".join(parts) + "."

def find_last_event_by_label(events, labels):
    for event in events:
        if event["label"].lower() in labels:
            return event
    return None

def ask_about_last_event(user_question: str) -> str:
    events = get_recent_events(limit=50)

    if not events:
        return "Ainda não há eventos detectados."

    question = user_question.lower().strip()

    # ===== CONFIANÇA =====
    if "confiança" in question or "indice" in question or "índice" in question:
        confidences = [evt["confidence"] for evt in events]
        max_conf = max(confidences)
        min_conf = min(confidences)
        avg_conf = sum(confidences) / len(confidences)
        
        if "maior" in question or "máxima" in question:
            event_max = next(e for e in events if e["confidence"] == max_conf)
            return f"Maior confiança: {max_conf:.2f} ({event_max['label']}) em {event_max['event_time']}"
        elif "menor" in question or "mínima" in question:
            event_min = next(e for e in events if e["confidence"] == min_conf)
            return f"Menor confiança: {min_conf:.2f} ({event_min['label']}) em {event_min['event_time']}"
        elif "média" in question:
            return f"Confiança média dos últimos {len(events)} eventos: {avg_conf:.2f}"
        else:
            return f"Confiança - Máxima: {max_conf:.2f}, Mínima: {min_conf:.2f}, Média: {avg_conf:.2f}"

    # ===== OBJETOS DETECTADOS =====
    if "quantos" in question or "quantidade" in question or "total" in question:
        labels_counter = Counter(evt["label"] for evt in events)
        
        total = len(events)
        if "pessoa" in question:
            count = labels_counter.get("person", 0)
            return f"Foram detectadas {count} pessoas nos últimos {total} eventos."
        elif "carro" in question or "veículo" in question or "veiculo" in question:
            count = sum([labels_counter.get(label, 0) for label in ["car", "truck", "bus", "motorcycle"]])
            return f"Foram detectados {count} veículos nos últimos {total} eventos."
        else:
            return f"Total de {total} eventos registrados. Distribuição: {dict(labels_counter)}"

    # ===== MAIS DETECTADO =====
    if "mais" in question and ("detectado" in question or "apareceu" in question or "frequente" in question):
        labels_counter = Counter(evt["label"] for evt in events)
        if labels_counter:
            most_common = labels_counter.most_common(1)[0]
            return f"Objeto mais detectado: '{most_common[0]}' com {most_common[1]} ocorrências"
        return "Sem dados suficientes."

    # ===== HORÁRIO / ÚLTIMO EVENTO =====
    if "quando" in question or "que horas" in question or "horário" in question or "horario" in question or "último" in question or "ultimo" in question:
        last = events[0]
        return f"Último evento: {last['label']} em {last['event_time']} (confiança: {last['confidence']:.2f})"

    # ===== OCORRÊNCIAS POR TIPO =====
    if "ocorrência" in question or "ocorrencia" in question or "quantas vezes" in question:
        labels_counter = Counter(evt["label"] for evt in events)
        summary = ", ".join([f"{label}: {count}" for label, count in labels_counter.most_common()])
        return f"Ocorrências nos últimos eventos: {summary}"

    # ===== RESUMO GERAL =====
    if "resumo" in question or "resumir" in question or "o que" in question or "teve" in question:
        labels_counter = Counter(evt["label"] for evt in events)
        confidences = [evt["confidence"] for evt in events]
        most_common = labels_counter.most_common(3)
        avg_conf = sum(confidences) / len(confidences)
        
        summary = f"Nos últimos {len(events)} eventos:\n"
        summary += f"- Objetos detectados: {', '.join([f'{label}({count})' for label, count in most_common])}\n"
        summary += f"- Confiança média: {avg_conf:.2f}\n"
        summary += f"- Evento mais recente: {events[0]['label']} em {events[0]['event_time']}"
        return summary

    # ===== PADRÃO DE ATIVIDADE =====
    if "padrão" in question or "padrao" in question or "atividade" in question:
        labels_counter = Counter(evt["label"] for evt in events)
        most_common = labels_counter.most_common(3)
        return f"Padrão de atividade: Predominante '{most_common[0][0]}' ({most_common[0][1]} vezes)"

    # ===== FALLBACK - RESPOSTA GERAL =====
    labels_counter = Counter(evt["label"] for evt in events)
    confidences = [evt["confidence"] for evt in events]
    most_common = labels_counter.most_common(1)[0] if labels_counter else ("desconhecido", 0)
    
    return (
        f"Análise dos últimos {len(events)} eventos:\n"
        f"- Mais detectado: {most_common[0]} ({most_common[1]}x)\n"
        f"- Confiança média: {sum(confidences)/len(confidences):.2f}\n"
        f"- Último evento: {events[0]['label']} às {events[0]['event_time']}"
    )