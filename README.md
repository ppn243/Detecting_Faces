Back-End
- Initialize environment in Terminal VSCode
  + python -m venv .venv
  + python -m pip install --upgrade pip
  + .venv\Scripts\activate: move to the environment in which to install the library
    + pip install flask
    + pip install opencv-python
    + pip install Pillow
    + pip install pandas
    + pip install ultralytics
    + pip install tensorflow
    + pip install scikit-learn
    + pip install tkinter
    + python app.py : Running the app [Back-End]
- Library: Using Flask to develop the project
- The integration of key Python libraries
  + OpenCV for face detection and recognition
  + PIL for image manipulation
  + Numpy for numerical operations
  + OS for file system management
  + tkinter for the graphical user interface
  + urllib for web interactions,
  + Pandas for efficient data handling creates a robust and comprehensive platform
- System Workflow
  ![image](https://github.com/ppn243/Detecting_Faces/assets/91375299/91f5a07e-924f-4158-b09d-1e5abc0e7968)
  + Face Registration
    + Captures facial images from the camera feed
    + Performs face detection and anti-spoofing measures
    + Extracts facial features and registers the user in the system
  + Face Login
    + Real-time face recognition on the camera feed
    + Compares recognized features with registered data
    +  Provides visual feedback on the GUI, including recognized names and login status
  + Data Communication
    + Utilizes the Requests library to send data (result and name) to the backend server for further processing
