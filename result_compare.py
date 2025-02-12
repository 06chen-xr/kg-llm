import openai
import pandas as pd
from neo4j import GraphDatabase
import openai
import json
import httpx
import re
from openai.types.chat.completion_create_params import ResponseFormat

# 设置 OpenAI API 密钥
api_key = ''

# 设置代理地址，否则无法连接chatgpt
proxies = "http://localhost:8001"


def retrieve_knowledge(news_article, threshold):
    # 使用 OpenAI 的嵌入模型，将新闻稿向量化
    try:
        # 使用 httpx 直接发起请求
        with httpx.Client(proxies=proxies) as client:
            response = client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "text-embedding-ada-002",
                    "input": news_article
                },
                timeout=60  # 超时设置
            )

            # 检查请求是否成功
            response.raise_for_status()

            # 解析响应数据
            data = response.json()
            query_embedding = data['data'][0]['embedding']

            print("嵌入向量获取成功！")
            # 您可以在此处使用 query_embedding 进行后续处理

    except httpx.HTTPError as e:
        print(f"HTTP 错误：{e}")
    except Exception as e:
        print(f"发生错误：{e}")

    with open("entity_embeddings.json", "r") as f:
        entity_embeddings = json.load(f)

    # 计算相似度，选择最相似的实体
    import numpy as np

    similarities = []
    query_vec = np.array(query_embedding)
    for name, embedding in entity_embeddings:
        entity_vec = np.array(embedding)
        cosine_sim = np.dot(query_vec, entity_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(entity_vec))
        similarities.append((name, cosine_sim))

    # 排序，选择相似度最高的实体
    similarities.sort(key=lambda x: x[1], reverse=True)
    print(similarities)
    top_entities = [name for name, sim in [i for i in similarities if i[1] > threshold]]

    # 根据选出的实体，检索相关的关系
    file_path = "graph_database_export.xlsx"  # 替换为你的 Excel 文件路径
    data = pd.read_excel(file_path)
    filtered_data = data[
        (data["entity_1"].isin(top_entities)) | (data["entity_2"].isin(top_entities))
        ]
    results = filtered_data
    results.reset_index(inplace=True)
    knowledge_texts = []
    for i in range(len(results)):
        from_name = results.iloc[i]['entity_1']
        from_label = results.iloc[i]['type_1']
        rel_type = results.iloc[i]['relation_1']
        to_name = results.iloc[i]['entity_2']
        to_label = results.iloc[i]['type_2']

        # 构建知识文本
        knowledge_text = f"实体类型：{from_label} {from_name} {rel_type.lower()} 实体类型：{to_label} {to_name}"
        knowledge_texts.append(knowledge_text)

    # 合并知识文本
    retrieved_knowledge = '\n'.join(knowledge_texts)
    print(knowledge_texts)

    return retrieved_knowledge


def query_openai(prompt, api_key, proxies=None):
    """封装请求GPT模型的函数"""
    with httpx.Client(proxies=proxies) as client:
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                ''
                "max_tokens": 2000
            },
            timeout=60
        )
    return response.json()['choices'][0]['message']['content']


def query_openai_json(prompt, api_key, proxies=None):
    """封装请求GPT模型的函数"""
    with httpx.Client(proxies=proxies) as client:
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "user", "content": prompt},
                ],

                "temperature": 0,
                "max_tokens": 2000
            },
            timeout=60
        )
    return response.json()['choices'][0]['message']['content']


def parse_entities_and_relationships(text):
    # 提取 JSON 部分
    entities_match = re.search(r'(?<="实体列表": )\[[^\]]+\]', text)
    relationships_match = re.search(r'(?<="关系列表": )\[[^\]]+\]', text)

    # 解析 JSON 数据
    entities = json.loads(entities_match.group()) if entities_match else []
    relationships = json.loads(relationships_match.group()) if relationships_match else []

    return {
        "实体列表": entities,
        "关系列表": relationships
    }


def count_entities_and_relationships(parsed_data):
    # 计算实体和关系的个数
    num_entities = len(parsed_data["实体列表"])
    num_relationships = len(parsed_data["关系列表"])
    return num_entities, num_relationships


