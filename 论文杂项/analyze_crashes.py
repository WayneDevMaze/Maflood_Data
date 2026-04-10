import os
import hashlib
import json

# 定义工具目录
tools = {
    "MAflood": "f:\\浙江警察学院\\MAflood-Data\\experiment\\libpng\\MAflood\\fuzz_out",
    "AFL": "f:\\浙江警察学院\\MAflood-Data\\experiment\\libpng\\AFL\\fuzz_out",
    "AFLFast": "f:\\浙江警察学院\\MAflood-Data\\experiment\\libpng\\AFLFast\\fuzz_out"
}

# 子目录
subdirs = ["s1", "s2", "s3", "m"]

# 存储所有crash信息
all_crashes = {}
crash_hashes = set()

# 遍历每个工具
for tool_name, tool_path in tools.items():
    tool_crashes = []
    
    # 遍历每个子目录
    for subdir in subdirs:
        crashes_dir = os.path.join(tool_path, subdir, "crashes")
        
        if os.path.exists(crashes_dir):
            # 遍历crashes目录中的文件
            for filename in os.listdir(crashes_dir):
                if filename == "README.txt":
                    continue
                
                crash_file = os.path.join(crashes_dir, filename)
                
                try:
                    # 读取文件内容
                    with open(crash_file, 'rb') as f:
                        content = f.read()
                    
                    # 计算哈希值
                    crash_hash = hashlib.md5(content).hexdigest()
                    
                    # 存储crash信息
                    crash_info = {
                        "tool": tool_name,
                        "subdir": subdir,
                        "filename": filename,
                        "hash": crash_hash,
                        "size": len(content)
                    }
                    
                    tool_crashes.append(crash_info)
                    crash_hashes.add(crash_hash)
                    
                except Exception as e:
                    print(f"Error reading {crash_file}: {e}")
    
    all_crashes[tool_name] = tool_crashes

# 统计信息
statistics = {
    "total_crashes": sum(len(crashes) for crashes in all_crashes.values()),
    "unique_crashes": len(crash_hashes),
    "per_tool": {}
}

for tool_name, crashes in all_crashes.items():
    # 计算每个工具的唯一crash数量
    tool_unique_hashes = set(crash["hash"] for crash in crashes)
    statistics["per_tool"][tool_name] = {
        "total": len(crashes),
        "unique": len(tool_unique_hashes)
    }

# 生成去重后的crash列表
deduplicated_crashes = {}
for tool_name, crashes in all_crashes.items():
    for crash in crashes:
        crash_hash = crash["hash"]
        if crash_hash not in deduplicated_crashes:
            deduplicated_crashes[crash_hash] = {
                "hash": crash_hash,
                "tools": [tool_name],
                "first_occurrence": {
                    "tool": tool_name,
                    "subdir": crash["subdir"],
                    "filename": crash["filename"]
                },
                "size": crash["size"]
            }
        else:
            if tool_name not in deduplicated_crashes[crash_hash]["tools"]:
                deduplicated_crashes[crash_hash]["tools"].append(tool_name)

# 保存结果
output_dir = "f:\\浙江警察学院\\MAflood-Data\\experiment\\libpng"

# 保存统计信息
with open(os.path.join(output_dir, "crash_statistics.json"), "w", encoding="utf-8") as f:
    json.dump(statistics, f, ensure_ascii=False, indent=2)

# 保存去重后的crash信息
with open(os.path.join(output_dir, "deduplicated_crashes.json"), "w", encoding="utf-8") as f:
    json.dump(list(deduplicated_crashes.values()), f, ensure_ascii=False, indent=2)

# 生成汇总报告
report_content = f"""
Libpng模糊测试Crash去重汇总报告

1. 总体统计
- 总Crash数量: {statistics['total_crashes']}
- 去重后Crash数量: {statistics['unique_crashes']}
- 重复率: {((statistics['total_crashes'] - statistics['unique_crashes']) / statistics['total_crashes'] * 100):.2f}%

2. 各工具统计
"""

for tool_name, stats in statistics['per_tool'].items():
    report_content += f"- {tool_name}: 总{stats['total']}个, 唯一{stats['unique']}个\n"

report_content += "\n3. 去重后Crash分布\n"

# 统计每个crash在多少个工具中出现
crash_tool_count = {}
for crash in deduplicated_crashes.values():
    count = len(crash['tools'])
    if count not in crash_tool_count:
        crash_tool_count[count] = 0
    crash_tool_count[count] += 1

for count, num_crashes in sorted(crash_tool_count.items()):
    report_content += f"- 在{count}个工具中出现: {num_crashes}个\n"

# 保存报告
with open(os.path.join(output_dir, "crash_analysis_report.txt"), "w", encoding="utf-8") as f:
    f.write(report_content)

print("分析完成！")
print(f"统计信息已保存到: {os.path.join(output_dir, 'crash_statistics.json')}")
print(f"去重后的crash信息已保存到: {os.path.join(output_dir, 'deduplicated_crashes.json')}")
print(f"分析报告已保存到: {os.path.join(output_dir, 'crash_analysis_report.txt')}")
