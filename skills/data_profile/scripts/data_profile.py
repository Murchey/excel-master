import sys
import json
import argparse
import pandas as pd
from pathlib import Path

def profile_excel(file_path):
    path = Path(file_path)
    
    # 防呆校验
    if not path.exists():
        return json.dumps({"status": "error", "message": f"文件不存在: {file_path}"}, ensure_ascii=False)
    
    if path.suffix.lower() not in ['.xlsx', '.xls', '.csv']:
        return json.dumps({"status": "error", "message": "仅支持 .xlsx, .xls 或 .csv 文件"}, ensure_ascii=False)

    try:
        # 读取数据 (默认读取第一页，如果是CSV按字符串读取防精度丢失)
        if path.suffix.lower() == '.csv':
            try:
                df = pd.read_csv(file_path, dtype=str, encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, dtype=str, encoding='gbk')
        else:
            df = pd.read_excel(file_path, dtype=str)

        # 构造探查报告字典
        profile_result = {
            "status": "success",
            "file_name": path.name,
            "total_rows": len(df),
            "total_cols": len(df.columns),
            "columns": {}
        }

        # 遍历列提取特征
        for col in df.columns:
            col_data = df[col]
            
            # 提取非空样本 (最多3个)
            valid_samples = col_data.dropna().astype(str).unique()
            samples = valid_samples[:3].tolist() if len(valid_samples) > 0 else []

            profile_result["columns"][col] = {
                "type": str(col_data.dtype),  # 强转str后通常是 'object'
                "null_count": int(col_data.isna().sum()),
                "unique_count": int(col_data.nunique(dropna=True)),
                "sample_values": samples
            }

        # 以 JSON 格式输出，方便大模型精准截取和反序列化
        return json.dumps(profile_result, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"解析失败: {str(e)}"}, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="提取表格数据特征并输出 JSON")
    parser.add_argument("file_path", help="要探查的 Excel 或 CSV 文件路径")
    
    args = parser.parse_args()
    
    # 直接 print 结果，Trae 会捕获 stdout 标准输出
    print(profile_excel(args.file_path))