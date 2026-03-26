import os
import cv2
import sqlite3
import threading
import time
from datetime import datetime
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from ultralytics import YOLO

from services.chat_service import ask_about_last_event

# =========================
# CONFIGURAÇÕES INICIAIS
# =========================
DB_PATH = "detections.db"
MODEL_PATH = "yolov8n.pt"   # pode trocar depois para yolo11n.pt se quiser
SAVE_DIR = "static/captures"
CAMERA_INDEX = 0

TARGET_CLASSES = {"person", "car", "truck", "bus", "motorcycle"}

os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs(SAVE_DIR, exist_ok=True)

# =========================
# FASTAPI
# =========================
app = FastAPI(title="AgroVision AI")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# =========================
# MODELOS DO CHAT
# =========================
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

# =========================
# MODELO YOLO
# =========================
model = YOLO(MODEL_PATH)

# =========================
# ESTADO GLOBAL
# =========================
last_frame = None
last_frame_lock = threading.Lock()
detection_state = defaultdict(int)

# =========================
# BANCO DE DADOS
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_time TEXT NOT NULL,
            label TEXT NOT NULL,
            confidence REAL NOT NULL,
            image_path TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def save_event(label: str, confidence: float, image_path: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO events (event_time, label, confidence, image_path)
        VALUES (?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        label,
        float(confidence),
        image_path
    ))

    conn.commit()
    conn.close()

def list_events(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT id, event_time, label, confidence, image_path
        FROM events
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]

# =========================
# PROCESSAMENTO DE STREAM
# =========================
def process_stream():
    global last_frame

    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("Erro: não foi possível abrir a câmera.")
        return

    print("Câmera iniciada com sucesso.")

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        results = model(frame, verbose=False)
        annotated_frame = frame.copy()

        frame_labels = []

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                label = model.names[cls_id]

                if label not in TARGET_CLASSES:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                # desenha caixa
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    annotated_frame,
                    f"{label} {conf:.2f}",
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

                frame_labels.append((label, conf))

        # salva último frame anotado
        with last_frame_lock:
            last_frame = annotated_frame.copy()

        # evita salvar infinitamente o mesmo tipo todo frame
        current_labels = {label for label, _ in frame_labels}

        for label, conf in frame_labels:
            if detection_state[label] == 0:
                filename = f"{label}_{int(time.time())}.jpg"
                relative_path = f"{SAVE_DIR}/{filename}"
                absolute_path = os.path.abspath(relative_path)

                cv2.imwrite(absolute_path, annotated_frame)
                save_event(label, conf, "/" + relative_path.replace("\\", "/"))

                detection_state[label] = 1

        # reseta estado quando o objeto some da cena
        for known_label in list(detection_state.keys()):
            if known_label not in current_labels:
                detection_state[known_label] = 0

        time.sleep(0.2)

# =========================
# STARTUP
# =========================
@app.on_event("startup")
def startup_event():
    init_db()
    thread = threading.Thread(target=process_stream, daemon=True)
    thread.start()

# =========================
# ROTAS
# =========================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    events = list_events(limit=10)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "events": events
    })

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/events", response_class=JSONResponse)
def events():
    return list_events(limit=20)

@app.get("/frame")
def get_frame():
    global last_frame

    with last_frame_lock:
        if last_frame is None:
            return Response(status_code=404)

        success, encoded_image = cv2.imencode(".jpg", last_frame)
        if not success:
            return Response(status_code=500)

        return Response(content=encoded_image.tobytes(), media_type="image/jpeg")

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    answer = ask_about_last_event(req.message)
    return ChatResponse(answer=answer)