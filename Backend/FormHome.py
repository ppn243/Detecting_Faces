import tkinter as tk
import cv2
from PIL import Image, ImageTk
from tkinter import messagebox
import numpy as np
from FormRegister import RegisterForm
from Handle import *
import urllib.request
import requests


# Create a class for the form
class CameraForm:
    def __init__(self, root, model, base_model):
        self.root = root
        self.root.title("Camera Form")
        # self.arrData = arrData

        # Load Process
        self.process = Process(model, base_model)
        self.temp = "ppn"
        self.count = 0

        # Create a frame to display camera feed
        self.frame = tk.Label(self.root)
        self.frame.pack()

        # Open the camera
        self.camera = cv2.VideoCapture(0)
        self.show_frame()
        self.data_sent = False

    def convert(self, result):
        boxes = result[0].boxes

        xyxy = pd.DataFrame(boxes.xyxy.cpu().numpy(), columns=[
                            'xmin', 'ymin', 'xmax', 'ymax'])
        conf = pd.DataFrame(boxes.conf.cpu().numpy(), columns=['confidence'])
        cls = pd.DataFrame(boxes.cls.cpu().numpy(), columns=['class'])

        result = pd.concat([xyxy, conf, cls], axis=1)

        return result.values.tolist()

    def close_form(self):
        # Đóng form
        self.root.destroy()

    def reset_data_sent_flag(self):
        self.data_sent = False

    # def SendData(self, result):
    #     # Điều chỉnh port phù hợp với cổng mà Flask của bạn đang chạy
    #     api_url = "http://localhost:5000/send_data"
    #     payload = {'result': result}

    #     try:
    #         response = requests.post(api_url, json=payload)
    #         if response.status_code == 200:
    #             print("Data sent successfully to backend")
    #         else:
    #             print("Error sending data to backend. Status code:",
    #                   response.status_code)
    #     except Exception as e:
    #         print("Error:", e)
    # # Khi bạn muốn gửi dữ liệu, thêm tên vào cuộc gọi SendData
    #     self.SendData(result)

    def SendResultToBackend(self, result):
        api_url = "http://localhost:5000/send_result"
        payload = {'result': result}

        # Kiểm tra xem đã gửi dữ liệu chưa
        if not self.data_sent:
            try:
                response = requests.post(api_url, json=payload)
                if response.status_code == 200:
                    print("Result sent successfully to backend")
                else:
                    print("Error sending result to backend. Status code:",
                          response.status_code)
            except Exception as e:
                print("Error:", e)

            # Cập nhật biến cờ để ngăn chặn việc gửi dữ liệu tiếp theo
            self.data_sent = True
            # Gọi phương thức để đóng form
            self.close_form()
            # Gọi phương thức để reset biến cờ, cho phép gửi dữ liệu tiếp theo
            self.reset_data_sent_flag()

    def show_frame(self):
        url = "http://172.16.4.114/cam-lo.jpg"
        # try:

        response = urllib.request.urlopen(url)

        img_array = np.array(bytearray(response.read()), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Các dòng mã xử lý detection và hiển thị ảnh giữ nguyên
        if frame is not None:
            res = self.process.model.predict(
                frame, save=False, imgsz=256, conf=0.4)
            result = self.convert(res)
            if len(result) != 0:
                face = result[0]
                print(face)
                xmin = int(face[0])  # xmin
                ymin = int(face[1])  # ymin
                xmax = int(face[2])  # xmax
                ymax = int(face[3])  # ymax
                crop_img = frame[ymin:ymax, xmin:xmax]
                if int(face[-1]) == 1:
                    frame = cv2.rectangle(
                        frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
                elif int(face[-1]) == 0:
                    frame = cv2.rectangle(
                        frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                crop_img = frame[ymin:ymax, xmin:xmax]
                resized_image = cv2.resize(
                    crop_img, (224, 224), interpolation=cv2.INTER_NEAREST)
                resized_image = np.expand_dims(resized_image, axis=0)
                vector = self.process.base_model.predict(
                    resized_image, verbose=0)
                result = self.process.compare(vector)
                if result != "Unknown" and not self.data_sent:
                    if result == self.temp and int(face[-1]) == 0:
                        self.count += 1
                        if self.count == 10:
                            ###############################################################################
                            self.SendResultToBackend(result)
                            # self.SendData('1', result)
                            print("result", result)
                            self.count = 0

                    else:
                        self.count = 0
                        self.temp = result

                cv2.putText(frame, result, (xmin, ymin-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Convert the frame to PIL Image
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)

            # Resize the image to fit the frame
            # //640, 480
            image = image.resize((480, 480), Image.LANCZOS)
            FRAME_INTERVAL_MS = int(1000 / 30)
            # Display the image on the frame
            photo = ImageTk.PhotoImage(image)
            self.frame.configure(image=photo)
            self.frame.image = photo
            self.root.after(FRAME_INTERVAL_MS, self.show_frame)
        # except Exception as e:
        #     print(f"Error retrieving image from ESP32-CAM: {e.args}")

            # Thực hiện xử lý lỗi tùy thuộc vào yêu cầu cụ thể của bạn

        # # Convert the frame to PIL Image
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # image = Image.fromarray(image)

        # # Resize the image to fit the frame
        # image = image.resize((640, 480), Image.LANCZOS)

        # # Display the image on the frame
        # photo = ImageTk.PhotoImage(image)
        # self.frame.configure(image=photo)
        # self.frame.image = photo
        # self.root.after(2, self.show_frame)

    # def SendData(self, data):
    #     self.arrData.write(data.encode('utf-8'))
