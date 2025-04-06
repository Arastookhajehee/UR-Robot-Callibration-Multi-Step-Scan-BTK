# Discription

This repository contains the implementation of a high-precision robotic calibration system using a custom 3D-printed end-effector equipped with an Intel RealSense D435 camera. The core of this project is an automated two-step calibration sequence that employs QR code detection at predefined base positions, integrating Python scripts with OpenCV and the Intel RealSense SDK for accurate 3D mapping. This sophisticated calibration technique ensures precise robot positioning, crucial for assembly tasks, with a repeatable accuracy of less than half a millimeter.

## Setting Up the Virtual Environment and Running RealSense_Server.py

### Prerequisites
* **Python 3.9.1** installed on your system. You can download it from [python.org](https://www.python.org/).
* **Intel RealSense d435i** depth camera
* **Grasshopper plugins:**:
    * RobotExMachina https://www.food4rhino.com/en/app/machina
    * RemoSharp https://www.remosharp.com
* **Direct USB connection** to the Intel RealSense d435i depth camera
* **3D Printed Callibration Tool** "scanner_mount_240525.3dm"
* [Recommended] OnRobot Finger Gripper RG6

End Effector | Print Settings for Ultimaker 3D Printers
------ | ------ 
![End Effector](./Images/Scanner%20End%20Effector%203D%20Print.jpg) | ![Printing Settings](./Images/3D%20Printing%20Settings.png)

### Mounting the Scanner
1. Mount the Scanner on the robot
2. Connect the scanner to PC via USB
3. Manually Callibrate the robot tool TCP using the 3-Point Method using the pointy end of the end effector
4. Write the TCP values in the Grasshopper file

Mounted End Effector | Mounted End Effector on Base
------ | ------ 
![Mounted End Effector](./Images/Scanner%20Mounted.jpg) | ![Mounted End Effector on Base](./Images/Point%20Callibration.jpg)

![TCP Values on Grasshopper](./Images/Tool%20TCP%20in%20GH.jpg)

### Steps to Set Up the Python Virtual Environment
1. Open a terminal or command prompt.
2. clone the repo and navigate to the folder:
    ```bash
    git clone https://github.com/Arastookhajehee/UR-Robot-Callibration-Multi-Step-Scan-BTK.git
    cd UR-Robot-Callibration-Multi-Step-Scan-BTK
    ```
3. Create a virtual environment:
    ```bash
    python -m venv .venv
    ```
4. Activate the virtual environment:
    - On Windows:
      ```bash
      .venv\Scripts\activate
      ```
5. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the RealSense_Server.py File
1. Ensure the virtual environment is activated.
2. Connect the Intel RealSense depth camera
3. Run the script:
    ```bash
    python RealSense_Server.py
    ```

### Connect to Robot via Machina Bridge
1. Ensure you are connected to the UR robot via a LAN cable
2. Ensure a healty connection to your robot py pinging it.
   * for more information please check: 
    * https://www.youtube.com/playlist?list=PLvxxYImPCApUffcv_KtdR-sQydA4O4CPH
    * https://www.youtube.com/watch?v=ztbUDMGq8b0&list=PLvxxYImPCApXj3tHVKmpTS_AuMPngnA47
3. Start Machina Bridge
4. Select UR as the robot brand (KUKA and ABB are also supported but not tested)
5. Connect to Robot and check the live connection with a simple command: 
    ```bach
    Move(0,0,30);
    ```

### Start the scanner on Grasshopper
1. Specify the scan result folder
2. choose a name for the robot collibration plane
3. place the 4 pre-defined point around where the QR codes should be
4. Turn these toggles to "True":
   * **Connect To Machina**
   * **Connect To Python Scanner**
   * **SAVE_TO_FILE**
5. Kick start the scanning sequence by clicking 
   * **robot move and scan**


Pre-Defined Points | Kick start buttons
------ | ------ 
![Multi-Step Calibration Scan Sequence](./Images/Pre-defined%20scan%20points.jpg) | ![Multi-Step Calibration Scan Sequence](./Images//Multi-Step%20Callibration%20Scan%20Sequence.jpg)

### Successful Scan Start
1. If the python script runs correctly, clicking the GH **robot move and scan** button the camera rgb feed should pop up as a window
2. If the scanner can find 4 QR codes it will automatically trigger a second scanning sequence in which the robot moves above the QR codes.
3. The result of the scan will be a .csv file with a plane defined in the robot's origin point coordinate system