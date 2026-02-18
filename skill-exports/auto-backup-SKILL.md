# Auto-Backup Skill

自动备份和恢复 workspace 文件的 skill。

## 核心规则

**修改重要文件前，必须先备份！**

重要文件包括：
- `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `IDENTITY.md`
- `memory/*.md`
- `skills/*/SKILL.md`
- 任何 `.md` 配置文件

## 备份命令

修改前执行：
```powershell
cd C:\Users\Administrator\.openclaw\workspace
git add -A
git commit -m "backup-before-edit"
```

## 恢复命令

### 查看历史
```powershell
cd C:\Users\Administrator\.openclaw\workspace
git log --oneline -10
```

### 查看某次提交改了什么
```powershell
git show <commit-hash> --stat
```

### 恢复单个文件到上一版本
```powershell
git checkout HEAD~1 -- <文件路径>
```

### 恢复所有文件到上一版本
```powershell
git reset --hard HEAD~1
```

### 恢复到指定版本
```powershell
git reset --hard <commit-hash>
```

### 只查看差异，不恢复
```powershell
git diff HEAD~1
```

## 使用场景

1. **我改坏了配置** → `git reset --hard HEAD~1`
2. **想看改了啥** → `git diff HEAD~1`
3. **只恢复某个文件** → `git checkout HEAD~1 -- AGENTS.md`
4. **彻底回滚到某个版本** → `git log --oneline` 找到 hash，然后 `git reset --hard <hash>`

## 自动化

每次修改重要文件前，我会自动执行备份。
如果忘了备份就改坏了，告诉我"恢复"或"回滚"，我会帮你处理。
