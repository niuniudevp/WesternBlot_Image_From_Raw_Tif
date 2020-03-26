import cv2
import numpy as np


def rotate_img(image, angle):
    # rotate a img without cut
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
 
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
 
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
 
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
 
    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


def resize_img(cv_img, scale_factor):
    # resize a img
    height, width = cv_img.shape[:2]
    res = cv2.resize(cv_img, (int(scale_factor * width), int(scale_factor * height)), interpolation=cv2.INTER_CUBIC)
    return res

def flip_img_h(cv_img):
    # 图像水平翻转
    return(cv2.flip(cv_img, 1))

def flip_img_v(cv_img):
    # 图像垂直翻转
    return(cv2.flip(cv_img, 0))


def flip_img_hv(cv_img):
    # 图像水平垂直翻转
    return(cv2.flip(cv_img, -1))


def bgr2rgb(cv_img):
    # 转换颜色模式
    return(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))