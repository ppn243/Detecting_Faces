import torch
import cv2
import pandas as pd
from ultralytics import YOLO


def convert(result):
    boxes = result[0].boxes

    xyxy = pd.DataFrame(boxes.xyxy.cpu().numpy(), columns=[
                        'xmin', 'ymin', 'xmax', 'ymax'])
    conf = pd.DataFrame(boxes.conf.cpu().numpy(), columns=['confidence'])
    cls = pd.DataFrame(boxes.cls.cpu().numpy(), columns=['class'])

    result = pd.concat([xyxy, conf, cls], axis=1)

    names = ['mask', 'no_mask']
    label_map = {i: name for i, name in enumerate(names)}
    result['name'] = result['class'].map(label_map)

    return result.values.tolist()


path = './Raw/a/img_0.jpg'
model = YOLO('best.pt')
image = cv2.imread(path)
res = model.predict(image, save=False, imgsz=256, conf=0.5)
result = convert(res)
for plate in result:
    # read plate number
    flag = 0
    x1 = int(plate[0])  # xmin
    y1 = int(plate[1])  # ymin
    x2 = int(plate[2])  # xmax
    y2 = int(plate[3])  # ymax
    print(plate[4])
    image = cv2.rectangle(image, (x1, y1), (x2, y2),
                          color=(0, 0, 225), thickness=2)

cv2.imshow("img", image)
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.destroyAllWindows()
# import cv2
# from mtcnn import MTCNN

# # Create an MTCNN detector
# detector = MTCNN()

# # Load an image or capture video from a webcam (adjust based on application type)
# image = cv2.imread('abc.jpg')  # For image processing
# # cap = cv2.VideoCapture(0)  # For webcam processing

# # Detect faces using MTCNN
# results = detector.detect_faces(image)

# # Process detected faces
# for result in results:
#     x, y, w, h = result['box']
#     confidence = result['confidence']
#     # Extract the face ROI
#     image = cv2.rectangle(image, (y, y+h), (x, x+w),
#                           color=(0, 0, 225), thickness=2)
# cv2.imshow("img", image)
# if cv2.waitKey(0) & 0xFF == ord('q'):
#     cv2.destroyAllWindows()
