import sys
import json
import argparse
import webbrowser
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__, template_folder='../templates')

data_store = {
    'mode': None,
    'files': [],
    'dataframes': [],
    'result': None
}


def load_excel_file(file_path):
    path = Path(file_path)
    if not path.exists():
        return None, f"文件不存在: {file_path}"
    
    try:
        if path.suffix.lower() == '.csv':
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='gbk')
        else:
            df = pd.read_excel(file_path)
        return df, None
    except Exception as e:
        return None, f"读取文件失败: {str(e)}"


def compare_dataframes(df1, df2, compare_columns, match_mode='exact'):
    result_rows = []
    
    if not compare_columns:
        compare_columns = list(set(df1.columns) & set(df2.columns))
    
    for idx1, row1 in df1.iterrows():
        for idx2, row2 in df2.iterrows():
            is_match = True
            diff_details = []
            
            for col in compare_columns:
                if col not in df1.columns or col not in df2.columns:
                    continue
                
                val1 = str(row1[col]) if pd.notna(row1[col]) else ''
                val2 = str(row2[col]) if pd.notna(row2[col]) else ''
                
                if match_mode == 'exact':
                    if val1 != val2:
                        is_match = False
                        diff_details.append({
                            'column': col,
                            'file1_value': val1,
                            'file2_value': val2
                        })
                elif match_mode == 'contains':
                    if val1 not in val2 and val2 not in val1:
                        is_match = False
                        diff_details.append({
                            'column': col,
                            'file1_value': val1,
                            'file2_value': val2
                        })
            
            if diff_details:
                result_rows.append({
                    'file1_row': idx1,
                    'file2_row': idx2,
                    'is_match': is_match,
                    'diffs': diff_details
                })
    
    return result_rows


def merge_dataframes(dfs, merge_type='vertical', key_columns=None, selected_columns=None):
    if not dfs:
        return None, "没有数据可合并"
    
    try:
        if selected_columns:
            dfs = [df[selected_columns] for df in dfs if all(col in df.columns for col in selected_columns)]
        
        if merge_type == 'vertical':
            result = pd.concat(dfs, ignore_index=True)
        elif merge_type == 'horizontal':
            result = pd.concat(dfs, axis=1)
        elif merge_type == 'key' and key_columns:
            result = dfs[0]
            for df in dfs[1:]:
                result = pd.merge(result, df, on=key_columns, how='outer')
        else:
            result = pd.concat(dfs, ignore_index=True)
        
        return result, None
    except Exception as e:
        return None, f"合并失败: {str(e)}"


@app.route('/')
def index():
    return render_template('index.html', mode=data_store['mode'])


@app.route('/api/data')
def get_data():
    result = {
        'mode': data_store['mode'],
        'files': []
    }
    
    for i, (fpath, df) in enumerate(zip(data_store['files'], data_store['dataframes'])):
        result['files'].append({
            'index': i,
            'name': Path(fpath).name,
            'columns': df.columns.tolist(),
            'rows': len(df),
            'data': df.head(100).to_dict('records')
        })
    
    return jsonify(result)


@app.route('/api/compare', methods=['POST'])
def compare():
    data = request.json
    columns = data.get('columns', [])
    match_mode = data.get('match_mode', 'exact')
    
    if len(data_store['dataframes']) < 2:
        return jsonify({'status': 'error', 'message': '需要两个文件进行比对'})
    
    df1 = data_store['dataframes'][0]
    df2 = data_store['dataframes'][1]
    
    results = compare_dataframes(df1, df2, columns, match_mode)
    
    diff_count = sum(1 for r in results if not r['is_match'])
    
    return jsonify({
        'status': 'success',
        'total_compared': len(results),
        'diff_count': diff_count,
        'results': results[:100]
    })


@app.route('/api/merge', methods=['POST'])
def merge():
    data = request.json
    merge_type = data.get('merge_type', 'vertical')
    key_columns = data.get('key_columns', [])
    selected_columns = data.get('selected_columns', [])
    
    result_df, error = merge_dataframes(
        data_store['dataframes'],
        merge_type,
        key_columns if key_columns else None,
        selected_columns if selected_columns else None
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error})
    
    data_store['result'] = result_df
    
    return jsonify({
        'status': 'success',
        'rows': len(result_df),
        'columns': result_df.columns.tolist(),
        'preview': result_df.head(50).to_dict('records')
    })


@app.route('/api/export', methods=['POST'])
def export():
    data = request.json
    output_path = data.get('output_path', '')
    operation = data.get('operation', '')
    
    if not output_path:
        return jsonify({'status': 'error', 'message': '未指定输出路径'})
    
    try:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        if operation == 'compare':
            df1 = data_store['dataframes'][0]
            df2 = data_store['dataframes'][1]
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df1.to_excel(writer, sheet_name='文件1', index=False)
                df2.to_excel(writer, sheet_name='文件2', index=False)
        elif operation == 'merge' and data_store['result'] is not None:
            data_store['result'].to_excel(output_path, index=False)
        else:
            return jsonify({'status': 'error', 'message': '没有可导出的数据'})
        
        return jsonify({
            'status': 'success',
            'output_file': str(output),
            'message': f'结果已保存到: {output}'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'导出失败: {str(e)}'})


@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return jsonify({'status': 'success', 'message': '服务已关闭'})


def open_browser(port):
    import time
    time.sleep(1.5)
    webbrowser.open(f'http://localhost:{port}')


def main():
    parser = argparse.ArgumentParser(description='Excel 文件可视化预览与操作')
    parser.add_argument('mode', choices=['compare', 'merge'], help='操作类型：compare（比对）或 merge（合并）')
    parser.add_argument('files', nargs='+', help='Excel 文件路径')
    parser.add_argument('--port', type=int, default=5000, help='Web 服务端口号')
    
    args = parser.parse_args()
    
    if args.mode == 'compare' and len(args.files) < 2:
        print(json.dumps({
            'status': 'error',
            'message': '比对模式需要至少两个文件'
        }, ensure_ascii=False))
        sys.exit(1)
    
    data_store['mode'] = args.mode
    data_store['files'] = args.files
    data_store['dataframes'] = []
    
    for fpath in args.files:
        df, error = load_excel_file(fpath)
        if error:
            print(json.dumps({
                'status': 'error',
                'message': error
            }, ensure_ascii=False))
            sys.exit(1)
        data_store['dataframes'].append(df)
    
    output_dir = None
    if args.files:
        first_file = Path(args.files[0])
        output_dir = first_file.parent.parent / 'excel_output'
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print(json.dumps({
        'status': 'success',
        'mode': args.mode,
        'url': f'http://localhost:{args.port}',
        'files': args.files,
        'output_dir': str(output_dir) if output_dir else None,
        'message': f'预览服务已启动，请在浏览器中打开 http://localhost:{args.port}'
    }, ensure_ascii=False))
    
    threading.Thread(target=open_browser, args=(args.port,), daemon=True).start()
    
    app.run(host='localhost', port=args.port, debug=False)


if __name__ == '__main__':
    main()