def extract_entities_and_relations(news_article, retrieved_knowledge, api_key, proxies=None):
    """执行多轮循环查询，逐步完善实体和关系抽取"""
    # 初次查询 - 基础实体与关系抽取
    initial_prompt = generate_prompt(news_article, retrieved_knowledge)
    initial_result = query_openai(initial_prompt, api_key, proxies)

    prev_total = 0
    total = 0
    loop = 1
    while total <= prev_total:

        second_prompt = generate_follow_up_prompt(initial_result, news_article)
        second_result = query_openai(second_prompt, api_key, proxies)

        parsed_data = parse_entities_and_relationships(second_result)
        num_entities, num_relationships = count_entities_and_relationships(parsed_data)
        # 根据个数迭代
        total = num_entities + num_relationships

        print(f"迭代次数:{loop}当前实体数: {num_entities}, 关系数: {num_relationships}, 总数: {total}")
        loop += 1

        # 检查终止条件
        if prev_total == total:
            print('迭代不再增加实体，迭代结束')
            break
        elif loop == 5:
            print('已达最高迭代次数,迭代结束')
            break
        prev_total = max(total, prev_total)

    return json.dumps(parsed_data, ensure_ascii=False, indent=4)


def generate_prompt(news_article, retrieved_knowledge):
    """生成初次查询的提示"""
    return f'''
请阅读以下新闻稿和相关知识，并按照要求提取实体和关系。

**实体类型定义：**

- **驱动因素（Driver）**：表示导致某些气候事件的直接驱动因子，例如大气阻塞、重度降水、暖空气输送、重度降水、积雪融化等，
- **调节因素（Modulator）**：表示调节气候事件强度或分布的背景因素，影响灾害严重程度和/或频率的事件、过程或现象。(例如：海洋表面温度模式)
- **灾害（Hazard）**：表示由驱动因素引发的气候灾害，可能造成负面社会或环境影响的现象、事件或过程。(例如：洪水，滑坡，霜冻，干旱，热浪)
- **影响（Impact）**：表示气候灾害对自然和社会的潜在影响，灾害引起的负面社会和环境后果（例如，建筑倒塌、环境污染、人员伤亡，人类健康）。

**链接类型定义：**

- **加剧**：表示一个实体加剧另一个实体的发生。
- **削弱**：表示一个实体削弱了另一个实体的发生。
- **增强**：表示一个实体增强了另一个实体的发生。

**新闻稿：**

{news_article}

**相关知识：**

{retrieved_knowledge}

你是一名信息抽取专家。请根据以下新闻稿内容和现有的实体及关系列表完成以下任务：

1. 仅提取来源于新闻稿的实体和关系，不能使用外挂知识库的内容。
2. 检查现有的实体和关系列表，确保它们的支持句子确实能从新闻稿中找到。如果找不到支持句子，则删除对应的实体或关系。
3. 检查现有的实体，是否存在语义相似的，进行合并
4. 检查现有结果中是否存在仅在外挂知识库中存在，而不在新闻稿中的实体或关系，去除这些内容。


### 任务要求
- 如果发现某个实体或关系的支持句子不在新闻稿中，请将其标记为删除。
- 保留符合要求的实体和关系，并输出修改后的实体列表和关系列表。


 **输出格式**：

   - **实体列表**（JSON 格式）：

     ```
     {{
       "实体列表": [
         {{"实体名称": "实体1", "实体类型": "类型1","新闻稿支持句子":""}},
         {{"实体名称": "实体2", "实体类型": "类型2","新闻稿支持句子":""}},
         ...
       ]
     }}
     ```

   - **关系列表**（JSON 格式）：

     ```
     {{
       "关系列表": [
         {{"起始实体": "实体1", "关系类型": "关系类型", "目标实体": "实体2","新闻稿支持句子":""}},
         ...
       ]
     }}
     ```
'''


