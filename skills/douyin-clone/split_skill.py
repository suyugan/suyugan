#!/usr/bin/env python3
"""Split SKILL.md into phase files."""
import os, re

SKILL_PATH = os.path.join(os.path.dirname(__file__), "SKILL.md")
PHASES_DIR = os.path.join(os.path.dirname(__file__), "phases")
os.makedirs(PHASES_DIR, exist_ok=True)

with open(SKILL_PATH, "r", encoding="utf-8-sig") as f:
    content = f.read()
    lines = content.split("\n")

print(f"Original: {len(lines)} lines, {len(content)} bytes")

# Find section boundaries by looking for ## 阶段 headers
# We'll split into these files:
# 1. SKILL.md (header + quick mode + spawn rules + phase overview)
# 2. phase1-data.md (阶段一 + 阶段1.5)
# 3. phase2-analysis.md (阶段二 + 2.5)
# 4. phase3-script.md (阶段三)
# 5. phase4-scenes.md (阶段四 + 4.5)
# 6. phase5-assets.md (阶段五 all)
# 7. phase6-compose.md (阶段六 + 七)

# Find line numbers for key sections
section_starts = {}
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == "## 阶段一：抓取数据":
        section_starts["phase1"] = i
    elif stripped == "## 阶段1.5：账号类型自动识别":
        section_starts["phase1.5"] = i
    elif stripped == "## 阶段二：AI分析出报告（含视频抽帧深度风格分析）":
        section_starts["phase2"] = i
    elif stripped.startswith("## 阶段2.5"):
        section_starts["phase2.5"] = i
    elif stripped == "## 阶段三：写文案":
        section_starts["phase3"] = i
    elif stripped == "## 阶段四：拆分场景 + 生成提示词":
        section_starts["phase4"] = i
    elif stripped.startswith("## 阶段4.5"):
        section_starts["phase4.5"] = i
    elif stripped.startswith("## 阶段五"):
        section_starts["phase5"] = i
    elif "## 阶段六" in stripped or "## 阶段5.4" in stripped:
        if "phase6" not in section_starts:
            section_starts["phase6_candidate"] = i
    # Look for phase 6 more carefully
    if re.match(r"^##\s+阶段六", stripped):
        section_starts["phase6"] = i
    if re.match(r"^##\s+阶段七", stripped) or re.match(r"^##\s+阶段7", stripped):
        section_starts["phase7"] = i

print("Section starts found:")
for k, v in sorted(section_starts.items(), key=lambda x: x[1]):
    print(f"  {k}: line {v+1} -> {lines[v][:60]}")

# Now extract sections
phase1_start = section_starts.get("phase1")
phase2_start = section_starts.get("phase2") or section_starts.get("phase1.5")
phase3_start = section_starts.get("phase3")
phase4_start = section_starts.get("phase4")
phase5_start = section_starts.get("phase5")
phase6_start = section_starts.get("phase6") or section_starts.get("phase6_candidate")

if not all([phase1_start, phase3_start, phase4_start, phase5_start]):
    print("ERROR: Could not find all section boundaries!")
    print(f"phase1={phase1_start}, phase3={phase3_start}, phase4={phase4_start}, phase5={phase5_start}")
    # Print all ## headers for debugging
    for i, line in enumerate(lines):
        if line.startswith("## "):
            print(f"  Line {i+1}: {line[:80]}")
    exit(1)

# If no phase6 found, search for it
if not phase6_start:
    for i, line in enumerate(lines):
        if "合成视频" in line and line.startswith("## "):
            phase6_start = i
            break
    if not phase6_start:
        # Just put everything after phase5 that's not phase5 into phase6
        # Look for the next ## after phase5 content ends
        print("WARNING: No explicit phase6 header found, searching...")
        for i, line in enumerate(lines[phase5_start+1:], phase5_start+1):
            if re.match(r"^## 阶段[六67]", line) or "合成" in line and line.startswith("## "):
                phase6_start = i
                print(f"  Found at line {i+1}: {line[:60]}")
                break

