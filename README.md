Back-End
- Initialize environment
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
- System Component
  + Face Registration
    + Capture and Detection: The system captures facial images from the camera feed and performs face detection using the OpenCV library.
    + Data Processing: Processes the captured facial data, extracts facial features, and registers the user in the system. After the image processing is completed in the "process" folder, an automated workflow is implemented to seamlessly transfer the processed images to the "Raw" folder
      ![image](https://github.com/ppn243/Detecting_Faces/assets/91375299/082190f5-1ae1-478c-aaa7-812a9357514e)
  + Face Login
    + Real-time Face Recognition: Implements real-time face recognition to authenticate users attempting to log in
    + Comparison and Authentication: Compares the recognized facial features with the registered data and authenticates the user
    + User Feedback: Provides visual feedback on the GUI, indicating the recognized person's name and login status

