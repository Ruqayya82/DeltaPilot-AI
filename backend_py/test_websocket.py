import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/prices"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")

            # Send a test message
            await websocket.send(json.dumps({"symbol": "AAPL"}))

            # Receive messages
            for i in range(3):  # Receive up to 3 messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    print(f"Received: {data}")
                except asyncio.TimeoutError:
                    print("No more messages received")
                    break

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())