import os
import sys
import argparse
import pandas as pd
from pathlib import Path

def convert_csv_to_excel(src_folder, dest_folder):
    # 检查源文件夹是否存在
    if not os.path.exists(src_folder):
        print(f"❌ 错误: 源文件夹 '{src_folder}' 不存在！")
        sys.exit(1)

    # 如果目标文件夹不存在，则自动创建
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
        print(f"📁 已创建目标文件夹: '{dest_folder}'")

    # 获取所有 csv 文件
    src_path = Path(src_folder)
    csv_files = [f for f in src_path.iterdir() if f.suffix.lower() == '.csv']

    if not csv_files:
        print(f"⚠️ 在 '{src_folder}' 中没有找到 CSV 文件 (.csv)。")
        return

    success_count = 0

    for file_path in csv_files:
        print(f"⏳ 正在处理: {file_path.name} ...", end=" ")
        try:
            # 读取 CSV
            # 1. 尝试以 utf-8-sig 读取（兼容无 BOM 和带 BOM 的 UTF-8，大部分现代软件输出格式）
            # 2. dtype=str 强制所有数据按字符串读取，防止金额转科学计数法、保留前导零（如00123）和小数点后精度。
            try:
                df = pd.read_csv(file_path, dtype=str, encoding='utf-8-sig')
            except UnicodeDecodeError:
                # 如果 UTF-8 解码失败，尝试使用 GBK 编码（国内早期 ERP 或老旧 Excel 导出的 CSV 常见编码）
                df = pd.read_csv(file_path, dtype=str, encoding='gbk')

            # 清理全空的行和列
            df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
            
            # 构造目标 Excel 文件路径
            dest_path = Path(dest_folder) / f"{file_path.stem}.xlsx"

            # 写入 Excel
            # engine='openpyxl' 是写入 .xlsx 格式必须的引擎。
            # 将字符串原样写入，打开 Excel 时可能会有“数字以文本形式存储”的绿色小三角，
            # 但这正是我们需要的：它保证了 100% 不会被 Excel 自动截断、转科学计数法或丢失小数尾零。
            df.to_excel(dest_path, index=False, engine='openpyxl')
            
            print("✅ 成功")
            success_count += 1

        except Exception as e:
            print(f"❌ 失败! 错误信息: {e}")

    print("-" * 30)
    print(f"🎉 处理完成！共成功转换 {success_count} 个文件。")

if __name__ == "__main__":
    # 配置命令行参数解析
    parser = argparse.ArgumentParser(description="将文件夹中的 CSV 批量安全转换为 Excel")
    parser.add_argument("src", help="源文件夹路径 (包含 CSV 文件)")
    parser.add_argument("dest", help="目标文件夹路径 (用于保存提取后的 Excel 文件)")
    
    args = parser.parse_args()
    
    convert_csv_to_excel(args.src, args.dest)