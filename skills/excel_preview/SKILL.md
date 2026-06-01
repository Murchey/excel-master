---
name: "excel_preview"
description: "Excel 文件可视化预览与操作技能，提供网页界面让用户可视化地进行文件比对和合并操作。遵循页面操作可视化原则，减少 Agent Token 消耗。"
---

# Excel Preview Skill (可视化预览操作技能)

## 核心目标

提供一个本地 Web 服务，让用户通过可视化网页界面进行 Excel 文件的比对和合并操作，**减少 Agent Token 消耗**，提升用户体验。

## 触发时机

- 用户需要比对两个或多个 Excel 文件的差异
- 用户需要合并多个 Excel 文件
- 用户希望可视化地选择比对列、筛选条件或合并规则
- 用户对数据操作规则不确定，需要交互式界面

## 设计原则

1. **页面操作可视化原则**：所有复杂操作通过网页界面完成，用户可以鼠标点击选择
2. **Agent 最小 Token 原则**：Agent 只需调用启动命令，具体操作由用户在网页完成
3. **交互友好原则**：提供直观的界面，减少用户学习成本

## 工具调用方式

- 脚本路径：`skills/excel_preview/scripts/preview_server.py`
- 调用命令：`python skills/excel_preview/scripts/preview_server.py <操作类型> <文件路径1> [文件路径2] [--port 端口号]`

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `操作类型` | 是 | `compare`（比对）或 `merge`（合并） |
| `文件路径1` | 是 | 第一个 Excel 文件的绝对路径 |
| `文件路径2` | 否 | 第二个 Excel 文件的绝对路径（比对时必填） |
| `--port` | 否 | Web 服务端口号，默认 5000 |

## 支持的操作模式

### 1. 文件比对模式 (compare)

**功能**：
- 并排展示两个 Excel 文件的数据
- 用户可以鼠标点击选择需要比对的列
- 支持设置比对规则（精确匹配、模糊匹配、数值范围等）
- 高亮显示差异行和差异单元格
- 导出比对结果

**使用场景**：
- 比对两个班级的成绩表
- 核对修改前后的数据差异
- 验证数据一致性

### 2. 文件合并模式 (merge)

**功能**：
- 展示所有待合并文件的数据
- 用户可以指定合并方式（纵向追加、横向合并、按列匹配合并）
- 用户可以选择需要合并的列
- 预览合并结果
- 导出合并后的文件

**使用场景**：
- 合并多个班级的成绩表
- 整合多个部门的数据
- 汇总分散的 Excel 文件

## 脚本输出格式

脚本启动后会输出 JSON 格式的启动信息：

```json
{
  "status": "success",
  "mode": "compare",
  "url": "http://localhost:5000",
  "files": ["path/to/file1.xlsx", "path/to/file2.xlsx"],
  "message": "预览服务已启动，请在浏览器中打开上述地址"
}
```

服务运行期间，用户操作结果会保存到指定位置，脚本退出时输出最终结果：

```json
{
  "status": "completed",
  "operation": "compare",
  "output_file": "path/to/comparison_result.xlsx",
  "message": "比对完成，结果已保存"
}
```

## Agent 行为约束

1. Agent 在执行比对或合并任务时，**必须询问用户**是否需要打开可视化页面操作
2. 如果用户选择可视化操作，Agent 调用此技能启动服务
3. Agent **不需要**详细询问比对规则或合并方式，这些由用户在网页界面完成
4. 服务启动后，Agent 等待用户完成操作并获取结果
5. Agent 只需传递文件路径和操作类型，**不要**传递具体的比对规则或合并配置

## 使用示例

### 比对两个文件

```powershell
python skills/excel_preview/scripts/preview_server.py compare "D:\workspace\project\temp\file1.xlsx" "D:\workspace\project\temp\file2.xlsx"
```

### 合并多个文件

```powershell
python skills/excel_preview/scripts/preview_server.py merge "D:\workspace\project\temp\file1.xlsx" "D:\workspace\project\temp\file2.xlsx" "D:\workspace\project\temp\file3.xlsx"
```

### 指定端口号

```powershell
python skills/excel_preview/scripts/preview_server.py compare "D:\workspace\project\temp\file1.xlsx" "D:\workspace\project\temp\file2.xlsx" --port 8080
```

## 工作流整合

### 1. 在定制化需求中的使用

```
1. 用户要求比对或合并 Excel 文件
2. Agent 调用 data_profile 获取数据特征（可选）
3. Agent 询问用户：是否需要打开可视化页面操作？
4. 如果用户选择可视化操作：
   a. Agent 调用 excel_preview 启动服务
   b. 用户在网页界面完成操作
   c. Agent 获取操作结果
5. 如果用户选择命令行操作：
   a. Agent 使用 excel_compare 或其他技能处理
```

### 2. 在通用化需求中的使用

```
1. 用户提供多个 Excel 文件
2. Agent 询问用户：是否需要打开可视化页面操作？
3. 如果用户选择可视化操作：
   a. Agent 调用 excel_preview 启动服务
   b. 用户在网页界面完成比对或合并
   c. Agent 获取操作结果
4. Agent 将结果保存到工作区
```

## 网页界面功能

### 比对模式界面

- **文件选择区**：左右两侧分别展示两个文件的数据表格
- **列选择区**：用户可以点击列头选择需要比对的列
- **规则设置区**：
  - 精确匹配：完全相等
  - 模糊匹配：包含关键词
  - 数值范围：在指定范围内
  - 忽略空值：跳过空单元格
- **差异高亮**：用不同颜色标记差异行和差异单元格
- **结果导出**：导出比对结果为 Excel 文件

### 合并模式界面

- **文件列表区**：展示所有待合并文件
- **合并方式选择**：
  - 纵向追加：将数据行合并
  - 横向合并：将数据列合并
  - 按列匹配合并：根据关键列匹配合并
- **列选择区**：选择需要合并的列
- **预览区**：预览合并结果
- **结果导出**：导出合并后的 Excel 文件

## 注意事项

1. 本技能仅支持 `.xlsx` 和 `.csv` 文件
2. Web 服务默认运行在 localhost，仅本机可访问
3. 服务启动后会自动打开浏览器，用户完成操作后关闭浏览器即可
4. 比对结果和合并结果会自动保存到工作区的 `excel_output` 目录
5. 如果文件较大，加载可能需要几秒钟时间
