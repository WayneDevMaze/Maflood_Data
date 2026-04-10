import json

# 读取去重后的crash文件
with open('f:\\浙江警察学院\\MAflood-Data\\experiment\\libpng\\deduplicated_crashes.json', 'r', encoding='utf-8') as f:
    crashes = json.load(f)

# 查找在多个工具中出现的crash
shared_crashes = []
for crash in crashes:
    if len(crash['tools']) > 1:
        shared_crashes.append(crash)

print(f"在多个工具中出现的crash数量: {len(shared_crashes)}")
print()

for crash in shared_crashes:
    print(f"Hash: {crash['hash']}")
    print(f"在工具中出现: {', '.join(crash['tools'])}")
    print(f"首次出现: {crash['first_occurrence']['tool']} - {crash['first_occurrence']['subdir']}/{crash['first_occurrence']['filename']}")
    print(f"文件大小: {crash['size']}字节")
    print()
