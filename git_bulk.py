#!/usr/bin/env python3
# git_bulk.py  —  Bulk Git helper for a folder of repositories
#
# Usage (from parent folder containing repo subfolders):
#   python git_bulk.py <command> [options]
# Or via a wrapper script/batch file called "gitb":
#   gitb <command> [options]
#
# Examples:
#   gitb status              # status for all repos
#   gitb status -o Kettle    # status for 'Kettle' only
#   gitb pull                # pull all
#   gitb pull -o Kettle -f   # force reset 'Kettle' to upstream
#   gitb push                # bulk push with default message
#   gitb push -i             # interactive push
#   gitb summary             # compact C/A/B flags per repo
#
# Windows:
#   - Ensure 'python' and 'git' are on PATH.
#   - Optional: use ssh-agent for SSH keys.
#
# Linux:
#   - Ensure 'python3' and 'git' are installed.
#   - Optional: 'chmod +x git_bulk.py' then './git_bulk.py status'.
#
# The script never stores passwords/passphrases; it just uses your normal
# shell environment (ssh-agent, Git credential manager, etc).

import os
import subprocess
import argparse
import sys


# --- ENVIRONMENT SETUP (no passphrase hacks) ---

def setup_environment():
    """
    Use the normal environment that your shell has.
    Authentication should be handled by ssh-agent (for SSH remotes)
    or Git Credential Manager (for HTTPS remotes).

    We do NOT set ASKPASS or hard-code passphrases here.
    """
    env = os.environ.copy()
    return env


GLOBAL_ENV = setup_environment()


# --- CORE UTILITIES ---

def get_git_subdirs(root_dir):
    repos = []
    items = sorted(os.listdir(root_dir))
    for item in items:
        full_path = os.path.join(root_dir, item)
        if os.path.isdir(full_path) and os.path.isdir(os.path.join(full_path, ".git")):
            repos.append(full_path)
    return repos


def find_repo(repos, target_name):
    target_lower = target_name.lower()
    for repo in repos:
        if os.path.basename(repo).lower() == target_lower:
            return repo
    print(f"❌ Repository '{target_name}' not found in {os.getcwd()}")
    return None


def run_command(command, cwd):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            env=GLOBAL_ENV,
        )
        return result
    except Exception:
        return None


# --- STATUS / SUMMARY ---

def check_status(repos):
    print(f"--- Checking Status for {len(repos)} repositories ---")
    dirty_repos = []

    for i, repo in enumerate(repos, 1):
        repo_name = os.path.basename(repo)

        sys.stdout.write(f"[{i}/{len(repos)}] Checking {repo_name}..." + " " * 20 + "\r")
        sys.stdout.flush()

        # 1. Fetch latest data
        try:
            fetch = subprocess.run(
                "git fetch",
                cwd=repo,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15,
                env=GLOBAL_ENV,
            )
        except subprocess.TimeoutExpired:
            print(f"\n❌ [{repo_name}]: TIMEOUT (Automation failed, manual check required)")
            continue

        if fetch.returncode != 0:
            err_text = fetch.stderr if fetch.stderr else "Unknown Git Error"
            first_line = err_text.strip().split("\n")[0]
            print(f"\n❌ [{repo_name}]: FETCH FAILED -> {first_line}")
            continue

        # 2. Check Local Status
        status = run_command("git status --porcelain", repo)
        ahead = run_command("git log @{u}..HEAD", repo)
        behind = run_command("git log HEAD..@{u}", repo)

        is_dirty = status and status.stdout.strip() != ""
        is_ahead = ahead and ahead.returncode == 0 and ahead.stdout.strip() != ""
        is_behind = behind and behind.returncode == 0 and behind.stdout.strip() != ""

        if is_dirty or is_ahead or is_behind:
            sys.stdout.write(" " * 60 + "\r")
            state = []
            if is_dirty:
                state.append("Uncommitted Changes")
            if is_ahead:
                state.append("Unpushed Commits")
            if is_behind:
                state.append("⬇️ Pending Pulls")
            print(f"[{repo_name}]: {', '.join(state)}")
            dirty_repos.append(repo)

    sys.stdout.write(" " * 60 + "\r")
    if not dirty_repos:
        print("All repositories are clean and up to date.")
    return dirty_repos

