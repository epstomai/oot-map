# 塞尔达传说：时之笛 本地收集进度管理器 (OoT Remake Collection & Live Sync Tracker)

参照 Nintendúo 互动地图结构，结合 Switch 2 Hookshot 本地 `progress.sav` / `caption.sav` 与官方多语言资源（`CNzh` / `JPja` / `USen`）构建的本地 WebUI 收集进度管理器。

## 功能特性

- **184 项全收集精准存档解析**：自动解析 `progress.sav`，覆盖 **100 只黄金蜘蛛**、**36 块心之碎片**、**8 个心之容器**、**10 处魔法豆**、**6 位大妖精**、**5 个空瓶** 及 **19 处重制版新增妖精的思绪**。
- **实时位置同步**：
  - **实时内存模式**（`hookshot.exe` 或兼容模拟器运行时自动通过只读 `ReadProcessMemory` 绑定游戏内坐标、面向角度与场景）。
  - **存档监听模式**（实时监听 `progress.sav` 文件变更并即时推送到前端，支持自动跟随最新存档槽位与主角当前所在地区/楼层）。
- **手动选择存档位置**：默认指向 `F:\games\SwitchGames\hookshot\game\user\save`，支持在界面内手动输入或通过目录浏览器选择任意存档文件夹与槽位（并显示 `caption.sav` 实时缩略图）。
- **日中英三语切换**：完整支持 **简体中文 / 日本語 / English**（地名同步取自游戏官方 `Location.msbt`），每项收集物均附带 **前置条件、时期/昼夜标签、收集提示与详细攻略**。

## 启动方式

双击 `run.bat`（或运行 `run.ps1`），程序会默认使用 **`18765`** 端口并在被占用时自动顺延到下一个可用端口，同时自动打开浏览器：

```powershell
python -m backend.app
```

也可以手动指定端口或关闭自动打开浏览器：

```powershell
python -m backend.app --port 18765 --no-browser
```

默认访问地址：<http://127.0.0.1:18765>（若端口顺延，请以控制台打印的 URL 为准）。

