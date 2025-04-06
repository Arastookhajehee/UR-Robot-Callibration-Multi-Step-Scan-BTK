import asyncio
import websockets
from qrplane_lib import QRPlane, Corner, D435_Scanner
import cv2
from pyzbar.pyzbar import decode
import threading
import time as t
import json

# List to store connected clients
connected_clients = []
current_plane = ""
base_plane = ""
sd_threshold_02 = 20
sd_threshold_01 = 1
active_sd_threshold = sd_threshold_01

all_planes = {}
final_average_planes = {}
startRecording = False


def run_scanner():   
    try:
        counter = 0
        scanner = D435_Scanner()
        while True:
            counter += 1
            color_image, coords = scanner.get_frames_and_coordinates()
            
            decoded_objects = decode(color_image)
            corner_objects = []
            try:

                # get the coordinates of the corners of the QR code
                color_image = D435_Scanner.get_corner_coordinates(decoded_objects, coords,all_planes,color_image)
                cv2.imshow("Image", color_image)
                cv2.waitKey(1) 
                # make the cv2 window always on top
                cv2.setWindowProperty("Image", cv2.WND_PROP_TOPMOST, 1)

            except Exception as e:
                print(e)
                    
            average_planes = D435_Scanner.process_planes(all_planes)
            for key in average_planes:
                average_plane = average_planes[key]

                # if the qrplane is not in the final_average_planes, add it
                if key not in final_average_planes:
                    final_average_planes[key] = average_plane    
                else:
                    current_plane = final_average_planes[key]
                    current_plane_sd = current_plane.standard_deviation
                    current_plane_is_solid = current_plane.solid
                    
                    if (current_plane_is_solid == True):
                        pass

                    if(current_plane.solid != True):
                        new_sd = average_plane.standard_deviation
                        if (new_sd < active_sd_threshold):
                            average_plane.solid = True
                            average_plane.base_plane = base_plane
                            final_average_planes[key] = average_plane
            
            # send_results(connected_clients)

    finally:
        # Stop the pipeline
        scanner.pipeline.stop()

async def send_results(connected_clients):
    for client in connected_clients:
        try:
            result_message_parts = []
            for key in final_average_planes:
                query_plane = final_average_planes[key]
                if (final_average_planes[key].solid == True):
                    result_message_parts.append(final_average_planes[key].serialize())
                    # print(final_average_planes[key].to_string())
            result_message = json.dumps(result_message_parts)
            if (len(result_message_parts) > 0):
                await client.send(result_message)
        except Exception as e:
            print(e)

# Function to handle new client connections
async def handle_connection(websocket):
    # Add the client to the list of connected clients
    connected_clients.append(websocket)
    print(f"New client connected. Total clients: {len(connected_clients)}")

    try:
        # Keep listening for messages from the client
        async for message in websocket:
            await on_message(message, websocket)
    except:
        # Remove the client from the list when the connection is closed
        connected_clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(connected_clients)}")
    finally:
        # Remove the client from the list when the connection is closed
        connected_clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(connected_clients)}")

async def on_message(message, websocket):
    global base_plane
    global all_planes
    global final_average_planes
    global startRecording
    global active_sd_threshold

    # print the message
    if ("|" in message):
        base_plane = message.replace("|","")

        # send back the results
        await send_results(connected_clients)

    elif (message == "startRecording"):
        # if the average planes are not empty, start recording
        if (len(final_average_planes) == 0):
            threading.Thread(target=run_scanner).start()
            final_average_planes = {}
            all_planes = {}
            await websocket.send("")
            print("Started Recording")
        else:
            final_average_planes  = {}
            all_planes = {}
            print("reset record")
    elif (message == "restartRecording"):
        final_average_planes = {}
        all_planes = {}
        await websocket.send("")
    elif (message == "echotest"):
        print("echo test")
        await websocket.send("echo test")
        

# # Start the WebSocket server
# start_server = websockets.serve(handle_connection, "localhost", 18580)

# # print the server address that clients need to connect to
# print(f"Server started. Connect to ws://localhost:18580")

async def main():
    # Start the WebSocket server
    start_server = await websockets.serve(handle_connection, "localhost", 18580)
    print(f"Server started. Connect to ws://localhost:18580")
    
    # Run the server forever
    await start_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())


