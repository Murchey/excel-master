# Excel-Master

**Excel-Master** 是一个面向学校、公司、单位等场合的 AI 助手，支持 Excel 文件的批量处理、定制化分析、表格核对和排版优化。系统通过 AI Agent 调度 Skill，实现自动化处理流程。

本项目不提供API，请自行部署。国内环境推荐trae cn, qwen code等，如需高度隐私化数据安全，请本地部署ollama服务，调用本地API。

---

## 目录结构

```
Excel-Master/
├─ skills/
│  ├─ mkdir_workspace/
│  ├─ excel_io/
│  ├─ excel_scriptsGen/
│  ├─ excel_compare/
│  ├─ data_profile/
│  ├─ excel_compat/
│  └─ excel_chart/
├─ workspace/                     # 用户工作区，运行时自动生成
├─ install_requirements.bat        # 安装依赖
├─ requirements.txt
├─ agent.md                        # AI Agent 工作流定义
└─ README.md
```

---

## 部署指南

### 1. 安装 Python

确保系统已安装 Python 3.9+，并加入环境变量。

### 2. 安装依赖

将 `install_requirements.bat` 与 `requirements.txt` 放在同级目录（项目根目录），双击或通过 CMD 执行：

```cmd
install_requirements.bat
```

* 使用阿里云 PyPI 镜像加速安装
* 默认会安装 `pandas`、`openpyxl`、`xlwings` 等 Excel 操作库

### 3. 初始化工作区

AI Agent 在执行任务前，会调用 `mkdir_workspace` Skill 自动创建以下目录：

```
./workspace/<user_project_name>/
├─ temp/                  # 临时 CSV 或中间文件
├─ generated_scripts/     # 定制化处理脚本
└─ excel_output/          # 输出 Excel 文件或报告
```

> `<user_project_name>` 由 Agent 根据用户项目自动生成或指定。

---

## 使用指南

### 1. 提供用户文件

将待处理 Excel 或 CSV 文件放在任意文件夹中。
在任务开始时，Agent 会将这些文件 **移动到工作区的 temp 目录**，保证后续操作统一管理。

### 2. 定制化需求

适用于少量表格的精细分析，例如文本处理、复杂整合或格式排版。

**操作流程**：

1. AI Agent 获取用户意图
2. 调用 `mkdir_workspace` 创建工作区
3. 调用 `excel_io.read()` 读取文件
4. 调用 `excel_scriptsGen` 生成定制化处理脚本
5. 执行脚本，处理数据或调整格式
6. 调用 `excel_io.write()` 保存结果，默认输出到 `excel_output`，可指定路径

### 3. 通用化需求

适用于大量表格的批量处理、简单核对或比对。

**操作流程**：

1. AI Agent 获取用户意图
2. 调用 `mkdir_workspace` 创建工作区
3. 调用 `excel_io.read()` 读取工作区 temp 目录内的文件
4. 调用 `excel_compare` 生成分析脚本并执行比对
5. 调用 `excel_io.write()` 保存比对结果

### 4. 数据图表生成

适用于数据可视化展示，帮助用户更直观地理解数据特征和趋势。

**支持图表类型**：
- **柱状图**：比较不同类别的数值大小（如各班级成绩对比）
- **折线图**：展示数据随时间或顺序的变化趋势（如成绩变化）
- **饼图**：展示各部分占整体的比例关系（如成绩等级分布）
- **散点图**：展示两个变量之间的关系（如数学与物理成绩关系）

**操作流程**：

1. AI Agent 调用 `data_profile` 获取数据特征
2. **询问用户**需要生成什么类型的图表
3. **询问用户**需要展示的数据范围（哪些列、哪些行、筛选条件）
4. 调用 `excel_chart` 生成图表
5. 图表保存到工作区 `excel_output` 目录
6. 向用户展示图表并询问反馈

**数据范围示例**：
- 展示数学和物理成绩：`{"columns": ["数学", "物理"]}`
- 筛选一班的数据：`{"filter": {"班级": "一班"}}`
- 展示前10行数据：`{"rows": {"start": 0, "end": 10}}`

### 5. 注意事项

* 所有操作均在 **工作区内执行**
* 临时 CSV 文件仅作中间使用，不覆盖原始文件
* `mkdir_workspace` Skill 必须先执行，保证工作区完整
* 异常处理：

  * 文件不存在 → 提示并停止
  * 分析脚本生成失败 → 返回错误信息

---

## 示例

*请注意，对AI描述的时候要求需求清晰明了。*

用户：帮我处理【原始资料文件夹路径】的学生成绩，要求得出优秀学生名单（80分以上的）

AI Agent：

1. 获取用户意图：

   * 批量处理多班级、多教师表格
   * 高度定制化数据处理与 Excel 排版

2. 创建工作区：

   * 调用 `mkdir_workspace` Skill

3. 读取文件：

   * 调用 `excel_io.read()` 读取工作区 temp 目录内的 Excel 文件


## 支持

* 批量处理多班级、多教师表格
* 高度定制化数据处理与 Excel 排版
* 数据可视化图表生成（柱状图、折线图、饼图、散点图）
* 旧版 .xls 文件自动转换为 .xlsx 格式
* 阿里云 PyPI 镜像加速安装依赖