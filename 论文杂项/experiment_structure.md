# 项目实验结构

## 1. 项目根目录结构

```
MAflood-Data/
├── MAflood/                # MAflood模糊测试工具源码
├── experiment/             # 实验结果目录
├── targets/                # 测试目标程序
├── README_CN.md            # 中文说明文档
└── README_EN.md            # 英文说明文档
```

## 2. 实验结果目录结构

### 2.1 LAVA-M 项目

```
experiment/LAVA-M/
├── AFL/                    # AFL工具测试结果
│   ├── 1/                  # 1实例测试
│   │   └── fuzz_out/       # 输出目录
│   ├── 4/                  # 4实例测试
│   │   └── fuzz_out/       # 输出目录（包含master、s1、s2、s3）
│   ├── 8/                  # 8实例测试
│   │   └── fuzz_out/       # 输出目录（包含m、s1-s7）
│   └── fuzz_in/            # 输入目录
├── AFLFast/                # AFLFast工具测试结果
│   ├── 1/                  # 1实例测试
│   │   └── fuzz_out/       # 输出目录
│   ├── 2/                  # 2实例测试
│   │   └── fuzz_out/       # 输出目录
│   ├── 4/                  # 4实例测试
│   │   └── fuzz_out/       # 输出目录
│   ├── 8/                  # 8实例测试
│   │   └── fuzz_out/       # 输出目录
│   └── fuzz_in/            # 输入目录
└── MAflood/                # MAflood工具测试结果
    ├── fuzz_in/            # 输入目录
    └── base64              # 测试目标程序
```

### 2.2 ffjpeg 项目

```
experiment/ffjpeg/
├── AFL/                    # AFL工具测试结果
│   ├── fuzz_in_bmp/        # BMP格式输入目录
│   ├── fuzz_in_jpg/        # JPEG格式输入目录
│   ├── fuzz_out_bmp-e/     # BMP格式编码测试输出目录
│   ├── fuzz_out_jpg-d/     # JPEG格式解码测试输出目录
│   └── ffjpeg              # 测试目标程序
├── AFLFast/                # AFLFast工具测试结果
│   ├── fuzz_in_bmp/        # BMP格式输入目录
│   ├── fuzz_in_jpg/        # JPEG格式输入目录
│   └── ffjpeg              # 测试目标程序
└── MAflood/                # MAflood工具测试结果
    ├── fuzz_in_bmp/        # BMP格式输入目录
    ├── fuzz_in_jpeg/       # JPEG格式输入目录
    ├── fuzz_out_bmp-e/     # BMP格式编码测试输出目录
    ├── fuzz_out_jpg-d/     # JPEG格式解码测试输出目录
    └── ffjpeg              # 测试目标程序
```

### 2.3 libpng 项目

```
experiment/libpng/
├── AFL/                    # AFL工具测试结果
│   ├── fuzz_in/            # 输入目录
│   ├── fuzz_out/           # 输出目录（包含master、s1、s2、s3）
│   └── pngfix              # 测试目标程序
├── AFLFast/                # AFLFast工具测试结果
│   ├── fuzz_in/            # 输入目录
│   ├── fuzz_out/           # 输出目录（包含master、s1、s2、s3）
│   └── pngfix              # 测试目标程序
└── MAflood/                # MAflood工具测试结果
    ├── fuzz_in/            # 输入目录
    ├── fuzz_out_0407/      # 输出目录（包含m、s1、s2、s3）
    └── pngfix              # 测试目标程序
```

## 3. 输出目录结构

每个模糊测试工具的输出目录通常包含以下文件和子目录：

```
fuzz_out/
├── crashes/                # 崩溃测试用例
├── queue/                  # 队列中的测试用例
├── .cur_input              # 当前输入文件
├── fuzz_bitmap             # 模糊测试位图
├── fuzzer_stats            # 模糊测试统计信息
├── plot_data               # 绘图数据
└── .synced/                # 多实例同步目录
```

## 4. 测试目标程序

1. **LAVA-M**：使用base64程序作为测试目标
2. **ffjpeg**：使用ffjpeg程序测试BMP和JPEG格式处理
3. **libpng**：使用pngfix程序测试PNG格式处理

## 5. 实验配置

### 5.1 实例配置

- **1实例**：单实例模式，不使用并行测试
- **2实例**：2个实例并行测试
- **4实例**：4个实例并行测试（1个master + 3个slave）
- **8实例**：8个实例并行测试（1个master + 7个slave）

### 5.2 测试命令示例

- **AFL**：`afl-fuzz -i fuzz_in/ -o fuzz_out/ -m none -- ./base64 -d @@`
- **AFLFast**：`afl-fuzz -p fast -i fuzz_in/ -o fuzz_out/ -m none -- ./base64 -d @@`
- **MAflood**：`MAflood -A 5 -i fuzz_in/ -o fuzz_out/ -m none -- ./base64 -d @@`

## 6. 分析结果目录

```
MAflood-Data/analysis/
├── test_results.json       # 提取的测试结果数据
├── visualization.html      # 可视化图表
└── comprehensive_report.md # 综合分析报告
```