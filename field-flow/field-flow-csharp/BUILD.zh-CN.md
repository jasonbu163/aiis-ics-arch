# 构建与运行

[English](BUILD.md)

目标验证宿主为 Windows 10 Enterprise LTSC 2021 x64。按所在环境的规则准备锁定的 .NET SDK 10.0.403，并记录 Windows 的具体版别和 build。该候选需要在 Windows 原生完成构建、测试和复制目录运行，才能作为 Windows 交付。

为 CLI home、包、构建产物和合成状态创建新的任务专用目录。在本工程目录打开 PowerShell：

```powershell
$FF_ROOT = Join-Path $env:TEMP ("ff-csharp-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $FF_ROOT | Out-Null
Write-Output $FF_ROOT
$env:DOTNET_CLI_HOME = Join-Path $FF_ROOT 'cli'
$env:NUGET_PACKAGES = Join-Path $FF_ROOT 'packages'
$env:NUGET_HTTP_CACHE_PATH = Join-Path $FF_ROOT 'http-cache'
$env:DOTNET_GENERATE_ASPNET_CERTIFICATE = 'false'
$env:DOTNET_ADD_GLOBAL_TOOLS_TO_PATH = 'false'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:MSBUILDDISABLENODEREUSE = '1'
$FF_BUILD = Join-Path $FF_ROOT 'build'
$FF_TARGET = @('-p:RuntimeIdentifier=win-x64', '-p:SelfContained=true', '-p:RuntimeFrameworkVersion=10.0.14', "-p:FFBuildRoot=$FF_BUILD")
$FF_PROJECTS = @('src/FieldFlow/FieldFlow.csproj', 'tests/FieldFlow.Fixture/FieldFlow.Fixture.csproj', 'tests/FieldFlow.Tests/FieldFlow.Tests.csproj')
foreach ($project in $FF_PROJECTS) {
    dotnet restore $project --locked-mode --configfile NuGet.Config @FF_TARGET
    if ($LASTEXITCODE -ne 0) { throw "restore failed $LASTEXITCODE" }
}
foreach ($project in $FF_PROJECTS) {
    dotnet build $project -c Release --no-restore --disable-build-servers @FF_TARGET
    if ($LASTEXITCODE -ne 0) { throw "build failed $LASTEXITCODE" }
}
dotnet test tests/FieldFlow.Tests/FieldFlow.Tests.csproj -c Release --no-build --no-restore @FF_TARGET
if ($LASTEXITCODE -ne 0) { throw "test failed $LASTEXITCODE" }
dotnet publish src/FieldFlow/FieldFlow.csproj -c Release --no-restore -p:PublishSingleFile=false -p:PublishTrimmed=false -p:PublishAot=false -o "$FF_ROOT/publish" @FF_TARGET
if ($LASTEXITCODE -ne 0) { throw "publish failed $LASTEXITCODE" }
```

完整保留 publish 目录中的 .NET runtime 和 SQLite native 文件。状态目录应新建在 publish 目录之外。

夹具是测试程序，不包含在发布目录中。在另一个 PowerShell 窗口设置与构建窗口相同的 `$FF_ROOT`，然后启动夹具：

```powershell
# 将 $FF_ROOT 设置为构建窗口中打印的同一个目录。
$FF_FIXTURE = Join-Path $FF_ROOT 'build/bin/FieldFlow.Fixture/Release/net10.0/win-x64/FieldFlow.Fixture.exe'
& $FF_FIXTURE "--report=$FF_ROOT/report.json"
```

等待 `{"ready":true}`，在产品窗口执行：

```powershell
$FF_COPY = Join-Path $FF_ROOT 'copied-app'
Copy-Item -Path "$FF_ROOT/publish" -Destination $FF_COPY -Recurse
$FF_CONFIG = (Resolve-Path "$FF_COPY/config/demo01.yaml").Path
$FF_EMPTY = Join-Path $FF_ROOT 'empty-cwd'
New-Item -ItemType Directory -Path $FF_EMPTY | Out-Null
$FF_APP = Join-Path $FF_COPY 'FieldFlow.exe'
Push-Location $FF_EMPTY
& $FF_APP --help --lang zh-CN
& $FF_APP config validate --config $FF_CONFIG
& $FF_APP state init --synthetic --mode dry_run --state-dir "$FF_ROOT/dry-state" --instance-id ff-csharp-demo01
& $FF_APP run --config $FF_CONFIG --state-dir "$FF_ROOT/dry-state"
# 按 Ctrl+C，等待进程退出。
& $FF_APP state inspect --state-dir "$FF_ROOT/dry-state"
Pop-Location
```

合成写入案例需用 `--mode execute` 创建另一个新状态目录，并在 `run` 加上 `--execute`。停止产品并等待退出后检查状态，再停止夹具并等待退出。夹具只监听本机回环端口 34102 和 34880。出现 `unknown` 后，应先核实结果再处理冲突写入。

Windows 发布及夹具的精确路径需要在目标宿主验证。当前候选范围不包括服务安装、真实设备连接或现场部署。
