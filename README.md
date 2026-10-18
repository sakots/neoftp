# neoftp

PaintBBS NEOのmasterブランチをGitHubから取得し、distの内容をFTPSで配置するツールです。

## 必要なもの

- Python 3.10以上（追加パッケージ不要）
- Git
- 明示的FTPS（ポート21）に対応したサーバーと、有効なTLS証明書

## 設定

`~/dev/neoftp.env` を作成してください。

```bash
HOST="ftp.example.com"
USER="your-user"
PASS="your-password"
LOCAL_DIR="~/dev/neoftp/neo/dist"
REMOTE_DIR="/apps/neo"
```

`HOST`はホスト名のみを指定します。`REMOTE_DIR`はFTPログイン後のファイルシステム上のパスです。公開URLのパスと一致するとは限らないため、サーバーの設定に合わせてください。

設定は `KEY=VALUE` 形式で、空白を含む値は引用符で囲みます。シェルスクリプトとして実行しないため、コマンド置換はできません。`LOCAL_DIR`では `~` と環境変数を展開し、相対パスはneoftpディレクトリを基準にします。

認証情報をリポジトリに含めず、設定ファイルの権限を制限してください。

```bash
chmod 600 ~/dev/neoftp.env
```

## 実行

```bash
python3 neoftp.py
# 別の設定ファイルを使う場合
python3 neoftp.py --config /path/to/neoftp.env
```

初回はneoftp内の `neo/` に [funige/neo](https://github.com/funige/neo) のmasterブランチをcloneします。次回以降は `git pull --ff-only` で更新します。既存のチェックアウトに変更がある場合や、origin・ブランチが異なる場合は停止します。上流にdistが含まれるため、ビルドは行いません。

更新後、`LOCAL_DIR`直下の `neo.js` と `neo.css` だけをアップロードします。どちらかが存在しない場合やシンボリックリンクの場合は、接続前に停止します。他のファイルやサブディレクトリはアップロードしません。接続とデータ転送の両方をTLSで暗号化し、証明書を検証します。必要なリモートディレクトリは作成し、同名ファイルは上書きします。リモート側だけにあるファイルは削除しません。

成功時は終了コード0、失敗時は1です。アップロードは一括切り替えではないため、途中で失敗すると一部だけ更新される場合があります。原因を解消して再実行してください。

## 更新履歴

### [2026/10/19] v0.2.1

- アップロード対象を `neo.js` と `neo.css` のみに変更。
- 必須ファイルがない場合、接続前に停止するよう修正。

### [2026/10/19] v0.2.0

- PaintBBS NEOのmasterブランチをclone・pullする機能を追加。
- 設定ファイルに基づきdistをFTPSで再帰配置する機能を追加。
- TLS証明書の検証と、既存チェックアウトの変更を保護する処理を追加。

### [2026/10/19] v0.1.0

- リポジトリ生やした
