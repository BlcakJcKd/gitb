# Git Bulk Manager (gitb)

**Git Bulk Manager** is a lightweight, cross-platform CLI tool for managing multiple Git repositories located under a single parent directory.

It’s perfect for developers, researchers, and multi-project workflows — especially when synchronizing work across multiple machines (home, work, HPC, etc.) without manually entering each folder.

---

# 🚀 Features

- **Dashboard Overview** of all repositories (Uncommitted, Ahead, Pending Pulls).
- **Bulk Operations:** Push or Pull all repositories in one command.
- **Repository-Specific Actions:** Run commands on one repo using `-o <Name>`.
- **Cross-Platform:** Works on Windows, Linux, macOS.
- **Credential-Safe:** Does *not* store passwords/passphrases; relies on SSH Agent or Git Credential Manager.
- **Smart Automation:** Skips repositories with errors and provides clear feedback.

---

# 🧠 Why This Exists

Managing 10+ Git repositories is common in:
- research labs  
- robotics projects  
- multi-module software systems  
- IoT + data collection pipelines  
- PhD workflows (your use-case)  

Traditional tooling requires entering each folder manually.

**gitb** solves this with:
- a *concise multi-repo status dashboard*
- bulk pull/push actions
- git-style commands and flags  

All while staying safe and simple.

---

# 📋 Prerequisites

- **Python 3.6+**
- **Git** in PATH
- **SSH keys** recommended for smooth authentication

---

# 🛠️ Installation

## Option A: Windows (PowerShell / CMD)

### Easiest installation — create a wrapper script
1. Save `git_bulk.py` somewhere, e.g.:  
   `C:\Users\YourName\Scripts\git_bulk.py`

2. Create a file named `gitb.cmd` in the same folder:

    ```cmd
    @echo off
    python "C:\Users\YourName\Scripts\git_bulk.py" %*
    ```

3. Add `C:\Users\YourName\Scripts` to your **PATH**.

That’s it — now you can run:

````

gitb status

````

### Optional: Build a standalone EXE with PyInstaller

```powershell
pip install pyinstaller
pyinstaller --onefile --name gitb git_bulk.py
````

Move `gitb.exe` into a folder on your PATH.

---

## Option B: Linux (Ubuntu/Debian)

```bash
mkdir -p ~/scripts
cp git_bulk.py ~/scripts/
chmod +x ~/scripts/git_bulk.py
sudo ln -s ~/scripts/git_bulk.py /usr/local/bin/gitb
```

Usage:

```bash
gitb status
```

---

# 📖 Usage & Cheatsheet

Run `gitb` inside a **parent directory** containing Git repositories.

---

## 📊 Dashboard & Status

| Command                  | Description                              |
| ------------------------ | ---------------------------------------- |
| **`gitb summary`**       | Overview of statuses using U/A/P flags.  |
| `gitb summary --offline` | No remote fetch (faster, works offline). |
| `gitb status`            | Detailed fetch + status report.          |
| `gitb list`              | List all repository folders detected.    |

### Legend

* **U** = **Uncommitted changes**
* **A** = **Ahead (not pushed)**
* **P** = **Pending pulls (remote has newer commits)**

---

## ⬇️ Pulling (Get Updates)

| Command                  | Description                                  |
| ------------------------ | -------------------------------------------- |
| **`gitb pull`**          | Pull updates for *all* repositories.         |
| `gitb pull -o <Name>`    | Pull only for `<Name>`.                      |
| `gitb pull -o <Name> -f` | ⚠️ Force reset — discards all local changes. |

---

## ⬆️ Pushing (Upload Changes)

| Command                  | Description                                                           |
| ------------------------ | --------------------------------------------------------------------- |
| **`gitb push`**          | Bulk push all repos with changes. ⚠️ Auto-commits all modified repos. |
| `gitb push -i`           | Interactive — asks before each push.                                  |
| `gitb push -o <Name>`    | Push only `<Name>`.                                                   |
| `gitb push -m "Message"` | Custom commit message.                                                |

---

## 🔍 Diagnostics & Info

| Command                    | Description                   |
| -------------------------- | ----------------------------- |
| `gitb branches`            | Show local + remote branches. |
| `gitb remotes`             | Show remote URLs.             |
| `gitb log -o <Name>`       | Last 5 commits for `<Name>`.  |
| `gitb log -o <Name> -n 10` | Last 10 commits.              |

---

# ⚠️ Troubleshooting

### Password prompts or authentication errors

Usually caused by SSH agent not running.

**Windows:**

```powershell
ssh-add -l
ssh-add "$env:USERPROFILE\.ssh\id_ed25519"
```

**Linux:**

```bash
ssh-add -l
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### Repo not detected

Ensure you're running inside the parent directory containing Git repos.

---

# 📄 License

Free for personal or commercial use.
Modify it to suit your workflow.

---
