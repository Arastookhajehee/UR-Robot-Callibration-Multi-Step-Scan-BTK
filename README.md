
# Setting Up the Virtual Environment and Running RealSense_Server.py

## Prerequisites
Ensure you have **Python 3.9.1** installed on your system. You can download it from [python.org](https://www.python.org/).

## Steps to Set Up the Virtual Environment
1. Open a terminal or command prompt.
2. clone the repo and navigate to the folder:
    ```bash
    cd /c:/Projects/BTU
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

## Running the RealSense_Server.py File
1. Ensure the virtual environment is activated.
2. Run the script:
    ```bash
    python RealSense_Server.py
    ```

## When Scripts Cannot Be Run
- Verify that Python is installed and added to your system's PATH.
- Ensure all dependencies are installed by running:
  ```bash
  pip install -r requirements.txt
  ```
- Check for syntax errors or missing files in the project directory.
- If the issue persists, consult the project documentation or seek assistance from the development team.