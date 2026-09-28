# 18.06 线性代数学习室

本地学习网站，按 `../action-roadmap.md` 的 14 次学习任务展开。现在同一个入口同时提供：

- 学习路线、数学公式、清单、阅读材料与浏览器 Python / NumPy 练习。
- 嵌入式 JupyterLab：打开原项目的 Julia notebook，编辑代码与 Markdown，运行单元格，并保存到磁盘。

**网站仅在本机运行，不发布线上服务。源码随课程仓库保存；登录信息、个人运行环境和缓存不提交到 Git。**

## 首次安装（从仓库克隆后）

准备 Python 3.13 和 Julia 1.12.5，然后在仓库根目录执行：

```sh
cd lab
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
./scripts/install-julia-packages.sh
.venv/bin/python scripts/cache_python_runtime.py
./start.sh
```

Julia 在 PATH 中时安装脚本会自动找到它；否则用 `JULIA_BIN=/完整路径/bin/julia ./scripts/install-julia-packages.sh`。依赖首次下载需要联网。Python 浏览器缓存步骤可跳过，此时首次运行 Python 练习需要联网。

启动脚本会从仓库中的 roadmap、README 和 `notes/` 生成网页内容与阅读快照；这些生成文件不重复提交。`.venv/`、`.runtime/` 和登录 token 也不提交，克隆后需在本机安装。

## 启动

在此目录运行：

```sh
./start.sh
```

入口为 <http://127.0.0.1:4186/learn/>。首次访问使用启动日志中的带 token 登录链接；登录后在同一浏览器访问普通入口即可。默认尝试打开浏览器。需要换端口时使用 `./start.sh 4187`。按 Ctrl+C 停止 Jupyter 及其内核。

网站只监听 `127.0.0.1`。Jupyter 的登录校验、同源限制和 XSRF 防护保持启用；没有将服务开放到局域网或外网。网站与 JupyterLab 同源，不需要粘贴 token 或关闭浏览器安全设置。

## 编辑和运行原 notebook

1. 点击网页顶部的 **「原始 notebook · 编辑运行」**，从列表选择文件；也可以在「课程材料」打开原 notebook 后点击 **「编辑并运行原文件」**。
2. 在编辑器中选中单元格并修改。内核请选择 **Julia 18.06 1.12**；原文件中旧的 `julia-0.6`、`julia-1.7` 等内核标识并不意味着本机安装了那些旧版本。
3. 点击 **「运行选中单元格」**，或在编辑器中按 **Shift+Enter**。需要终止长时间运算时点击 **「中断运行」**，也可以在 JupyterLab 的 Kernel 菜单重启内核。
4. 点击 **「保存当前文档」**，或按 **Ctrl / ⌘ + S**；JupyterLab 也会定时自动保存。
5. 点击「返回学习路线」仅隐藏编辑器，不关闭已打开的 notebook。再次进入时继续使用现有标签和内核。可用「独立窗口」打开完整 JupyterLab。

Jupyter 的文件根目录为 `../`。从网站列表打开的文件是 **`../notes/*.ipynb` 原文件**，不是 `dist/materials/` 中的阅读快照。运行结果和 Markdown 单元格可随 notebook 一起保存。保存修改会影响原文件；需要保留独立练习版本时，可在 JupyterLab 中使用另存为 / Duplicate。

原材料阅读视图连接 Jupyter 后会读取磁盘中的最新内容，下载按钮也下载当前原文件。

## 总结保存在哪里

- 原 notebook 内的 **Markdown 单元格**：随 notebook 保存到真实 `.ipynb` 文件，关闭浏览器后仍存在。
- 学习路线页面的 **「我的理解与问题」**、勾选进度及 Python 编辑器内容：仍保存在当前浏览器的 localStorage；没有自动迁移或覆盖原有记录。
- 「下载 .ipynb」可导出当前 Python 练习、讲解和浏览器中的总结。

## Julia 环境与兼容性

本项目使用官方 **Julia 1.12.5**、IJulia 和隔离的 Julia 项目环境 `julia/`。原 notebook 涵盖 Julia 0.5–1.12 多个时期，安装内核不等于所有历史语法、依赖和外部数据源都自动兼容。

