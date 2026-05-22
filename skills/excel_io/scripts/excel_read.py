import os
import sys
import argparse
import pandas as pd
from pathlib import Path

def convert_excel_to_csv(src_folder, dest_folder):
    # 检查源文件夹是否存在
    if not os.path.exists(src_folder):
        print(f"❌ 错误: 源文件夹 '{src_folder}' 不存在！")
        sys.exit(1)

    # 如果目标文件夹不存在，则自动创建
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
        print(f"📁 已创建目标文件夹: '{dest_folder}'")

    # 获取所有 excel 文件
    src_path = Path(src_folder)
    excel_files = [f for f in src_path.iterdir() if f.suffix.lower() in ['.xlsx', '.xls']]

    if not excel_files:
        print(f"⚠️ 在 '{src_folder}' 中没有找到 Excel 文件 (.xlsx 或 .xls)。")
        return

    success_count = 0

    for file_path in excel_files:
        print(f"⏳ 正在处理: {file_path.name} ...", end=" ")
        try:
            # 读取 Excel。
            # dtype=str 强制所有数据按字符串读取，防止金额转科学计数法、防止小数精度丢失或自动补零。
            # sheet_name=None 会读取所有的工作表 (Sheet)。
            excel_data = pd.read_excel(file_path, sheet_name=None, dtype=str)

            for sheet_name, df in excel_data.items():
                # 清理空数据：如果一整行或一整列全是 NaN，则删除（可选，视具体业务需求而定）
                df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
                
                # 构造 CSV 文件名。如果有多个 Sheet，格式为: 文件名_Sheet名.csv
                # 如果只有一个 Sheet，也可以直接叫 文件名.csv
                if len(excel_data) == 1:
                    csv_filename = f"{file_path.stem}.csv"
                else:
                    csv_filename = f"{file_path.stem}_{sheet_name}.csv"
                
                dest_path = Path(dest_folder) / csv_filename

                # 写入 CSV。
                # encoding='utf-8-sig' 确保 Windows Excel 打开时不乱码（带 BOM 头）。
                df.to_csv(dest_path, index=False, encoding='utf-8-sig')
            
            print("✅ 成功")
            success_count += 1

        except Exception as e:
            print(f"❌ 失败! 错误信息: {e}")

    print("-" * 30)
    print(f"🎉 处理完成！共成功转换 {success_count} 个文件。")

if __name__ == "__main__":
    # 配置命令行参数解析
    parser = argparse.ArgumentParser(description="将文件夹中的 Excel 批量安全转换为 CSV")
    parser.add_argument("src", help="源文件夹路径 (包含 Excel 文件)")
    parser.add_argument("dest", help="目标文件夹路径 (用于保存提取后的 CSV 文件)")
    
    args = parser.parse_args()
    
    convert_excel_to_csv(args.src, args.dest)