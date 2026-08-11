# 后端构建

English version: [BUILD.md](BUILD.md)

run.py 是本地 reload 开发入口，main.py 是禁用 reload 的源码/package 入口。build.py 是可选的 PyInstaller one-directory 构建，必须在目标 OS/CPU 上执行。

~~~bash
uv sync --frozen
uv run python -m py_compile settings.py main.py run.py build.py
uv run python build.py
~~~

package 只包含源码/运行资源和脱敏的 .env.example，不会复制真实 .env、客户输入、数据库 dump 或日志。数据库迁移和 bootstrap 仍须在单独获批的环境任务中由运维显式执行。
