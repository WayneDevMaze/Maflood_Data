#!/usr/bin/env python3
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体支持（如果需要）
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 定义数据目录
BASE_DIR = '../experiment'
OUTPUT_DIR = '.'

# 工具列表
TOOLS = ['AFL', 'AFLFast', 'MAflood']

# 目标列表
TARGETS = ['LAVA-M', 'ffjpeg', 'libpng']

# 线程配置
THREADS = [1, 4, 8]

# 设置全局图表样式，按照学术水准美化
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'Times New Roman',
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'figure.figsize': (10, 6),
    'figure.dpi': 300,
    'lines.linewidth': 2.0,
    'lines.markersize': 4,
    'axes.linewidth': 1.0,
    'grid.linewidth': 0.8,
    'grid.alpha': 0.7
})

# 提取plot_data文件中的数据
def extract_plot_data(file_path):
    """从plot_data文件中提取数据"""
    if not os.path.exists(file_path):
        return None
    
    # 读取文件
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # 解析数据
    data = []
    # 处理表头，去除注释符号
    header_line = lines[0].strip()
    if header_line.startswith('#'):
        header_line = header_line[1:].strip()
    headers = [h.strip() for h in header_line.split(',')]
    
    for line in lines[1:]:
        values = [v.strip() for v in line.strip().split(',')]
        if len(values) != len(headers):
            continue
        
        # 转换数据类型
        row = {}
        for i, (header, value) in enumerate(zip(headers, values)):
            if header == 'map_size':  # map_size 是百分比
                row[header] = float(value.strip('%'))
            else:
                try:
                    row[header] = int(value)
                except ValueError:
                    try:
                        row[header] = float(value)
                    except ValueError:
                        row[header] = value
        
        data.append(row)
    
    return pd.DataFrame(data)

# 收集所有数据
def collect_data():
    """收集所有实验数据"""
    all_data = {}
    
    for target in TARGETS:
        target_data = {}
        for tool in TOOLS:
            tool_data = {}
            
            if target == 'LAVA-M':
                # LAVA-M有不同线程数的测试
                for thread in THREADS:
                    if tool == 'MAflood':
                        # MAflood的目录结构不同
                        plot_path = os.path.join(BASE_DIR, target, tool, 'fuzz_out', 'master', 'plot_data')
                    else:
                        plot_path = os.path.join(BASE_DIR, target, tool, str(thread), 'fuzz_out', 'master', 'plot_data')
                    
                    df = extract_plot_data(plot_path)
                    if df is not None:
                        tool_data[thread] = df
            elif target == 'ffjpeg':
                # ffjpeg测试BMP和JPEG格式
                for format_type in ['bmp', 'jpg']:
                    if tool == 'MAflood':
                        plot_path = os.path.join(BASE_DIR, target, tool, f'fuzz_out_{format_type}-e', 'm', 'plot_data')
                    else:
                        plot_path = os.path.join(BASE_DIR, target, tool, f'fuzz_out_{format_type}-e', 'master', 'plot_data')
                    
                    df = extract_plot_data(plot_path)
                    if df is not None:
                        tool_data[format_type] = df
            elif target == 'libpng':
                # libpng测试
                if tool == 'MAflood':
                    plot_path = os.path.join(BASE_DIR, target, tool, 'fuzz_out', 'm', 'plot_data')
                else:
                    plot_path = os.path.join(BASE_DIR, target, tool, 'fuzz_out', 'master', 'plot_data')
                
                df = extract_plot_data(plot_path)
                if df is not None:
                    tool_data['png'] = df
            
            if tool_data:
                target_data[tool] = tool_data
        
        if target_data:
            all_data[target] = target_data
    
    return all_data

