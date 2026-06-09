import json
import os
import random
from email.mime import text


def read_json_file(file_path):
    """
    从JSON文件中读取数据

    Args:
        file_path (str): JSON文件的路径

    Returns:
        dict/list: 解析后的JSON数据，如果出错则返回None
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 文件 {file_path} 不存在")
            return None
        # 打开并读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None
    except IOError as e:
        print(f"文件读取错误: {e}")
        return None
    except Exception as e:
        print(f"未知错误: {e}")
        return None

def set_ip(id:int, ips:str):
    ip_str = ",".join(ips)
    s = f"id={id} enabled=yes comment= type=0 nexthop= interface=l2tp00000000 mode=0 src_addr={ip_str} dst_addr= protocol=any src_port= dst_port= dst_type=0 area_code= iface_band=0 week=1234567 time=00:00-23:59"
    return s

def split_list_into_groups(data: list, num_groups: int) -> list:
    """
    将列表按平均数量分成指定的组数

    Args:
        data: 要分组的字典数据
        num_groups: 要分成的组数

    Returns:
        分组后的二维列表
    """
    random.shuffle(data)

    if not data:
        return []

    if num_groups <= 0:
        raise ValueError("组数必须大于0")

    if num_groups > len(data):
        raise ValueError("组数不能大于列表长度")

    # 计算每组的基本数量和余数
    total_length = len(data)
    base_size = total_length // num_groups
    remainder = total_length % num_groups

    groups = []
    start_index = 0

    for i in range(num_groups):
        # 前remainder组多分配一个元素，确保均匀分配
        current_size = base_size + (1 if i < remainder else 0)
        end_index = start_index + current_size
        groups.append(data[start_index:end_index])
        start_index = end_index

    return groups

def write_to_file(network_data: list, num_groups, output_file: str):
    """
       将分组结果写入文件

       Args:
           network_data: IP地址列表
           num_groups: 分组数量
           output_file: 输出文件路径
       """
    ip_list = split_list_into_groups(network_data, num_groups)
    with open(output_file, 'w', encoding='utf-8') as f:
        for i in range(len(ip_list)):
            x = ip_list[i]
            text = set_ip(i+1, x)
            f.write(text + '\n')


def main(num_groups:int, file_path, write_file_path):
    if num_groups <= 0:
        raise ValueError("组数必须大于0")

    # 读取JSON数据
    print(f"正在读取文件: {file_path}")
    network_data = read_json_file(file_path)
    network_data = network_data["Data"]["data"]
    network_data = [item["ip_addr"] for item in network_data if item.get("ip_addr")]

    data_len = len(network_data)
    if num_groups > data_len:
        raise ValueError("组数不能大于列表长度")

    if network_data:
        print("文件读取成功!\n")
        print("数量:",data_len)
        # print("基本信息:",split_list_into_groups(network_data,9))
        write_to_file(network_data, num_groups, write_file_path)

        # 显示基本信息

    else:
        print("无法读取JSON文件")


if __name__ == "__main__":
    # JSON文件路径
    file_path = "D:\\code\\tools\\路由地址配置\\ip.json"
    write_file_path = "D:\\code\\tools\\路由地址配置\\1_路由分流设置.txt"
    main(9, file_path, write_file_path)
