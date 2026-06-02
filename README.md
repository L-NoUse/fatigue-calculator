# 个人疲劳度分析系统（Python期末作业）

一个基于 Python 的桌面端疲劳度分析工具。软件使用 CustomTkinter 构建现代化图形界面，根据用户年龄、体重、活动水平和每日生活数据，计算个性化疲劳值，并提供恢复建议、历史记录和趋势图。

## 功能特点

- 多用户档案管理
- 根据年龄、体重、活动水平生成个人标准
- 支持睡眠、工作/学习、屏幕娱乐、饮水、运动、心情和身体状态录入
- 按运动时间和运动强度计算等效运动量
- 实时计算疲劳值和疲劳等级
- 自动生成恢复建议
- 支持问号说明和标准说明弹窗
- 保存当前用户历史记录
- 显示疲劳趋势图
- 支持打包为 Windows exe

## 技术栈

- Python
- CustomTkinter
- Matplotlib
- CSV / JSON 本地存储
- PyInstaller

## 安装依赖

建议使用项目自带虚拟环境，或重新创建虚拟环境：

```powershell
cd D:\fatigue_calculator
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

如果下载依赖较慢，可以使用国内镜像：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 30
```

## 运行程序

```powershell
cd D:\fatigue_calculator
.\.venv\Scripts\python.exe gui_app.py
```

也可以运行入口文件：

```powershell
.\.venv\Scripts\python.exe main.py
```

## 打包 exe

项目提供了打包脚本：

```powershell
cd D:\fatigue_calculator
.\build_exe.ps1
```

打包完成后，exe 会生成在：

```text
dist\FatigueCalculator.exe
```

## 数据文件

程序运行后会在项目目录生成本地数据文件：

- `users.json`：用户档案
- `fatigue_data.csv`：疲劳记录

这些文件属于本地用户数据，默认不会提交到 Git。

## 项目结构

```text
fatigue_calculator/
├── gui_app.py              # CustomTkinter 图形界面
├── main.py                 # 程序入口
├── data_manager.py         # 用户和记录读写
├── fatigue_calculator.py   # 疲劳度计算逻辑
├── standards.py            # 年龄、饮水、运动等标准定义
├── help_texts.py           # 问号说明和标准说明文本
├── chart.py                # 独立趋势图展示函数
├── requirements.txt        # Python 依赖
├── build_exe.ps1           # Windows exe 打包脚本
└── FatigueCalculator.spec  # PyInstaller 配置
```

## 疲劳值说明

疲劳值范围为 `0-100`，数值越高表示越疲劳：

- `0-30`：状态良好
- `31-60`：轻度疲劳
- `61-80`：中度疲劳
- `81-100`：严重疲劳

系统会根据睡眠、工作/学习、屏幕娱乐、饮水、运动、心情、身体状态和特殊状态综合计算。

## 注意事项

本软件用于日常疲劳状态记录和自我管理，不属于医学诊断工具。如果长期出现严重疲劳、身体不适或睡眠异常，请及时咨询专业医生。
