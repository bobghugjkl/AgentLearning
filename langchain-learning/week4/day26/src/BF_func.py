#!/usr/bin/env python3
"""
文件名: BF_AI_detectionV3.py
作者: Calvin Chan <calvin888cn@gmail.com>
创建日期: 2025-12-01
最后修改: 2025-12-04

版权所有 (C) 2025 Calvin Chan. 保留所有权利。

说明:
    本程序受版权法和国际条约的保护。未经书面许可，任何单位或个人
    不得以任何形式复制、修改、发行、出租、表演、传播或以其他方式
    使用本程序的任何部分。

    如果您获得了授权使用本程序，请遵守相应的许可协议。

许可:
    本程序采用 MIT 许可协议。
    详情请参阅 LICENSE 文件或访问：
    https://opensource.org/licenses/MIT

免责声明:
    本程序按"原样"提供，不附带任何明示或暗示的担保，包括但不限于
    适销性、特定用途适用性和非侵权性的担保。在任何情况下，作者或
    版权持有人均不对任何直接、间接、附带、特殊、惩罚性或后果性损害
    （包括但不限于数据丢失、利润损失或业务中断）承担责任，无论
    其基于合同、侵权或其他理论，即使已被告知可能发生此类损害。
"""


"""
东营宝丰AI检测系统V3.0
调用本方法前请确保数据库已经构建,feature_database.pkl已放入根目录下
支持检测图像中的多个刹车片目标，自动旋转校正后进行型号识别
"""

import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from ultralytics import YOLO
from src.build_match_fea import PartRecognitionSystem
import logging
import os

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局模型缓存，避免重复加载
_MODEL_STATE = {'loaded': False}