def summary_repos(repos, offline=False):
    print(f"--- Summary for {len(repos)} repositories ---")
    print("U=Uncommitted changes, A=Ahead (not pushed), P=Pending pulls\n")
    if offline:
        print("(offline mode: skipping 'git fetch')")

    for repo in repos:
        repo_name = os.path.basename(repo)

        # Optionally fetch
        if not offline:
            try:
                fetch = subprocess.run(
                    "git fetch",
                    cwd=repo,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=15,
                    env=GLOBAL_ENV,
                )
            except subprocess.TimeoutExpired:
                print(f"[{repo_name}]  FETCH TIMEOUT")
                continue

            if fetch.returncode != 0:
                err_text = fetch.stderr if fetch.stderr else "Unknown Git Error"
                first_line = err_text.strip().split("\n")[0]
                print(f"[{repo_name}]  FETCH FAILED: {first_line}")
                continue

        status = run_command("git status --porcelain", repo)
        ahead = run_command("git log @{u}..HEAD", repo)
        behind = run_command("git log HEAD..@{u}", repo)

        is_dirty = status and status.stdout.strip() != ""
        is_ahead = ahead and ahead.returncode == 0 and ahead.stdout.strip() != ""
        is_behind = behind and behind.returncode == 0 and behind.stdout.strip() != ""

        flags = []
        flags.append("U" if is_dirty else "-")
        flags.append("A" if is_ahead else "-")
        flags.append("P" if is_behind else "-")

        print(f"[{repo_name}]  {' '.join(flags)}")

# --- WRITE ACTIONS (push / pull) ---

def push_repo(repo, message="Auto-update"):
    repo_name = os.path.basename(repo)
    print(f"Processing {repo_name}...")
    run_command("git add .", repo)
    run_command(f'git commit -m "{message}"', repo)
    res = run_command("git push", repo)
    if res and res.returncode == 0:
        print(f"✅ {repo_name} pushed.")
    else:
        print(f"❌ {repo_name} push failed.")


def push_bulk(repos, message="Bulk auto-push", interactive=False):
    dirty_repos = check_status(repos)
    if not dirty_repos:
        return

    if interactive:
        print("\n--- Interactive Push Mode ---")
        for repo in dirty_repos:
            repo_name = os.path.basename(repo)
            choice = input(f"Push changes for '{repo_name}'? (y/n): ").lower()
            if choice == "y":
                push_repo(repo, message=message)
    else:
        print("\n--- Batch Push Mode ---")
        for repo in dirty_repos:
            push_repo(repo, message=message)


def pull_batch(repos):
    print("\n--- Batch Pull Mode ---")
    failed_repos = []
    for repo in repos:
        repo_name = os.path.basename(repo)
        print(f"Pulling {repo_name}...", end="\r")
        res = run_command("git pull", repo)
        if not res or res.returncode != 0:
            print(f"❌ {repo_name} encountered an issue.")
            failed_repos.append(repo_name)
        elif "Already up to date" not in (res.stdout or ""):
            print(f"⬇️  {repo_name} updated.")

    if failed_repos:
        print("\n⚠️  Merge conflicts/errors in:")
        for name in failed_repos:
            print(f" - {name}")
    else:
        print("\nAll repositories checked.")


def pull_single(repo):
    repo_name = os.path.basename(repo)
    print(f"Pulling {repo_name}...")
    res = run_command("git pull", repo)
    if res and res.returncode == 0:
        out = res.stdout.strip()
        print(out if out else "Already up to date.")
    else:
        print(f"❌ Pull failed: {res.stderr if res else 'Unknown error'}")


def pull_force_single(repo):
    repo_name = os.path.basename(repo)
    print(f"⚠️  Force resetting {repo_name} to match remote...")
    run_command("git fetch --all", repo)
    res = run_command("git reset --hard @{u}", repo)
    if res and res.returncode == 0:
        print(f"✅ {repo_name} synced to remote.")
    else:
        print(f"❌ Failed.")


# --- READ-ONLY HELPERS ---

def list_repos(repos):
    print(f"--- Repositories in {os.getcwd()} ---")
    for repo in repos:
        print(os.path.basename(repo))


def show_branches(repos):
    for repo in repos:
        repo_name = os.path.basename(repo)
        print(f"\n[{repo_name}] branches:")
        res = run_command("git branch --all --verbose --no-abbrev", repo)
        if res and res.returncode == 0:
            print(res.stdout.strip())
        else:
            print(f"  (error running git branch)")


