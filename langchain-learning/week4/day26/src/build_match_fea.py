#!/usr/bin/env python3
"""
文件名: build_feature_database.py
作者: Calvin Chan <calvin888cn@gmail.com>
创建日期: 2025-11-25
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
构建特征数据库,使用resnet50模型提取特征,使用faiss进行相似度搜索。提供测试函数与主函数的接口。
"""

import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, efficientnet_b0
from PIL import Image
import pickle
import json
from pathlib import Path
from typing import List, Dict
import faiss
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureExtractor:
    """特征提取器类，支持多种预训练模型"""
    
    def __init__(self, model_name: str = 'resnet50', device: str = 'auto'):
        """
        初始化特征提取器
        
        Args:
            model_name: 模型名称 ('resnet50', 'efficientnet_b0')
            device: 设备 ('auto', 'cpu', 'cuda')
        """
        self.model_name = model_name
        self.device = self._get_device(device)
        self.model = self._load_model()
        self.transform = self._get_transform()
        
    def _get_device(self, device: str) -> torch.device:
        """获取计算设备"""
        if device == 'auto':
            return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        return torch.device(device)
    
    def _load_model(self):
        """加载预训练模型"""
        if self.model_name == 'resnet50':
            # 检查是否存在本地微调模型
            model_path = './models/resnet50_finetuned.pth'
            if Path(model_path).exists():
                logger.info(f"发现本地微调模型，正在加载: {model_path}")
                try:
                    # 先加载权重文件，获取分类层的维度信息
                    state_dict = torch.load(model_path, map_location=self.device)
                    
                    # 从保存的权重中获取分类层的输出维度
                    if 'fc.weight' in state_dict:
                        num_classes = state_dict['fc.weight'].shape[0]
                        logger.info(f"检测到微调模型分类层维度: {num_classes} 个类别")
                    else:
                        raise ValueError("权重文件中未找到分类层权重")
                    
                    # 创建 ResNet50 模型结构（兼容新旧版本的 torchvision）
                    try:
                        from torchvision.models import ResNet50_Weights
                        model = resnet50(weights=None)  # 新版本不使用预训练权重
                    except (ImportError, AttributeError, TypeError):
                        model = resnet50(pretrained=False)  # 旧版本
                    
                    # 修改分类层以匹配微调模型的类别数
                    num_ftrs = model.fc.in_features
                    model.fc = torch.nn.Linear(num_ftrs, num_classes)
                    
                    # 加载微调后的权重
                    model.load_state_dict(state_dict, strict=True)
                    logger.info("本地微调模型权重加载成功")
                except Exception as e:
                    logger.warning(f"加载本地微调模型失败: {e}，将使用原始预训练模型")
                    try:
                        from torchvision.models import ResNet50_Weights
                        model = resnet50(weights=ResNet50_Weights.DEFAULT)
                    except (ImportError, AttributeError):
                        model = resnet50(pretrained=True)
            else:
                logger.info("未找到本地微调模型，使用原始预训练模型")
                try:
                    from torchvision.models import ResNet50_Weights
                    model = resnet50(weights=ResNet50_Weights.DEFAULT)
                except (ImportError, AttributeError):
                    model = resnet50(pretrained=True)
            # 移除最后的分类层，保留特征提取部分
            model = torch.nn.Sequential(*list(model.children())[:-1])
            self.feature_dim = 2048
        elif self.model_name == 'resnet18':
            from torchvision.models import resnet18
            model = resnet18(pretrained=True)
            model = torch.nn.Sequential(*list(model.children())[:-1])
            self.feature_dim = 512
        elif self.model_name == 'resnet101':
            from torchvision.models import resnet101
            model = resnet101(pretrained=True)
            model = torch.nn.Sequential(*list(model.children())[:-1])
            self.feature_dim = 2048
        elif self.model_name == 'efficientnet_b0':
            model = efficientnet_b0(pretrained=True)
            # 移除最后的分类层
            model = torch.nn.Sequential(*list(model.children())[:-1])
            self.feature_dim = 1280
        elif self.model_name == 'efficientnet_b3':
            from torchvision.models import efficientnet_b3
            model = efficientnet_b3(pretrained=True)
            model = torch.nn.Sequential(*list(model.children())[:-1])
            self.feature_dim = 1536
        elif self.model_name == 'densenet121':
            from torchvision.models import densenet121
            model = densenet121(pretrained=True)
            # DenseNet需要特殊处理
            model = torch.nn.Sequential(*list(model.features.children()), 
                                       torch.nn.AdaptiveAvgPool2d((1, 1)))
            self.feature_dim = 1024
        elif self.model_name == 'mobilenet_v3_large':
            from torchvision.models import mobilenet_v3_large
            model = mobilenet_v3_large(pretrained=True)
            model = torch.nn.Sequential(*list(model.children())[:-1])
            self.feature_dim = 960
        elif self.model_name == 'vit_b_16':
            from torchvision.models import vit_b_16
            model = vit_b_16(pretrained=True)
            # ViT需要特殊处理，移除分类头
            model.heads = torch.nn.Identity()
            self.feature_dim = 768
        elif self.model_name=='dinov3':
            import timm
            backbone = timm.create_model('vit_small_patch16_224', pretrained=False, num_classes=0)
            ckpt_path = './models/dinov3_vits16_pretrain_lvd1689m-08c60483.pth'
            if Path(ckpt_path).exists():
                logger.info(f"加载DINOv3预训练权重: {ckpt_path}")
                state = torch.load(ckpt_path, map_location='cpu')
                if 'model' in state: 
                    state = state['model']
                state = {k.replace('module.', ''): v for k, v in state.items()}
                backbone.load_state_dict(state, strict=False)
                logger.info("DINOv3权重加载成功")
            else:
                logger.warning(f"未找到DINOv3权重文件: {ckpt_path}，使用随机初始化")
            
            class DinoV3PatchExtractor(torch.nn.Module):
                def __init__(self, backbone):
                    super().__init__()
                    self.backbone = backbone
                    
                def forward(self, x):
                    # 返回所有 patch tokens (不包含 CLS)
                    feats = self.backbone.forward_features(x)  # (B, 197, 384) 或类似
                    patch_feats = feats[:, 1:, :]  # 去掉 CLS token
                    # patch_feats = feats[:, backbone.num_prefix_tokens:, :]
                    return patch_feats.mean(dim=1)  # 全局平均 → (B, 384)
            
            model = DinoV3PatchExtractor(backbone)
            self.feature_dim = 384
            
        elif self.model_name == 'convnext_tiny':
            from torchvision.models import convnext_tiny
            try:
                from torchvision.models import ConvNeXt_Tiny_Weights
                model = convnext_tiny(weights=ConvNeXt_Tiny_Weights.DEFAULT)
            except (ImportError, AttributeError):
                model = convnext_tiny(pretrained=True)
            # 移除分类头，保留特征提取部分
            model.classifier = torch.nn.Identity()
            self.feature_dim = 768
            logger.info("使用ConvNeXt-Tiny模型，特征维度: 768")
            
        elif self.model_name == 'convnext_small':
            from torchvision.models import convnext_small
            try:
                from torchvision.models import ConvNeXt_Small_Weights
                model = convnext_small(weights=ConvNeXt_Small_Weights.DEFAULT)
            except (ImportError, AttributeError):
                model = convnext_small(pretrained=True)
            model.classifier = torch.nn.Identity()
            self.feature_dim = 768
            logger.info("使用ConvNeXt-Small模型，特征维度: 768")
            
        elif self.model_name == 'convnext_base':
            from torchvision.models import convnext_base
            try:
                from torchvision.models import ConvNeXt_Base_Weights
                model = convnext_base(weights=ConvNeXt_Base_Weights.DEFAULT)
            except (ImportError, AttributeError):
                model = convnext_base(pretrained=True)
            model.classifier = torch.nn.Identity()
            self.feature_dim = 1024
            logger.info("使用ConvNeXt-Base模型，特征维度: 1024")
            
        elif self.model_name == 'convnext_large':
            from torchvision.models import convnext_large
            try:
                from torchvision.models import ConvNeXt_Large_Weights
                model = convnext_large(weights=ConvNeXt_Large_Weights.DEFAULT)
            except (ImportError, AttributeError):
                model = convnext_large(pretrained=True)
            model.classifier = torch.nn.Identity()
            self.feature_dim = 1536
            logger.info("使用ConvNeXt-Large模型，特征维度: 1536")
            
        model.eval()
        model.to(self.device)
        return model
    
    def _get_transform(self):
        """获取图像预处理变换"""
        if self.model_name == 'dinov3':
            return transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # DINOv3 推荐
            ])
        else:
            return transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                std=[0.229, 0.224, 0.225])
            ])
    
    def extract_features(self, image_path: str) -> np.ndarray:
        """
        从图像中提取特征
        
        Args:
            image_path: 图像路径
            
        Returns:
            特征向量 (1D numpy array)
        """
        try:
            # 读取图像
            image = Image.open(image_path).convert('RGB')
            
            # 预处理
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # 特征提取
            with torch.no_grad():
                features = self.model(input_tensor)
                features = features.squeeze().cpu().numpy()
            
            # L2归一化
            features = features / np.linalg.norm(features)
            
            return features
            
        except Exception as e:
            logger.error(f"特征提取失败 {image_path}: {e}")
            return None

