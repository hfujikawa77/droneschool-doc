<div align="center">
<h3>ドローンエンジニア養成塾 デベロッパーコース</h3>
<h2>BlueOS アプリ開発ガイド</h2><br>
(WSL2 + SITL → BlueOS Extension 開発)<br/>
Ver.1.0.0 - 2026.6.12
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
  - [4.4. 演習4 Web API 化](#44-演習4-web-api-化)
  - [4.5. 演習5 Docker 化](#45-演習5-docker-化)
  - [4.6. 演習6 BlueOS Extension 化](#46-演習6-blueos-extension-化)
  - [4.7. 演習7 Web UI 開発](#47-演習7-web-ui-開発)
  - [4.8. 演習8 操作パネル](#48-演習8-操作パネル)
- [5. 第3部 実機編 ― BlueOS Extension を実機で運用](#5-第3部-実機編--blueos-extension-を実機で運用)
  - [5.1. 演習1 実機接続](#51-演習1-実機接続)
  - [5.2. 演習2 フェイルセーフ監視](#52-演習2-フェイルセーフ監視)
  - [5.3. 演習3 通知連携](#53-演習3-通知連携)
- [6. 最終課題](#6-最終課題)
- [7. 発展課題](#7-発展課題)
- [8. Appendix](#8-appendix)

<!-- /code_chunk_output -->

<div style="page-break-before:always"></div>

# 1. はじめに

本ガイドは、ArduPilot / BlueOS 環境向けの **Companion Computer アプリケーション開発** を学ぶための演習カリキュラムです。

WSL 上のシミュレータ (SITL) で動作確認したコードを、そのまま BlueOS Extension として Raspberry Pi 上で動かすことを最終目標とします。

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
    ├─→ Mission Planner (UDP)
    ├─→ QGroundControl (UDP)
    ├─→ MAVLink2REST (ポート6040)
    └─→ Python アプリ (UDP:14550)
```

Python アプリは `udp:192.168.42.1:14550` に接続することで FC のデータを受信できます。

<div style="page-break-before:always"></div>

# 3. 第1部 WSL編 ― pymavlink 基礎

**目的:** ArduPilot・MAVLink・pymavlink の基礎を学ぶ。実機や BlueOS を使わず、PC のみで開発できる状態を作る。

SITL を起動した状態で各演習を進めてください。

```bash
# SITL 起動
sim_vehicle.py -v Copter --map --console -L Kawachi
```

---

## 3.1. 演習1 MAVLink接続

**学習内容**
- SITL への pymavlink 接続
- HEARTBEAT 受信による接続確認

**手順**

```python
from pymavlink import mavutil

# SITL に UDP で接続
master = mavutil.mavlink_connection("udp:127.0.0.1:14550")

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

master = mavutil.mavlink_connection("udp:127.0.0.1:14550")
master.wait_heartbeat()

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

master = mavutil.mavlink_connection("udp:127.0.0.1:14550")
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

master = mavutil.mavlink_connection("udp:127.0.0.1:14550")
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

master = mavutil.mavlink_connection("udp:127.0.0.1:14550")
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

master = mavutil.mavlink_connection("udp:127.0.0.1:14550")
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

事前に **[コンパニオンコンピュータ環境構築手順書](../drone-dev-env-setup-guide/cc-blueos-setup-guide.md)** を完了し、下記の状態になっていること：

| チェック | 内容 |
|--------|------|
| ☐ | BlueOS が起動し、ホットスポット（192.168.42.1）に接続できる |
| ☐ | Manual ボード設定済み（Master Endpoint: UDP Server 0.0.0.0:14551） |
| ☐ | WSL 上の SITL が起動済み（`sim_vehicle.py -v ArduCopter -L Kawachi --out udp:192.168.42.1:14551`） |

---

## 4.1. 演習1 BlueOS 接続

**学習内容**
- BlueOS のネットワーク構成
- MAVLink Router エンドポイント経由での pymavlink 接続

**BlueOS のネットワーク構成（Manual ボード + 外部 SITL）**

```
WSL (Ubuntu) ── UDP 14551 ──→ 192.168.42.1:14551

Raspberry Pi (BlueOS)  IP: 192.168.42.1
  ArduPilot Manager → Manual ボード（外部 SITL からテレメトリを受信）
  MAVLink Router → UDP Server 14550 を公開
  → PC 上の Python アプリはここに接続する
```

**接続先の変更（WSL との差分はここだけ）**

```python
# WSL 版（SITL がローカルで動作）
master = mavutil.mavlink_connection("udp:127.0.0.1:14550")

# BlueOS 版（BlueOS ホットスポット IP に変更）
BLUEOS_IP = "192.168.42.1"  # BlueOS ホットスポット IP
master = mavutil.mavlink_connection(f"udp:{BLUEOS_IP}:14550")
```

**成果物:** BlueOS 経由で接続し、テレメトリを表示するスクリプト

---

## 4.2. 演習2 MAVLink Router 理解

**学習内容**
- MAVLink Router によるデータ経路の理解
- BlueOS Web UI でのエンドポイント管理

**BlueOS Web UI でのエンドポイント確認**

1. ブラウザで `http://<BlueOS_IP>` を開く
2. 左メニュー → `Vehicle Setup` → `MAVLink Endpoints` を選択
3. 既存エンドポイントを確認し、必要に応じて Python アプリ向けエンドポイントを追加する

**エンドポイント追加例（BlueOS Web UI）**

| 項目 | 値 |
|-----|-----|
| Connection type | UDP Server |
| IP | 0.0.0.0 |
| Port | 14660 |

**成果物:** データ経路図の理解 + エンドポイント追加手順の習得

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

## 4.4. 演習4 Web API 化

**学習内容**
- FastAPI を使ったドローン制御 REST API サーバーの構築

**インストール**

```bash
pip install fastapi uvicorn
```

**api_server.py**

```python
from fastapi import FastAPI
from pymavlink import mavutil

app = FastAPI(title="Drone API")

BLUEOS_IP = "192.168.42.1"  # BlueOS ホットスポット IP（第1部 WSL 版は 127.0.0.1）
master = mavutil.mavlink_connection(f"udp:{BLUEOS_IP}:14550")
master.wait_heartbeat()

@app.get("/status")
def get_status():
    msg = master.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=3)
    if msg:
        return {"alt": msg.relative_alt / 1000, "lat": msg.lat / 1e7, "lon": msg.lon / 1e7}
    return {"error": "timeout"}

@app.post("/arm")
def arm():
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0
    )
    return {"result": "arm command sent"}

@app.post("/disarm")
def disarm():
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0
    )
    return {"result": "disarm command sent"}

@app.post("/takeoff/{altitude}")
def takeoff(altitude: float):
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, altitude
    )
    return {"result": f"takeoff command sent (alt={altitude}m)"}
```

**起動**

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8080
```

**成果物:** `/status`, `/arm`, `/disarm`, `/takeoff/{altitude}` を持つ API サーバー

---

## 4.5. 演習5 Docker 化

**学習内容**
- Dockerfile の作成
- コンテナとしてのアプリ実行
- BlueOS Extension 化への準備

**ディレクトリ構成**

```
drone-monitor/
├── Dockerfile
├── requirements.txt
└── api_server.py
```

**requirements.txt**

```
fastapi
uvicorn
pymavlink
requests
```

**Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080"]
```

**ビルドと起動**

```bash
# ビルド
docker build -t drone-monitor .

# 実行（SITL に接続）
docker run -p 8080:8080 drone-monitor

# 動作確認
curl http://localhost:8080/status
```

**成果物:** `docker build` / `docker run` で起動できるアプリ

---

## 4.6. 演習6 BlueOS Extension 化

**学習内容**
- BlueOS Extension の構造（metadata.json）
- Kraken サービスによる Extension 管理
- BlueOS 左メニューへの統合

**Extension の最小構成**

```
drone-monitor/
├── Dockerfile
├── requirements.txt
├── api_server.py
└── metadata.json         ← BlueOS Extension に必須
```

**metadata.json**

```json
{
  "name": "Drone Monitor",
  "description": "ドローン状態監視・制御パネル",
  "icon": "mdi-drone",
  "version": "1.0.0",
  "permissions": {
    "NetworkMode": "host"
  },
  "port": 8080,
  "route": "/drone-monitor",
  "webpage": "/drone-monitor",
  "api": "/drone-monitor/api",
  "works_in_relative_paths": true,
  "extra_query": ""
}
```

**Docker Hub へのイメージ公開**

BlueOS は Docker Hub からイメージを pull してインストールするため、事前にイメージを公開しておく必要があります。

1. [hub.docker.com](https://hub.docker.com) で無料アカウントを作成する
2. ターミナルでログインする
   ```bash
   docker login
   ```
3. イメージに Docker Hub 用のタグを付ける（`<username>` は自分のアカウント名）
   ```bash
   docker tag drone-monitor <username>/drone-monitor:latest
   ```
4. Docker Hub へ push する
   ```bash
   docker push <username>/drone-monitor:latest
   ```

**BlueOS へのインストール手順（BlueOS Web UI）**

1. ブラウザで `http://<BlueOS_IP>` を開く
2. 左メニュー → `Tools` → `Extensions Manager`
3. `Add Extension` をクリックし、以下を入力する

   | 項目 | 値 |
   |-----|-----|
   | Docker image | `<username>/drone-monitor` |
   | Tag | `latest` |

4. `Install` を押下

インストール後、BlueOS の左メニューに **Drone Monitor** が追加されます。

**成果物:** BlueOS 左メニューに表示される Drone Monitor Extension

---

## 4.7. 演習7 Web UI 開発

**学習内容**
- HTML/CSS/JavaScript による状態表示 UI
- API サーバーと UI の統合（FastAPI で静的ファイルを配信）

**ui/index.html の例**

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>Drone Monitor</title>
  <style>
    body { font-family: sans-serif; padding: 20px; background: #1e1e2e; color: #cdd6f4; }
    .card { background: #313244; border-radius: 8px; padding: 16px; margin: 8px 0; }
    .label { color: #a6adc8; font-size: 0.85em; }
    .value { font-size: 1.4em; font-weight: bold; }
  </style>
</head>
<body>
  <h2>Drone Monitor</h2>
  <div class="card">
    <div class="label">高度</div>
    <div class="value" id="alt">-- m</div>
  </div>
  <div class="card">
    <div class="label">GPS</div>
    <div class="value" id="gps">--, --</div>
  </div>
  <div class="card">
    <div class="label">バッテリー</div>
    <div class="value" id="bat">-- V</div>
  </div>
  <div class="card">
    <div class="label">モード</div>
    <div class="value" id="mode">--</div>
  </div>

  <script>
    async function update() {
      const res = await fetch("/status");
      const d   = await res.json();
      document.getElementById("alt").textContent = (d.alt?.toFixed(1) ?? "--") + " m";
      document.getElementById("gps").textContent = d.lat
        ? `${d.lat.toFixed(6)}, ${d.lon.toFixed(6)}`
        : "--";
    }
    setInterval(update, 1000);
    update();
  </script>
</body>
</html>
```

**FastAPI で静的ファイルを配信（api_server.py に追記）**

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="ui", html=True), name="ui")
```

**成果物:** ブラウザでドローンの状態を監視できる Web UI

---

## 4.8. 演習8 操作パネル

**学習内容**
- ARM / DISARM / TAKEOFF / RTL ボタンの追加
- Mission Planner なしで基本操作を可能にする

**ui/index.html に操作ボタンを追加**

```html
<div class="card">
  <button onclick="sendCmd('/arm', 'POST')">ARM</button>
  <button onclick="sendCmd('/disarm', 'POST')">DISARM</button>
  <button onclick="sendCmd('/takeoff/10', 'POST')">TAKEOFF (10m)</button>
  <button onclick="sendCmd('/rtl', 'POST')">RTL</button>
</div>

<script>
  async function sendCmd(path, method) {
    const res = await fetch(path, { method });
    const d   = await res.json();
    alert(d.result);
  }
</script>
```

**api_server.py に RTL エンドポイントを追加**

```python
@app.post("/rtl")
def rtl():
    mode_id = master.mode_mapping()["RTL"]
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )
    return {"result": "RTL command sent"}
```

**成果物:** Mission Planner なしで ARM・DISARM・TAKEOFF・RTL を操作できる Web パネル

<div style="page-break-before:always"></div>

# 5. 第3部 実機編 ― BlueOS Extension を実機で運用

**目的:** BlueOS Extension を実機の Raspberry Pi で動作させる。**接続先 IP の変更以外はコードを変えない。**

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

**変更点（ここだけ）**

```python
# SITL 版
BLUEOS_IP = "127.0.0.1"

# 実機版（Raspberry Pi の IP に変更）
BLUEOS_IP = "192.168.42.1"  # BlueOS ホットスポット IP（環境に合わせて変更）
```

**接続確認手順**

1. Raspberry Pi に BlueOS をインストールして起動
2. PC を BlueOS と同じネットワークに接続
3. ブラウザで `http://192.168.2.2` を開いて BlueOS Web UI を確認
4. `api_server.py` の `BLUEOS_IP` を BlueOS の IP に変更して実行
5. `/status` エンドポイントで実機のテレメトリが取得できることを確認

**成果物:** 実機のモニタリング動作確認

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

master = mavutil.mavlink_connection(f"udp:{BLUEOS_IP}:14550")
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
- [ ] ARM ボタン
- [ ] DISARM ボタン
- [ ] TAKEOFF ボタン（高度入力付き）
- [ ] RTL ボタン

**通知機能**
- [ ] LINE / Discord / Slack のいずれかへの通知

**異常検知**
- [ ] GPS 異常の検知と通知
- [ ] バッテリー低下の検知と通知
- [ ] EKF 異常の検知と通知
- [ ] Failsafe 発生の検知と通知

### 成果物の構成

```
drone-monitor/
├── Dockerfile
├── requirements.txt
├── metadata.json
├── api_server.py       ← FastAPI バックエンド
└── ui/
    └── index.html      ← Web UI
```

BlueOS の左メニューから Web UI にアクセスし、ドローンの見守り・基本操作ができる状態を最終目標とします。

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
