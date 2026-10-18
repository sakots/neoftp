# AGENTS.md

neoftpは、Githubからpaintbbs NEOの最新版をダウンロードして、[https://oekakibbs.moe/apps/neo/]([https://oekakibbs.moe/apps/neo/)にFTPSで配置するツールです。

## Paintbbs NEOの場所

paintbbs NEOの最新版は、[https://github.com/funige/neo](https://github.com/funige/neo)のmasterブランチです。

## 設定ファイル

FTPの設定ファイルは、`~/dev/neoftp.env`に置きます。

```bash
HOST="(配置ホスト)"
USER="(ユーザー)"
PASS="(パスワード)"
LOCAL_DIR="(ローカルのneoのdistディレクトリ)"
REMOTE_DIR="(アップロード先)"
```

## neoのダウンロード

NEOはneoftpディレクトリ内にGithubからクローン、pullします。

## 更新履歴加筆の際の注意

- `README.md`と`changelog.md`に更新履歴を記入する。
- 更新履歴の形式は、`### [YYYY/MM/DD] vx.x.x`のあとに箇条書き。
- ～～を修正、～～の機能を追加、のような形式で書くこと。
