# Backend Build

Chinese version: [BUILD.zh-CN.md](BUILD.zh-CN.md)

run.py is the local reload-enabled entry. main.py is the reload-disabled source/package entry. build.py is an optional PyInstaller one-directory build and must be executed on the target OS/CPU.

~~~bash
uv sync --frozen
uv run python -m py_compile settings.py main.py run.py build.py
uv run python build.py
~~~

The package contains source/runtime resources and a sanitized .env.example; it never copies real .env, customer inputs, database dumps or logs. Database migration and bootstrap remain explicit operator actions in a separately approved environment task.
