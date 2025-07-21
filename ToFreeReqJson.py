import os
import json
import uuid
from bs4 import BeautifulSoup
import markdownify  # 需要安装：pip install markdownify


def determine_level(file_number):
    """根据文件名确定语法等级"""
    num = int(file_number)
    if 1 <= num <= 207:
        return "N1"
    elif 208 <= num <= 362:
        return "N2"
    elif 363 <= num <= 521:
        return "N3"
    elif 522 <= num <= 640:
        return "N4"
    elif 641 <= num <= 793:
        return "N5"
    return "Unknown"


def extract_section_content(section_header):
    """提取标题后的内容部分"""
    content = []
    next_sib = section_header.find_next_sibling()

    while next_sib and next_sib.name != "h1":
        if next_sib.name == "p":
            content.append(str(next_sib))
        next_sib = next_sib.find_next_sibling()

    return "".join(content)


def html_to_json(input_dir, output_file):
    """转换HTML文件为JSON格式"""
    grammar_data = []

    # 获取并按数字排序所有HTML文件
    html_files = sorted(
        [f for f in os.listdir(input_dir) if f.endswith(".html")],
        key=lambda x: int(x.split(".")[0])
    )

    for filename in html_files:
        file_path = os.path.join(input_dir, filename)
        file_number = filename.split(".")[0]

        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

            # 获取整个语法内容区域
            grammar_content = soup.find("div", class_="grammar-content")
            if not grammar_content:
                continue

            # 提取标题（语法内容）
            grammar_span = grammar_content.find("span", class_="grammar")
            title = grammar_span.find_parent("h1").find_next_sibling("p").get_text().strip()

            # 将整个内容转换为Markdown
            html_content = "".join(str(tag) for tag in grammar_content.contents)
            markdown_content = markdownify.markdownify(html_content)

            # 创建数据项
            grammar_item = {
                "id": file_number,
                "uuid": str(uuid.uuid4()),  # 生成随机UUID[9,10](@ref)
                "title": title,
                "content": markdown_content,
                "level": determine_level(file_number),
                "child": []
            }

            grammar_data.append(grammar_item)

    # 保存为JSON文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(grammar_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    input_directory = "grammar_pages"
    output_json = "grammar_data.json"

    html_to_json(input_directory, output_json)
    print(f"转换完成！已保存到 {output_json}")
