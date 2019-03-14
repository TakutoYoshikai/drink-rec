import cv2
import os
import sys
from statistics import mean


def compare(target_img_path, comparing_img_path):
    target_img = cv2.imread(target_img_path)
    comparing_img = cv2.imread(comparing_img_path)
    channels = (0, 1, 2)
    hist_size = 256
    ranges = (0, 256)
    tmp = []
    for channel in channels:
        target_hist = cv2.calcHist([target_img], [channel], None, [hist_size], ranges)
        comparing_hist = cv2.calcHist([comparing_img], [channel], None, [hist_size], ranges)
        tmp.append(cv2.compareHist(target_hist, comparing_hist, 0))
    return mean(tmp)

