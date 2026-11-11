# Build and run

[中文](BUILD.zh-CN.md)

The target validation host is Windows 10 Enterprise LTSC 2021 x64. Install or unpack the pinned .NET SDK 10.0.403 according to your environment policy. Record the exact Windows edition and build. This candidate must pass native Windows build, tests and copied-directory execution before being treated as a Windows delivery.

Use a new task-owned directory for CLI home, packages, build output and synthetic state. In PowerShell, from this project directory:

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

Keep the entire publish folder together, including its .NET runtime files and SQLite native assets. Use a new state directory outside the publish folder.

The fixture is a test executable, not part of the publish folder. Copy the value of `$FF_ROOT` into a separate PowerShell window and start the fixture there:

```powershell
# Assign $FF_ROOT to the same directory printed by the build window.
$FF_FIXTURE = Join-Path $FF_ROOT 'build/bin/FieldFlow.Fixture/Release/net10.0/win-x64/FieldFlow.Fixture.exe'
& $FF_FIXTURE "--report=$FF_ROOT/report.json"
```

Wait for `{"ready":true}`. In the product window:

```powershell
$FF_COPY = Join-Path $FF_ROOT 'copied-app'
Copy-Item -Path "$FF_ROOT/publish" -Destination $FF_COPY -Recurse
$FF_CONFIG = (Resolve-Path "$FF_COPY/config/demo01.yaml").Path
$FF_EMPTY = Join-Path $FF_ROOT 'empty-cwd'
New-Item -ItemType Directory -Path $FF_EMPTY | Out-Null
$FF_APP = Join-Path $FF_COPY 'FieldFlow.exe'
Push-Location $FF_EMPTY
& $FF_APP --help --lang en-US
& $FF_APP config validate --config $FF_CONFIG
& $FF_APP state init --synthetic --mode dry_run --state-dir "$FF_ROOT/dry-state" --instance-id ff-csharp-demo01
& $FF_APP run --config $FF_CONFIG --state-dir "$FF_ROOT/dry-state"
# Press Ctrl+C and wait for the process to exit.
& $FF_APP state inspect --state-dir "$FF_ROOT/dry-state"
Pop-Location
```

For the synthetic write example create another new state directory with `--mode execute` and add `--execute` to `run`. Stop and wait for the product, inspect the state, then stop and wait for the fixture. The fixture only listens on loopback ports 34102 and 34880. `unknown` requires reconciliation before any conflicting write.

The Windows publish and the exact fixture paths must be checked on the target host. No service installation, real device connection or field deployment is included in this candidate.