def generate_follow_up_prompt(initial_result, news_article):
    """生成第二轮查询的提示"""
    return f'''
根据以下已识别的实体和关系，请进一步检查是否存在遗漏的关系。
首轮识别出来的内容：{initial_result}
你是一名信息抽取专家。请根据以下新闻稿内容，对当前的实体和关系列表进行重新审阅，完成以下任务：

**实体类型定义：**

- **驱动因素（Driver）**：表示导致某些气候事件的直接驱动因子，例如大气阻塞、重度降水、暖空气输送、重度降水、积雪融化等，
- **调节因素（Modulator）**：表示调节气候事件强度或分布的背景因素，影响灾害严重程度和/或频率的事件、过程或现象。(例如：海洋表面温度模式)
- **灾害（Hazard）**：表示由驱动因素引发的气候灾害，可能造成负面社会或环境影响的现象、事件或过程。(例如：洪水，滑坡，霜冻，干旱，热浪)
- **影响（Impact）**：表示气候灾害对自然和社会的潜在影响，灾害引起的负面社会和环境后果（例如，建筑倒塌、环境污染、人员伤亡，人类健康）。

**链接类型定义：**

- **加剧**：表示一个实体加剧另一个实体的发生。
- **引发**：表示一个实体引发另一个实体的发生
- **削弱**：表示一个实体削弱了另一个实体的发生。
- **增强**：表示一个实体增强了另一个实体的发生。

关系例子：
    1.	热带和副热带气旋带来的重度降水经常导致洪水的发生，对基础设施造成破坏。
    2.	海洋表面温度模式是影响大气阻塞的重要调节因子，可能加剧极端天气事件。
    3.	温度上升直接驱动热浪的形成，并对人类健康产生严重威胁，尤其是老年人群体。

任务要求：
1. 重新阅读新闻稿，寻找遗漏的实体和关系，补充到列表中。
2. 检查现有结果中是否存在仅在外挂知识库中存在，而不在新闻稿中的实体或关系，去除这些内容。
3. 输出以下几个部分：
   - **修改后的实体列表和关系列表**：整合新增和保留的内容。
   - **新增的实体或关系**：列出新增内容，并提供对应的支持句子。


自我检查与迭代：
1. 在完成提取后，对结果进行自我检查，找出可能遗漏的实体或关系。
2. 如果发现遗漏，请更新"实体列表"或"关系列表"，并输出完整的最新结果。
3. 如果没有新的实体或关系需要添加，请声明“提取完成，无需进一步迭代”。


**新闻稿：**

{news_article}

完成以下要求：
请逐句检查新闻稿中的表述，找出可能遗漏的关系，并按要求输出对应的格式,并按照要求标注链接类型，并提供支持关系的原文句子。最终请只输出完整的json格式结果，输出格式要求如下
**输出格式**：

   - **实体列表**（JSON 格式）：

     ```json
     {{
       "实体列表": [
         {{"实体名称": "实体1", "实体类型": "类型1","新闻稿支持句子":""}},
         {{"实体名称": "实体2", "实体类型": "类型2","新闻稿支持句子":""}},
         ...
       ]
     }}
     ```

   - **关系列表**（JSON 格式）：

     ```json
     {{
       "关系列表": [
         {{"起始实体": "实体1", "关系类型": "关系类型", "目标实体": "实体2","新闻稿支持句子":""}},
         ...
       ]
     }}
     ```

'''


def parse_extracted_entities_and_relations(raw_str):
    """解析格式化字符串中的实体和关系，并转换为JSON格式。"""
    entities = []
    relations = []

    # 使用正则表达式匹配实体和关系部分
    entity_pattern = r"- (.*?)（(.*?)）\s*：\s*(.*)"
    relation_pattern = r"- (.*?)\s+(.*?)\s+(.*)"

    # 分割原始字符串为行
    lines = raw_str.split('\n')
    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 判断当前处理的是实体还是关系部分
        if "实体：" in line:
            current_section = "entity"
            continue
        elif "关系：" in line:
            current_section = "relation"
            continue

        # 根据当前部分解析内容
        if current_section == "entity":
            match = re.match(entity_pattern, line)
            if match:
                entity_type = match.group(2).strip()
                entity_name = match.group(3).strip()
                entities.append({"实体名称": entity_name, "实体类型": entity_type})

        elif current_section == "relation":
            match = re.match(relation_pattern, line)
            if match:
                start_entity = match.group(1).strip()
                relation_type = match.group(2).strip()
                target_entity = match.group(3).strip()
                relations.append({
                    "起始实体": start_entity,
                    "关系类型": relation_type,
                    "目标实体": target_entity,
                })

    # 构建最终的JSON结构
    result = {
        "实体列表": entities,
        "关系列表": relations
    }

    return json.dumps(result, ensure_ascii=False, indent=4)


def parse_result(result):
    """解析GPT返回的结果，提取实体和关系"""
    result = parse_extracted_entities_and_relations(result)
    result_json = json.loads(result)
    entities = result_json.get("实体列表", [])
    relations = result_json.get("关系列表", [])
    return entities, relations