class OBBDetector:
    """基于YOLOv8 OBB的目标检测器"""
    
    def __init__(self, model_path: str):
        """
        初始化OBB检测器
        
        Args:
            model_path: YOLOv8 OBB模型路径
        """
        logger.info(f"加载OBB模型: {model_path}")
        self.model = YOLO(model_path)
        logger.info("OBB模型加载完成")
    
    def detect(self, image_input, conf_threshold: float = 0.25) -> list:
        """
        检测图像中的OBB目标，可传入路径或BGR数组
        
        Args:
            image_input: 输入图像路径或BGR数组
            conf_threshold: 置信度阈值
            
        Returns:
            检测结果列表，每个元素包含bbox坐标和置信度
        """
        logger.info("开始检测图像")
        
        # 运行OBB检测
        results = self.model(image_input, conf=conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            if result.obb is not None and len(result.obb.xyxyxyxy) > 0:
                boxes = result.obb.xyxyxyxy.cpu().numpy()  # OBB的4个点坐标 [x1,y1,x2,y2,x3,y3,x4,y4]
                confidences = result.obb.conf.cpu().numpy()
                cls_ids = result.obb.cls.cpu().numpy()
                
                for i, (box, conf, cls_id) in enumerate(zip(boxes, confidences, cls_ids)):
                    # OBB格式: (x1,y1, x2,y2, x3,y3, x4,y4)
                    points = box.reshape(4, 2)
                    detections.append({
                        'points': points,  # 4个角点坐标
                        'confidence': float(conf),
                        'class_id': int(cls_id),
                        'index': i
                    })
        
        logger.info(f"检测到 {len(detections)} 个目标")
        return detections


class ImageRotator:
    """图像旋转校正器"""
    
    @staticmethod
    def calculate_rotation_angle(points: np.ndarray) -> float:
        """
        从OBB的4个点计算旋转角度
        
        Args:
            points: OBB的4个角点坐标，shape (4, 2)
            
        Returns:
            旋转角度（度），顺时针为正
        """
        # 找到最上和最下的点，计算角度
        # 使用第一个点作为参考，计算到其他点的角度
        center = points.mean(axis=0)
        
        # 找到最长边作为主方向
        edges = [
            np.linalg.norm(points[1] - points[0]),
            np.linalg.norm(points[2] - points[1]),
            np.linalg.norm(points[3] - points[2]),
            np.linalg.norm(points[0] - points[3])
        ]
        max_edge_idx = np.argmax(edges)
        
        # 计算最长边的角度
        if max_edge_idx == 0:
            vec = points[1] - points[0]
        elif max_edge_idx == 1:
            vec = points[2] - points[1]
        elif max_edge_idx == 2:
            vec = points[3] - points[2]
        else:
            vec = points[0] - points[3]
        
        angle_rad = np.arctan2(vec[1], vec[0])
        angle_deg = np.degrees(angle_rad)
        
        # 将角度归一化到[-90, 90]度范围，使其水平
        if angle_deg > 90:
            angle_deg -= 180
        elif angle_deg < -90:
            angle_deg += 180
        
        return -angle_deg  # 取负值用于旋转校正
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> tuple:
        """
        旋转图像使其水平
        
        Args:
            image: 输入图像
            angle: 旋转角度（度），顺时针为正
            
        Returns:
            (旋转后的图像, 旋转矩阵)
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        # 获取旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # 计算新图像的尺寸
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        # 调整旋转矩阵的平移部分
        rotation_matrix[0, 2] += (new_w / 2) - center[0]
        rotation_matrix[1, 2] += (new_h / 2) - center[1]
        
        # 旋转图像
        rotated = cv2.warpAffine(image, rotation_matrix, (new_w, new_h),
                                 flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT,
                                 borderValue=(0, 0, 0))
        
        return rotated, rotation_matrix
    
    @staticmethod
    def extract_rotated_roi(image: np.ndarray, obb_points: np.ndarray, expand_ratio: float = 0.1) -> np.ndarray:
        """
        从图像中提取OBB区域，旋转到水平后裁剪 (与 run_pipeline_obb_crops.py 逻辑完全一致)
        
        Args:
            image: 原始图像
            obb_points: OBB的4个角点坐标，shape (4, 2)
            expand_ratio: 提取特征前将框扩大的比例，0.2表示扩大20%
            
        Returns:
            提取并旋转校正后的ROI图像
        """
        src_pts = obb_points.astype(np.float32)
        
        # --- 放大检测框 ---
        if expand_ratio > 0:
            center = np.mean(src_pts, axis=0)
            scale_factor = 1.0 + expand_ratio
            src_pts = center + (src_pts - center) * scale_factor
        
        # 计算边长
        side1_len = np.linalg.norm(src_pts[0] - src_pts[1])
        side2_len = np.linalg.norm(src_pts[1] - src_pts[2])
        
        w = int(np.round(max(side1_len, side2_len)))
        h = int(np.round(min(side1_len, side2_len)))
        
        # 目标矩形点 (水平)
        dst_pts_horizontal = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32)
        target_dst_pts = dst_pts_horizontal
        target_w, target_h = w, h
        
        # 确保长边对应长边，以保证摆正
        if side1_len < side2_len:
            src_pts = np.roll(src_pts, 1, axis=0)
            
        # 透视变换
        try:
            M = cv2.getPerspectiveTransform(src_pts, target_dst_pts)
            roi = cv2.warpPerspective(image, M, (target_w, target_h))
        except Exception as e:
            logger.warning(f"透视变换失败，使用边界框方法: {e}")
            # 如果透视变换失败，使用边界框方法
            x, y, bbox_w, bbox_h = cv2.boundingRect(src_pts.reshape(1, -1, 2).astype(np.int32))
            margin = 5
            x = max(0, x - margin)
            y = max(0, y - margin)
            bbox_w = min(image.shape[1] - x, bbox_w + 2 * margin)
            bbox_h = min(image.shape[0] - y, bbox_h + 2 * margin)
            roi = image[y:y+bbox_h, x:x+bbox_w]
            if roi.size == 0:
                roi = image
                
        return roi


class MultiTargetRecognition:
    """多目标检测与识别系统"""
    
    def __init__(self, obb_model_path: str, feature_database_path: str, recognition_model: str = 'resnet50'):
        """
        初始化多目标识别系统
        
        Args:
            obb_model_path: YOLOv8 OBB模型路径
            feature_database_path: 特征数据库路径
            recognition_model: 特征提取模型名称
        """
        logger.info("初始化多目标识别系统...")
        self.detector = OBBDetector(obb_model_path)
        self.rotator = ImageRotator()
        self.recognition_system = PartRecognitionSystem(feature_database_path, recognition_model)
        logger.info("系统初始化完成")
    def process_image(self, image_or_path, conf_threshold: float = 0.25, top_k: int = 5) -> dict:
        """
        处理图像：检测、旋转、识别
        
        Args:
            image_or_path: 输入图像路径或BGR数组
            conf_threshold: 检测置信度阈值
            top_k: 检索时返回的相似图像数量
            
        Returns:
            处理结果字典
        """
        # 读取或直接使用输入图像
        if isinstance(image_or_path, (str, Path)):
            image_path = str(image_or_path)
            original_image = cv2.imread(image_path)
            if original_image is None:
                return {'success': False, 'error': '无法读取图像'}
        else:
            image_path = None
            original_image = image_or_path.copy()
        
        # 1. 检测OBB目标
        detections = self.detector.detect(image_or_path, conf_threshold)
        
        if len(detections) == 0:
            return {'success': False, 'error': '未检测到任何目标'}
        
        # 可选：如果你想单独保存仅有OBB框的结果图，可以在这里加上保存逻辑
        # obb_debug_image = original_image.copy()
        # for det in detections:
        #     pts = det['points'].reshape(-1, 1, 2).astype(np.int32)
        #     cv2.polylines(obb_debug_image, [pts], isClosed=True, color=(255, 0, 0), thickness=2)
        # cv2.imwrite("debug_obb_only.jpg", obb_debug_image)
        
        # 2. 对每个目标进行处理
        results = []
        for i, detection in enumerate(detections):
            logger.info(f"处理目标 {i+1}/{len(detections)}")
            
            # 提取并旋转ROI
            roi = self.rotator.extract_rotated_roi(original_image, detection['points'])
            
            if roi.size == 0:
                logger.warning(f"目标 {i+1} ROI为空，跳过")
                continue
            
            # 保存临时ROI图像用于识别（roi已经是BGR格式）
            # 我们将其保存到一个 debug 文件夹中以便查看裁剪和扩展后的效果
            debug_dir = "./results/debug_roi"
            os.makedirs(debug_dir, exist_ok=True)
            temp_roi_path = os.path.join(debug_dir, f"roi_target_{i+1}.jpg")
            cv2.imwrite(temp_roi_path, roi)
            logger.info(f"已保存裁剪后的 ROI 图像用于调试: {temp_roi_path}")
            
            try:
                # 3. 识别型号
                recognition_result = self.recognition_system.recognize_part(temp_roi_path, top_k)
                
                if recognition_result['success']:
                    results.append({
                        'target_index': i + 1,
                        'confidence_detection': detection['confidence'],
                        'points': detection['points'],
                        'predicted_model_id': recognition_result['predicted_model_id'],
                        'recognition_confidence': recognition_result['confidence'],
                        'similar_images': recognition_result['similar_images'],
                        'model_votes': recognition_result['model_votes'],
                        'roi_image': roi
                    })
                    logger.info(f"目标 {i+1} 识别完成: 型号ID={recognition_result['predicted_model_id']}")
                else:
                    results.append({
                        'target_index': i + 1,
                        'confidence_detection': detection['confidence'],
                        'points': detection['points'],
                        'error': recognition_result.get('error', '识别失败'),
                        'roi_image': roi
                    })
            except Exception as e:
                logger.error(f"目标 {i+1} 识别失败: {e}")
                results.append({
                    'target_index': i + 1,
                    'confidence_detection': detection['confidence'],
                    'points': detection['points'],
                    'error': str(e),
                    'roi_image': roi
                })
            # 移除了 finally 块里的文件删除逻辑，保留调试图片
        
        return {
            'success': True,
            'image_path': image_path,
            'original_image': original_image,
            'total_targets': len(detections),
            'results': results
        }

    def save_overlay_with_labels(self, result: dict, save_path: str):
        """
        在原图上绘制所有检测到的OBB框及每个目标的匹配类别，并保存
        """
        image = cv2.imread(result['image_path'])
        if image is None:
            logger.error("读取原图失败，无法保存结果覆盖图")
            return
        overlay = image.copy()
        for item in result['results']:
            points = item.get('points')
            if points is None:
                continue
            pts = points.reshape(-1, 1, 2).astype(np.int32)
            color = (0, 255, 0) if 'predicted_model_id' in item else (0, 0, 255)
            cv2.polylines(overlay, [pts], isClosed=True, color=color, thickness=2)
            # 文本标签
            if 'predicted_model_id' in item:
                label_text = f"Model:{item['predicted_model_id']}"
            else:
                label_text = f"Error"
            # 放置文字位置：多边形的左上（最小x+y）
            idx = np.argmin(points.sum(axis=1))
            anchor = tuple(points[idx].astype(int))
            cv2.putText(overlay, label_text, (anchor[0], max(0, anchor[1]-5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
        cv2.imwrite(save_path, overlay)
        logger.info(f"检测与匹配结果图已保存: {save_path}")
    
    def visualize_results(self, result: dict, save_path: str = None):
        """
        可视化检测和识别结果
        
        Args:
            result: process_image返回的结果
            save_path: 保存路径，如果为None则显示
        """
        if not result['success']:
            logger.error("无法可视化：处理失败")
            return
        
        # 读取原始图像
        original_image = cv2.imread(result['image_path'])
        original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        
        # 计算子图布局
        num_targets = len(result['results'])
        cols = min(3, num_targets + 1)
        rows = (num_targets + cols) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
        if num_targets == 0:
            axes = np.array([axes])
        else:
            axes = axes.flatten() if axes.ndim > 1 else [axes]
        
        # 显示原始图像
        axes[0].imshow(original_image_rgb)
        axes[0].set_title(f'原始图像\n检测到 {result["total_targets"]} 个目标')
        axes[0].axis('off')
        
        # 显示每个检测到的目标
        for i, target_result in enumerate(result['results']):
            if i + 1 >= len(axes):
                break
                
            roi = target_result.get('roi_image')
            if roi is not None:
                # ROI是BGR格式，转换为RGB用于显示
                if len(roi.shape) == 3 and roi.shape[2] == 3:
                    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                else:
                    roi_rgb = roi
                axes[i + 1].imshow(roi_rgb)
                
                if 'predicted_model_id' in target_result:
                    title = f"TargetID: {target_result['target_index']}\n"
                    title += f"ModelID: {target_result['predicted_model_id']}\n"
                    title += f"Confidence_Detection: {target_result['confidence_detection']:.3f}\n"
                    title += f"Confidence_Matching: {target_result['recognition_confidence']:.3f}"
                else:
                    title = f"TargetID: {target_result['target_index']}\n"
                    title += f"Error: {target_result.get('error', 'Unknown Error')}"
                
                axes[i + 1].set_title(title)
                axes[i + 1].axis('off')
        
        # 隐藏多余的子图
        for i in range(num_targets + 1, len(axes)):
            axes[i].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"结果已保存到: {save_path}")
        else:
            plt.show()


# --- 加载模型 ---
def loadmodels():
    """
    加载检测与识别模型，供process_frame/界面调用。
    """
    global _MODEL_STATE
    if _MODEL_STATE.get('loaded'):
        return _MODEL_STATE

    base_dir = os.path.dirname(os.path.abspath(__file__))
    obb_model_path = os.path.join(base_dir, "../models/brake_obb_best_20260124.pt")
    feature_database_path = os.path.join(base_dir, "../models/feature_database.pkl")
        # 检查文件是否存在

    for p in [obb_model_path, feature_database_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"必要文件不存在: {p}")
    
    system = MultiTargetRecognition(
        obb_model_path=obb_model_path,
        feature_database_path=feature_database_path
    )
    
    _MODEL_STATE = {
        'loaded': True,
        'system': system,
        'obb_model_path': obb_model_path,
        'feature_database_path': feature_database_path
    }
    return _MODEL_STATE


def _draw_overlay(result: dict) -> np.ndarray:
    """根据识别结果在原图上叠加多边形与标签（标签居中显示在框内）"""
    image = result.get('original_image')
    if image is None and result.get('image_path'):
        image = cv2.imread(result['image_path'])
    if image is None:
        return None
    
    overlay = image.copy()
    
    for item in result.get('results', []):
        points = item.get('points')
        if points is None:
            continue
            
        pts = points.reshape(-1, 1, 2).astype(np.int32)
        color = (0, 255, 0) if 'predicted_model_id' in item else (0, 0, 255)
        
        # 绘制边框
        cv2.polylines(overlay, [pts], isClosed=True, color=color, thickness=5)
        
        # 标签文本
        label_text = f"Model:{item['predicted_model_id']}" if 'predicted_model_id' in item else "Error"
        
        # ──────────────────────────────
        # 关键修改：计算多边形中心作为文字位置
        # ──────────────────────────────
        center_x = int(points[:, 0].mean())
        center_y = int(points[:, 1].mean())
        text_anchor = (center_x, center_y)   # 这就是文字的中心位置（近似）
        
        # 获取文字大小，以便精确垂直居中
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        thickness = 3
        (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
        
        # 让文字真正垂直居中（左下角坐标 = 中心点向上偏移半个文字高度）
        text_x = center_x - text_w // 2
        text_y = center_y + text_h // 2
        
        # 防止文字超出图像边界（可选）
        text_x = max(5, min(text_x, image.shape[1] - text_w - 5))
        text_y = max(text_h + 5, min(text_y, image.shape[0] - 5))
        
        # 可选：给文字加一个半透明背景矩形（强烈推荐，提升可读性）
        bg_padding = 8
        bg_tl = (text_x - bg_padding, text_y - text_h - bg_padding)
        bg_br = (text_x + text_w + bg_padding, text_y + bg_padding + baseline)
        overlay_bg = overlay.copy()
        cv2.rectangle(overlay_bg, bg_tl, bg_br, color, -1)  # 填充颜色背景
        # 混合半透明
        cv2.addWeighted(overlay_bg, 0.6, overlay, 0.4, 0, overlay)
        
        # 绘制文字（白色更醒目，也可以用 color）
        cv2.putText(overlay, label_text, (text_x, text_y),
                    font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
        
        # 如果你不想加背景，直接这样也行（纯色文字）：
        # cv2.putText(overlay, label_text, (text_x, text_y),
        #             font, font_scale, color, thickness, cv2.LINE_AA)
    
    return overlay


def process_frame(image: np.ndarray, conf_threshold: float = 0.25, top_k: int = 5, system: MultiTargetRecognition = None):
    """
    传入一张 BGR 图像，返回标注后的图像以及文本摘要（供UI调用）。
    
    Args:
        image: BGR格式的图像数组
        conf_threshold: 检测置信度阈值
        top_k: 检索时返回的相似图像数量
        system: 可选的MultiTargetRecognition实例，如果提供则直接使用，否则调用loadmodels()加载
    """
    if system is None:
        state = loadmodels()
        system = state['system']
    
    result = system.process_image(image, conf_threshold=conf_threshold, top_k=top_k)
    if not result['success']:
        return image, f"处理失败: {result.get('error', '未知错误')}"
    
    annotated = _draw_overlay(result)
    # 生成简短摘要
    texts = [f"检测到 {result['total_targets']} 个目标"]
    for item in result['results']:
        if 'predicted_model_id' in item:
            texts.append(f"ID{item['target_index']}: {item['predicted_model_id']} (det {item['confidence_detection']:.2f}, match {item['recognition_confidence']:.2f})")
        else:
            texts.append(f"ID{item['target_index']}: 识别失败")
    summary = " | ".join(texts)
    return annotated, summary


def classify_image(image_path: str, conf_threshold: float = 0.25, top_k: int = 5, save_path: str = None):
    """
    便捷接口：读取单张图片完成检测+分类，可选保存结果。
    """
    loadmodels()

    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"无法读取图片: {image_path}")
    annotated, summary = process_frame(image, conf_threshold=conf_threshold, top_k=top_k)
    if save_path:
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
        cv2.imwrite(save_path, annotated)
        print(f"*图像已写入{save_path}*")
    return annotated, summary



if __name__ == "__main__":
    classify_image(image_path="./imgs/test_input/Image_20260302143024469.png",save_path="./results/v3uitest.png")