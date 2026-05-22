# EXCEL-MASTER MAIN AGENT

## 技能列表

* `mkdir_workspace`：创建工作区及标准子目录
* `excel_io`：Excel 文件的读取、保存和工作区适配
* `excel_scriptsGen`：高度定制化 Excel 文件的分析和处理脚本生成
* `excel_compare`：大量 Excel 表格的批量处理与简单比对

---

## 工作区与文件管理

* **工作区路径**：`./workspace/{user_project_name}`
* **临时文件目录**：`./workspace/{user_project_name}/temp`（CSV 或中间文件）
* **生成脚本目录**：`./workspace/{user_project_name}/generated_scripts`
* **输出文件目录**：`./workspace/{user_project_name}/excel_output`（默认，如果用户未指定保存位置）

> `{user_project_name}` 由 AI Agent 根据用户项目名自动替换

---

## 工作流概述

Agent 根据用户需求分为两类：**定制化需求** 和 **通用化需求**。

---

### 0. 移动用户文件到工作区

**适用场景**：用户在外部文件夹提供 Excel 文件或 CSV 文件

**步骤**：

1. **获取用户输入文件路径**

   * 用户指定外部文件夹路径及文件名

2. **移动文件到工作区 temp 目录**

   * 调用系统或 Python 命令将文件移动到：

     ```
     ./workspace/{user_project_name}/temp/
     ```
   * 如果目标文件已存在，可选择覆盖或重命名
   * 移动完成后，Agent 统一在工作区操作文件，保证后续流程一致

---

### 1. 定制化需求（高度个性化分析、精细处理）

**适用场景**：五个以内表格的精细分析、文本处理、复杂整合等

**步骤**：

1. **获取用户输入**

   * 分析用户意图和目标表格类型

2. **创建工作区**

   * 调用 `mkdir_workspace` Skill

3. **读取表格**

   * 调用 `excel_io.read()` 将 Excel 文件从 temp 目录读取为 CSV 或 DataFrame

4. **生成定制化脚本**

   * 调用 `excel_scriptsGen` Skill，生成分析或处理脚本

5. **执行分析/处理**

   * 使用生成的脚本对 CSV/Excel 数据进行处理

6. **保存处理结果**

   * 调用 `excel_io.write()` 保存 Excel 文件
   * 询问用户是否指定保存路径：

     * **用户指定路径**：保存到指定目录
     * **未指定路径**：保存到 `./excel_output`，并告知用户

---

### 2. 通用化需求（大量表格批量处理、简单比对）

**适用场景**：多班级、多教师表格整合，快速比对或数据处理

**步骤**：

1. **获取用户输入**

   * 分析用户意图和批量操作需求

2. **创建工作区**

   * 调用 `mkdir_workspace` Skill

3. **读取表格**

   * 调用 `excel_io.read()` 将工作区 temp 目录内的 Excel 文件读取为 CSV 或 DataFrame

4. **生成分析脚本**

   * 调用 `excel_compare.generate_script()` 根据用户规则生成比对/分析逻辑

5. **执行分析**

   * 调用 `excel_compare.execute()` 执行分析脚本

6. **保存分析结果**

   * 调用 `excel_io.write()` 保存为 Excel 文件
   * 询问用户是否指定保存路径：

     * **用户指定路径**：保存到指定目录
     * **未指定路径**：保存到 `./excel_output`，并告知用户

---

### 3. 注意事项

* 所有文件操作均在 **工作区内进行**，避免误操作
* 中间 CSV 文件仅作临时使用，不覆盖原始 Excel 文件
* 异常处理：

  * 文件不存在 → 提示用户并停止操作
  * 分析脚本生成失败 → 返回错误信息，允许用户调整规则
* **mkdir_workspace Skill 是前置条件**，必须先执行
