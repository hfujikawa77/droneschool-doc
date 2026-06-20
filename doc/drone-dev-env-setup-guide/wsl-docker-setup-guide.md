<div align="center">
<h3>ドローンエンジニア養成塾 デベロッパーコース</h3>
<h2>WSL Docker セットアップガイド</h2><br>
(WSL2 + Ubuntu22.04 への Docker Engine インストール)<br/>
Ver.1.0.0 - 2026.6.15
</div>

<!--
Ver.1.0.0 - 2026.6.15 - 初版
-->

Table of Contents
<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [1. はじめに](#1-はじめに)
- [2. Docker Engine インストール](#2-docker-engine-インストール)
  - [2.1. 必要パッケージのインストール](#21-必要パッケージのインストール)
  - [2.2. Docker 公式リポジトリの追加](#22-docker-公式リポジトリの追加)
  - [2.3. Docker Engine のインストール](#23-docker-engine-のインストール)
  - [2.4. sudo なしで実行できるようにする](#24-sudo-なしで実行できるようにする)
- [3. 動作確認](#3-動作確認)
- [4. Docker Hub アカウント作成](#4-docker-hub-アカウント作成)
  - [4.1. アカウントの作成](#41-アカウントの作成)
  - [4.2. メールアドレスの確認](#42-メールアドレスの確認)
  - [4.3. WSL からのログイン確認](#43-wsl-からのログイン確認)

<!-- /code_chunk_output -->

<div style="page-break-before:always"></div>

# 1. はじめに

本ガイドは、WSL2（Ubuntu22.04）に Docker Engine をインストールする手順を説明します。

**前提条件**
- WSL2（Ubuntu22.04）インストール済み

> **Note:** Docker Desktop（Windows アプリ）をすでにインストールしている場合、WSL integration を有効にすることで WSL 内から Docker が使用できます。その場合、本ガイドの手順は不要です。

<div style="page-break-before:always"></div>

# 2. Docker Engine インストール

## 2.1. 必要パッケージのインストール

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
```

## 2.2. Docker 公式リポジトリの追加

```bash
# GPG キーの追加
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# リポジトリの追加
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

## 2.3. Docker Engine のインストール

```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

## 2.4. sudo なしで実行できるようにする

```bash
sudo usermod -aG docker $USER
newgrp docker
```

> **Note:** `newgrp docker` はシェルのグループを即時反映させるコマンドです。WSL を再起動した場合も設定は引き継がれます。

<div style="page-break-before:always"></div>

# 3. 動作確認

```bash
docker run hello-world
```

以下のように表示されれば成功です。

```bash
Hello from Docker!
This message shows that your installation appears to be working correctly.
~ 中略 ~
For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

<div style="page-break-before:always"></div>

# 4. Docker Hub アカウント作成

Docker Hub は Docker イメージを公開・取得するためのレジストリサービスです。アカウントを作成しておくと、イメージの取得回数制限（レート制限）が緩和され、自分のイメージを push できるようになります。

## 4.1. アカウントの作成

1. ブラウザで Docker Hub のサインアップページを開きます。
   - https://hub.docker.com/signup
2. 以下を入力して **Sign Up** をクリックします。
   - **Username**: 任意のユーザー名（小文字・数字・ハイフンが使用可能。後でイメージ名に使われます）
   - **Email**: 受信可能なメールアドレス
   - **Password**: パスワード

> **Note:** ここで決めた **Username** は、後の `docker login` やイメージ名（`ユーザー名/イメージ名`）で使用します。控えておいてください。

## 4.2. メールアドレスの確認

1. 登録したメールアドレスに Docker から確認メールが届きます。
2. メール内の **Verify email address**（メールアドレスを確認）リンクをクリックして、アカウントを有効化します。

> **Note:** メールアドレスの確認が完了していないと、`docker login` に失敗する場合があります。

## 4.3. WSL からのログイン確認

WSL のターミナルから Docker Hub にログインできることを確認します。

```bash
docker login
```

ユーザー名とパスワードの入力を求められるので、4.1 で作成したものを入力します。以下のように表示されればログイン成功です。

```bash
Login Succeeded
```

> **Note:** ログイン情報は `~/.docker/config.json` に保存され、次回以降は再入力なしで利用できます。ログアウトする場合は `docker logout` を実行します。
