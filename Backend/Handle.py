import torch
import tensorflow as tf
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import cv2
import os
import time
import pandas as pd


class Process():
    def __init__(self, model, base_model) -> None:
        self.model = model
        self.base_model = base_model
        json_file = open(
            './final_antispoofing_models/finalyearproject_antispoofing_model_mobilenet.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model_anti = tf.keras.models.model_from_json(loaded_model_json)
        self.model_anti.load_weights(
            './final_antispoofing_models/finalyearproject_antispoofing_model_96-0.967368.h5')
        self.labels = {}
        self.EmbeddingVectors = {}

    def getLabels(self):
        i = 0
        for dir in os.listdir("./Process/"):
            self.labels[i] = dir
            i += 1

    def getEmbeddingVector(self):
        path = "./EmbeddingVector/"
        for dir in os.listdir(path):
            vector = np.load(f"{path}{dir}", allow_pickle=True)
            self.EmbeddingVectors[dir.split(".")[0]] = vector

    def similarity(self, vector1, vector2):
        vector1 = vector1.reshape((1, -1))
        vector2 = vector2.reshape((1, -1))
        return cosine_similarity(vector1, vector2)

    def anti_spoofing(self, img):
        print("Debug: Inside anti_spoofing function")
        image = cv2.resize(img, (160, 160), interpolation=cv2.INTER_NEAREST)
        image = np.expand_dims(image, axis=0)
        preds = self.model_anti.predict(image, verbose=0)
        print("Debug: Predictions from anti_spoofing:", preds)
        return preds[0][0]

    def compare(self, vector):
        self.getLabels()
        self.getEmbeddingVector()
        if len(self.labels) == 0:
            return "Unknown"
        results = []
        for i in range(len(self.labels)):
            result = self.similarity(
                vector, self.EmbeddingVectors[self.labels[i]])
            results.append(result[0][0])
        print("Debug: Similarity results:", results)
        index = np.argmax(results)
        # print(results[index])
        if results[index] >= 0.55:
            return self.labels[index]
        else:
            return "Unknown"


class Create():
    def __init__(self, model, base_model) -> None:
        self.model = model
        self.base_model = base_model

    def convert(self, result):
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

    def ProcessData(self, name):
        print("Debug: Processing data for", name)
        path = "./Raw/"
        os.makedirs(name=f"./Process/{name}")
        dirs = os.listdir(path + name)
        for dir in dirs:
            print("Debug: Processing image", dir)
            image = cv2.imread(path + name + "\\" + dir)
            res = self.model.predict(
                image, save=False, imgsz=256, conf=0.1)
            result = self.convert(res)
            # print("result", result)
            if (len(result)) != 0:
                face = result[0]
                xmin = int(face[0])  # xmin
                ymin = int(face[1])  # ymin
                xmax = int(face[2])  # xmax
                ymax = int(face[3])  # ymax
                crop_img = image[ymin:ymax, xmin:xmax]
                # Print the size of the cropped image
                print("Debug: Cropped image size", crop_img.shape)
                resized_image = cv2.resize(
                    crop_img, (224, 224), interpolation=cv2.INTER_NEAREST)
                # Print the size of the resized image
                print("Debug: Resized image size", resized_image.shape)
                # print("resize",resized_image.shape)
                cv2.imwrite(f"./Process/{name}/crop{dir}", resized_image)
            else:
                print("không có mặt")
                print("Debug: No face detected in the image")
                print("Debug: Image size before resizing", image.shape)
                print("Debug: Skipped processing image", dir)

    def CreateEmbeddingVector(self, name):
        path = f"./Process/{name}/"
        features = []
        for dir in os.listdir(path):
            img = cv2.imread(path + dir)
            img = np.expand_dims(img, axis=0)
            feature = self.base_model.predict(img, verbose=0)
            features.append(feature)
        vector = np.mean(features, axis=0)
        np.save(f'./EmbeddingVector/{name}.npy', vector)
