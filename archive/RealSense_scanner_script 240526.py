import websocket
from qrplane_lib import QRPlane, Corner, D435_Scanner
import cv2
from pyzbar.pyzbar import decode
import threading

# create a list of planes

all_planes = {}
final_average_planes = {}
startRecording = False

def on_message(ws, message):
    global all_planes
    global final_average_planes
    global startRecording

    # print the message
    if ("|" in message):
        message_parts = message.split("|")
        qr_content = message_parts[0]
        is_solid = message_parts[1] == "True"
        base_plane = message_parts[2]

        # print(final_average_planes)
        # the plane is not in the final_average_planes get it
        if qr_content in final_average_planes:
            final_average_planes[qr_content] = QRPlane([], qr_content)
            existing_plane = final_average_planes[qr_content]
            existing_plane.solid = is_solid
            existing_plane.base_plane = base_plane

            final_average_planes[qr_content] = existing_plane
    elif (message == "startRecording"):
        # if the average planes are not empty, start recording
        if (len(final_average_planes) == 0):
            threading.Thread(target=run_scanner).start()
        else:
            final_average_planes  = {}
            all_planes = {}
            print("reset record")
    elif (message == "startRecording"):
        startRecording = False


    


def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    print("Waiting for Scan Start Command From GH")


websocket.enableTrace(False)
# make ws global
global ws

server_url = 'wss://remosharp-public-server10.glitch.me/'
local_server_url = "ws://127.0.0.1:18580/RemoSharp"

ws = websocket.WebSocketApp(local_server_url,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)


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
                    if(final_average_planes[key].solid != True):
                        final_average_planes[key] = average_plane 
                #     if (final_average_planes[key].standard_deviation > average_plane.standard_deviation):
                #         average_plane.solid = True
                #         final_average_planes[key] = average_plane
                # send the average plane to the server
            
            try:
                for key in final_average_planes:
                    query_plane = final_average_planes[key]
                    if (final_average_planes[key].solid != True):
                        ws.send(final_average_planes[key].serialize())
                        if (counter % 10 == 0):
                            print(final_average_planes[key].to_string())
            except Exception as e:
                print(e)


    finally:
        # Stop the pipeline
        scanner.pipeline.stop()
    
# start scanner on a differnet thread


# make the client open the connection
# it should both send the handshake request and receive the handshake response
ws.on_open = on_open
ws.run_forever()