from openai import OpenAI


def llm_inference(prompt: str) -> str:
    """
    调用 DeepSeek API 进行 LLM 推理，根据传入的 prompt 得到最终输出结果。

    参数:
      prompt (str): 整合了图像候选信息、用户描述以及文本特征摘要的提示信息。

    返回:
      str: LLM 推理后的最终输出结果（经过清理后的文本）。

    注意：
      请替换 <DeepSeek API Key> 为你实际的 DeepSeek API 密钥，并确保 base_url 与 DeepSeek 官方要求一致。
    """
    # 使用 DeepSeek 官方 OpenAI SDK 样例初始化客户端
    client = OpenAI(api_key="sk-29695b54f9934ed7ba96ff0534ffb95b", base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": "You are an expert in geological materials and related fields."},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )

    # 获取返回的文本结果
    result = response.choices[0].message.content.strip()

    # 如果返回内容被 Markdown 的代码块包裹（例如使用三引号），去除它
    if result.startswith("```") and result.endswith("```"):
        result = result[3:-3].strip()

    return result


if __name__ == "__main__":
    # 示例 prompt，用于测试 llm_inference 函数
    sample_prompt = (
        "候选矿物信息：\n"
        "名称: Quartz, 置信度: 0.92, 详情: 常见矿物，主要成分为二氧化硅\n"
        "名称: Feldspar, 置信度: 0.85, 详情: 主要用于陶瓷和玻璃制造\n"
        "\n用户描述：\n这是一块呈灰色、纹理细腻的岩石，矿物纯度较高。\n"
        "\n文本特征摘要：\n文本特征已提取\n"
        "\n请结合以上信息，给出最终判断和详细解释。"
    )

    result = llm_inference(sample_prompt)
    print("LLM 推理结果：")
    print(result)
