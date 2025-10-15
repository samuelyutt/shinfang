CV + RL Take-Home Technical Assessment
==

[Google Drive](https://drive.google.com/drive/folders/1svWeStc2BDo3CV--Wjoui4d9eZjz-G-L?usp=sharing)
> PART 1 [預測結果](https://drive.google.com/drive/folders/10pkTWKLaZPkkVEK8X55xRvwwwZCt5QiT?usp=sharing)及[訓練過程](https://drive.google.com/drive/folders/18STSy5n9LyDUquRuXJrjRM3As0z8a7tS?usp=sharing)。

PART 1: Computer Vision
--

針對提供的 RGBT ROS Bag建置一套從影像取得、拆分處理、資料集標註、Segmentation 模型訓練到推論的完整流程。 
最終目標為實現料理場域中鍋具與相關器具（如蛋、鍋子、鍋鏟、容器等）之即時遮罩生成，以利後續影像辨識與監控應用。

- 解析並訂閱 Bag 影像資料 
- 拆分 RGB 與 Thermal 影像 
- 對 Thermal 圖像進行增強處理以利辨識 
- 重新發佈拆分後的 ROS2 Topics 
- 準備可訓練的 Segmentation Dataset 
- 建立模型訓練與 Inference Pipeline 
- 完成結果紀錄與文件撰寫

### TODO List

#### 前置與環境建置
- [x] 建立 ROS2 + Docker + Conda + PyTorch 開發環境
- [x] 安裝 OpenCV、cv_bridge 等相關依賴
- [x] 建立 ROS 套件結構與資料夾規劃

#### ROS Bag 處理
- [x] 播放 ROS2 Bag
- [x] 撰寫 Subscriber 拆分 RGBT 影像
- [x] Thermal 圖像增強與可視化處理
- [x] 重新發佈 RGB / Thermal Topics

#### 資料集製作
- [x] 影像擷取（png）
- [x] 使用 Labelme 進行分割標註（json）
- [x] 轉換為 Mask（png）
- [x] 轉換為 YOLO / COCO Labels（txt）
- [x] 資料拆分成 train / val
- [x] 產生 data.yaml

#### Segmentation 模型訓練與推論
- [x] 撰寫 solution.ipynb，載入資料集
- [x] 訓練模型並微調參數
- [x] 驗證模型推論與可視化
- [x] 匯出權重與推論成果

#### 文件與成果
- [x] 撰寫安裝與執行說明

---

### ROS 的操作與影像處理

#### Environment Setup
```bash
ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
xhost + $ip
docker run -it --name rosenv --net=host -e DISPLAY=$ip:0 -v ./ws:/ws ros:humble bash
```
```bash
source /opt/ros/humble/setup.bash
apt update && apt install -y ros-humble-cv-bridge python3-opencv
```

#### ROS2 Bag 處理與影像拆分
```bash
ros2 bag play interview_perception_exam01
python3 solution.py
```

使用 `solution.py` 作為 Subscriber node，流程如下：

1. 接收壓縮 RGBT 影像。
2. 解碼。
3. 拆分 RGB 與 Thermal 資訊。
4. Thermal 圖像進行增強與轉換。
5. 發佈兩個獨立 Topics（RGB / Thermal）。
6. 影像儲存，輸出 png 格式影像，作為後續訓練資料來源。

### 訓練 Segmentation Model

#### 資料集製作
1. 透過前步驟取得影像。
2. 使用 Labelme 進行語意分割標註，產生 json annotations。
3. 轉為 Masks。
    ```bash
    python3 gen_masks.py
    ```
4. 產生 Labels。
    ```bash
    python3 gen_labels.py
    ```
5. 拆分資料集與配置 data.yaml。
    ```
    coco_dataset/
    ├─ train/
    │  ├─ images/
    │  └─ labels/
    ├─ val/
    │  ├─ images/
    │  └─ labels/
    └─ data.yaml
    ```

#### Segmentation 模型訓練

透過 `solution.ipynb` 以 YOLO 進行 training 以及 inference。
1. 載入資料集
2. 定義模型架構與參數
3. 訓練、驗證與超參數調整
4. 儲存訓練模型與結果
    ```
    runs/segment/
        ├── train/ (訓練模型、訓練過程)
        │   ├── weights/
        │   │   └── best.pt
        │   └── ...
        └── predict/ (結果)
    ```

### 情境題
1. 在你看來，機器人在執行料理任務的過程中，有哪些關鍵性的 Perception 資訊是機器人
必須精確掌握的？你會如何設計系統或方法來實作並有效獲取這些 Perception 資訊？
    > 在料理任務中，我認為機器人必須精準掌握食材位置、狀態變化（如：切塊、熟度、顏色變化）、器具辨識與操作區域安全性。我會以多感測器融合的方式建構感知系統：使用 RGB-D 相機取得物件位置與深度資訊，用語義分割模型辨識食材與器具，再搭配即時物件追蹤與力回饋感測器來監控抓取與接觸狀態。此外，透過標準化資料集與影像前處理流程，可確保感知模型在不同光源與環境下維持穩定。

2. 假設上述的感知模型已經訓練完成，且達到理想的準確度與可靠性，你接下來會如何將這
個模型實際應用在機器人的料理任務流程當中？
    > 在感知模型已訓練完成的情況下，我會將其整合至機器人的任務控制流程中，作為決策與動作規劃的輸入來源。我的具體作法是：模型負責提供即時的物件定位、分類與狀態資訊，這些結果會餵給任務規劃器與運動控制模組，用於抓取、切割、翻面、擺盤等動作決策。此外，我會將系統設計為回饋式架構：當模型輸出偵測到狀態變更（如：食材熟度達標、物件移動），控制流程會即時更新動作指令，確保料理任務具備自適應性與連續性。


---

PART 2: Robot Learning
--

使用 Diffusion Policy（或等效實作）在 Push-T 環境訓練 visuomotor policy，資料集依序為 v1 與 v2，完成後需部署至模擬環境並計算成功率。

### 架構概覽

流程包含：資料解壓與檢查、建立 dataset loader、訓練模型、載入 checkpoint、在 gym-pusht 執行推論並統計成功率。

### 資料處理

解壓 .zarr，檢查 keys、影像、狀態與動作維度，再進行影像縮放與正規化、狀態與動作標準化。如需可加入輕量增強。實作 PyTorch Dataset 以回傳 obs 與對應 action。

### 模型與訓練

可使用官方 DP 或等效實作，核心為 image encoder + state encoder + diffusion 模型。訓練建議 batch_size 32～128、lr 約 1e-4、timesteps 約 1000，視硬體調整 epochs 與 checkpoint 間隔。

### 訓練環境與步驟

建立虛擬環境、安裝依賴（torch、zarr、gym-pusht 等），解壓資料集後執行官方或自製 train script，指定 config 與資料路徑。

### 部署與評估

匯入 gym-pusht 環境與 checkpoint，建立 policy.act(obs) 的推論流程。在 N 次 episodes 中反覆 reset、step、判斷 success（由 info 或距離閾值）。輸出成功率與回報等統計。

### 風險與替代方案

可能遇到運算量過大、資料尺度不一致、採樣不穩等問題，可簡化模型、正規化資料或降低 diffusion steps。亦可先用 baseline 做初測再換 DP。