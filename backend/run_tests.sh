#!/bin/bash

# ================================================================================
# 后端 API 测试运行脚本
# ================================================================================
#
# 用法：
#   bash run_tests.sh              # 运行所有测试
#   bash run_tests.sh --cov     # 运行测试并生成覆盖率报告
#   bash run_tests.sh --verbose  # 详细输出
#
# ================================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 函数：打印带颜色的信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    print_error "uv 未安装，请先安装 uv"
    exit 1
fi

# 运行测试
echo "==================================="
echo "开始运行后端 API smoke 测试..."
echo "==================================="
echo ""

print_info "将使用 uv 运行 pytest，并默认执行 smoke 用例：auth + plan"
uv run pytest tests/test_auth.py tests/test_plan.py -v --tb=short "$@"

# 检查退出码
if [ $? -eq 0 ]; then
    print_success "Smoke 测试通过！"
else
    print_error "测试失败，退出码: $?"
    exit 1
fi

echo ""
echo "==================================="
echo "测试完成"
echo "==================================="
