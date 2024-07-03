### アプリケーション編 Workshop用 GitHub準備
1. **前提事項**: 
   - CC環境構築手順書（`cc-dev-env-setup-guide.pdf`）の手順が完了しており、`http://github.com/tajisoft/droneschool` からcloneされていること。
   - [GitHubアカウント作成](https://docs.github.com/ja/get-started/start-your-journey/creating-an-account-on-github) が完了していること。

2. **リポジトリのフォーク**:
   - GitHubで、`https://github.com/tajisoft/droneschool` を開きます。
   - ページ右上の`Fork`ボタンをクリックして、リポジトリを自分のアカウントにフォークします。

3. **既存のローカルリポジトリの設定変更**:
   - 既にcloneしているローカルGitリポジトリに移動します。
     ```bash
     cd 
     cd GitHub/droneschool
     ```
   - 現在のリモートリポジトリのURLを確認します。
     ```bash
     git remote -v
     ```
   - `origin` を自分のフォークしたリポジトリのURLに変更します。  
     URLの `＜GitHubアカウント名＞` はご自身のアカウント名に置き換えてください。（例: `https://github.com/hfujikawa77/droneschool.git`）
     ```bash
     git remote set-url origin https://github.com/＜GitHubアカウント名＞/droneschool.git
     git remote -v    # 変更が反映されていることを確認
     ```
   - 元のリポジトリを `upstream` として追加します。
     ```bash
     git remote add upstream https://github.com/tajisoft/droneschool.git
     git remote -v    # upstream リモートリポジトリが追加されたことを確認
     ```

1. **新しいブランチを作成し、チェックアウトする**:
   - ブランチ名の `＜fname-lname＞` はご自身の氏名に置き換えてください。（例: `17th_hideyuki-fujikawa` ）
     ```bash
     git checkout -b 17th_＜fname-lname＞
     ```

2. **ディレクトリとファイルを作成する**:
   - 作業ディレクトリを作成します。  
     ディレクトリ名の ＜fname-lname＞ はご自身の氏名に置き換えてください。（例: `workshop/17th/hideyuki-fujikawa` ）
     ```bash
     mkdir -p workshop/17th/＜fname-lname＞
     ```
   - README.md ファイルを作成してテキストを追加します。
     ```bash
     echo "Hello, ArduPilot!" > workshop/17th/＜fname-lname＞/README.md
     ```

1. **変更をステージングし、コミットする**:
   - 変更をステージングします。
     ```bash
     git add workshop/17th/＜fname-lname＞/README.md
     ```
   - コミットメッセージを付けてコミットします。
     ```bash
     git commit -m "Add 17th workshop folder with README.md"
     ```

2. **変更をリモートリポジトリにプッシュする**:
   ```bash
   git push origin 17th_＜fname-lname＞
   ```

3. **Pull Requestの作成**:
   - GitHubの `https://github.com/＜GitHubアカウント名＞/droneschool/pulls` ページに移動します。
   - `New pull request`ボタンをクリックします。
   - 比較するベースとなるリポジトリとブランチ、そして自分のフォークしたリポジトリとブランチを選択します。
     - **base repository**: `tajisoft/droneschool`
     - **base**: `master`
     - **head repository**: `＜GitHubアカウント名＞/droneschool`
     - **compare**: `17th_＜fname-lname＞`
   - Pull Requestのタイトルと本文を入力し、 `Create pull request`ボタンをクリックして、Pull Requestを作成します。

