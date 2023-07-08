import os
from utils import SaveUtils
from utils import ImageUtils
from PyKakao import Karlo

class KakaoAI:
    karlo = Karlo(service_key = os.environ['KAKAO_API_KEY'])
    saveUtils = SaveUtils('__output/kakaoAI/')
    def __init__(self):
        pass

    def handleResponse(self, response, keyword):
        if response is None or response.get("images") is None:
            msg = ''
            if isinstance(response, dict):
                msg = response.get('msg')
            raise Exception(f"Error occurred while getting image from Kakao AI: {msg}")
        results = []
        for imageDict in response.get("images"):
            imgBase64 = imageDict.get('image')
            imageFile = self.saveUtils.saveImageFromBase64('KakaoImage_' + keyword, imgBase64)
            results.extend(imageFile)
        print(results)
        return results

    def getKakaoImage(self, q, keyword, nbImage = 1):
        response = self.karlo.text_to_image(q, nbImage)
        return self.handleResponse(response, keyword)

    def getKakaoImageTransform(self, imgFile, keyword, nbImage = 1):
        imgBase64 = ImageUtils.getBase64FromImageFile(imgFile)
        response = self.karlo.transform_image(image = imgBase64, batch_size=nbImage)
        return self.handleResponse(response, keyword)

    def ask_kakao_image_edit(self, sourceImgFile, maskingImgFile, q, keyword, nbImage = 1):
        sourceImgFileBase64 = ImageUtils.getBase64FromImageFile(sourceImgFile)
        maskingImgFileBase64 = ImageUtils.getBase64FromImageFile(maskingImgFile)
        response = self.karlo.inpaint_image(image = sourceImgFileBase64, mask = maskingImgFileBase64, text = q, batch_size = nbImage)
        return self.handleResponse(response, keyword)