class DatabaseBuilder:
    """特征数据库构建器"""
    
    def __init__(self, feature_extractor: FeatureExtractor):
        self.feature_extractor = feature_extractor
        self.database = {}
        self.feature_matrix = None
        self.image_paths = []
        self.model_ids = []
        self.metadata = []
        
    def parse_label(self, image_path: Path) -> str:
        """
        从路径解析类别标签 (父文件夹名)
        
        Args:
            image_path: 图片路径 (Path对象)
            
        Returns:
            class_name: 类别名称 (作为 model_id)
        """
        return image_path.parent.name
    
    def build_database(self, database_dir: str) -> Dict:
        """
        构建特征数据库
        
        Args:
            database_dir: 数据库图像文件夹路径
            
        Returns:
            数据库字典
        """
        logger.info(f"开始构建特征数据库: {database_dir}")
        
        database_path = Path(database_dir)
        if not database_path.exists():
            raise ValueError(f"数据库路径不存在: {database_dir}")
        
        # 获取所有图像文件 (递归查找)
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(database_path.rglob(ext))
        
        logger.info(f"找到 {len(image_files)} 个图像文件")
        
        features_list = []
        metadata_list = []
        
        for i, image_path in enumerate(image_files):
            if (i + 1) % 50 == 0:
                logger.info(f"处理图像 {i+1}/{len(image_files)}: {image_path.name}")
            
            # 解析文件名获取型号ID (现在改为获取文件夹名)
            model_id = self.parse_label(image_path)
            filename = image_path.name
            
            # 提取特征
            features = self.feature_extractor.extract_features(str(image_path))
            
            if features is not None:
                features_list.append(features)
                metadata_list.append({
                    'image_path': str(image_path),
                    'filename': filename,
                    'model_id': model_id,
                    'image_index': len(features_list) - 1
                })
            else:
                logger.warning(f"跳过无效图像: {image_path}")
        
        # 构建特征矩阵
        if features_list:
            self.feature_matrix = np.array(features_list)
            self.image_paths = [meta['image_path'] for meta in metadata_list]
            self.model_ids = [meta['model_id'] for meta in metadata_list]
            self.metadata = metadata_list
            
            # 构建数据库
            self.database = {
                'features': self.feature_matrix,
                'metadata': metadata_list,
                'model_ids': self.model_ids,
                'image_paths': self.image_paths,
                'feature_dim': self.feature_extractor.feature_dim,
                'model_name': self.feature_extractor.model_name,
                'total_images': len(features_list),
                'unique_models': len(set(self.model_ids))
            }
            
            logger.info(f"数据库构建完成:")
            logger.info(f"  - 总图像数: {self.database['total_images']}")
            logger.info(f"  - 唯一型号数: {self.database['unique_models']}")
            logger.info(f"  - 特征维度: {self.database['feature_dim']}")
            logger.info(f"  - 使用模型: {self.database['model_name']}")
            
            return self.database
        else:
            raise ValueError("没有成功提取到任何特征")
    
    def load_existing(self, database_path: str):
        """加载已有数据库到构建器，便于增量更新"""
        db_path = Path(database_path)
        if not db_path.exists():
            raise ValueError(f"数据库文件不存在: {database_path}")
        with open(db_path, 'rb') as f:
            self.database = pickle.load(f)
        self.feature_matrix = np.array(self.database['features'])
        self.image_paths = list(self.database['image_paths'])
        self.model_ids = list(self.database['model_ids'])
        self.metadata = list(self.database['metadata'])
        logger.info(f"已加载现有数据库，用于增量更新: 向量数={len(self.image_paths)}")
    
    def incremental_add(self, new_images_dir: str) -> Dict:
        """
        增量添加新目录中的图像到现有数据库（仅追加，不删除）
        
        Args:
            new_images_dir: 新增图像所在文件夹
        Returns:
            更新后的数据库字典
        """
        if not self.database:
            raise ValueError("请先加载或构建数据库，再进行增量添加")
        new_dir = Path(new_images_dir)
        if not new_dir.exists():
            raise ValueError(f"新增图像目录不存在: {new_images_dir}")
        # 收集新图像 (递归)
        new_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            new_files.extend(new_dir.rglob(ext))
        logger.info(f"增量更新: 待检查 {len(new_files)} 张图像")
        # 去重：按绝对路径或文件名避免重复
        existing_set = set(self.image_paths)
        added = 0
        features_to_append = []
        new_metadata = []
        for image_path in new_files:
            image_str = str(image_path)
            if image_str in existing_set:
                continue
            
            model_id = self.parse_label(image_path)
            filename = image_path.name
            
            features = self.feature_extractor.extract_features(image_str)
            if features is None:
                logger.warning(f"增量跳过无效图像: {image_str}")
                continue
            features_to_append.append(features)
            new_metadata.append({
                'image_path': image_str,
                'filename': filename,
                'model_id': model_id,
                'image_index': len(self.image_paths) + len(features_to_append) - 1
            })
            added += 1
        if added == 0:
            logger.info("没有可增量添加的新图像")
            return self.database
        # 追加到特征矩阵与元数据
        new_features_array = np.array(features_to_append)
        if self.feature_matrix is None or self.feature_matrix.size == 0:
            self.feature_matrix = new_features_array
        else:
            self.feature_matrix = np.vstack([self.feature_matrix, new_features_array])
        self.image_paths.extend([m['image_path'] for m in new_metadata])
        self.model_ids.extend([m['model_id'] for m in new_metadata])
        self.metadata.extend(new_metadata)
        # 更新数据库字典
        self.database['features'] = self.feature_matrix
        self.database['metadata'] = self.metadata
        self.database['model_ids'] = self.model_ids
        self.database['image_paths'] = self.image_paths
        self.database['total_images'] = len(self.image_paths)
        self.database['unique_models'] = len(set(self.model_ids))
        logger.info(f"增量添加完成: 新增 {added} 张，现有总数 {self.database['total_images']}")
        return self.database
    
    def save_database(self, save_path: str):
        """保存数据库到文件"""
        if not self.database:
            raise ValueError("数据库为空，请先构建数据库")
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存为pickle文件
        with open(save_path, 'wb') as f:
            pickle.dump(self.database, f)
        
        logger.info(f"数据库已保存到: {save_path}")
        
        # 同时保存JSON元数据文件
        json_path = save_path.with_suffix('.json')
        json_data = {
            'total_images': self.database['total_images'],
            'unique_models': self.database['unique_models'],
            'feature_dim': self.database['feature_dim'],
            'model_name': self.database['model_name'],
            'model_ids': self.database['model_ids'],
            'image_paths': self.database['image_paths']
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"元数据已保存到: {json_path}")

