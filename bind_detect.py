import cv2
from matplotlib.pylab import *
import numpy as np
img = cv2.imread('wb.png',0)
th2,img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#cv2.startWindowThread()

subplot(4,1,1)
imshow(img,'gray')
img = cv2.GaussianBlur(img,(5,5),0)
subplot(4,1,2)
imshow(img,'gray')
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,5))
img = cv2.erode(~img,kernel,1)
img = np.array(~img)
subplot(4,1,3)
imshow(img,'gray')
y= np.sum(img ==0,axis = 0)
subplot(4,1,4)
plot(y)
show()