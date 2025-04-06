import asyncio
import websockets
import threading

# List to store connected clients
connected_clients = []

async def handle_message(websocket, path):
    # Append the client to the list of connected clients
    connected_clients.append(websocket)

    try:
        while True:
            # Wait for a message from the client
            message = await websocket.recv()

            # Echo the message to all connected clients
            for client in connected_clients:
                await client.send(message)
    except:
        connected_clients.remove(websocket)

# Start the WebSocket server
start_server = websockets.serve(handle_message, 'localhost', 8765)

async def send_ping():
    while True:
        # Iterate over connected clients
        for client in connected_clients:
            try:
                # Send "still there?" message to client
                await client.send("still there?")
            except websockets.exceptions.ConnectionClosed:
                # Remove disconnected client from the list
                connected_clients.remove(client)
        await asyncio.sleep(3)  # Wait for 10 seconds before sending the next ping

# Start sending pings to connected clients
asyncio.ensure_future(send_ping())

# start a new thread and run the send_ping function
threading.Thread(target=send_ping).start()

# Run the server indefinitely
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()