已安装常用包：IJulia、PyPlot、Plots、Interact、Symbolics、SymPy、Images、FileIO、ImageMagick、QuadGK、Polynomials、FFTW、ForwardDiff、BenchmarkTools、KrylovKit、IterativeSolvers。线性代数、统计和稀疏矩阵的标准库随 Julia 提供。

为避免 Julia 1.12 多线程与课程 PyPlot/PyCall 的冲突，内核固定使用 `--threads=1,0`。PyPlot 复用本项目 Python 环境中的 Matplotlib，以无界面的 Agg 后端输出图像。

已知限制：

- 旧版 `Interact` / WebIO 的 JupyterLab 前端扩展与 JupyterLab 4 不兼容，目前不启用这些滑块组件。普通 Julia 单元格及静态绘图可执行。
- 旧示例中的 `eig`、`eye`、`linspace`、`Flux.Data.MNIST` 等接口可能需要更新；不能保证任意旧 notebook 都无需修改即可整本运行。
- 部分高级图论、优化和机器学习案例依赖额外包，可执行 `./scripts/install-julia-packages.sh --extras` 安装。它不会自动改写课程代码。
- 首次导入某些 Julia 包可能需要预编译，等待时间会比后续运行更长。

## 环境位置与复现

- `.venv/`：本地 Python / JupyterLab / Jupyter Server。
- `.runtime/julia-1.12.5/`：官方 Julia 运行时；下载记录及 SHA256 保存在 `.runtime/julia-version.json`。
- `.runtime/julia-depot/`：Julia 包与编译缓存。
- `.runtime/jupyter-data/kernels/julia-1806/`：此项目专用 Julia 内核。
- `.runtime/jupyter-token` 与 `.runtime/jupyter-runtime/`：本地登录信息及运行状态，已加入忽略规则，不应分享。
- `julia/Project.toml`、`julia/Manifest.toml`：Julia 依赖锁定。
- `requirements.txt`、`requirements.lock.txt`：Python 依赖与当前安装版本。

如需重新安装 Python 环境：

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.lock.txt
./scripts/install-julia-packages.sh
```

Julia 安装脚本优先使用 `JULIA_BIN`，其次复用本地已下载运行时，再从 PATH 查找 Julia。迁移到其他电脑时重新运行安装脚本注册内核；不要复制包含绝对路径的旧 kernelspec 或 Python 虚拟环境。

## 浏览器 Python 模式

Python 练习仍通过独立 Web Worker / Pyodide 0.27.7 运行。优先使用完整的本地缓存；缓存不完整时仍从 CDN 联网加载。每次运行使用新的变量空间。可显示文本、异常和 Matplotlib 静态图像；停止会终止 worker，180 秒超时自动停止。

缓存位于 `.runtime/pyodide/`，可运行 `python scripts/cache_python_runtime.py` 下载 NumPy、Matplotlib 和运行文件。全部下载并校验成功后才生成 `ready.json`，避免启用不完整缓存。其他未缓存的库不保证离线可用；退回纯静态服务器时会使用原 CDN。

它不等同于 Julia/Jupyter 内核，不支持服务器进程、GPU 或交互式 `input()`。原 Julia notebook 请使用新工作台运行。

## 维护与检查

- `scripts/generate_content.py` 从原路线、摘要与 notebook 生成课程内容和阅读快照。改写的 Python 练习在 `scripts/lessons.py`。
- `scripts/serve.py` 启动本地 Jupyter；`scripts/lab_extension.py` 提供经过认证的课程页面与原文件列表。
- `dist/notebook-bridge.js` 将学习网站连接到同源 JupyterLab。
- `tests/julia_notebooks.py` 在内存中执行原始 Gram–Schmidt、QR、Conditioning 示例，并检查原文件未改变。
- `tests/jupyter_browser_check.py` 使用临时 notebook 验证网页编辑、执行、保存与重新打开；结束后清理临时文件。
- `tests/browser_check.py` 保留原 Python 学习网站的交互测试；需要 Playwright。

实现依据：[Jupyter Server 扩展文档](https://jupyter-server.readthedocs.io/en/latest/developers/extensions.html)、[IJulia 安装与自定义内核](https://ijulia.org/stable/manual/installation/)、[Julia 官方下载](https://julialang.org/downloads/)。