def show_remotes(repos):
    for repo in repos:
        repo_name = os.path.basename(repo)
        print(f"\n[{repo_name}] remotes:")
        res = run_command("git remote -v", repo)
        if res and res.returncode == 0:
            print(res.stdout.strip())
        else:
            print(f"  (error running git remote -v)")


def show_log(repo, num_commits=5):
    repo_name = os.path.basename(repo)
    print(f"\n[{repo_name}] last {num_commits} commits:")
    cmd = f"git log -n {num_commits} --oneline --graph --decorate"
    res = run_command(cmd, repo)
    if res and res.returncode == 0:
        print(res.stdout.strip())
    else:
        print(f"  (error running git log)")


# --- MAIN CONTROLLER ---

def main():
    parser = argparse.ArgumentParser(description="Bulk Git Manager (gitb-style CLI)")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Action")

    # status
    p_status = subparsers.add_parser("status", help="Check status (fetch + local changes/ahead/behind)")
    p_status.add_argument("-o", "--one", dest="repo_name", help="Operate on a single repo")

    # pull
    p_pull = subparsers.add_parser("pull", help="Pull updates from remote")
    p_pull.add_argument("-o", "--one", dest="repo_name", help="Operate on a single repo")
    p_pull.add_argument("-f", "--force", action="store_true", help="Force reset (only with --one)")

    # push
    p_push = subparsers.add_parser("push", help="Push local changes to remote")
    p_push.add_argument("-o", "--one", dest="repo_name", help="Operate on a single repo")
    p_push.add_argument("-i", "--interactive", action="store_true", help="Interactive mode (confirm per repo)")
    p_push.add_argument("-m", "--message", default="Bulk auto-push", help="Commit message to use")

    # list
    p_list = subparsers.add_parser("list", help="List detected repositories")
    p_list.add_argument("-o", "--one", dest="repo_name", help="Show only the named repo")

    # summary
    p_summary = subparsers.add_parser("summary", help="Short summary: C/A/B flags per repo")
    p_summary.add_argument("-o", "--one", dest="repo_name", help="Operate on a single repo")
    p_summary.add_argument("--offline", action="store_true", help="Do NOT fetch before summarising")

    # branches
    p_branches = subparsers.add_parser("branches", help="Show branches in each repo")
    p_branches.add_argument("-o", "--one", dest="repo_name", help="Operate on a single repo")

    # remotes
    p_remotes = subparsers.add_parser("remotes", help="Show remotes for each repo")
    p_remotes.add_argument("-o", "--one", dest="repo_name", help="Operate on a single repo")

    # log
    p_log = subparsers.add_parser("log", help="Show last N commits for a repo")
    p_log.add_argument("-o", "--one", dest="repo_name", required=False, help="Repo name (required for log)")
    p_log.add_argument("-n", "--num", type=int, default=5, help="Number of commits to show (default: 5)")

    args = parser.parse_args()
    root_dir = os.getcwd()
    repos = get_git_subdirs(root_dir)

    # Resolve target repos if -o/--one given
    target_repos = repos
    target_repo = None
    if hasattr(args, "repo_name") and args.repo_name:
        target_repo = find_repo(repos, args.repo_name)
        if not target_repo:
            return
        target_repos = [target_repo]

    if args.command == "status":
        check_status(target_repos)

    elif args.command == "pull":
        if args.repo_name:
            if args.force:
                pull_force_single(target_repo)
            else:
                pull_single(target_repo)
        else:
            if args.force:
                print("❌ --force is only allowed when using --one / -o for pull.")
                return
            pull_batch(repos)

    elif args.command == "push":
        if args.repo_name:
            push_repo(target_repo, message=args.message)
        else:
            push_bulk(repos, message=args.message, interactive=args.interactive)

    elif args.command == "list":
        list_repos(target_repos)

    elif args.command == "summary":
        summary_repos(target_repos, offline=args.offline)

    elif args.command == "branches":
        show_branches(target_repos)

    elif args.command == "remotes":
        show_remotes(target_repos)

    elif args.command == "log":
        if not args.repo_name:
            print("❌ 'log' requires --one / -o <repo_name> to avoid spamming all repos.")
            return
        show_log(target_repo, num_commits=args.num)


if __name__ == "__main__":
    main()