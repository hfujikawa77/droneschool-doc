<div align="center">
<h3>ドローンエンジニア養成塾 デベロッパーコース</h3>
<h2>BlueOS アプリ開発ガイド</h2><br>
(WSL2 + SITL → BlueOS Extension 開発)<br/>
Ver.1.1.0 - 2026.6.18
</div>

Table of Contents
<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [1. はじめに](#1-はじめに)
  - [1.1. 学習の流れ](#11-学習の流れ)
  - [1.2. 前提条件](#12-前提条件)
- [2. BlueOS アーキテクチャ](#2-blueos-アーキテクチャ)
  - [2.1. BlueOS とは](#21-blueos-とは)
  - [2.2. コンテナ構成とサービス](#22-コンテナ構成とサービス)
  - [2.3. MAVLink Router の役割](#23-mavlink-router-の役割)
- [3. 第1部 WSL編 ― pymavlink 基礎](#3-第1部-wsl編--pymavlink-基礎)
  - [3.1. 演習1 MAVLink接続](#31-演習1-mavlink接続)
  - [3.2. 演習2 テレメトリ取得](#32-演習2-テレメトリ取得)
  - [3.3. 演習3 コマンド送信](#33-演習3-コマンド送信)
  - [3.4. 演習4 自動離陸](#34-演習4-自動離陸)
  - [3.5. 演習5 自動航行](#35-演習5-自動航行)
  - [3.6. 演習6 イベント監視](#36-演習6-イベント監視)
- [4. 第2部 BlueOS編 ― Companion Computer アプリ開発](#4-第2部-blueos編--companion-computer-アプリ開発)
  - [4.1. 演習1 BlueOS 接続](#41-演習1-blueos-接続)
  - [4.2. 演習2 MAVLink Router 理解](#42-演習2-mavlink-router-理解)
  - [4.3. 演習3 MAVLink2REST 利用](#43-演習3-mavlink2rest-利用)
  - [4.4. 演習4 アプリ開発（Vibe コーディング）](#44-演習4-アプリ開発vibe-コーディング)
  - [4.5. 演習5 BlueOS Extension 化（`/dronify-blueos`）](#45-演習5-blueos-extension-化dronify-blueos)
  - [4.6. 演習6 BlueOS への配布（build / push / install）](#46-演習6-blueos-への配布build--push--install)
- [5. 第3部 実機編 ― BlueOS Extension を実機で運用](#5-第3部-実機編--blueos-extension-を実機で運用)
  - [5.1. 演習1 実機接続](#51-演習1-実機接続)
  - [5.2. 演習2 フェイルセーフ監視](#52-演習2-フェイルセーフ監視)
  - [5.3. 演習3 通知連携](#53-演習3-通知連携)
- [6. 最終課題](#6-最終課題)
  - [BlueOS Extension版 ドローン見守りシステム](#blueos-extension版-ドローン見守りシステム)
    - [機能要件](#機能要件)
    - [成果物の構成](#成果物の構成)
- [7. 発展課題](#7-発展課題)
    - [AI 副操縦士](#ai-副操縦士)
    - [AprilTag 追従](#apriltag-追従)
    - [YOLO 物体検出](#yolo-物体検出)
    - [複数機管理](#複数機管理)
- [8. Appendix](#8-appendix)
  - [8.1. BlueOS](#81-blueos)
  - [8.2. MAVLink2REST](#82-mavlink2rest)
  - [8.3. pymavlink](#83-pymavlink)
  - [8.4. FastAPI](#84-fastapi)
  - [8.5. Docker](#85-docker)
  - [8.6. 参考リンク](#86-参考リンク)

<!-- /code_chunk_output -->

<div style="page-break-before:always"></div>

# 1. はじめに

本ガイドは、ArduPilot / BlueOS 環境向けの **Companion Computer アプリケーション開発** を学ぶための演習カリキュラムです。

WSL 上のシミュレータ (SITL) で動作確認したコードを、そのまま BlueOS Extension として Raspberry Pi 上で動かすことを最終目標とします。

> **演習の進め方（3分クッキング形式）**
> 演習時間中は、**完成済みのアプリ（素版 / BlueOS版）を使って動作を確認**します（料理番組のように、完成品を見ながら要点をおさえる形式）。
> アプリ自体を **Vibe コーディングで生成する作業（演習4）、`/dronify-blueos` で BlueOS 化する作業（演習5）、BlueOS への配布（演習6）は、各自の宿題**として取り組んでください。
> 完成版・プロンプト・スキルはすべて `droneschool` リポジトリに収録されています（取り込み方は第2部冒頭を参照）。

## 1.1. 学習の流れ

```
WSL + SITL
    ↓  pymavlink でドローンと通信する基礎を身につける
pymavlink 基礎
    ↓  ローカルスクリプトを Companion Computer アプリへ発展させる
BlueOS + SITL
    ↓  再現性のある配布形式にする
Docker 化
    ↓  BlueOS の左メニューに組み込む
BlueOS Extension 化
    ↓  コードを変えずに実機に接続する
実機接続
    ↓  運用レベルの機能を追加する
運用自動化
```

## 1.2. 前提条件

本ガイドを進める前に、下記の環境構築ガイドを完了しておいてください。

> **[開発環境構築手順書](../drone-dev-env-setup-guide/drone-dev-env-setup-guide.md)**
> Windows10/11 + WSL2 (Ubuntu22.04) + Visual Studio Code

完了済みであること：

| チェック | 内容 |
|--------|------|
| ☐ | WSL2 (Ubuntu22.04) インストール済み |
| ☐ | ArduPilot ビルド環境セットアップ済み |
| ☐ | SITL 起動確認済み |
| ☐ | pymavlink インストール済み |
| ☐ | Docker インストール済み（第2部から必要） |
| ☐ | `droneschool` リポジトリをフォーク＆クローン済み・ワークブランチ作成済み（[環境構築手順書 9.4](../drone-dev-env-setup-guide/drone-dev-env-setup-guide.md#94-課題提出用githubリポジトリ準備)） |
| ☐ | `droneschool` の master を自分のブランチに取り込み済み（`vibe-coding/` と `.claude/skills/dronify-blueos/` がある。第2部冒頭参照） |
| ☐ | AIコーディングエージェント（Claude Code / Codex / GitHub Copilot CLI のいずれか）が使える状態 |

<div style="page-break-before:always"></div>

# 2. BlueOS アーキテクチャ

## 2.1. BlueOS とは

BlueOS は Blue Robotics が開発した、Raspberry Pi 上で動作する **Companion Computer OS** です。
ArduPilot フライトコントローラーと連携し、Web UI による設定・監視・Extension（拡張アプリ）の管理を提供します。

- GitHub: https://github.com/bluerobotics/BlueOS
- ポート 80 の Web UI からすべての操作が可能
- Docker コンテナとして各サービスが分離されている

## 2.2. コンテナ構成とサービス

BlueOS は Docker Compose で複数のサービスを管理します。主要サービスとポートは以下の通りです。

| ポート | サービス | 用途 |
|--------|---------|------|
| 80 | NGINX (フロントエンド) | Web UI のエントリポイント |
| 81 | Helper | サービスディスカバリ / システム情報 API |
| 6040 | MAVLink2REST | MAVLink ↔ REST API 変換 |
| 8000 | ArduPilot Manager | フライトコントローラー管理 API |
| 9134 | Kraken | Extension のインストール・管理 |
| 8088 | ttyd | ブラウザ上のターミナル |
| 7777 | File Browser | ファイルブラウザ |

NGINX がリバースプロキシとして各サービスを `/helper/`, `/mavlink2rest/`, `/ardupilot-manager/`, `/kraken/` などのパスで公開しています。

## 2.3. MAVLink Router の役割

フライトコントローラー (FC) からの MAVLink データを複数のクライアントに同時配信します。

```
FC (シリアル)
    ↓
MAVLink Router (BlueOS内部)
    ├─→ Mission Planner (外部PC・UDP)
    ├─→ QGroundControl (外部PC・UDP)
    ├─→ MAVLink2REST (ポート6040)
    └─→ Extension アプリ (BlueOS内部・host.docker.internal:14550)
```

外部 PC からの監視は Mission Planner / QGroundControl が `192.168.42.1:14550` に接続して行います（演習1）。
一方、自作の **Extension アプリは BlueOS 上で動作**し、内部から `host.docker.internal:14550` 経由で同じ Router に接続します（演習6以降）。

<div style="page-break-before:always"></div>

# 3. 第1部 WSL編 ― pymavlink 基礎

**目的:** ArduPilot・MAVLink・pymavlink の基礎を学ぶ。実機や BlueOS を使わず、PC のみで開発できる状態を作る。

SITL を起動した状態で各演習を進めてください。

```bash
# SITL 起動
sim_vehicle.py -v Copter --map --console -L Kawachi
```

> **作業フォルダの約束**
> 各演習の課題ソースは、自分のワークフォルダ `~/GitHub/droneschool/workshop/<期>/<名前>/` の下に作成してください（例: `~/GitHub/droneschool/workshop/21st/hideyuki-fujikawa/`）。ワークブランチと作業ディレクトリの作り方は [環境構築手順書 9.4](../drone-dev-env-setup-guide/drone-dev-env-setup-guide.md#94-課題提出用githubリポジトリ準備) を参照してください。

---

## 3.1. 演習1 MAVLink接続

**学習内容**
- SITL への pymavlink 接続
- HEARTBEAT 受信による接続確認

**手順**

```python
from pymavlink import mavutil

# SITL に UDP で接続
master = mavutil.mavlink_connection("tcp:127.0.0.1:5762")

# 最初の HEARTBEAT を待つ（接続確認）
master.wait_heartbeat()
print("接続成功")
print(f"  System ID  : {master.target_system}")
print(f"  Component  : {master.target_component}")
```

**成果物:** SITL への接続確認プログラム

---

## 3.2. 演習2 テレメトリ取得

**学習内容**
- HEARTBEAT・GLOBAL_POSITION_INT・SYS_STATUS・ATTITUDE メッセージの受信と解析

**手順**

```python
from pymavlink import mavutil

master = mavutil.mavlink_connection("tcp:127.0.0.1:5762")
master.wait_heartbeat()

# TCP で SITL に直接接続した場合、テレメトリは自動送出されない。
# MAVProxy 経由の UDP 接続では MAVProxy がストリーム要求を代行するが、
# 直接接続ではこの要求を自分で送る必要がある。
master.mav.request_data_stream_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL,
    10,   # 10 Hz
    1     # 開始
)

while True:
    msg = master.recv_match(
        type=["GLOBAL_POSITION_INT", "SYS_STATUS", "ATTITUDE"],
        blocking=True
    )
    if msg is None:
        continue

    if msg.get_type() == "GLOBAL_POSITION_INT":
        print(f"Alt  : {msg.relative_alt / 1000:.1f} m")
        print(f"GPS  : ({msg.lat / 1e7:.6f}, {msg.lon / 1e7:.6f})")

    if msg.get_type() == "SYS_STATUS":
        print(f"Bat  : {msg.voltage_battery / 1000:.1f} V")
```

**期待出力例**

```
Alt  : 10.0 m
GPS  : (35.879129, 140.339683)
Bat  : 15.8 V
```

---

## 3.3. 演習3 コマンド送信

**学習内容**
- ARM / DISARM / モード変更コマンドの送信

**手順**

```python
from pymavlink import mavutil

master = mavutil.mavlink_connection("tcp:127.0.0.1:5762")
master.wait_heartbeat()

def set_mode(mode_name):
    mode_id = master.mode_mapping()[mode_name]
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )

def arm():
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0
    )

def disarm():
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 0, 0, 0, 0, 0, 0, 0
    )

set_mode("GUIDED")
arm()
```

---

## 3.4. 演習4 自動離陸

**学習内容**
- GUIDED モードへの移行と TAKEOFF コマンド

**手順**

```python
import time
from pymavlink import mavutil

master = mavutil.mavlink_connection("tcp:127.0.0.1:5762")
master.wait_heartbeat()

# GUIDED モードに設定
mode_id = master.mode_mapping()["GUIDED"]
master.mav.set_mode_send(
    master.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    mode_id
)

# ARM
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 1, 0, 0, 0, 0, 0, 0
)
time.sleep(2)

# 高度 10m まで離陸
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0, 0, 0, 0, 0, 0, 0, 10
)
print("離陸コマンド送信 (目標高度: 10m)")
```

**成果物:** `takeoff(altitude)` 関数

---

## 3.5. 演習5 自動航行

**学習内容**
- `SET_POSITION_TARGET_GLOBAL_INT` による GOTO コマンド

**手順**

```python
from pymavlink import mavutil

master = mavutil.mavlink_connection("tcp:127.0.0.1:5762")
master.wait_heartbeat()

def goto(lat, lon, alt):
    master.mav.set_position_target_global_int_send(
        0,                                          # time_boot_ms
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b0000111111111000,                         # type_mask (位置のみ有効)
        int(lat * 1e7),                             # lat_int
        int(lon * 1e7),                             # lon_int
        alt,                                        # alt (m)
        0, 0, 0,                                    # vx, vy, vz
        0, 0, 0,                                    # afx, afy, afz
        0, 0                                        # yaw, yaw_rate
    )

goto(35.880000, 140.340000, 10)
print("GOTO コマンド送信")
```

**成果物:** `goto(lat, lon, alt)` 関数

---

## 3.6. 演習6 イベント監視

**学習内容**
- 状態変化（ARM/DISARM・モード変更・RTL開始）の検出

**手順**

```python
from pymavlink import mavutil

master = mavutil.mavlink_connection("tcp:127.0.0.1:5762")
master.wait_heartbeat()

prev_armed = None
prev_mode  = None

while True:
    msg = master.recv_match(type="HEARTBEAT", blocking=True)
    if msg is None:
        continue

    armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
    mode  = mavutil.mode_string_v10(msg)

    if armed != prev_armed:
        print("ARMされました" if armed else "DISARMされました")
        prev_armed = armed

    if mode != prev_mode:
        print(f"モード変更: {mode}")
        if mode == "RTL":
            print("RTL 開始")
        prev_mode = mode
```

<div style="page-break-before:always"></div>

# 4. 第2部 BlueOS編 ― Companion Computer アプリ開発

**目的:** WSL で動作確認したスクリプトを Companion Computer アプリケーションへ発展させる。最終的に BlueOS の左メニューに追加される Extension を作成する。

**第2部の前提環境:** Raspberry Pi 上で動作する BlueOS を使用する。FC は接続せず、**WSL 上の外部 SITL** を BlueOS の Manual ボードに接続した構成で進める。

事前に **コンパニオンコンピュータ（BlueOS）環境構築手順書** を完了し、下記の状態になっていること：

| チェック | 内容 |
|--------|------|
| ☐ | BlueOS が起動し、PCからホットスポット（192.168.42.1）に接続済み |
| ☐ | Manual ボード設定済み（Master Endpoint: UDP Server 0.0.0.0:14551） |
| ☐ | WSL 上の SITL が起動済み（`sim_vehicle.py -v ArduCopter -L Kawachi --out udp:192.168.42.1:14551`） |

> **【重要】教材の最新化（master の取り込み）**
> 本演習で使う Vibe コーディング教材（`vibe-coding/`）と Agent Skill（`.claude/skills/dronify-blueos/`）は、`droneschool` リポジトリの master に後から追加されました。[環境構築手順書 9.4](../drone-dev-env-setup-guide/drone-dev-env-setup-guide.md#94-課題提出用githubリポジトリ準備) で作成した自分のブランチ（例 `21st_<fname-lname>`）には含まれていないため、作業前に master を取り込んでください。
>
> 1. GitHub 上で自分のフォークの `master` を **Sync fork**（9.4 の「フォーク元の変更の取り込み」と同じ）
> 2. ローカルで master を更新し、自分のワークブランチへ取り込む：
>    ```bash
>    cd ~/GitHub/droneschool
>    git checkout master
>    git pull
>    git checkout 21st_<fname-lname>      # 自分のワークブランチ
>    git merge master
>    ```
> 3. 取り込めたか確認（両方が存在すれば OK）：
>    ```bash
>    ls vibe-coding/ .claude/skills/dronify-blueos/
>    ```

> **使用するAIコーディングエージェント**
> 本演習の Vibe コーディング（演習4）と BlueOS 化（演習5）は、ターミナルで動く AI コーディングエージェントで進めます。**Claude Code・Codex を推奨**します。**GitHub Copilot CLI でも実施可能**です（いずれも CLI 版。IDE 拡張ではありません）。
> ※ BlueOS 化で使う `/dronify-blueos` は Claude Code の **Agent Skill**（`/コマンド` で起動）です。Codex / GitHub Copilot CLI では、`.claude/skills/dronify-blueos/SKILL.md` の内容を**プロンプトとして渡して**同じ手順を実行してください。

---

## 4.1. 演習1 BlueOS 接続

**学習内容**
- BlueOS のネットワーク構成と、3つの「接続モデル」の住み分け
- Mission Planner を使ったモニタリング接続の確認

**BlueOS のネットワーク構成（Manual ボード + 外部 SITL）**

```
WSL (Ubuntu) ── UDP 14551 ──→ 192.168.42.1:14551

Raspberry Pi (BlueOS)  IP: 192.168.42.1
  ArduPilot Manager → Manual ボード（外部 SITL からテレメトリを受信）
  MAVLink Router → UDP Server 14550 を公開
        ├─→ Mission Planner（外部 PC・運用モニタリング）
        └─→ Drone Web Control Extension（BlueOS 内部・host.docker.internal 経由）
```

**3つの接続モデル（重要）**

本ガイドでは接続のしかたが用途ごとに分かれます。混同しないように整理しておきます。

| 用途 | 誰が | 接続先 | 登場 |
|------|------|--------|------|
| アプリのロジック開発・検証 | WSL の Python / コンテナ | ローカル SITL `tcp:127.0.0.1:5762` | 第1部・4.4・4.5 |
| 本番（Extension） | BlueOS 上のコンテナ | Board（Router）`udpout:host.docker.internal:14550` | 4.6 以降 |
| 運用モニタリング | Mission Planner（外部 PC） | Router `192.168.42.1:14550` | 本演習 |

> アプリ開発はローカル SITL（第1部・4.4・4.5）で完結し、完成したアプリは Extension として BlueOS 上で Board に接続します（4.6 以降）。**外部 PC からの監視は Mission Planner が担当**し、自作アプリを外部から BlueOS につなぐ必要はありません。本演習ではこの監視経路を確認します。

**Mission Planner からの接続手順**

1. PC を BlueOS のホットスポット（`192.168.42.1`）に接続する
2. Mission Planner 右上の接続種別で **`UDPCl`（UDP Client）** を選ぶ
3. 接続先を入力する（BlueOS の `UDP Server 14550` に対してクライアント接続する）

   | 項目 | 値 |
   |-----|-----|
   | Host | `192.168.42.1` |
   | Port | `14550` |

4. `Connect` を押下し、HUD に姿勢・GPS・高度などのテレメトリが表示されることを確認する

> BlueOS 側に `UDP Server 14550` が無い場合は、`Vehicle Setup → MAVLink Endpoints`（演習2）で追加するか、`UDP Client`（送信先＝PCのIP:14550）エンドポイントを作成し、Mission Planner 側を `UDP`（受信待ち）で開いても構いません。

**成果物:** Mission Planner で BlueOS 経由のテレメトリを表示し、3つの接続モデルの住み分けを理解する

---

## 4.2. 演習2 MAVLink Router 理解

**学習内容**
- MAVLink Router によるデータ経路の理解
- BlueOS Web UI でのエンドポイント管理

**BlueOS Web UI でのエンドポイント確認**

1. ブラウザで `http://<BlueOS_IP>` を開く
2. 左メニュー → `Vehicle Setup` → `MAVLink Endpoints` を選択
3. 既存エンドポイントを確認し、各クライアントがどの経路で接続しているかを把握する
   - `UDP Server 14550` … Mission Planner などの監視クライアント（演習1）と、BlueOS 内部の Extension（演習6以降）が共有
   - `MAVLink2REST`（6040）… REST 変換（演習3）

**エンドポイントを追加するケース**

監視用クライアントをもう一つ増やしたい場合などは、`MAVLink Endpoints` で新規エンドポイントを追加します。

| 項目 | 値 |
|-----|-----|
| Connection type | UDP Server |
| IP | 0.0.0.0 |
| Port | 14660 |

> **Extension は新規エンドポイント不要:** 演習6以降の Drone Web Control Extension は、既存の `UDP Server 14550` に **BlueOS 内部から `host.docker.internal` 経由**で接続します。MAVLink Router は1つのエンドポイントへ複数クライアントが同時接続できるため、Mission Planner（外部）と Extension（内部）が同じ 14550 を共有しても問題ありません。

**成果物:** データ経路図の理解 + エンドポイント管理（確認・追加）手順の習得

---

## 4.3. 演習3 MAVLink2REST 利用

**学習内容**
- BlueOS 内の MAVLink2REST (ポート 6040) を使った REST API による MAVLink データ取得
- JSON 形式でのデータ解析

**手順**

```python
import requests

BLUEOS_IP = "192.168.42.1"

# MAVLink2REST 経由で高度取得
url = f"http://{BLUEOS_IP}/mavlink2rest/mavlink/vehicles/1/components/1/messages/GLOBAL_POSITION_INT"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    alt = data["message"]["relative_alt"] / 1000
    print(f"高度: {alt:.1f} m")
else:
    print(f"エラー: {response.status_code}")
```

**MAVLink2REST の主要エンドポイント**

| エンドポイント | 説明 |
|--------------|------|
| `/mavlink2rest/mavlink/vehicles` | 接続中の機体一覧 |
| `/mavlink2rest/mavlink/vehicles/1/components/1/messages` | 全メッセージ一覧 |
| `/mavlink2rest/mavlink/vehicles/1/components/1/messages/HEARTBEAT` | HEARTBEAT |
| `/mavlink2rest/mavlink/vehicles/1/components/1/messages/GLOBAL_POSITION_INT` | GPS 位置・高度 |
| `/mavlink2rest/mavlink/vehicles/1/components/1/messages/SYS_STATUS` | バッテリー等 |

**成果物:** REST API を使った高度取得ツール

---

## 4.4. 演習4 アプリ開発（Vibe コーディング）

**学習内容**
- 仕様と技術スタックを指定し、AI コーディング（Vibe コーディング）で Web 制御アプリを生成する
- 生成物をローカル SITL で動作確認する

**考え方**

第1部で学んだ pymavlink の操作を、ここでは手書きで積み上げるのではなく、**仕様（何を作るか）と技術スタック（何で作るか）を与えて AI に生成させます**。本講座の主眼は「アプリを書くこと」ではなく、生成したアプリを **BlueOS Extension として動かすための要件**（演習5）にあります。

**技術スタック**

| 層 | 技術 |
|---|---|
| バックエンド | Python / FastAPI / pymavlink |
| リアルタイム通信 | WebSocket |
| フロントエンド | HTML / JavaScript ＋ Leaflet（地図） |

**機能仕様**

- 表示：接続状態・ARM 状態・フライトモード・GPS 座標・高度（リアルタイム）
- 地図：機体の現在位置と航跡
- 操作：ARM / TAKEOFF（高度指定）/ LAND / GoTo（緯度・経度・高度）/ モード変更

**Vibe コーディング（宿題）**

上記の仕様＋技術スタックは、生成用プロンプト **`vibe-coding/build-prompt.md`** にまとまっています。これを自分のワークフォルダにコピーし、AI コーディングエージェントにそのプロンプトで指示してアプリ（以後 **Drone Web Control**）を生成します。

```bash
# ① ワークフォルダを作成し、生成プロンプトをコピー
mkdir -p ~/GitHub/droneschool/workshop/21st/hideyuki-fujikawa
cp ~/GitHub/droneschool/vibe-coding/build-prompt.md \
   ~/GitHub/droneschool/workshop/21st/hideyuki-fujikawa/
```

```bash
# ② ワークフォルダで AI コーディングエージェントを起動し、build-prompt.md で指示する
cd ~/GitHub/droneschool/workshop/21st/hideyuki-fujikawa
claude        # または codex / copilot（CLI 版）
# → 「build-prompt.md の指示に従ってアプリを生成して」と依頼する
```

> `build-prompt.md` は冒頭でアプリ名（既定 `drone-web-app`）と作成先パス（未指定ならプロンプトのある場所）を確定させます。生成されるアプリは `<ワークフォルダ>/drone-web-app/` 配下になります。

> このアプリは演習5で **そのまま Docker 化・BlueOS Extension 化**します。BlueOS で動かすための要件（接続先・`register_service`・`avoid_iframes` 等）は演習5で `/dronify-blueos` が適用し、演習6で配布します。

> **演習では完成版を使います（3分クッキング）。** 上記の生成作業は宿題です。演習時間中は完成・素版 **`vibe-coding/drone-web-app/`** をそのまま使って、以下のローカル動作確認を行います。

**ローカル動作確認（WSL + SITL）**

```bash
# ① SITL（第1部と同じ。tcp:5762 を自動で開く）
sim_vehicle.py -v Copter --console -L Kawachi
```

```bash
# ② アプリ起動（接続先をローカル SITL に上書き）
#    演習: 完成版 vibe-coding/drone-web-app / 宿題: 自分が生成したアプリ
cd ~/GitHub/droneschool/vibe-coding/drone-web-app/backend
MAV_ENDPOINT=tcp:127.0.0.1:5762 uvicorn main:app --host 0.0.0.0 --port 9999
```

ブラウザで `http://localhost:9999/` を開き、地図・テレメトリ・操作ボタンが動くことを確認します。

> 接続先は環境変数 `MAV_ENDPOINT` で切り替えます。未指定だと BlueOS 用の既定値（`udpout:host.docker.internal:14550`）になるため、ローカルでは `tcp:127.0.0.1:5762` を明示します。

**成果物:** ローカル SITL で地図・テレメトリ・操作ができる Web アプリ

---

## 4.5. 演習5 BlueOS Extension 化（`/dronify-blueos`）

**学習内容**
- 演習4で作ったアプリを **BlueOS Extension として動かすための要件**を満たす
- Agent Skill **`/dronify-blueos`** で Docker 化＋Extension 要件を一括適用 → ローカルビルド検証する

> AI が生成しただけのアプリでは、BlueOS 固有の要件が**満たされません**。本講座の中核がこの要件であり、`/dronify-blueos` がこれらを一問一答で確定 → 自動適用 → ローカルビルド検証まで行います（**Docker 化と Extension 化をまとめて適用**）。配布（build / push / install）は演習6で自分で行います。

**`/dronify-blueos` が適用する要件**

スキルが何をするかを理解しておきます（実装は自動。詳細は `.claude/skills/dronify-blueos/SKILL.md`）。

*Docker 化*

- **`Dockerfile`**：`python:3.11-slim` ベースで backend / frontend をコピーし、ポート **9999** で uvicorn 起動。`--no-access-log`（Helper の継続ヘルスチェックでログ肥大 → VIEW LOGS タイムアウトを防ぐ）
- **`.dockerignore`**：イメージ最小化

*Extension 化*

| # | 要件 | なぜ必要か |
|---|------|-----------|
| ① | **permissions LABEL（bridge + ポート固定）** | Kraken は LABEL を Docker API 設定としてそのまま使う。`avoid_iframes` で `http://<IP>:9999/` を直接開くためポートは固定（`HostPort:"9999"`） |
| ② | **`/register_service`（`avoid_iframes: true`）** | Helper はこの JSON で左メニューを生成。WebSocket は nginx 自動ルートが WS 非対応のため、直接ポートを開かせる |
| ③ | **`GET /` が 200 を返す** | Helper は `/` で生存確認。200 以外だと `/register_service` を呼ばずメニューに出ない |
| ④ | **MAVLink 接続（bridge / Router 対策）** | `host.docker.internal` 接続・非ブロック接続・`mode_mapping_byname` での明示マップ・自機のみ受信（mode/armed の点滅防止） |
| ⑤ | **Leaflet をローカル同梱** | BlueOS ホットスポット接続中はネットに出られず CDN 不達（`L is not defined`） |

> **モードマップの落とし穴:** Plane の `GUIDED=15` を Copter に送ると Copter ではモード 15 が **AUTOTUNE** になり「Mode change to Autotune failed」になります（Copter は `GUIDED=4`）。これが `mode_mapping_byname` を使う理由です。
>
> **Router 側:** BlueOS の MAVLink Endpoint は **UDP Server `0.0.0.0:14550`** で公開しておきます（演習1の構成）。
>
> **ポート:** **9999** で統一します（8080 は BlueOS 内の `mavlink-server` が使用済みのため避ける）。

**`/dronify-blueos` の実行（宿題）**

演習4で生成したアプリに対して、ワークフォルダでスキルを実行します。

```bash
cd ~/GitHub/droneschool/workshop/21st/hideyuki-fujikawa/drone-web-app
claude        # Claude Code を起動
# → /dronify-blueos を実行（アプリ名・ポート・機体種別などの一問一答に答える）
```

> **`/dronify-blueos` が使える理由:** このスキルは `droneschool/.claude/skills/dronify-blueos/` にあります。ワークフォルダが droneschool リポジトリの**中**にあれば、Claude Code が親ディレクトリを辿ってスキルを検出するため、`/dronify-blueos` がそのまま使えます（コピー不要）。ワークフォルダを droneschool の外に作ると検出されないので注意してください。

> Codex / GitHub Copilot CLI は `.claude/skills/` を読みません。その場合は `/dronify-blueos` の代わりに `.claude/skills/dronify-blueos/SKILL.md` の内容をプロンプトとして渡してください。
>
> スキルは上記要件の適用と **ローカルビルド検証**（`GET /` が 200、`/register_service` の JSON、`permissions` LABEL の確認）まで行います。**push と BlueOS インストールは行いません**（演習6で自分で実施）。

**ローカル確認（完成版で確認）**

演習では、すでに要件が適用済みの完成・BlueOS版 **`vibe-coding/drone-web-app-blueos/`** を使って、コンテナ起動を確認します（スキル適用は宿題）。

```bash
# ① SITL
sim_vehicle.py -v Copter --console -L Kawachi
```

```bash
# ② ビルド & 起動（接続先をローカル SITL に上書き）
cd ~/GitHub/droneschool/vibe-coding/drone-web-app-blueos
docker build -t drone-web-app .
docker run --rm --network host -e MAV_ENDPOINT=tcp:127.0.0.1:5762 drone-web-app
# → ブラウザ http://localhost:9999/
```

> **`--network host` と `-e MAV_ENDPOINT`:** ローカルでは host ネットワークで SITL に直結し、接続先を `tcp:5762` へ明示します。BlueOS（演習6）では env を渡さず、既定の `host.docker.internal` で Router に繋ぎます。

**成果物:** 要件適用済み・ローカル検証済みの Extension イメージ

---

## 4.6. 演習6 BlueOS への配布（build / push / install）

**学習内容**
- 演習5のイメージを **マルチアーキ**でビルドして Docker Hub に push する
- BlueOS の Web UI から Extension としてインストールし、動作を確認する

> ここは `/dronify-blueos` が行わない**手作業の配布フェーズ**です。マルチアーキ build → Docker Hub へ push → BlueOS にインストール、までを各自で行います。

**Docker Hub へのイメージ公開（自分で実施）**

BlueOS は Docker Hub からイメージを pull するため、事前に公開しておきます。Raspberry Pi は arm64 のため、`docker buildx` で **マルチアーキ**ビルドして push します。

```bash
docker login
docker buildx create --use            # 初回のみ
# push 時に "blob upload unknown" が出たら --provenance=false を付けて再実行
docker buildx build --platform linux/amd64,linux/arm64 --provenance=false \
  -t <username>/drone-web-app:latest --push .
```

`https://hub.docker.com/r/<username>/drone-web-app` でイメージ（amd64/arm64）を確認します。

**BlueOS へのインストール（Web UI）**

1. `http://<BlueOS_IP>` → 左メニュー `Extensions` → `INSTALLED` タブ
2. 右下の `+` → `Create from scratch`
3. 以下を入力する

   | 項目 | 値 |
   |-----|-----|
   | Extension Identifier | `<username>.drone-web-control` |
   | Extension Name | `Drone Web Control` |
   | Docker image | `<username>/drone-web-app` |
   | Docker tag | `latest` |

   ![Create Extension ダイアログ](media/blueos-extensions-010.png)

4. 下部の JSON エディタ（初期値 `{}`）に、演習5①の `permissions` と同じ内容を入力する

   ```json
   {
     "ExposedPorts": { "9999/tcp": {} },
     "HostConfig": {
       "PortBindings": { "9999/tcp": [{ "HostPort": "9999" }] },
       "ExtraHosts": ["host.docker.internal:host-gateway"]
     }
   }
   ```

   > **重要:** `Create from scratch` ではこの JSON エディタの内容が **LABEL より優先**されます（内部的に `user_permissions` として扱われ、LABEL は読まれない）。`{}` のままだとポートがマップされず**メニューに出ません**。必ず入力してください。

5. `CREATE` を押下

インストール後、左メニューに **Drone Web Control** が追加されます。詳細画面で Status が `Up` になっていれば起動成功。クリックすると `avoid_iframes` により **`http://<BlueOS_IP>:9999/` が新規ウィンドウで開きます**。

![インストール済み Extension の詳細](media/blueos-extensions-020.png)

**動作確認（Definition of Done）**

- [ ] 左メニューに **Drone Web Control** が出る／クリックで `:9999` が開く
- [ ] ステータス（接続/ARM/モード/座標/高度）が**点滅せず安定**して表示
- [ ] ARM / TAKEOFF / LAND / GoTo / モード変更が機能（TAKEOFF で **GUIDED** に入る）
- [ ] オフラインでも地図ウィジェット・マーカー・航跡が描画（タイルは灰色で可）

**よくあるトラブル**

| 症状 | 原因 | 対策 |
|---|---|---|
| メニューに出ない | bridge/ポート未設定（JSONエディタ空）／`GET /` が 200 でない | 演習5①の permissions を JSON エディタに入力／演習5③で `/` が 200 を返す |
| TAKEOFF で AUTOTUNE 失敗 | Plane のモードマップを誤適用 | `mode_mapping_byname` で機体タイプから生成（演習5④） |
| ARM/モード表示が点滅 | GCS の HEARTBEAT も拾っている | 受信を自機（target）に限定（演習5④） |
| 地図が出ない | CDN（unpkg/OSM）に到達できない | Leaflet をローカル同梱（演習5⑤） |
| VIEW LOGS がタイムアウト | アクセスログ肥大 | `uvicorn ... --no-access-log`（演習5） |

**成果物:** BlueOS 左メニューから開ける Drone Web Control Extension

<div style="page-break-before:always"></div>

# 5. 第3部 実機編 ― BlueOS Extension を実機で運用

**目的:** 同じ Extension を実機の Raspberry Pi で動作させる。**コードもイメージも変えない。SITL ボードを実機 FC に差し替えるだけ。**

実機環境の構成:

```
[フライトコントローラー] ←シリアル→ [Raspberry Pi (BlueOS)]
                                         ↓ Wi-Fi
                                     [PC / スマホ]
                                    http://<BlueOS_IP>
```

---

## 5.1. 演習1 実機接続

**学習内容**
- 実機フライトコントローラーへのテレメトリ接続
- BlueOS MAVLink Router 経由でのデータ取得

**変更点（コードは変えない）**

Extension はコンテナ内から `host.docker.internal:14550`（BlueOS の MAVLink Router）に接続します。この経路は SITL でも実機でも同じなので、**アプリのコードもイメージも変更不要**です。変わるのは BlueOS 側の「どの機体を Router に流すか」だけです。

- SITL: 外部 SITL → Manual ボード（演習1の構成）
- 実機: フライトコントローラー → シリアル接続

**接続確認手順**

1. Raspberry Pi に BlueOS をインストールして起動
2. FC を BlueOS にシリアル接続し、`Vehicle Setup` で認識させる
3. MAVLink Endpoint に **UDP Server `0.0.0.0:14550`** があることを確認（無ければ追加）
4. 演習6でインストールした **Drone Web Control** をそのまま起動
5. 実機のテレメトリ（姿勢・GPS・モード）が UI に表示されることを確認

**成果物:** 実機での Extension 動作確認（コード無変更）

---

## 5.2. 演習2 フェイルセーフ監視

**学習内容**
- 異常状態の検出と警告

**監視対象と検出方法**

| 異常 | 検出方法 |
|-----|---------|
| GPS 異常 | `GPS_RAW_INT.fix_type < 3` |
| バッテリー低下 | `SYS_STATUS.voltage_battery < 閾値` |
| EKF 異常 | `EKF_STATUS_REPORT.flags` |
| RC 喪失 | `RC_CHANNELS.rssi == 0` |

**実装例（フェイルセーフ監視スレッド）**

```python
import threading
from pymavlink import mavutil

# Extension（コンテナ内）から Router へ。演習5と同じ接続先。
master = mavutil.mavlink_connection("udpout:host.docker.internal:14550")
master.wait_heartbeat()

BATTERY_THRESHOLD_V = 14.0  # 警告電圧 (V)

def monitor():
    while True:
        msg = master.recv_match(
            type=["GPS_RAW_INT", "SYS_STATUS"],
            blocking=True, timeout=5
        )
        if msg is None:
            continue

        if msg.get_type() == "GPS_RAW_INT" and msg.fix_type < 3:
            print("GPS 異常: Fix なし")

        if msg.get_type() == "SYS_STATUS":
            volt = msg.voltage_battery / 1000
            if volt < BATTERY_THRESHOLD_V:
                print(f"バッテリー低下: {volt:.1f} V")

threading.Thread(target=monitor, daemon=True).start()
```

**成果物:** 異常検知と警告を行うモニタリングシステム

---

## 5.3. 演習3 通知連携

**学習内容**
- Discord Webhook を使った外部通知の実装

**Discord Webhook の設定**

1. Discord サーバーの通知を送りたいチャンネルを開く
2. チャンネル設定 → `連携サービス` → `ウェブフック` → `新しいウェブフック`
3. 作成した Webhook の URL をコピーする

**実装例**

```python
import requests

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/<your-webhook-url>"

def notify(message: str):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

# フェイルセーフ検知時に呼び出す
notify("バッテリー低下を検知しました！")
notify("GPS 異常: Fix なし")
```

**フェイルセーフ監視と組み合わせる**

```python
def monitor():
    while True:
        msg = master.recv_match(
            type=["GPS_RAW_INT", "SYS_STATUS"],
            blocking=True, timeout=5
        )
        if msg is None:
            continue

        if msg.get_type() == "GPS_RAW_INT" and msg.fix_type < 3:
            notify("GPS 異常: Fix なし")

        if msg.get_type() == "SYS_STATUS":
            volt = msg.voltage_battery / 1000
            if volt < BATTERY_THRESHOLD_V:
                notify(f"バッテリー低下: {volt:.1f} V")
```

**成果物:** フェイルセーフ検知時に Discord へ通知するシステム

<div style="page-break-before:always"></div>

# 6. 最終課題

## BlueOS Extension版 ドローン見守りシステム

第1部〜第3部で学んだ技術を組み合わせて、以下の機能を持つ BlueOS Extension を完成させてください。

### 機能要件

**表示機能**
- [ ] ARM 状態の表示
- [ ] Flight Mode の表示
- [ ] GPS 状態の表示
- [ ] 高度の表示
- [ ] バッテリー電圧の表示

**操作機能**
- [ ] ARM / DISARM
- [ ] TAKEOFF（高度入力付き）/ LAND
- [ ] GoTo（緯度・経度・高度）
- [ ] モード変更（RTL 等）

**通知機能**
- [ ] Discord / Slack のいずれかへの通知

**異常検知**
- [ ] GPS 異常の検知と通知
- [ ] バッテリー低下の検知と通知
- [ ] EKF 異常の検知と通知
- [ ] Failsafe 発生の検知と通知

### 成果物の構成

```
drone-web-app/
├── Dockerfile          ← BlueOS Extension の LABEL（permissions ほか）
├── backend/
│   ├── main.py         ← FastAPI + WebSocket（/register_service を含む）
│   └── requirements.txt
└── frontend/
    ├── index.html / script.js / style.css
    └── leaflet/        ← Leaflet ローカル同梱
```

演習4で Vibe コーディングしたアプリ（Drone Web Control）に、通知・異常検知を加えて完成させます。BlueOS の左メニューから開き、ドローンの見守り・基本操作ができる状態を最終目標とします。

> **教材（`droneschool` リポジトリ）**
> - 生成プロンプト: `vibe-coding/build-prompt.md`
> - 完成・素版: `vibe-coding/drone-web-app/`（ローカル SITL で動く最小構成）
> - 完成・BlueOS版: `vibe-coding/drone-web-app-blueos/`（Extension 化まで適用済み）
> - BlueOS 化スキル: `.claude/skills/dronify-blueos/`

<div style="page-break-before:always"></div>

# 7. 発展課題

### AI 副操縦士
自然言語コマンドを MAVLink コマンドに変換するエージェントの開発。

```
「10mまで上昇して」 → GUIDED + TAKEOFF(10)
「RTLして」         → set_mode("RTL")
```

### AprilTag 追従
カメラで AprilTag を検出し、ビジョンベースで機体を制御する。

### YOLO 物体検出
人物・車両を検出してアラートを送信する監視システムの開発。

### 複数機管理
複数の機体を同時に監視・制御するダッシュボードの開発。

<div style="page-break-before:always"></div>

# 8. Appendix

## 8.1. BlueOS
- 公式サイト: https://bluerobotics.com/blueos
- GitHub: https://github.com/bluerobotics/BlueOS
- ドキュメント: https://blueos.cloud/docs

## 8.2. MAVLink2REST
- GitHub: https://github.com/patrickelectric/mavlink2rest
- API ドキュメント: `http://<BlueOS_IP>/mavlink2rest/docs`

## 8.3. pymavlink
- GitHub: https://github.com/ArduPilot/pymavlink
- サンプルコード: https://www.ardusub.com/developers/pymavlink.html

## 8.4. FastAPI
- ドキュメント: https://fastapi.tiangolo.com/ja/

## 8.5. Docker
- 公式ドキュメント: https://docs.docker.com/
- Dockerfile リファレンス: https://docs.docker.com/engine/reference/builder/

## 8.6. 参考リンク
- ArduPilot MAVLink コマンド一覧: https://ardupilot.org/dev/docs/mavlink-commands.html
- BlueOS Extension 開発ガイド: https://blueos.cloud/docs/blueos/1.4/development/extensions/
