import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from BF_func import loadmodels, process_frame
import cv2

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

# ── 启动时加载模型（只加载一次）─────────────────────
print("加载刹车片检测模型...")
_state = loadmodels()
_system = _state['system']
print("模型加载完成！")


# ── 工具1：检测刹车片 ─────────────────────────────
@tool
def detect_brake_pad(image_path: str) -> str:
    """检测图像中的刹车片并识别型号。
    输入图像路径，返回检测到的刹车片数量、型号ID和置信度。
    适用于需要识别刹车片型号的场景。

    Args:
        image_path: 图像文件的完整路径
    """
    image = cv2.imread(image_path)
    if image is None:
        return f"错误：无法读取图像 {image_path}"

    annotated, summary = process_frame(image, system=_system)

    # 保存标注后的图像
    save_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "annotated_result.jpg")
    cv2.imwrite(save_path, annotated)

    return f"{summary}\n标注图像已保存至：{save_path}"


# ── 工具2：查询SOP处置建议 ────────────────────────
@tool
def query_sop(model_id: str) -> str:
    """根据刹车片型号查询标准操作规程（SOP）和处置建议。
    适用于已知型号ID，需要获取对应处置方案的场景。

    Args:
        model_id: 刹车片型号ID，如 D1415W、BFD3053N
    """
    # 模拟SOP数据库（真实场景用RAG检索SOP文档）
    sop_database = {
        "D1415W": "D1415W型号适用于丰田凯美瑞前轮。更换建议：厚度低于3mm时立即更换；检查制动盘磨损情况；建议配套使用原厂制动液。",
        "BFD3053N": "BFD3053N型号适用于福特F-150后轮。更换建议：定期检查磨损指示器；建议每30000km更换一次；注意检查卡钳活塞是否正常回位。",
        "DEFAULT": "未找到该型号的SOP记录，请联系技术支持或查阅原厂手册。"
    }

    advice = sop_database.get(model_id, sop_database["DEFAULT"])
    return f"型号 {model_id} 的SOP建议：{advice}"


# ── 工具3：生成检测报告 ───────────────────────────
@tool
def generate_report(detection_summary: str, sop_advice: str) -> str:
    """根据检测结果和SOP建议生成完整的检测报告。
    适用于需要输出正式检测报告的场景。

    Args:
        detection_summary: 检测结果摘要
        sop_advice: SOP处置建议
    """
    from datetime import datetime

    report = f"""
========================================
        刹车片检测报告
========================================
检测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【检测结果】
{detection_summary}

【处置建议】
{sop_advice}

【结论】
检测完成，请根据以上建议进行处置。
如有疑问请联系技术支持。
========================================
"""

    # 保存报告
    save_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(save_dir, exist_ok=True)
    report_path = os.path.join(save_dir, "detection_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    return f"报告已生成并保存至：{report_path}\n{report}"


# ── 创建 Agent ────────────────────────────────────
agent = create_react_agent(
    model,
    tools=[detect_brake_pad, query_sop, generate_report],
)
print("Agent 创建完成！")

# ── 测试 ──────────────────────────────────────────
if __name__ == "__main__":
    # 换成你实际有的刹车片图片路径
    test_image = input("请输入测试图片路径：").strip()

    print(f"\n开始检测：{test_image}")
    result = agent.invoke({
        "messages": [HumanMessage(
            f"请检测这张图片中的刹车片：{test_image}，"
            f"识别型号后查询SOP建议，最后生成完整检测报告。"
        )]
    })

    print("\n=== Agent 最终回答 ===")
    print(result['messages'][-1].content)