# Importing all the required packages and libraries
import os
import tensorflow as tf
import tensorflow_hub as hub
import cv2
import requests
import numpy as np
import matplotlib.pyplot as plt
 

# def class ScaleImage

class ScaleImage:
    # This is a model of Enhanced Super Resolution GAN Model
    # The link given here is a model of ESRGAN model
    esrgn_path = "https://tfhub.dev/captain-pool/esrgan-tf2/1"
    model = None
    def __init__(self):
        pass

    def getModel(self):
        if self.model is None:
            self.model = hub.load(self.esrgn_path)
        return self.model

    def preprocessing(self, img, scale):
        imageSize = (tf.convert_to_tensor(img.shape[:-1]) // scale) * scale
        cropped_image = tf.image.crop_to_bounding_box(
            img, 0, 0, imageSize[0], imageSize[1])
        preprocessed_image = tf.cast(cropped_image, tf.float32)
        return tf.expand_dims(preprocessed_image, 0)
    
    def srmodel(self, img, scale):
        preprocessed_image = self.preprocessing(img, scale)  # Preprocess the LR Image
        new_image = self.getModel()(preprocessed_image)  # Runs the model
        # returns the size of the original argument that is given as input
        return tf.squeeze(new_image) / 255.0

    def resize(self, hr_image_np, targetResolutionWidth, targetResolutionHeight):
        width = hr_image_np.shape[1]
        height = hr_image_np.shape[0]
        scaleWidth = targetResolutionWidth / width
        scaleHeight = targetResolutionHeight / height
        scale = min(scaleWidth, scaleHeight)
        hr_image = cv2.resize(hr_image_np, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        return hr_image

    def scale(self, imgFilePath, outputFilePath = '', targetResolutionWidth = 1920, targetResolutionHeight = 1080):
        if outputFilePath == None or outputFilePath == '': outputFilePath = imgFilePath
        # Loading the image of the GFG Logo
        img = cv2.imread(imgFilePath)
        # print resolutions
        width = img.shape[1]
        height = img.shape[0]
        # return if img resolution is larger than target
        if width >= targetResolutionWidth * 0.7 or height >= targetResolutionHeight * 0.7:
            return
        
        scaleWidth = targetResolutionWidth / width
        scaleHeight = targetResolutionHeight / height
        scale = min(scaleWidth, scaleHeight)
        scale = 2 ** round(np.log2(scale))

        print(f'File({imgFilePath}) scale : {width} x {height} to {width * scale} x {height * scale}')

        # scale with targetResolutionWidth and targetResolutionHeight
        image_plot = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        hr_image = self.srmodel(image_plot, scale)
        # Convert the high-resolution image to a numpy array
        hr_image_np = hr_image.numpy()
        #hr_image_np = self.resize(hr_image_np, targetResolutionWidth, targetResolutionHeight)
        
        tf.keras.utils.save_img(outputFilePath, hr_image_np)
        # plt.title(hr_image.shape)
        # plt.imshow(hr_image)
        # plt.show()
    