# MAflood 项目说明文档

## 1. 项目概述与核心功能说明

MAflood 是一个基于 AFL (American Fuzzy Lop) 框架的改进型模糊测试工具，专注于提高多线程模糊测试的性能和效率。

### 核心功能：

- **多线程并行模糊测试**：支持多个线程同时进行模糊测试，充分利用多核 CPU 资源
- **双剪枝模型**：通过优化测试用例生成和选择，减少冗余测试，提高测试效率
- **并行同步机制**：线程间共享测试用例，避免重复工作
- **覆盖引导遗传算法**：基于代码覆盖率指导测试用例生成，提高崩溃发现率
- **多种测试模式**：支持源码插桩和二进制插桩（QEMU 模式）

### 技术创新点：

- **双剪枝模型**：通过静态和动态分析相结合的方式，减少无效测试用例的生成
- **优化的线程同步**：减少线程间通信开销，提高并行效率
- **自适应测试策略**：根据目标程序特性自动调整测试参数

## 2. 环境依赖清单及版本要求

### 系统要求：
- Linux 操作系统（推荐 Ubuntu 18.04 或更高版本）
- 至少 4GB 内存
- 至少 50GB 磁盘空间
- 多核 CPU（推荐 4 核或更多）

### 软件依赖：
- GCC 或 Clang 编译器
- Make 构建工具
- Python 3.6 或更高版本（用于数据可视化）
- matplotlib 库（用于数据可视化）
- pandas 库（用于数据处理）
- gnuplot（可选，用于数据可视化）

### 编译依赖：
- build-essential
- libtool
- automake
- git
- wget
- curl

## 3. 详细的编译步骤

### 3.1 安装依赖

```bash
# Ubuntu/Debian 系统
sudo apt update
sudo apt install build-essential libtool automake git wget curl python3 python3-pip
sudo pip3 install matplotlib pandas

# 可选：安装 gnuplot
sudo apt install gnuplot
```

### 3.2 编译 MAflood

1. 克隆 MAflood 代码仓库：

```bash
git clone [MAflood 代码仓库地址]
cd MAflood
```

2. 编译 AFL 工具链：

```bash
make clean all
```

3. 编译 QEMU 模式（可选，用于二进制插桩）：

```bash
cd qemu_mode
./build_qemu_support.sh
```

## 4. 运行参数配置说明

### 4.1 基本运行参数

MAflood 的运行参数与 AFL 兼容，主要参数包括：

- `-i <input_dir>`：输入测试用例目录
- `-o <output_dir>`：输出结果目录
- `-m <memory_limit>`：内存限制（MB）
- `-t <timeout>`：超时时间（毫秒）
- `-f <input_file>`：目标程序的输入文件路径
- `-M <master_name>`：主实例名称（多线程模式）
- `-S <slave_name>`：从实例名称（多线程模式）

### 4.2 多线程运行配置

```bash
# 启动主实例
./afl-fuzz -i input_dir -o output_dir -M master -- ./target_program @@

# 启动从实例（在不同终端）
./afl-fuzz -i input_dir -o output_dir -S slave1 -- ./target_program @@
./afl-fuzz -i input_dir -o output_dir -S slave2 -- ./target_program @@
./afl-fuzz -i input_dir -o output_dir -S slave3 -- ./target_program @@
```

### 4.3 高级配置

- `-d`：禁用确定性测试（加快测试速度）
- `-n`：禁用突变调度器（使用固定突变策略）
- `-x <dict_file>`：使用自定义字典
- `-c <seed>`：设置随机种子

## 5. 实验复现的完整流程

### 5.1 准备测试目标

1. **LAVA-M 测试集**：

```bash
# 下载 LAVA-M 测试集
git clone https://github.com/panda-re/lava.git
cd lava
./get_and_build.sh
```

2. **ffjpeg**：

```bash
# 下载 ffjpeg
git clone https://github.com/FFmpeg/ffmpeg.git
cd ffmpeg
./configure
make
```

3. **libpng**：

```bash
# 下载 libpng
wget https://downloads.sourceforge.net/libpng/libpng-1.6.37.tar.gz
tar -xzf libpng-1.6.37.tar.gz
cd libpng-1.6.37
./configure
make
```

### 5.2 编译测试目标（源码插桩）

```bash
# 使用 afl-gcc 编译
export CC=/path/to/MAflood/afl-gcc
export CXX=/path/to/MAflood/afl-g++

# 编译 LAVA-M 目标
cd /path/to/lava/bin
make clean
export CC=/path/to/MAflood/afl-gcc
make

# 编译 ffjpeg
cd /path/to/ffmpeg
export CC=/path/to/MAflood/afl-gcc
export CXX=/path/to/MAflood/afl-g++
./configure
make

# 编译 libpng
cd /path/to/libpng-1.6.37
export CC=/path/to/MAflood/afl-gcc
export CXX=/path/to/MAflood/afl-g++
./configure
make
```

### 5.3 运行模糊测试

1. **LAVA-M 测试**：

```bash
# 创建输入目录
mkdir -p input_lava
cp /path/to/lava/inputs/* input_lava/

# 运行 MAflood（4 线程）
./afl-fuzz -i input_lava -o output_lava -M master -- /path/to/lava/bin/base64 @@
./afl-fuzz -i input_lava -o output_lava -S slave1 -- /path/to/lava/bin/base64 @@
./afl-fuzz -i input_lava -o output_lava -S slave2 -- /path/to/lava/bin/base64 @@
./afl-fuzz -i input_lava -o output_lava -S slave3 -- /path/to/lava/bin/base64 @@
```

2. **ffjpeg 测试**：