def parse_generated_string(generated_str):
    """
    解析生成的字符串，提取实体列表和关系列表。
    :param generated_str: 包含实体和关系的字符串
    :return: 包含实体列表和关系列表的字典
    """
    # 使用正则表达式提取 JSON 块
    json_blocks = re.findall(r"```json\n(.*?)```", generated_str, re.DOTALL)

    # 初始化结果字典
    result = {
        "实体列表": [],
        "关系列表": []
    }

    # 解析每个 JSON 块
    for block in json_blocks:
        try:
            parsed_json = json.loads(block)
            if "实体列表" in parsed_json:
                result["实体列表"] = parsed_json["实体列表"]
            if "关系列表" in parsed_json:
                result["关系列表"] = parsed_json["关系列表"]
        except json.JSONDecodeError:
            print(f"解析失败：{block}")
            continue

    return result

font='''**输出格式**：

       - **实体列表**（JSON 格式）：

         ```
         {{
           "实体列表": [
             {{"实体名称": "实体1", "实体类型": "类型1"}},
             {{"实体名称": "实体2", "实体类型": "类型2"}},
             ...
           ]
         }}
         ```

       - **关系列表**（JSON 格式）：

         ```
         {{
           "关系列表": [
             {{"起始实体": "实体1", "关系类型": "关系类型", "目标实体": "实体2"}},
             ...
           ]
         }}
         ```'''
def zero_shot(news_article,font):
    return f'''
    请阅读以下新闻稿和相关知识，并按照要求提取实体和关系。

    **实体类型定义：**

    - **驱动因素（Driver）**：表示导致某些气候事件的直接驱动因子
    - **调节因素（Modulator）**：表示调节气候事件强度或分布的背景因素，影响灾害严重程度和/或频率的事件、过程或现象
    - **灾害（Hazard）**：表示由驱动因素引发的气候灾害，可能造成负面社会或环境影响的现象、事件或过程。
    - **影响（Impact）**：表示气候灾害对自然和社会的潜在影响，灾害引起的负面社会和环境后果（。

    **链接类型定义：**

    - **加剧**：表示一个实体加剧另一个实体的发生。
    - **削弱**：表示一个实体削弱了另一个实体的发生。
    - **增强**：表示一个实体增强了另一个实体的发生。

    **新闻稿：**

    {news_article}

     {font}
    '''

def few_shot(news_article,font):
    return f'''
    请阅读以下新闻稿和相关知识，并按照要求提取实体和关系。

    **实体类型定义：**

    - **驱动因素（Driver）**：表示导致某些气候事件的直接驱动因子
    - **调节因素（Modulator）**：表示调节气候事件强度或分布的背景因素，影响灾害严重程度和/或频率的事件、过程或现象
    - **灾害（Hazard）**：表示由驱动因素引发的气候灾害，可能造成负面社会或环境影响的现象、事件或过程。
    - **影响（Impact）**：表示气候灾害对自然和社会的潜在影响，灾害引起的负面社会和环境后果（。

    **链接类型定义：**

    - **加剧**：表示一个实体加剧另一个实体的发生。
    - **削弱**：表示一个实体削弱了另一个实体的发生。
    - **增强**：表示一个实体增强了另一个实体的发生。
    示例：
    新闻稿：
    “热带气旋引发了严重洪水，淹没了多个沿海村庄。海洋表面温度的升高被认为是影响气旋强度的重要因素。”

    提取结果：
        •	实体：
        •	热带气旋（Driver）
        •	洪水（Hazard）
        •	海洋表面温度（Modulator）
        •	关系：
        •	热带气旋 引发 洪水
        •	海洋表面温度 增强 热带气旋
    **新闻稿：**

    {news_article}

     {font}
    '''

