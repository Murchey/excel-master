# excel_compare Skill

```yaml
name: "excel_compare"
description: "大量 Excel 表格的批量处理与简单比对，适用于多班级、多教师表格核对"
```

---

## 工作流说明

**重要**：在调用 `excel_compare` 之前，必须先完成以下步骤：

1. **数据探查**：调用 `data_profile` 获取数据特征
2. **需求确认**：调用 `excel_preview confirm` 打开 WEB 页面让用户确认需求
3. **获取配置**：从 `excel_preview` 获取用户确认的需求配置
4. **生成脚本**：根据用户配置调用 `excel_compare` 生成比对脚本

---

## 主要职责

`excel_compare` 负责 **批量 Excel 文件的快速比对和分析**，适用于通用化任务，包括：

1. **批量表格读取与整合**

   * 支持读取工作区内多个 Excel 文件
   * **支持递归扫描子目录**：传入目录路径时自动扫描所有子目录中的 Excel 文件
   * 自动识别列名和数据类型
   * 合并多个文件为统一 DataFrame

2. **表格比对与差异分析**

   * 单列或多列比对（如学号、姓名、课程编号等）
   * 差异标记、异常高亮
   * 简单数据处理（求和、平均、计数等）

3. **分析结果输出**

   * 将比对结果保存为 Excel 文件
   * 可选择保存到默认工作区输出目录或用户指定目录

---

## 工作区与路径

* **工作区根路径**：

  ```text
  ./workspace/<user_project_name>/
  ```
* **临时 CSV 文件**：

  ```text
  ./workspace/<user_project_name>/temp/
  ```
* **生成分析脚本保存目录**（可选）：

  ```text
  ./workspace/<user_project_name>/generated_scripts/
  ```
* **输出 Excel 文件**：

  ```text
  ./workspace/<user_project_name>/excel_output/
  ```

> `<user_project_name>` 由 agent 根据用户项目名自动替换。

---

## 使用示例

### 1. 批量读取和合并 Excel 文件

```python
from excel_compare import merge_excel_files

merged_df = merge_excel_files(
    file_list=[
        "./workspace/my_project/temp/class1.xlsx",
        "./workspace/my_project/temp/class2.xlsx"
    ],
    key_columns=["学号", "姓名"],
    output_dir="./workspace/my_project/temp"
)
print("合并完成，临时文件生成在工作区 temp 中")
```

### 2. 简单比对多个表格

```python
from excel_compare import compare_excel_files

comparison_result = compare_excel_files(
    file_list=[
        "./workspace/my_project/temp/class1.xlsx",
        "./workspace/my_project/temp/class2.xlsx"
    ],
    compare_columns=["学号", "姓名", "成绩"],
    highlight_diff=True,  # 将差异标红
    output_path="./workspace/my_project/excel_output/comparison_result.xlsx"
)
print("比对完成，结果已保存")
```

---

## 参数说明

| 参数                           | 说明                             |
| ---------------------------- | ------------------------------ |
| `file_list`                  | 待比对或合并的 Excel 文件列表（绝对路径）       |
| `key_columns`                | 合并或比对的关键列，用于匹配记录               |
| `compare_columns`            | 指定需要比对的列（可选，默认比对所有列）           |
| `highlight_diff`             | 是否在输出 Excel 中高亮显示差异（布尔值）       |
| `output_dir` / `output_path` | 输出文件路径，默认保存到工作区 `excel_output` |

---

## 注意事项

1. 确保所有待比对 Excel 文件存在且列名一致。
2. 输出目录需存在，否则 agent 会提前创建。
3. 支持多表批量处理，但单次处理表格数量过多时，建议在 agent 中分批执行以避免内存占用过高。
4. 对于列名不一致或缺失，建议先使用 `excel_scriptsGen` 做标准化处理。