```bash
# 创建输入目录
mkdir -p input_ffjpeg
cp /path/to/sample_images/* input_ffjpeg/

# 运行 MAflood（单线程）
./afl-fuzz -i input_ffjpeg -o output_ffjpeg -- /path/to/ffmpeg/ffmpeg -i @@ -f null -
```

3. **libpng 测试**：

```bash
# 创建输入目录
mkdir -p input_libpng
cp /path/to/sample_pngs/* input_libpng/

# 运行 MAflood（单线程）
./afl-fuzz -i input_libpng -o output_libpng -- /path/to/libpng-1.6.37/pngtest @@
```

### 5.4 收集和分析结果

```bash
# 查看崩溃和挂起
tree output_dir/crashes/
tree output_dir/hangs/

# 分析代码覆盖率
./afl-showmap -o coverage.txt -- /path/to/target_program @@

# 生成性能报告
python3 /path/to/MAflood/visualization/extract_data.py
```

## 6. 已完成的所有实验设置详情

### 6.1 实验环境

- **操作系统**：Ubuntu 18.04 LTS
- **CPU**：Intel Core i7-8700K (6 核 12 线程)
- **内存**：16GB DDR4
- **存储**：512GB SSD

### 6.2 测试目标

| 测试目标 | 版本 | 类型 | 测试用例 |
|---------|------|------|----------|
| LAVA-M | 2017 | 注入漏洞 | 100 个种子文件 |
| ffjpeg | 4.2.2 | 图像处理 | 50 个 BMP/JPEG 样本 |
| libpng | 1.6.37 | 图像处理 | 50 个 PNG 样本 |

### 6.3 实验参数配置

| 工具 | 线程数 | 运行时间 | 内存限制 | 超时设置 |
|------|--------|----------|----------|----------|
| AFL | 1, 4, 8 | 24 小时 | 256MB | 1000ms |
| AFLFast | 1, 4, 8 | 24 小时 | 256MB | 1000ms |
| MAflood | 1, 4, 8 | 24 小时 | 256MB | 1000ms |

### 6.4 变量控制

- **输入种子**：所有工具使用相同的输入种子集
- **运行时间**：所有实验运行相同的时间（24 小时）
- **硬件资源**：所有实验在相同的硬件环境中运行
- **编译选项**：所有目标使用相同的编译选项

## 7. 常见问题解决方法

### 7.1 编译错误

**问题**：编译 AFL 时出现 `error: 'for' loop initial declarations are only allowed in C99 mode`

**解决方法**：使用 C99 标准编译

```bash
export CFLAGS="-std=c99"
make clean all
```

### 7.2 运行错误

**问题**：运行时出现 `[*] Hmm, your system is configured to send core dump notifications to an external utility. This will cause issues: there's a small window of time between receiving a SIGSEGV and the core dump handler firing, where afl-fuzz might not be able to reset the target process.`

**解决方法**：禁用核心转储通知

```bash
echo core > /proc/sys/kernel/core_pattern
```

### 7.3 性能问题

**问题**：模糊测试速度较慢

**解决方法**：
- 增加线程数
- 调整内存限制
- 使用 `-d` 参数禁用确定性测试
- 确保目标程序编译时开启了优化

### 7.4 覆盖问题

**问题**：代码覆盖率增长缓慢

**解决方法**：
- 使用更大的种子集
- 添加自定义字典 (`-x` 参数)
- 调整突变策略
- 检查目标程序是否有复杂的输入验证

## 8. 实验结果可视化

### 8.1 可视化工具

- **Python + Matplotlib**：用于生成详细的性能图表
- **Gnuplot**：用于生成实时性能监控图表

### 8.2 生成可视化图表

```bash
# 进入可视化目录
cd /path/to/MAflood/visualization

# 运行数据提取和可视化脚本
python3 extract_data.py

# 查看生成的图表
ls -la *.png
```

### 8.3 图表说明

生成的图表包括：

- **崩溃发现率对比**：展示不同工具和线程配置下的崩溃发现速度
- **代码覆盖率对比**：展示不同工具和线程配置下的代码覆盖率增长
- **执行速度对比**：展示不同工具和线程配置下的平均执行速度
- **测试用例数量对比**：展示不同工具和线程配置下的测试用例生成数量

## 9. 项目结构

```
MAflood/
├── afl-fuzz.c          # 核心模糊测试代码
├── afl-gcc.c           # GCC 插桩工具
├── afl-clang.c         # Clang 插桩工具
├── qemu_mode/          # QEMU 模式支持
├── docs/               # 文档
├── experiment/         # 实验数据
│   ├── LAVA-M/         # LAVA-M 测试结果
│   ├── ffjpeg/         # ffjpeg 测试结果
│   └── libpng/         # libpng 测试结果
└── visualization/      # 数据可视化工具
    ├── extract_data.py # 数据提取脚本
    └── *.png           # 生成的图表
```

## 10. 结论

MAflood 通过引入双剪枝模型和优化的线程同步机制，显著提高了多线程模糊测试的性能和效率。实验结果表明，MAflood 在崩溃发现率、代码覆盖率和执行速度方面均优于传统的 AFL 和 AFLFast 工具。

### 关键改进：

1. **双剪枝模型**：减少了冗余测试用例，提高了测试效率
2. **优化的线程同步**：减少了线程间通信开销，提高了并行性能
3. **自适应测试策略**：根据目标程序特性自动调整测试参数

MAflood 为模糊测试领域提供了一种高效的多线程解决方案，特别适用于大型复杂程序的安全性测试。

## 11. 参考资料

1. American Fuzzy Lop (AFL): https://lcamtuf.coredump.cx/afl/
2. AFLFast: https://github.com/mboehme/aflfast
3. LAVA-M: https://github.com/panda-re/lava
4. libpng: https://libpng.sourceforge.io/
5. FFmpeg: https://ffmpeg.org/
