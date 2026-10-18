#!/usr/bin/env python3
"""Update PaintBBS NEO and deploy its distribution over explicit FTPS."""

import argparse
import ftplib
import os
from pathlib import Path
import shlex
import ssl
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
UPSTREAM = "https://github.com/funige/neo.git"


def load_config(path):
    values = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        tokens = shlex.split(line, comments=True)
        if not tokens:
            continue
        if len(tokens) != 1 or "=" not in tokens[0]:
            raise ValueError(f"設定ファイルの{number}行目は KEY=VALUE 形式にしてください")
        key, value = tokens[0].split("=", 1)
        values[key] = value
    for key in ("HOST", "USER", "PASS", "LOCAL_DIR", "REMOTE_DIR"):
        if not values.get(key):
            raise ValueError(f"設定に {key} が必要です")
        if "\r" in values[key] or "\n" in values[key]:
            raise ValueError(f"{key} に改行は使用できません")
    return values


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def update_neo():
    repo = ROOT / "neo"
    if not repo.exists():
        subprocess.run(["git", "clone", "--branch", "master", "--single-branch", UPSTREAM, str(repo)], check=True)
        return
    if not (repo / ".git").is_dir():
        raise ValueError("neo/ はGitリポジトリではありません")
    if git("-C", str(repo), "remote", "get-url", "origin") != UPSTREAM:
        raise ValueError("neo/ のoriginがNEO公式リポジトリではありません")
    if git("-C", str(repo), "branch", "--show-current") != "master":
        raise ValueError("neo/ のブランチがmasterではありません")
    if git("-C", str(repo), "status", "--porcelain"):
        raise ValueError("neo/ に未コミットの変更があります。更新を中止しました")
    subprocess.run(["git", "-C", str(repo), "pull", "--ff-only", "origin", "master"], check=True)


def enter_directory(ftp, path):
    for part in path.split("/"):
        if not part or part == ".":
            continue
        try:
            ftp.cwd(part)
        except ftplib.error_perm as exc:
            if not str(exc).startswith("550"):
                raise
            ftp.mkd(part)
            ftp.cwd(part)


def upload_files(ftp, files):
    for entry in files:
        with entry.open("rb") as stream:
            ftp.storbinary(f"STOR {entry.name}", stream)
        print(f"アップロード: {entry.name}")
    return len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path.home() / "dev/neoftp.env", help="設定ファイル (既定: ~/dev/neoftp.env)")
    args = parser.parse_args()
    try:
        config = load_config(args.config.expanduser())
        local = Path(os.path.expandvars(config["LOCAL_DIR"])).expanduser()
        if not local.is_absolute():
            local = ROOT / local
        update_neo()
        files = [local / name for name in ("neo.js", "neo.css")]
        for entry in files:
            if entry.is_symlink() or not entry.is_file():
                raise ValueError(f"配布ファイルがないかシンボリックリンクです: {entry}")
        with ftplib.FTP_TLS(context=ssl.create_default_context(), timeout=60) as ftp:
            ftp.connect(config["HOST"], 21)
            ftp.login(config["USER"], config["PASS"])
            ftp.prot_p()
            if config["REMOTE_DIR"].startswith("/"):
                ftp.cwd("/")
            enter_directory(ftp, config["REMOTE_DIR"])
            count = upload_files(ftp, files)
            ftp.quit()
        print(f"配置完了: {count}ファイル")
        return 0
    except (OSError, ValueError, EOFError, ftplib.Error, subprocess.CalledProcessError):
        # Server replies can echo credentials; do not print raw exceptions.
        print("配置失敗: 設定、Gitの状態、接続先・証明書・アクセス権を確認してください", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
