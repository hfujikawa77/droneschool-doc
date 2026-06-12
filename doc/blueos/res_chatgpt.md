BlueOS × pymavlink アプリ開発演習カリキュラム

目的

本演習では、ArduPilot/BlueOS環境向けの Companion Computer アプリケーション開発を学ぶ。

受講者は以下のステップで学習を進める。

WSL + SITL
↓
pymavlink基礎
↓
BlueOS + SITL
↓
Docker化
↓
BlueOS Extension化
↓
実機接続
↓
運用自動化

最終的には、

「BlueOS Extensionとして動作するドローン支援アプリ」

を開発できることを目標とする。

---

第1部 WSL編

目的

ArduPilot、MAVLink、pymavlinkの基礎を学ぶ。

実機やBlueOSを使わずにPCのみで開発できる状態を作る。

---

演習1 MAVLink接続

学習内容

- SITL起動
- pymavlink接続
- HEARTBEAT受信

成果物

master = mavutil.mavlink_connection("udp:127.0.0.1:14550")

接続確認プログラム

---

演習2 テレメトリ取得

学習内容

- HEARTBEAT
- GLOBAL_POSITION_INT
- SYS_STATUS
- ATTITUDE

成果物

Mode : GUIDED
Alt  : 10m
GPS  : 3D Fix
Bat  : 15.8V

---

演習3 コマンド送信

学習内容

- ARM
- DISARM
- モード変更

成果物

arm()
disarm()
set_mode()

---

演習4 自動離陸

学習内容

- GUIDED
- TAKEOFF

成果物

takeoff(10)

---

演習5 自動航行

学習内容

- SET_POSITION_TARGET_GLOBAL_INT
- GOTO

成果物

goto(lat, lon, alt)

---

演習6 イベント監視

学習内容

状態変化の検出

- ARM
- DISARM
- MODE変更
- RTL

成果物

ARMされました
RTL開始

---

第2部 BlueOS編

目的

ローカルスクリプトから、Companion Computerアプリケーションへ発展させる。

---

演習1 BlueOS接続

学習内容

- MAVLink Router
- Endpoint
- BlueOSネットワーク構成

成果物

BlueOS経由で接続

udp:192.168.x.x:14550

---

演習2 MAVLink Router理解

学習内容

データ経路の理解

FC
↓
MAVLink Router
↓
Mission Planner
↓
QGroundControl
↓
Python App

成果物

ネットワーク構成図

---

演習3 MAVLink2REST利用

学習内容

- REST API
- JSON取得

成果物

requests.get(...)

高度取得ツール

---

演習4 Web API化

学習内容

FastAPI

成果物

/status
/arm
/disarm
/takeoff

を持つAPIサーバ

---

演習5 Docker化

学習内容

- Dockerfile
- コンテナ実行

成果物

docker build
docker run

可能なアプリ

---

演習6 BlueOS Extension化

学習内容

- metadata.json
- Extension構造
- BlueOS統合

成果物

BlueOS左メニューに

Drone Monitor

を追加

---

演習7 Web UI開発

学習内容

表示系UI

- 高度
- GPS
- モード
- バッテリー

成果物

ブラウザで状態監視

---

演習8 操作パネル

学習内容

操作系UI

- ARM
- DISARM
- TAKEOFF
- RTL

成果物

Mission Plannerなしで基本操作

---

第3部 実機編

目的

BlueOS Extensionを実機で利用する。

変更点は接続先のみ。

---

演習1 実機接続

学習内容

- Telemetry接続
- 状態取得

成果物

実機モニタリング

---

演習2 フェイルセーフ監視

学習内容

異常検知

- GPS異常
- バッテリー低下
- EKF異常
- RC喪失

成果物

警告システム

---

演習3 通知連携

学習内容

外部通知

- LINE
- Discord
- Telegram
- Slack

成果物

運用通知

---

演習4 音声連携

学習内容

StackChan連携

成果物

ARMしました
RTL開始
バッテリー低下です

音声通知

---

最終課題

BlueOS Extension版 ドローン見守りシステム

表示機能

- ARM状態
- Flight Mode
- GPS状態
- 高度
- バッテリー

操作機能

- ARM
- DISARM
- TAKEOFF
- RTL

通知機能

- LINE通知
- Discord通知
- StackChan通知

異常検知

- GPS異常
- Battery異常
- EKF異常
- Failsafe発生

---

発展課題

AI副操縦士

自然言語

10mまで上昇
RTLして

↓

MAVLinkコマンド変換

---

AprilTag追従

ビジョンベース制御

---

YOLO物体検出

人物・車両検出

---

音声操縦

StackChan音声入力

---

複数機管理

複数機の同時監視・制御

---

このカリキュラムの狙い

受講者が学ぶのは単なるPythonではなく、

MAVLink
↓
Companion Computer
↓
Docker
↓
BlueOS
↓
Extension開発
↓
実機運用

という、現在のArduPilotエコシステムで実際に使われている開発手法そのものである。

WSLで開発したコードが、そのままBlueOS Extensionになり、そのまま実機で動作する構成を目指す。
