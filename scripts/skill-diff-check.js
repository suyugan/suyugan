#!/usr/bin/env node
/**
 * Skill版本对比工具
 * 对比git上次commit和当前工作区的skill文件差异
 * 找出"改了但没commit"和"该改但没改"的文件
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const WORKSPACE = 'C:\\Users\\Administrator\\.openclaw\\workspace';
const MEMORY_DIR = path.join(WORKSPACE, 'memory');
const SKILLS_DIR = path.join(WORKSPACE, 'skills');

// 1. 找出skill文件的未提交变更
console.log('=== Skill文件未提交变更 ===');
try {
  const diff = execSync('git diff --name-only HEAD -- skills/', { cwd: WORKSPACE, encoding: 'utf8' });
  const staged = execSync('git diff --name-only --cached -- skills/', { cwd: WORKSPACE, encoding: 'utf8' });
  const untracked = execSync('git ls-files --others --exclude-standard -- skills/', { cwd: WORKSPACE, encoding: 'utf8' });
  
  const allChanges = [...new Set([...diff.trim().split('\n'), ...staged.trim().split('\n'), ...untracked.trim().split('\n')].filter(Boolean))];
  
  if (allChanges.length === 0) {
    console.log('✅ 所有skill文件已提交');
  } else {
    console.log(`⚠️ ${allChanges.length}个文件有未提交变更：`);
    allChanges.forEach(f => console.log(`  - ${f}`));
  }
} catch (e) {
  console.log('⚠️ git检查失败:', e.message);
}

// 2. 检查最近memory中提到但skill可能没同步的规则
console.log('\n=== Memory vs Skill同步检查 ===');
const today = new Date();
const files = [];
for (let i = 0; i < 3; i++) {
  const d = new Date(today);
  d.setDate(d.getDate() - i);
  const fname = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}.md`;
  const fpath = path.join(MEMORY_DIR, fname);
  if (fs.existsSync(fpath)) files.push(fpath);
}

// 关键词：表示学到了新东西的信号
const SIGNAL_WORDS = ['必须', '不能', '应该', '改成', '正确做法', '解决方案', '注意', '防止', '修复', 'fix:', '发现', '原来'];

let memoryRules = [];
files.forEach(fpath => {
  const content = fs.readFileSync(fpath, 'utf8');
  const lines = content.split('\n');
  lines.forEach((line, i) => {
    if (SIGNAL_WORDS.some(w => line.includes(w)) && line.trim().length > 10) {
      memoryRules.push({ file: path.basename(fpath), line: i + 1, text: line.trim() });
    }
  });
});

if (memoryRules.length === 0) {
  console.log('✅ 最近3天memory无新规则');
} else {
  console.log(`📋 最近3天memory中有${memoryRules.length}条可能需要同步的规则：`);
  memoryRules.forEach(r => console.log(`  [${r.file}:${r.line}] ${r.text.substring(0, 80)}`));
}

// 3. 检查MEMORY.md中的规则是否在skill中有对应
console.log('\n=== MEMORY.md规则覆盖检查 ===');
const memoryMd = fs.readFileSync(path.join(WORKSPACE, 'MEMORY.md'), 'utf8');
const rules = memoryMd.match(/- \*\*.+?\*\*.+/g) || [];
console.log(`MEMORY.md中有${rules.length}条加粗规则，建议定期人工审查是否都同步到了skill。`);

// 4. 统计skill文件最后修改时间
console.log('\n=== Skill文件活跃度 ===');
const skillDirs = fs.readdirSync(SKILLS_DIR).filter(d => fs.statSync(path.join(SKILLS_DIR, d)).isDirectory());
const stale = [];
const weekAgo = Date.now() - 7 * 24 * 3600 * 1000;

skillDirs.forEach(dir => {
  const skillMd = path.join(SKILLS_DIR, dir, 'SKILL.md');
  if (fs.existsSync(skillMd)) {
    const stat = fs.statSync(skillMd);
    if (stat.mtimeMs < weekAgo) {
      stale.push({ name: dir, lastMod: stat.mtime.toISOString().split('T')[0] });
    }
  }
});

if (stale.length > 0) {
  console.log(`📅 ${stale.length}个skill超过7天未更新（可能需要检查）：`);
  stale.forEach(s => console.log(`  - ${s.name} (最后更新: ${s.lastMod})`));
} else {
  console.log('✅ 所有skill近7天都有更新');
}

console.log('\n完成。');