# 生成崩溃发现率对比图表
def plot_crashes_comparison(data, target, filename):
    """Generate crash discovery rate comparison chart"""
    plt.figure()
    
    for tool in TOOLS:
        if tool not in data:
            continue
        
        tool_data = data[tool]
        if target == 'LAVA-M':
            # 按线程数绘制
            for thread in THREADS:
                if thread not in tool_data:
                    continue
                df = tool_data[thread]
                if 'unique_crashes' in df.columns:
                    # 计算时间差（转换为小时）
                    time_diff = (df['unix_time'] - df['unix_time'].iloc[0]) / 3600
                    # 绘制平滑曲线
                    plt.plot(time_diff, 
                             df['unique_crashes'], 
                             label=f'{tool} ({thread} threads)',
                             linewidth=2.5)
        else:
            # 按格式绘制
            for fmt in tool_data:
                df = tool_data[fmt]
                if 'unique_crashes' in df.columns:
                    # 计算时间差（转换为小时）
                    time_diff = (df['unix_time'] - df['unix_time'].iloc[0]) / 3600
                    # 绘制平滑曲线
                    plt.plot(time_diff, 
                             df['unique_crashes'], 
                             label=f'{tool} ({fmt})',
                             linewidth=2.5)
    
    plt.title(f'{target} - Crash Discovery Rate Comparison')
    plt.xlabel('Time (hours)')
    plt.ylabel('Number of Crashes')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