def cot(news_article,font):
    return f'''
    请阅读以下新闻稿和相关知识，并按照要求提取实体和关系。

    **实体类型定义：**

    - **驱动因素（Driver）**：表示导致某些气候事件的直接驱动因子
    - **调节因素（Modulator）**：表示调节气候事件强度或分布的背景因素，影响灾害严重程度和/或频率的事件、过程或现象
    - **灾害（Hazard）**：表示由驱动因素引发的气候灾害，可能造成负面社会或环境影响的现象、事件或过程。
    - **影响（Impact）**：表示气候灾害对自然和社会的潜在影响，灾害引起的负面社会和环境后果（。

    **链接类型定义：**

    - **加剧**：表示一个实体加剧另一个实体的发生。
    - **削弱**：表示一个实体削弱了另一个实体的发生。
    - **增强**：表示一个实体增强了另一个实体的发生。
    
    
    ### 任务要求
    按照以下步骤完成任务：
    step1. 逐句阅读新闻稿，识别符合定义的实体。
    step2. 确定实体之间是否存在关系，并标注关系类型。
    step3. 验证提取结果是否与新闻稿内容一致。
    
    示例：
    **新闻稿**：
    “重度降水引发了洪水，对多个村庄造成严重破坏。大气阻塞模式是影响降水的主要因素。”
    
    **分步骤推理**：
    1. **识别实体**：
     - **句子 1**：重度降水引发了洪水。
       - 提取实体：“重度降水”（Driver），支持句子：“重度降水引发了洪水。”
       - 提取实体：“洪水”（Hazard），支持句子：“重度降水引发了洪水。”
     - **句子 2**：大气阻塞模式是影响降水的主要因素。
       - 提取实体：“大气阻塞模式”（Modulator），支持句子：“大气阻塞模式是影响降水的主要因素。”
    
    2. **识别关系**：
     - **句子 1**：重度降水引发了洪水。
       - 提取关系：“重度降水” 引发 “洪水”，支持句子：“重度降水引发了洪水。”
     - **句子 2**：大气阻塞模式是影响降水的主要因素。
       - 提取关系：“大气阻塞模式” 增强 “重度降水”，支持句子：“大气阻塞模式是影响降水的主要因素。”
       
    3.**验证并输出**：
    - 验证所有实体和关系是否有支持句子。

    **新闻稿：**

    {news_article}

     {font}
    '''

def ReAct(news_article,font):
    return f'''
    请阅读以下新闻稿和相关知识，并按照要求提取实体和关系。

    **实体类型定义：**

    - **驱动因素（Driver）**：表示导致某些气候事件的直接驱动因子
    - **调节因素（Modulator）**：表示调节气候事件强度或分布的背景因素，影响灾害严重程度和/或频率的事件、过程或现象
    - **灾害（Hazard）**：表示由驱动因素引发的气候灾害，可能造成负面社会或环境影响的现象、事件或过程。
    - **影响（Impact）**：表示气候灾害对自然和社会的潜在影响，灾害引起的负面社会和环境后果（。

    **链接类型定义：**

    - **加剧**：表示一个实体加剧另一个实体的发生。
    - **削弱**：表示一个实体削弱了另一个实体的发生。
    - **增强**：表示一个实体增强了另一个实体的发生。
    
    ### 任务要求
    1. **行动**：首先提取所有可能的实体及其类型。
    2. **推理**：分析实体之间的关系，根据上下文确定关系类型。
    3. **验证**：确保提取的每个实体和关系都能从新闻稿中找到支持句子。

    **新闻稿：**

    {news_article}

     {font}
    '''


def main():
    news_set = pd.read_excel('news_subset.xlsx')
    news_article = news_set['full_text'][5]

    retrieved_knowledge = retrieve_knowledge(news_article, threshold=0.8)

    # 实体和关系抽取
    result = extract_entities_and_relations(news_article, retrieved_knowledge, api_key, proxies=proxies)

    print('模型输出：')
    print(result)

    # 解析结果
    try:
        # 将模型输出的字符串转换为 JSON 对象
        output = json.loads(result)
        entities = output.get('实体列表', [])
        relations = output.get('关系列表', [])

        print('\n提取的实体：')
        for entity in entities:
            print(entity)

        print('\n提取的关系：')
        for relation in relations:
            print(relation)
    except json.JSONDecodeError:
        print('无法解析模型输出，请检查输出格式。')

def diff_prompt():
    news_set = pd.read_excel('news_subset.xlsx')
    news_article = news_set['full_text'][20]

    # 实体和关系抽取
    prompt = cot(news_article,font)
    result = query_openai(prompt,api_key,proxies=proxies)
    parsed_data = parse_entities_and_relationships(result)
    num_entities, num_relationships = count_entities_and_relationships(parsed_data)
    # 根据个数迭代
    total = num_entities + num_relationships

    print(f"当前实体数: {num_entities}, 关系数: {num_relationships}, 总数: {total}")
    print('模型输出：')
    print(result)

    # 解析结果
    try:
        # 将模型输出的字符串转换为 JSON 对象
        output = json.loads(result)
        entities = output.get('实体列表', [])
        relations = output.get('关系列表', [])

        print('\n提取的实体：')
        for entity in entities:
            print(entity)

        print('\n提取的关系：')
        for relation in relations:
            print(relation)
    except json.JSONDecodeError:
        print('无法解析模型输出，请检查输出格式。')

if __name__ == '__main__':
    # main()
    diff_prompt()