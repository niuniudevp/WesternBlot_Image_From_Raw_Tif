import cv2
import numpy as np


def rotateImage(image, angle):
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    x = (w * sin * sin - h * cos * sin) / (sin * sin - cos * cos)
    y = cos * x / sin
    nH = int(np.sqrt(x**2 + y**2))
    nW = int(np.sqrt((h - y)**2 + (w - x)**2))
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    rotated = cv2.warpAffine(image, M, (nW, nH))
    return (rotated)


def rotate_img(image, angle, Cut_Edge=False):
    # rotate a img without cut
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    if Cut_Edge:
        x = (w * sin**2 - h * cos * sin) / (sin**2 - cos**2)
        y = cos * x / sin
        nH = int(np.sqrt(x**2 + y**2))
        nW = int(np.sqrt((h - y)**2 + (w - x)**2))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


def resize_img(cv_img, scale_factor):
    # resize a img
    height, width = cv_img.shape[:2]
    res = cv2.resize(cv_img,
                     (int(scale_factor * width), int(scale_factor * height)),
                     interpolation=cv2.INTER_CUBIC)
    return res


def flip_img_h(cv_img):
    # 图像水平翻转
    return (cv2.flip(cv_img, 1))


def flip_img_v(cv_img):
    # 图像垂直翻转
    return (cv2.flip(cv_img, 0))


def flip_img_hv(cv_img):
    # 图像水平垂直翻转
    return (cv2.flip(cv_img, -1))


def CV_Img_Transform(CV_Img,
                     Flip_H=0,
                     Flip_V=0,
                     Angle=0,
                     Cut_Edge_on_Rotation=False):
    if Flip_V:
        CV_Img = flip_img_h(CV_Img)
    if Flip_H:
        CV_Img = flip_img_v(CV_Img)
    if Angle != 0:
        if Cut_Edge_on_Rotation:
            CV_Img = rotate_img(CV_Img, Angle, True)
        else:
            CV_Img = rotate_img(CV_Img, Angle, False)
    return CV_Img


def bgr2rgb(cv_img):
    # 转换颜色模式
    return (cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))


def cv2RdImg(img_path):
    # 读取图片
    return cv2.imread(img_path)


def cv2PutText(cv_img, text: str, Around_Rect: list):
    # 添加文字
    p1, p2 = Around_Rect
    (fw, fh), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
    h, w, _ = cv_img.shape
    TL = (min(p1[0], p2[0]), min(p1[1], p2[1]))
    BR = (max(p1[0], p2[0]), max(p1[1], p2[1]))
    Text_h = int((TL[1] + BR[1]) / 2 + fh / 2)
    if w - BR[0] - 5 > fw:
        pos = (BR[0] + 5, Text_h)
    elif TL[0] - 5 > fw:
        pos = (TL[0] - 5 - fw, Text_h)
    else:
        pos = (BR[0] + 5, Text_h)
    cv_img = cv2.putText(cv_img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                         (0, 255, 0), 2)
    return cv_img


def cv2DrawRect(cv_img, p1: tuple, p2: tuple):
    # 画框
    cv2.rectangle(cv_img, p1, p2, (0, 255, 0), 1)
    return cv_img


def cv2SaveTif(cv_img, save_path):
    # 保存图片
    cv2.imwrite(save_path, cv_img)
