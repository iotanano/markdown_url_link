import streamlit as st
import re

def format_markdown(markdown_text):
    """
    格式化 Markdown 文本：
    1. 将 "数字、" 改为 "数字. "
    2. 删除多余的空行，仅在标题前保留一个空行
    """
    # 替换 "数字、" 为 "数字. "
    markdown_text = re.sub(r'(\d+)、', r'\1. ', markdown_text)

    # 删除多余的空行，只保留标题前一个空行
    lines = markdown_text.splitlines()
    formatted_lines = []
    previous_line_empty = True
    for line in lines:
        if line.strip() == "":  #当前行是空行
            if not previous_line_empty:  #上一个不是空行，当前是空行，可以添加
                formatted_lines.append(line)
                previous_line_empty = True
        elif line.strip().startswith("#"):  #当前行是标题
            if not previous_line_empty:  #上一个不是空行，当前是标题，需要添加一个空行。
                formatted_lines.append("")
            formatted_lines.append(line)
            previous_line_empty = False
        else: #当前行不是空行，也不是标题，正常添加
            formatted_lines.append(line)
            previous_line_empty = False

    return "\n".join(formatted_lines).strip()

def add_urls_to_markdown(markdown_text, urls):
    """为 Markdown 标题添加 URL 链接，并应用其他格式化规则，并生成表格"""
    formatted_markdown = format_markdown(markdown_text)
    
    # 修改标题中的中文数字为阿拉伯数字
    def replace_chinese_number(match):
        chinese_num = match.group(1)
        num_map = {"一": "1", "二": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9", "十": "10"}
        arabic_num = num_map.get(chinese_num, chinese_num)
        return f"关卡 {arabic_num}"

     # 匹配标题
    lines = formatted_markdown.splitlines()
    header_pattern = re.compile(r"^(#+)\s*(关卡|通关题)([\u4e00-\u9fa5]*)(.*)")


    linked_markdown_lines = []
    table_rows = []  # 用于存储表格行的列表
    url_index = 0
    i = 0
    while i < len(lines):
        line = lines[i]

         # 1. 修改标题
        header_match = header_pattern.match(line)
        if header_match:
            level = header_match.group(1)
            title_prefix = header_match.group(2)
            chinese_number = header_match.group(3)
            title_suffix = header_match.group(4)

            # 修改通关题为关卡N
            if title_prefix == "通关题":
                title_prefix = "关卡"
                line = re.sub(r"通关题", f"关卡 {len(urls)}", line)

            # 处理中文数字转阿拉伯数字
            line = re.sub(r"关卡([\u4e00-\u9fa5]+)", replace_chinese_number, line)

            # 确保标题使用一个中文冒号，并添加标题链接
            title_text = line.replace(level,"").strip()
            title_text = re.sub(r'[:：、]+', '：', title_text, 1)  # 确保只有一个中文冒号，并处理顿号
            url = urls[url_index]
            linked_markdown_lines.append(f'{level} [{title_text}]({url})')

            # 生成表格行
            linked_title = f"[{title_text}]({url})"
            if url_index == 0:
                access_condition = "无"
                reward = 1
            elif url_index == len(urls) - 1:
                access_condition = f"到达关卡 {url_index + 1}"
                reward = 6
            else:
                access_condition = f"到达关卡 {url_index + 1}"
                reward = url_index
                if url_index == 1:
                     reward = 1
            table_rows.append(f"| {linked_title} | {access_condition} | {reward} |")

            # 2. 处理标题下的正文
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("#"):
                text_line = lines[i]

                 # 删除 "中文:" 后为空的段落
                if re.match(r"^[\u4e00-\u9fa5]+:\s*$", text_line.strip()):
                    i += 1
                    continue

                # 确保正文中 "关卡 N" 与后面的文本使用一个中文冒号
                text_line = re.sub(r"(关卡\s*\d+)([:：、]+)", r"\1：", text_line, 1)

                # 3. 段落开头加粗，并确保只有一个中文冒号
                text_line = re.sub(r"^([\u4e00-\u9fa5]+)[:：]+", r"**\1**：", text_line, 1)


                linked_markdown_lines.append(text_line)
                i += 1

            # 4. 添加结尾段落（添加中文括号）
            if url_index == 0:
                linked_markdown_lines.append(f"**关卡材料：**[{urls[url_index]}]({urls[url_index]})（**报名后即可访问，fork 后即可运行教案、写作业**）")
            else:
                linked_markdown_lines.append(f"**关卡材料：**[{urls[url_index]}]({urls[url_index]})（到达关卡 {url_index+1} 后方可访问）")

            url_index += 1

        else:
            linked_markdown_lines.append(line)
            i += 1

    # 生成表格 markdown 文本
    table_header = "| 关卡材料链接 | 访问条件 | 闯关鲸币奖励 |"
    separator = "| :------------- | :-------: | :---------: |"
    table = "\n".join([table_header, separator] + table_rows)

    # 添加表格前的文字和表格后的分隔线及文字
    intro_text = "🐳：请依次访问下方蓝色超链接的关卡教案材料，点击【Fork】-【运行】，拷贝教案到你的工作台，进入编程界面后点击【运行所有】即可复现教案，编写代码、答题闯关。满分即可晋级至下一关，完成全部关卡即可通关。"
    separator_line = "\n\n---\n\n"
    detail_intro_text = "关卡详细介绍如下："

    return f"{intro_text}\n\n{table}{separator_line}{detail_intro_text}\n" +  "\n".join(linked_markdown_lines).strip()

def copy_to_clipboard(text):
    """将文本复制到剪贴板"""
    st.session_state.copied_text = text
    st.success("已复制到剪贴板！")

def main():
    st.title("Markdown Header URL Link Inserter")

    st.markdown("""
    This app allows you to add URLs as clickable links to markdown headers, format the text, and add extra context.
    """)

    # Input fields
    markdown_input = st.text_area("Markdown Input", height=300, help="Paste your markdown text here.")
    url_input = st.text_area("URLs Input", height=150, help="Enter one URL per line, matching the order of markdown headers.")

    # Generate button
    if st.button("Generate Markdown with Links"):
        try:
            if not markdown_input.strip() or not url_input.strip():
                st.warning("Please provide both markdown text and URLs.")
            else:
                 urls = [url.strip() for url in url_input.splitlines() if url.strip()] #去掉空行
                 updated_markdown = add_urls_to_markdown(markdown_input, urls)
                 
                 if updated_markdown:
                    # Display the updated markdown
                    st.text_area("Updated Markdown", value=updated_markdown, height=300)
                    col1, col2, _ = st.columns([0.2, 0.6, 0.2])  # Adjusted column ratios
                    with col1:
                        if st.button("复制 Markdown", key="copy_button", on_click=copy_to_clipboard, args=[updated_markdown]):
                            pass
                    with col2:
                       if "copied_text" in st.session_state:
                           st.text_area("已复制内容", value=st.session_state.copied_text, height=50, disabled=True)
                    st.download_button("Download Markdown", updated_markdown, "updated_markdown_with_links.md", "text/markdown")

        except ValueError as e:
            st.error(str(e))

if __name__ == "__main__":
    main()