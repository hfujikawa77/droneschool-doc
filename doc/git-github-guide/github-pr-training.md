## ドローンエンジニア養成塾 Pull Request 演習
### 1. はじめに
   - 本演習の目的はArduPilotプロジェクトに貢献手段であるPull Requestの作成方法を学ぶことです。
   - 本演習は[ArduPilot WikiのGitチュートリアル](https://ardupilot.org/dev/docs/git-branch.html)をGitHub Webページ上の操作で完結するようにアレンジしたものです。実際の開発ではローカルにリポジトリをCloneして行います。  
   ![alt text](media/github-pr-training-009.jpg)
   - GitHubアカウントを持ってない人は、[GitHubアカウント作成手順](https://docs.github.com/ja/get-started/start-your-journey/creating-an-account-on-github) を参照して、アカウントを作成してください。

### 2. リポジトリのフォーク
   1. [ArduPilotリポジトリ](https://github.com/ardupilot/ardupilot)にアクセスします。
   1. ページ右上の`Fork`ボタンをクリックして、リポジトリを自分のアカウントにフォークします。  
   ![alt text](media/github-pr-training-010.jpg)

### 3. 新しいブランチ作成
   1. フォークしたリポジトリのページ `https://github.com/＜GitHubアカウント名＞/ardupilot` に移動します。
   1. リポジトリページの上部にあるブランチのドロップダウンリストから`master`を選択します。
   1. ブランチのドロップダウンの下部にある`Find or create a branch`フィールドに新しいブランチ名`ardupilot_git_tutorial` を入力します。  
   1. ボタン名が`Create branch ardupilot_git_tutorial from master`になっていることを確認してクリックします。  
   ![alt text](media/github-pr-training-020.jpg)
   1. 新しく作成されたブランチ`ardupilot_git_tutorial` に切り替わっていることを確認します。  
   ![alt text](media/github-pr-training-030.jpg) 

<div style="page-break-before:always"></div>

### 4. ファイル変更とコミット&プッシュ
   1. フォークしたリポジトリのメインページに戻り、ブランチ`ardupilot_git_tutorial` が選択されていることを確認します。
   2. `Tools/GIT_Test/GIT_Success.txt` ファイルを開きます。
   3. キーボードの`.`をクリックします。VS Code Web版が起動することを確認します。
   4. ファイル`GIT_Success.txt`を開き、末尾に自分の名前（firstname lastname）を追加します。
   5. `Ctrl + S`をクリックして変更を保存します。  
   6. 画面左側メニューから`ソース管理`をクリックします。  
   ![alt text](media/github-pr-training-050.jpg)
   7. `GIT_Success.txt` を右クリックして、`変更のステージング`をクリックします。  
   ![alt text](media/github-pr-training-060.jpg)
   8. メッセージに下記を入力して`コミットとプッシュ`ボタンをクリックします。この操作によりファイル変更がフォークしたリポジトリに反映されます。
      ```
      Tools: add name to GIT_Success.txt
      ```
      ![alt text](media/github-pr-training-070.jpg)

<div style="page-break-before:always"></div>

### 5. Pull Requestの作成
   1. フォークしたリポジトリのメインページに戻り、 `Compare & pull request`ボタンをクリックします。  
   ![alt text](media/github-pr-training-080.jpg)
   1. 比較するベースとなるリポジトリとブランチ、そして自分のフォークしたリポジトリとブランチを選択します。
       - **base repository**: `Ardupilot/ardupilot`
       - **base**: `master`
       - **head repository**: `＜GitHubアカウント名＞/ardupilot`
       - **compare**: `ardupilot_git_tutorial`
   1. タイトルと本文を以下のように入力します。
      ```
      Tools: add name to GIT_Success.txt
      ```
      ![alt text](media/github-pr-training-090.jpg)
   1. `Create pull request`ボタンをクリックして、Pull Requestを作成します。  
      ![alt text](media/github-pr-training-100.jpg)
   3. ArduPilotリポジトリの [Pull requestsタブ](https://github.com/ArduPilot/ardupilot/pulls) を開いてPull Requestが作成されていることを確認します。

### 6. ArduPilot本線の変更の取り込み
   1. フォークしたリポジトリのメインページに戻り、 ブランチ`master`を選択します。
   1. `Sync fork`ボタンをクリックします。
   1. `Update Branch`ボタンをクリックします。ArduPilot本線の最新の変更が取り込まれたことを確認します。  
   ![alt text](media/github-pr-training-110.jpg)