class SimilaritySearch:
    """相似度搜索类"""
    
    def __init__(self, database_path: str):
        """
        初始化相似度搜索器
        
        Args:
            database_path: 数据库文件路径
        """
        self.database = self._load_database(database_path)
        self.index = self._build_faiss_index()
        
    def _load_database(self, database_path: str) -> Dict:
        """加载数据库"""
        with open(database_path, 'rb') as f:
            database = pickle.load(f)
        
        logger.info(f"数据库加载完成:")
        logger.info(f"  - 总图像数: {database['total_images']}")
        logger.info(f"  - 唯一型号数: {database['unique_models']}")
        logger.info(f"  - 特征维度: {database['feature_dim']}")
        
        return database
    
    def _build_faiss_index(self):
        """构建FAISS索引以加速搜索"""
        features = self.database['features'].astype('float32')
        
        # 使用L2距离的索引
        index = faiss.IndexFlatL2(features.shape[1])
        index.add(features)
        
        logger.info(f"FAISS索引构建完成，包含 {index.ntotal} 个向量")
        return index
    
    def search_similar(self, query_features: np.ndarray, top_k: int = 5) -> List[Dict]:
        """
        搜索最相似的图像
        
        Args:
            query_features: 查询特征向量
            top_k: 返回前k个最相似的结果
            
        Returns:
            相似度搜索结果列表
        """
        # 确保特征向量是2D的
        if query_features.ndim == 1:
            query_features = query_features.reshape(1, -1)
        
        query_features = query_features.astype('float32')
        
        # 搜索最相似的向量
        distances, indices = self.index.search(query_features, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            distance = distances[0][i]
            similarity = 1.0 / (1.0 + distance)  # 转换为相似度分数
            
            metadata = self.database['metadata'][idx]
            results.append({
                'image_path': metadata['image_path'],
                'filename': metadata['filename'],
                'model_id': metadata['model_id'],
                'similarity': similarity,
                'distance': distance,
                'rank': i + 1
            })
        return results


    def predict_model_id(self, query_features: np.ndarray, top_k: int = 5) -> Dict:
        """
        预测查询图像的型号ID
        
        Args:
            query_features: 查询特征向量
            top_k: 用于投票的相似图像数量
            
        Returns:
            预测结果字典
        """
        # 搜索最相似的图像
        similar_results = self.search_similar(query_features, top_k)
        
        # 统计型号ID的投票
        model_votes = {}
        total_similarity = 0
        
        for result in similar_results:
            model_id = result['model_id']
            similarity = result['similarity']
            
            if model_id not in model_votes:
                model_votes[model_id] = 0
            model_votes[model_id] += similarity
            total_similarity += similarity
        predicted_model_id = similar_results[0]['model_id']
        confidence = similar_results[0]['similarity']
        # 找到得票最多的型号
        # predicted_model_id = max(model_votes.keys(), key=lambda x: model_votes[x])
        # confidence = model_votes[predicted_model_id] / total_similarity
        
        return {
            'predicted_model_id': predicted_model_id,
            'confidence': confidence,
            'model_votes': model_votes,
            # 'model_votes': {},
            'similar_images': similar_results
        }

class PartRecognitionSystem:
    """工业零部件型号识别系统"""
    
    def __init__(self, database_path: str, model_name: str = 'resnet50'):
        """
        初始化识别系统
        
        Args:
            database_path: 特征数据库路径
            model_name: 特征提取模型名称
        """
        self.feature_extractor = FeatureExtractor(model_name)
        self.similarity_search = SimilaritySearch(database_path)
        
    def recognize_part(self, image_path: str, top_k: int = 5) -> Dict:
        """
        识别零部件型号
        
        Args:
            image_path: 查询图像路径
            top_k: 返回的相似图像数量
            
        Returns:
            识别结果
        """
        logger.info(f"开始识别零部件: {image_path}")
        
        # 提取查询图像特征
        query_features = self.feature_extractor.extract_features(image_path)
        
        if query_features is None:
            return {
                'success': False,
                'error': '无法提取图像特征'
            }
        
        # 预测型号ID
        prediction = self.similarity_search.predict_model_id(query_features, top_k)
        
        result = {
            'success': True,
            'image_path': image_path,
            'predicted_model_id': prediction['predicted_model_id'],
            'confidence': prediction['confidence'],
            'model_votes': prediction['model_votes'],
            'similar_images': prediction['similar_images']
        }
        
        logger.info(f"识别完成: 型号ID={result['predicted_model_id']}, 置信度={result['confidence']:.3f}")
        
        return result

def main():
    """主函数 - 构建或增量更新特征数据库"""
    
    # 配置参数
    DEFAULT_DATABASE_DIR = r"D:\BaiduSyncdisk\database"  # 默认数据库图像文件夹
    DEFAULT_ADD_DIR = r"D:\BaiduSyncdisk\database"   # 默认增量图像文件夹
    SAVE_PATH = "./models/feature_database.pkl"  # 保存路径
    MODEL_NAME = "resnet50"  # 特征提取模型

    
    try:
        logger.info(f"初始化特征提取器: {MODEL_NAME}")
        feature_extractor = FeatureExtractor(MODEL_NAME)
        db_builder = DatabaseBuilder(feature_extractor)
        
        if Path(SAVE_PATH).exists():
            print("\n检测到已有特征数据库。")
            print("请选择操作:")
            print("1. 重新构建数据库 (全量重建)")
            print("2. 增量添加新子类别/图像 (只追加)")
            choice = input("请输入 1 或 2: ").strip()
            if choice == '2':
                add_dir = input(f"请输入增量图像文件夹路径(回车默认 {DEFAULT_ADD_DIR}): ").strip()
                if add_dir == '':
                    add_dir = DEFAULT_ADD_DIR
                logger.info("加载现有数据库用于增量更新...")
                db_builder.load_existing(SAVE_PATH)
                logger.info("开始增量添加...")
                database = db_builder.incremental_add(add_dir)
                logger.info("保存更新后的数据库...")
                db_builder.save_database(SAVE_PATH)
            else:
                # 全量重建
                database_dir = input(f"请输入重建使用的数据库文件夹(回车默认 {DEFAULT_DATABASE_DIR}): ").strip()
                if database_dir == '':
                    database_dir = DEFAULT_DATABASE_DIR
                logger.info("开始全量重建特征数据库...")
                database = db_builder.build_database(database_dir)
                logger.info("保存特征数据库...")
                db_builder.save_database(SAVE_PATH)
        else:
            # 初次构建
            database_dir = input(f"请输入数据库文件夹路径(回车默认 {DEFAULT_DATABASE_DIR}): ").strip()
            if database_dir == '':
                database_dir = DEFAULT_DATABASE_DIR
            logger.info("开始构建特征数据库...")
            database = db_builder.build_database(database_dir)
            logger.info("保存特征数据库...")
            db_builder.save_database(SAVE_PATH)
        
        logger.info("操作完成！")
        # 显示数据库统计信息
        print("\n=== 数据库统计信息 ===")
        print(f"总图像数: {database['total_images']}")
        print(f"唯一型号数: {database['unique_models']}")
        print(f"特征维度: {database['feature_dim']}")
        print(f"使用模型: {database['model_name']}")
        model_counts = {}
        for model_id in database['model_ids']:
            model_counts[model_id] = model_counts.get(model_id, 0) + 1
        print("\n=== 各型号图像数量 ===")
        for model_id in sorted(model_counts.keys()):
            print(f"型号 {model_id}: {model_counts[model_id]} 张图像")
    except Exception as e:
        logger.error(f"构建/更新数据库时发生错误: {e}")
        raise

if __name__ == "__main__":
    main()