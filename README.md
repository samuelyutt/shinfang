# CV + RL Take-Home Technical Assessment
[Google Drive](https://drive.google.com/drive/folders/1svWeStc2BDo3CV--Wjoui4d9eZjz-G-L?usp=sharing)

## 一、專案背景與目標
本專案的主要任務為針對提供的 RGBT ROS Bag，建置一套從影像取得、拆分處理、資料集標註、Segmentation 模型訓練到推論的完整流程。  
最終目標為實現料理場域中鍋具與相關器具（如蛋、鍋子、鍋鏟、容器等）之即時遮罩生成，以利後續影像辨識與監控應用。

### 核心工作：
- 解析並訂閱 Bag 影像資料  
- 拆分 RGB 與 Thermal 影像  
- 對 Thermal 圖像進行增強處理以利辨識  
- 重新發佈拆分後的 ROS2 Topics  
- 準備可訓練的 Segmentation Dataset  
- 建立模型訓練與 Inference Pipeline  
- 完成結果紀錄與文件撰寫  

---

## 二、TODO List（工作規劃）

### 前置與環境建置
- [x] 建立 ROS2 + Docker + Conda + PyTorch 開發環境
- [x] 安裝 OpenCV、cv_bridge 等相關依賴
- [x] 建立 ROS 套件結構與資料夾規劃

### ROS Bag 處理
- [x] 播放 ROS2 Bag
- [x] 撰寫 Subscriber 拆分 RGBT 影像
- [x] Thermal 圖像增強與可視化處理
- [x] 重新發佈 RGB / Thermal Topics

### 資料集製作
- [x] 影像擷取（png）
- [x] 使用 Labelme 進行分割標註（json）
- [x] 轉換為 Mask（png）
- [x] 轉換為 YOLO / COCO Labels（txt）
- [x] 資料拆分成 train / val
- [x] 產生 data.yaml

### Segmentation 模型訓練與推論
- [x] 撰寫 solution.ipynb，載入資料集
- [x] 訓練模型並微調參數
- [x] 驗證模型推論與可視化
- [x] 匯出權重與推論成果

### 文件與成果
- [x] 撰寫安裝與執行說明

---

## 三、系統環境建置

本專案採用 Docker 建立 ROS2 Humble 環境，以避免版本衝突並方便部署。

### Docker 容器建立
```bash
ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
xhost + $ip
docker run -it --name rosenv --net=host -e DISPLAY=$ip:0 -v ./ws:/ws ros:humble bash
```
```bash
source /opt/ros/humble/setup.bash
apt update && apt install -y ros-humble-cv-bridge python3-opencv
```

## 四、ROS2 Bag 處理與影像拆分流程
### Play Bag 及影像擷取與拆分流程
```bash
ros2 bag play interview_perception_exam01
python3 solution.py
```

使用 solution.py 作為 Subscriber 節點，流程如下：

1. 接收壓縮 RGBT 影像。
2. 解碼。
3. 拆分 RGB 與 Thermal 資訊。
4. Thermal 圖像進行增強與轉換。
5. 發佈兩個獨立 Topics（RGB / Thermal）。
6. 影像儲存，輸出 png 格式影像，作為後續訓練資料來源。

## 五、資料集製作流程
1. 影像取得：ROS Bag → png 影像
2. 使用 Labelme 進行語意分割標註，產生 json annotations 。
3. 轉為 Mask
    ```bash
    python3 gen_masks.py
    ```
4. 產生 Labels
    ```bash
    python3 gen_labels.py
    ```
5. 拆分資料集與配置 data.yaml
    ```
    coco_dataset/
    ├─ train/
    │  ├─ images/
    │  ├─ labels/
    ├─ val/
    │  ├─ images/
    │  └─ labels/
    └─ data.yaml
    ```

## 六、Segmentation 模型訓練與推論

### solution.ipynb
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