# Header section (everything before phase1)
header = lines[:phase1_start]

# Phase files content
phase1_lines = lines[phase1_start:phase2_start] if phase2_start else lines[phase1_start:phase3_start]
# phase1.5 is between phase1 proper and phase2
if "phase1.5" in section_starts and "phase2" in section_starts:
    phase1_end = section_starts["phase2"]
else:
    phase1_end = phase3_start

phase1_content = lines[phase1_start:phase1_end]
phase2_content = lines[phase1_end:phase3_start] if phase1_end != phase3_start else []

# Actually let me redo this more carefully
# phase1-data: from 阶段一 to 阶段二 (includes 1.5)
p1_start = section_starts.get("phase1", phase1_start)
p2_start = section_starts.get("phase2", phase3_start)
p3_start = phase3_start
p4_start = phase4_start
p5_start = phase5_start
p6_start = phase6_start if phase6_start else len(lines)

phase_files = {
    "phase1-data.md": lines[p1_start:p2_start],
    "phase2-analysis.md": lines[p2_start:p3_start],
    "phase3-script.md": lines[p3_start:p4_start],
    "phase4-scenes.md": lines[p4_start:p5_start],
    "phase5-assets.md": lines[p5_start:p6_start],
    "phase6-compose.md": lines[p6_start:],
}

# Write phase files
total_phase_lines = 0
for fname, phase_lines in phase_files.items():
    if not phase_lines:
        print(f"SKIP {fname} (empty)")
        continue
    
    # Add header comment
    phase_header = f"<!-- 本文件是 douyin-clone 技能的子文件，完整流程见 ../SKILL.md -->\n\n"
    phase_content = phase_header + "\n".join(phase_lines)
    
    fpath = os.path.join(PHASES_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(phase_content)
    
    total_phase_lines += len(phase_lines)
    print(f"Written {fname}: {len(phase_lines)} lines, {len(phase_content)} bytes")

# Now write the slim SKILL.md
# Keep the header, add a phase directory/index
phase_index = """
---

## 📂 阶段详细文档（子代理按需读取）

完整流程拆分为独立文件，子代理只需读取对应阶段的文件：

| 阶段 | 文件 | 内容 |
|------|------|------|
| 1-1.5 | `phases/phase1-data.md` | 抓取数据 + 账号类型识别 |
| 2-2.5 | `phases/phase2-analysis.md` | AI分析报告 + 风格模板提取 + 推荐选题 |
| 3 | `phases/phase3-script.md` | 写文案 |
| 4-4.5 | `phases/phase4-scenes.md` | 拆分场景 + 生成提示词 + 风格样片 |
| 5 | `phases/phase5-assets.md` | 生成素材（即梦生图/视频/Remotion/TTS/BGM） |
| 6-7 | `phases/phase6-compose.md` | 合成视频 + 上传 + 质量评估 + 发布 |

### 子代理Spawn时的读取规则
- **子代理1（分析+文案）**：读 `phases/phase1-data.md` + `phases/phase2-analysis.md`
- **子代理2（TTS+BGM）**：读 `phases/phase5-assets.md` 中的5.2和5.3部分
- **子代理3（即梦生图）**：读 `phases/phase5-assets.md` 中的5.1部分
- **子代理4（合成+交付）**：读 `phases/phase6-compose.md`
- **不要读整个SKILL.md！只读对应的phase文件！**
"""

slim_content = "\n".join(header) + phase_index
with open(SKILL_PATH, "w", encoding="utf-8") as f:
    f.write(slim_content)

slim_lines = slim_content.count("\n") + 1
print(f"\nSlim SKILL.md: {slim_lines} lines, {len(slim_content)} bytes")
print(f"Phase files total: {total_phase_lines} lines")
print(f"Original total: {len(lines)} lines")
print(f"New total: {slim_lines + total_phase_lines} lines")
