from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import asyncio
import websockets

# ----- Configurações -----
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 8080  # Render geralmente usa 8080 ou a porta do env
WS_HOST = "0.0.0.0"
WS_PORT = 1488
API_KEY = "key123"

# ----- Dados -----
jobs_list = []
clients = set()

# ----- Flask -----
app = Flask(__name__)
CORS(app)

@app.route("/pets", methods=["GET"])
def get_pets():
    return jsonify(jobs_list)

@app.route("/webhook", methods=["POST"])
def webhook():
    key = request.headers.get("X-API-KEY")
    if key != API_KEY:
        return "Unauthorized", 401

    data = request.json
    job_ids = data.get("job_ids", [])
    join_links = data.get("join_links", [])

    if job_ids or join_links:
        new_entry = {
            "job_ids": job_ids,
            "join_links": join_links
        }
        jobs_list.append(new_entry)
        print(f"✅ Novo Job/Link adicionado: {new_entry}")

        # Broadcast para WebSocket
        asyncio.run_coroutine_threadsafe(broadcast_message(new_entry), ws_loop)

    return "", 204

# ----- WebSocket -----
async def ws_handler(websocket):
    clients.add(websocket)
    print(f"[WS] Cliente conectado: {len(clients)}")
    try:
        async for _ in websocket:
            pass
    finally:
        clients.remove(websocket)
        print(f"[WS] Cliente desconectado: {len(clients)}")

async def broadcast_message(message):
    if clients:
        await asyncio.wait([client.send(str(message)) for client in clients])
        print(f"[WS] Enviado para {len(clients)} clientes")

async def start_ws_server():
    async with websockets.serve(ws_handler, WS_HOST, WS_PORT):
        print(f"[WS] Rodando em ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()  # Mantém servidor rodando

def start_ws_loop():
    global ws_loop
    ws_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(ws_loop)
    ws_loop.run_until_complete(start_ws_server())

# ----- Inicialização -----
if __name__ == "__main__":
    # Inicia WebSocket em thread separada
    threading.Thread(target=start_ws_loop, daemon=True).start()

    # Inicia Flask
    print(f"Flask rodando em http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT)