# 生成代码覆盖率对比图表
def plot_coverage_comparison(data, target, filename):
    """Generate code coverage comparison chart"""
    plt.figure()
    
    for tool in TOOLS:
        if tool not in data:
            continue
        
        tool_data = data[tool]
        if target == 'LAVA-M':
            # 按线程数绘制
            for thread in THREADS:
                if thread not in tool_data:
                    continue
                df = tool_data[thread]
                if 'map_size' in df.columns:
                    # 计算时间差（转换为小时）
                    time_diff = (df['unix_time'] - df['unix_time'].iloc[0]) / 3600
                    # 绘制平滑曲线
                    plt.plot(time_diff, 
                             df['map_size'], 
                             label=f'{tool} ({thread} threads)',
                             linewidth=2.5)
        else:
            # 按格式绘制
            for fmt in tool_data:
                df = tool_data[fmt]
                if 'map_size' in df.columns:
                    # 计算时间差（转换为小时）
                    time_diff = (df['unix_time'] - df['unix_time'].iloc[0]) / 3600
                    # 绘制平滑曲线
                    plt.plot(time_diff, 
                             df['map_size'], 
                             label=f'{tool} ({fmt})',
                             linewidth=2.5)
    
    plt.title(f'{target} - Code Coverage Comparison')
    plt.xlabel('Time (hours)')
    plt.ylabel('Coverage (%)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

# 生成执行速度对比图表
def plot_exec_speed_comparison(data, target, filename):
    """Generate execution speed comparison chart"""
    plt.figure()
    
    # 收集数据
    labels = []
    values = []
    
    for tool in TOOLS:
        if tool not in data:
            continue
        
        tool_data = data[tool]
        if target == 'LAVA-M':
            # 按线程数绘制
            for thread in THREADS:
                if thread not in tool_data:
                    continue
                df = tool_data[thread]
                if 'execs_per_sec' in df.columns:
                    # 计算平均执行速度
                    avg_speed = df['execs_per_sec'].mean()
                    labels.append(f'{tool} ({thread} threads)')
                    values.append(avg_speed)
        else:
            # 按格式绘制
            for fmt in tool_data:
                df = tool_data[fmt]
                if 'execs_per_sec' in df.columns:
                    # 计算平均执行速度
                    avg_speed = df['execs_per_sec'].mean()
                    labels.append(f'{tool} ({fmt})')
                    values.append(avg_speed)
    
    # 绘制柱状图，调整宽度
    x = np.arange(len(labels))
    width = 0.6  # 调整柱状图宽度
    
    plt.bar(x, values, width=width, align='center')
    plt.xticks(x, labels, rotation=45, ha='right')
    
    plt.title(f'{target} - Average Execution Speed Comparison')
    plt.xlabel('Tool and Configuration')
    plt.ylabel('Execution Speed (execs/sec)')
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

# 生成测试用例数量对比图表
def plot_testcases_comparison(data, target, filename):
    """Generate test case count comparison chart"""
    plt.figure()
    
    for tool in TOOLS:
        if tool not in data:
            continue
        
        tool_data = data[tool]
        if target == 'LAVA-M':
            # 按线程数绘制
            for thread in THREADS:
                if thread not in tool_data:
                    continue
                df = tool_data[thread]
                if 'paths_total' in df.columns:
                    # 计算时间差（转换为小时）
                    time_diff = (df['unix_time'] - df['unix_time'].iloc[0]) / 3600
                    # 绘制平滑曲线
                    plt.plot(time_diff, 
                             df['paths_total'], 
                             label=f'{tool} ({thread} threads)',
                             linewidth=2.5)
        else:
            # 按格式绘制
            for fmt in tool_data:
                df = tool_data[fmt]
                if 'paths_total' in df.columns:
                    # 计算时间差（转换为小时）
                    time_diff = (df['unix_time'] - df['unix_time'].iloc[0]) / 3600
                    # 绘制平滑曲线
                    plt.plot(time_diff, 
                             df['paths_total'], 
                             label=f'{tool} ({fmt})',
                             linewidth=2.5)
    
    plt.title(f'{target} - Test Case Count Comparison')
    plt.xlabel('Time (hours)')
    plt.ylabel('Number of Test Cases')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

# 为ffjpeg生成单独的覆盖率对比图表（每个fuzzer一个子图）
def plot_ffjpeg_coverage_separate(data, filename):
    """Generate separate coverage comparison charts for ffjpeg (one subplot per fuzzer)"""
    # 创建一个3x1的子图布局
    fig, axes = plt.subplots(3, 1, figsize=(10, 15), sharex=True)
    
    # 为每个工具创建单独的子图
    for i, tool in enumerate(TOOLS):
        if tool not in data:
            continue
        
        ax = axes[i]
        tool_data = data[tool]
        
        # 绘制不同格式的测试结果
        for fmt in tool_data:
            df = tool_data[fmt]
            if 'map_size' in df.columns:
                # 计算时间差（转换为小时）
                time_diff = (df['unix_time'] - df['unix_time'].iloc[0]) / 3600
                # 绘制平滑曲线
                ax.plot(time_diff, 
                         df['map_size'], 
                         label=f'{fmt}',
                         linewidth=2.5)
        
        ax.set_title(f'{tool} - Code Coverage')
        ax.set_ylabel('Coverage (%)')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper left')
    
    # 设置共享的x轴标签
    axes[-1].set_xlabel('Time (hours)')
    
    # 调整子图间距
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

# 主函数
def main():
    # 收集数据
    print("收集实验数据...")
    all_data = collect_data()
    
    # 生成图表
    print("生成可视化图表...")
    for target in TARGETS:
        if target not in all_data:
            continue
        
        target_data = all_data[target]
        
        # 生成崩溃发现率对比图表
        plot_crashes_comparison(target_data, target, f'{target}_crashes_comparison.png')
        
        # 生成代码覆盖率对比图表
        if target == 'ffjpeg':
            # 为ffjpeg生成单独的覆盖率对比图表
            plot_ffjpeg_coverage_separate(target_data, f'{target}_coverage_comparison.png')
        else:
            # 为其他目标生成常规的覆盖率对比图表
            plot_coverage_comparison(target_data, target, f'{target}_coverage_comparison.png')
        
        # 生成执行速度对比图表
        plot_exec_speed_comparison(target_data, target, f'{target}_exec_speed_comparison.png')
        
        # 生成测试用例数量对比图表
        plot_testcases_comparison(target_data, target, f'{target}_testcases_comparison.png')
    
    print("可视化图表生成完成！")

if __name__ == "__main__":
    main()
