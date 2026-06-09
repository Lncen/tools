import re
from pathlib import Path


def extract_links_from_file(input_file, output_file=None):
    """
    从文件中提取链接

    Args:
        input_file: 输入的md文件路径
        output_file: 输出提取结果的文件路径（可选）

    Returns:
        提取到的链接列表
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+/'

    extracted_links = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            urls = re.findall(url_pattern, line)
            for url in urls:
                url = url.rstrip('.,;:!?)">]')
                if url:
                    extracted_links.append({
                        'line_number': line_num,
                        'url': url,
                        'original_line': line.strip()
                    })

        if output_file and extracted_links:
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in extracted_links:
                    f.write(f"{item['url']}\n")

        return extracted_links

    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
        return []
    except Exception as e:
        print(f"处理文件时出错：{e}")
        return []


def calculate_cost(quantity, unit_price):
    """计算单项成本"""
    return quantity * unit_price


def format_output(label, links):
    """格式化输出链接列表"""
    print("\n==========")
    for link in links:
        print(f"{label}----{link['url']}")


def main(z_config, s_config, f_config):
    """
    主函数

    Args:
        z_config: [数量, 单价] 配置
        s_config: [数量, 单价] 配置
        f_config: [数量, 单价] 配置
    """
    input_file = Path(__file__).parent / 'url.md'

    print(f"正在读取文件：{input_file}")
    print("正在提取链接...")

    links = extract_links_from_file(input_file)
    num = len(links)

    if not links:
        print("未找到任何链接")
        return

    print(f"\n成功提取到 {num} 个链接")

    # 格式化输出三类链接
    format_output(z_config[0], links)
    format_output(s_config[0], links)
    format_output(f_config[0], links)

    # 计算成本
    z_total = calculate_cost(int(z_config[0]), float(z_config[1]))
    s_total = calculate_cost(int(s_config[0]), float(s_config[1]))
    f_total = calculate_cost(int(f_config[0]), float(f_config[1]))

    total_cost = z_total + s_total + f_total

    print(f"\n成本计算:")
    zx = f"{z_config[0]}×{z_config[1]}"
    sx = f"{s_config[0]}×{s_config[1]}"
    fx = f"{f_config[0]}×{f_config[1]}"
    print(f"\n{zx} + {sx} + {fx} = {total_cost:.2f}")

    final_result = total_cost * num
    print(f"{total_cost:.2f} × {num} = {final_result:.2f}")


def get_input(prompt, default):
    """
    获取用户输入，支持默认值

    Args:
        prompt: 提示信息
        default: 默认值 [数量, 单价]

    Returns:
        [数量, 单价] 列表
    """
    user_input = input(f"{prompt}（默认 数量:{default[0]}, 单价:{default[1]}）：").strip()

    if not user_input:
        return default

    try:
        parts = user_input.split(',')
        quantity = int(parts[0].strip())
        return [quantity, default[1]]
    except ValueError:
        print("输入无效，使用默认值")
        return default


if __name__ == "__main__":
    # 默认配置 [数量, 单价]
    default_z = [100, 0.006]
    default_s = [50, 0.02]
    default_f = [100, 0.003]

    try:
        z = get_input("z", default_z)
        s = get_input("s", default_s)
        f = get_input("f", default_f)

        main(z, s, f)
    except KeyboardInterrupt:
        print("\n\n程序已取消")
