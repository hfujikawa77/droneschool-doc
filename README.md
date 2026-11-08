# droneschool-doc
ドローンエンジニア養成塾（ドキュメント）

講義で使うガイド・手順書の **Markdown 正本** を管理するリポジトリです。
講義スライド側（[`droneschool-material`](https://github.com/hfujikawa77/droneschool-material)）で配布する PDF は、ここの md から作成します。

## ドキュメント一覧

| フォルダ | 内容 |
|---|---|
| [`doc/drone-dev-env-setup-guide/`](doc/drone-dev-env-setup-guide/) | 開発環境構築（ドローン開発環境 / Claude Code 環境 / BlueOS 環境 / WSL・Docker） |
| [`doc/app-dev-guide/`](doc/app-dev-guide/) | BlueOS アプリ開発ガイド |
| [`doc/docker-sitl/`](doc/docker-sitl/) | ArduPilot SITL（Docker）開発環境 |
| [`doc/git-github-guide/`](doc/git-github-guide/) | Git / GitHub ガイド（PR トレーニング Web 版・ローカル版、最新取得手順） |
| [`doc/learning-resource/`](doc/learning-resource/) | 初学者向け学習リソース |

各フォルダの `media/` は、md から参照するスクリーンショット画像です。

## 関連リポジトリ

- [`hfujikawa77/droneschool-material`](https://github.com/hfujikawa77/droneschool-material) … 講義スライド・試験などの教材
- [`hfujikawa77/droneschool`](https://github.com/hfujikawa77/droneschool) … 受講生のワークフォルダ

## 開発環境構築手順書
[手順書](doc/drone-dev-env-setup-guide/)はMarkdownで書かれています。<br/>

必要な拡張機能を入れます。<br/>
- yzhang.markdown-all-in-one
- yzane.markdown-pdf

PDFファイルを作成する場合は、Markdownファイルを開いた状態で、コマンドパレット（`F1`押下）から下記コマンドを実行してください。
1. プレビューして表示を確認するには`[Markdown: Open Preview to the Side]`を実行
2. 項番、目次の変更がある場合は`[Markdown All in One: Add/Update section numbers]` → `[Markdown All in One: Update Table TOC]`の順番で実行
4. PDFファイルにエクスポートするには`[Markdown PDF: Export(pdf)]`を実行

<br/>
※ html中間ファイルが生成された後PDF化されます。
