BlueOSを使ったアプリ開発演習のメニューを提案します。提供されたコードベースのコンテキストに基づき、WSL環境からBlueOS環境（ラズパイ）への段階的なアプローチを考慮しています。 [1](#0-0) [2](#0-1) 

---

## 演習メニュー提案

### 段階1: WSL環境での基礎演習

#### 1.1 BlueOSアーキテクチャ理解
- **目的**: BlueOSのコンテナ化アーキテクチャとサービス構造を理解
- **内容**: 
  - Docker Composeを使用した開発環境の構築 [2](#0-1) 
  - Core Container内のサービス構造の確認
  - Helperサービスによるサービスディスカバリメカニズムの学習 [3](#0-2) 

#### 1.2 pymavlink基礎
- **目的**: pymavlinkを使用したMAVLink通信の基礎を学習
- **内容**:
  - MAVLink2Restサービス（ポート6040）を通じたMAVLinkメッセージの送受信 [4](#0-3) 
  - 基本的なMAVLinkメッセージ（HEARTBEAT, ATTITUDE等）の解析
  - SITLシミュレーション環境でのテスト

#### 1.3 REST API基礎
- **目的**: BlueOSのREST APIを使用したサービス制御を学習
- **内容**:
  - HelperサービスAPI（ポート81）によるシステム情報取得 [5](#0-4) 
  - ArduPilot Manager API（ポート8000）による自動操縦制御 [6](#0-5) 

### 段階2: BlueOS環境（ラズパイ）での応用演習

#### 2.1 実機接続とMAVLink通信
- **目的**: 実際のフライトコントローラーとの通信を確立
- **内容**:
  - ArduPilot Managerによるボード検出とファームウェア管理 [7](#0-6) 
  - MAVLinkルーター（MAVLinkRouter/MAVP2P）の設定とエンドポイント管理 [8](#0-7) [9](#0-8) 
  - pymavlinkを使用した実機データのリアルタイム解析

#### 2.2 Extension開発基礎
- **目的**: BlueOS Extensionシステムの理解と簡単なExtension作成
- **内容**:
  - Extensionディスカバリメカニズムの理解 [10](#0-9) 
  - KrakenサービスによるExtension管理の学習 [11](#0-10) 
  - シンプルなPythonベースExtensionの作成（pymavlinkを使用したデータ表示）

#### 2.3 Extension応用
- **目的**: より複雑なExtensionの開発
- **内容**:
  - Extensionメタデータの定義とNGINXルート設定
  - pymavlinkを使用した高度なデータ処理Extension
  - フロントエンドコンポーネントとの連携

### 演習構成の推奨事項

#### 環境設定
- **WSL環境**: Docker Desktop + Docker Composeを使用したBlueOS開発環境 [2](#0-1) 
- **ラズパイ環境**: 公式BlueOSイメージまたはカスタムビルド

#### 必要なコンポーネント
- Python 3.x + pymavlink
- Docker
- （ラズパイ環境）Raspberry Pi 3/4 + フライトコントローラー

#### 学習目標
1. BlueOSのマイクロサービスアーキテクチャを理解
2. pymavlinkを使用したMAVLink通信を習得
3. Extensionシステムを使用した機能拡張を実現
4. WSLから実機へのスムーズな移行プロセスを体験

## Notes

この提案はBlueOSの公式ドキュメントとコードベースに基づいています。実際の演習では、参加者のスキルレベルに応じて内容を調整することをお勧めします。Extension開発では、KrakenサービスのAPIドキュメントを参照することで、より高度な機能を実装できます [12](#0-11) 。

Wiki pages you might want to explore:
- [Overview (bluerobotics/BlueOS)](/wiki/bluerobotics/BlueOS#1)
- [ArduPilot Manager (bluerobotics/BlueOS)](/wiki/bluerobotics/BlueOS#4.1)

### Citations

**File:** README.md (L95-108)
```markdown
## Development Environment

Docker based development environment is available for via the [`core/compose/compose.yml`](core/compose/compose.yml) docker compose file. This will start a development environment with all the required services as well as mount all of the needed directories in this repository for development.

```bash
cd core/compose/ && docker compose pull && cd - # Ensure that docker is up-to-date
docker compose -f core/compose/compose.yml up
```

When restarting the development environment you may need to remove the volumes to ensure that the development environment is clean.

```bash
docker compose -f core/compose/compose.yml down
```
```

**File:** core/compose/compose.yml (L1-60)
```yaml
version: '3.7'
services:
  blueos-core:
    image: bluerobotics/blueos-core:master
    container_name: blueos-core
    privileged: true
    # This can be used as an alternative to ports binding
    # Using host as a network mode is only supported for linux
    # Ref: https://docs.docker.com/network/drivers/host
    network_mode: host
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /run/udev:/run/udev
      - /etc/resolv.conf:/etc/resolv.conf
      - /etc/machine-id:/etc/machine-id
      - ./workspace/userdata:/usr/blueos/userdata
      - ./workspace/logs:/var/logs/blueos
      - ./workspace/config:/root/.config
      - ./workspace/blueos:/etc/blueos
      # Allow changes made to the repository to be directly reflected in the running container
      - ../start-blueos-core:/usr/bin/start-blueos-core
      - ../tools/blueos_startup_update/blueos_startup_update.py:/usr/bin/blueos_startup_update.py
      - ../services:/home/pi/services
    pid: "host"
    environment:
      - BLUEOS_DISABLE_SERVICES=cable_guy,wifi,commander
      - BLUEOS_DISABLE_MEMORY_LIMIT=true
      - BLUEOS_DISABLE_STARTUP_UPDATE=true
  #   ports:
  #     - "80:80"
  #     - "81:81"       # Helper
  #     - "2748:2748"   # NMEA Injector
  #     - "3478:3478"   # MAVLink Camera Manager Stun server
  #     - "5173:5173"   # Cockpit development port
  #     - "6020:6020"   # MAVLink Camera Manager REST API and interface
  #     - "6021:6021"   # MAVLink Camera Manager Signalling server
  #     - "6030:6030"   # System Information
  #     - "6040:6040"   # MAVLink2Rest
  #     - "7777:7777"   # File Browser
  #     - "8081:8081"   # Version Chooser
  #     - "8088:8088"   # ttyd - Terminal
  #     - "8554:8554"   # MAVLink Camera Manager RTSP server
  #     - "9000:9000"   # Wifi Manager
  #     - "9090:9090"   # Cable-guy
  #     - "9100:9100"   # Commander
  #     - "9101:9101"   # Bag Of Holding
  #     - "9110:9110"   # Ping Service
  #     - "9111:9111"   # Beacon Service
  #     - "9120:9120"   # Pardal
  #     - "9134:9134"   # Kraken
  #     - "27353:27353" # Bridget
  #     - "49153:49153" # Cockpit
  cloud-telemetry:
    image: public.ecr.aws/blueos/bcloud-agent
    container_name: blueos-cloud-telemetry
    privileged: true
    restart: always
    network_mode: host
    pid: "host"
    volumes:
```

**File:** core/tools/nginx/nginx.conf (L69-72)
```text
        location /ardupilot-manager/ {
            include cors.conf;
            proxy_pass http://127.0.0.1:8000/;
        }
```

**File:** core/tools/nginx/nginx.conf (L112-115)
```text
        location /helper/ {
            include cors.conf;
            proxy_pass http://127.0.0.1:81/;
        }
```

**File:** core/tools/nginx/nginx.conf (L117-120)
```text
        location /kraken/ {
            include cors.conf;
            proxy_pass http://127.0.0.1:9134/;
        }
```

**File:** core/services/ardupilot_manager/autopilot_manager.py (L444-465)
```python
    @staticmethod
    async def available_boards(include_bootloaders: bool = False) -> List[FlightController]:
        all_boards = await BoardDetector.detect(True)
        if include_bootloaders:
            return all_boards
        return [board for board in all_boards if FlightControllerFlags.is_bootloader not in board.flags]

    async def change_board(self, board: FlightController) -> None:
        logger.info(f"Trying to run with '{board.name}'.")
        boards = await self.available_boards()
        if not any(board.name == detectedboard.name for detectedboard in boards):
            logger.error(f"Attempted to change active board to {board} which is not detected.")
            logger.info(f"detected boards are: {boards}")
            raise ValueError(f"Cannot use '{board.name}'. Board not detected.")
        self.set_preferred_board(board)
        await self.kill_ardupilot()
        await self.start_ardupilot()

    def set_preferred_board(self, board: FlightController) -> None:
        logger.info(f"Setting {board.name} as preferred flight-controller.")
        self.configuration["preferred_board"] = board.dict(exclude={"path"})
        self.settings.save(self.configuration)
```

**File:** core/services/ardupilot_manager/mavlink_proxy/Manager.py (L24-54)
```python
class Manager:
    def __init__(self, preferred_tool: Optional[str] = None) -> None:
        available_interfaces = Manager.available_interfaces()
        if not available_interfaces:
            raise RuntimeError(
                "No MAVLink routers found,"
                " make sure that at least one is installed."
                f" Supported: {Manager.possible_interfaces()}"
            )

        if preferred_tool:
            self.tool = AbstractRouter.get_interface(preferred_tool)()
        else:
            self.tool = available_interfaces[0]()
        self.should_be_running = False
        self._last_valid_endpoints: Set[Endpoint] = set()

    @staticmethod
    def possible_interfaces() -> List[str]:
        return AbstractRouter.possible_interfaces()

    @staticmethod
    def available_interfaces() -> List[Type[AbstractRouter]]:
        return AbstractRouter.available_interfaces()

    def use(self, interface: AbstractRouter) -> None:
        self.tool = interface

    def add_endpoint(self, endpoint: Endpoint) -> None:
        self.tool.add_endpoint(endpoint)

```

**File:** core/services/ardupilot_manager/mavlink_proxy/MAVP2P.py (L23-42)
```python
    def assemble_command(self, master_endpoint: Endpoint) -> str:
        # Convert endpoint format to mavlink-router format
        def convert_endpoint(endpoint: Endpoint) -> str:
            if endpoint.connection_type == EndpointType.Serial:
                return f"serial:{endpoint.place}:{endpoint.argument}"
            if endpoint.connection_type == EndpointType.TCPServer:
                return f"tcps:{endpoint.place}:{endpoint.argument}"
            if endpoint.connection_type == EndpointType.TCPClient:
                return f"tcpc:{endpoint.place}:{endpoint.argument}"
            if endpoint.connection_type == EndpointType.UDPServer:
                return f"udps:{endpoint.place}:{endpoint.argument}"
            if endpoint.connection_type == EndpointType.UDPClient:
                return f"udpc:{endpoint.place}:{endpoint.argument}"
            raise ValueError(f"Endpoint of type {endpoint.connection_type} not supported on MAVP2P.")

        filtered_endpoints = Endpoint.filter_enabled(self.endpoints())
        endpoints = " ".join([convert_endpoint(endpoint) for endpoint in [master_endpoint, *filtered_endpoints]])

        return f"{self.binary()} {endpoints} --streamreq-disable"

```

**File:** core/frontend/src/App.vue (L542-576)
```vue
    computed_menu(): menuItem[] {
      const foundExtensions = helper.services
        .filter((service: Service) : boolean => service.metadata !== null)
        .map((service: Service) => {
          const address = this.createExtensionAddress(service)
          return {
            title: service.metadata?.name ?? 'Service name',
            icon: service.metadata?.icon?.startsWith('/')
              ? `${address}${service.metadata.icon}`
              : service.metadata?.icon ?? 'mdi-puzzle',
            route: this.addExtraQuery(service.metadata?.route ?? address, service.metadata?.extra_query),
            new_page: service.metadata?.avoid_iframes ?? service.metadata?.new_page,
            advanced: false,
            text: service.metadata?.description ?? 'Service text',
            extension: true,
            disabled: this.isBehindWebProxy && !service.metadata?.works_in_relative_paths,
          }
        })

      const filteredDefaultMenu = this.menus.filter((menu) => !menu.advanced || settings.is_pirate_mode)

      const extensions: menuItem[] = [
        {
          title: 'Extensions',
          icon: 'mdi-puzzle',
          route: '/tools/extensions-manager',
          advanced: false,
          text: 'Manage BlueOS extensions',
          beta: true,
        },
        ...foundExtensions,
      ] as menuItem[]

      return [...filteredDefaultMenu, ...extensions].sort((a, b) => a.title.localeCompare(b.title))
    },
```

**File:** core/services/kraken/api/app.py (L19-22)
```python
application = FastAPI(
    title="Kraken API",
    description="Kraken is the BlueOS service responsible for installing and managing extensions.",
)
```

**File:** core/services/kraken/setup.py (L5-26)
```python
setuptools.setup(
    name="Kraken",
    version="0.1.0",
    description="Manages BlueOS extensions",
    license="MIT",
    py_modules=[],
    install_requires=[
        "semver == 3.0.2",
        "aiodocker == 0.21.0",
        "aiocache == 0.12.2",
        "appdirs == 1.4.4",
        "commonwealth == 0.1.0",
        "fastapi == 0.105.0",
        # Enforce anyio fastapi subdependency to avoid conflict with starlette
        "anyio == 3.7.1",
        "fastapi-versioning == 0.9.1",
        "loguru == 0.5.3",
        "psutil == 5.7.2",
        "uvicorn == 0.13.4",
        "dataclass-wizard == 0.22.3",
    ],
)
```
