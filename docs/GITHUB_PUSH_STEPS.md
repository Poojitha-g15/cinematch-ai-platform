# GitHub Push Steps

Recommended repository name:

```text
cinematch-ai-platform
```

If replacing your existing repo, rename this repo first:

```text
User-Authentication-Movie-Platform
```

to:

```text
cinematch-ai-platform
```

Then use these commands from your Downloads folder.

## 1. Clone the renamed GitHub repo

```bash
cd ~/Downloads
git clone https://github.com/Poojitha-g15/cinematch-ai-platform.git cinematch-ai-platform-github
```

## 2. Copy this updated project into the GitHub folder

```bash
rsync -av --delete --exclude='.git' cinematch-ai-platform/ cinematch-ai-platform-github/
```

## 3. Open in VS Code

```bash
cd cinematch-ai-platform-github
code .
```

## 4. Push changes

```bash
git add .
git commit -m "Build CineMatch AI full-stack movie platform"
git push origin main
```

If branch error happens:

```bash
git branch -M main
git push -u origin main
```

If remote error happens:

```bash
git remote set-url origin https://github.com/Poojitha-g15/cinematch-ai-platform.git
git push -u origin main
```
