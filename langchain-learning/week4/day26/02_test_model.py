import sys
import os

# 把 src 目录加入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from BF_func import loadmodels, process_frame
import cv2
import numpy as np

print("开始加载模型...")
state = loadmodels()
print("模型加载成功！")

# 用一张空白图测试
test_image = np.zeros((480, 640, 3), dtype=np.uint8)
annotated, summary = process_frame(test_image, system=state['system'])
print(f"测试结果：{summary}")