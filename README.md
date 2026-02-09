# EDA 設計環境稽核系統 (EDA Design Environment Audit System)

這是我想要從**半導體硬體研發工程師**轉職 **IC設計 CAD/EDA工程師**所開發的**第三個個人專案**。

---

## 專案目標:

本專案專注於 「Sign-off階段前的環境一致性校驗」，在晶片設計流程中，一個專案往往包含數百個設計模組，在最終簽核（Sign-off）階段，手動檢查每個模組的環境設定（PDK 版本、Library 統一性、運算資源配置）極度低效且易出錯。模擬設計團隊在多個不同的伺服器或專案版本下跑模擬。
開發一個工具**透過 Python 開發高效能稽核引擎，同步掃描數百個設計模組，確保所有環境參數符合Golden Spec，並在通過後自動觸發後續 EDA 驗證流程**。

---

## 專案功能:

- **主要功能**：
    - **平行讀取與格式識別**：用`multiprocessing.Pool`開啟多個進程並同時讀取，讀取檔案時，根據副檔名（.json, .csv, .yaml, .tcl）自動切換不同的 load 函式。
    - **數據解析**：使用`Regex`在.json/.csv/.yaml/.tcl 多種格式檔案中，精準過濾出想要的數據。
    - **自動化處理**：
     - ■ 稽核通過後，利用`subprocess`動態啟動下一階段 EDA 工具（如 Formality），實現 Flow 自動化。
     - ■ 資料彙整與視覺化報表：把檢查結果存入`List of Dictionaries`，轉換成`Pandas DataFrame`，呼叫 .to_html()。   
    - **內建說明模式**：提供指令使用範例，引導使用者如何執行主程式。

- **專案架構**：
    - **非結構化資料解析**：從非結構化資料（如 Verilog,TCL）提取所需數據。
    - **各項目稽核**：
     - ■ 環境一致性：利用`Python Sets`快速比對模組目錄是否缺失關鍵檔案。
     - ■ 資源合規性：稽核各工具的記憶體分配與優先級，防止因硬體配置錯誤導致的模擬崩潰。
     - ■ PDK 版本校驗：確保統一使用專案規定的 PDK 版本。 
    - **自動化處理**：
     - ■ 自動生成格式化的錯誤通知信件草稿（Log），精確列出違規項與負責人。
     - ■ 動態注入環境變數並模擬啟動 EDA 工具。
---

## 如何執行:

請確保您的環境已安裝Python3.13，並安裝必要的第三方套件（pip install pandas pyyaml）。

1.Clone儲存庫
```
git clone https://github.com/Chia-Rou-Huang/EDA_Env_Audit_System.git
cd EDA_Env_Audit_System

```

2.依賴套件

pip install pandas pyyaml jinja2


3.執行

在執行正式稽核前，需先生成模擬的設計模組數據，並準備好模擬執行檔：

```
bash
# 生成 200 個模組的測試數據與Golden Spec
python3 gen_data.py

# 建立模擬執行檔並賦予權限 (Mac/Linux)
echo -e '#!/bin/bash\necho "Formality Mock Tool: Verified $2"' > bin/formality
chmod +x bin/formality

```

執行主稽核程式(可以直接執行，或透過參數指定核心數量)

```

bash
# 模式 A：標準執行 (自動偵測所有 CPU 核心)
python3 main_auditor.py

# 模式 B：指定使用 n 個平行執行緒
python3 main_auditor.py --jobs n

# 模式 C：查看完整指令說明
python3 main_auditor.py --help

```
---

## 範例輸出:

###📁稽核紀錄(audit_trace.log)

```
2026-02-08 15:26:00 - [INFO] - 掃描模組目錄: ./input_data
2026-02-08 15:26:00 - [INFO] - 偵測到 200 個專案，啟動平行處理執行緒 (Jobs=4)
2026-02-08 15:26:01 - [INFO] - 任務完成。報表：output/final_report.html，錯誤清單：output/violation_list.csv

```

###📁HTML report(final_report.html)





###📁Error list(violation_list.csv)


| Module_ID | Engineer | Total_Issues | Issue_Summary |
| :--- | :--- | :--- | :--- |
| **mod_001** | engineer_6 | 1 | PDK 版本非法: v2.0 |
| **mod_002** | engineer_10 | 1 | PDK 版本非法: v4.0 |
| **mod_004** | engineer_2 | 1 | PDK 版本非法: v4.0 |
| **mod_006** | engineer_5 | 1 | 工具報表遺失: ['Formality'] |
| **mod_008** | engineer_6 | 1 | PDK 版本非法: v4.0 |
| **mod_009** | engineer_5 | 1 | 工具報表遺失: ['VCS'] |
| **mod_010** | engineer_2 | 10 | JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| PDK 版本非法: v4.0 \| 全域環境日期錯誤: 2025-05-10 |
<details>
<summary>點此展開查看其餘違規模組清單</summary>
| **mod_015** | engineer_6 | 4 | 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk Power 記憶體不足: 實際僅8GB |
| **mod_016** | engineer_10 | 1 | 工具報表遺失: ['PrimeTime', 'Formality'] |
| **mod_017** | engineer_9 | 1 | PDK 版本非法: v4.0 |
| **mod_018** | engineer_3 | 1 | 工具報表遺失: ['VCS'] |
| **mod_019** | engineer_6 | 1 | PDK 版本非法: v4.0 |
| **mod_020** | engineer_6 | 10 | 製程不符: 實際為 N12 \| JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_021** | engineer_7 | 1 | PDK 版本非法: v4.0 |
| **mod_022** | engineer_6 | 2 | 工具報表遺失: ['RedHawk', 'Formality', 'PrimeTime'] \| PDK 版本非法: v2.0 |
| **mod_025** | engineer_5 | 2 | Formal 版本衝突: ['v3.0', 'v2.0'] \| PDK 版本非法: v2.0 |
| **mod_026** | engineer_4 | 1 | PDK 版本非法: v2.0 |
| **mod_027** | engineer_7 | 1 | PDK 版本非法: v4.0 |
| **mod_028** | engineer_7 | 1 | 工具報表遺失: ['RedHawk', 'PrimeTime', 'Formality'] |
| **mod_030** | engineer_3 | 14 | JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 工具 RedHawk Power 記憶體不足: 實際僅8GB \| PDK 版本非法: v2.0 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_031** | engineer_9 | 1 | PDK 版本非法: v4.0 |
| **mod_032** | engineer_2 | 1 | 工具報表遺失: ['RedHawk', 'Formality'] |
| **mod_035** | engineer_1 | 1 | PDK 版本非法: v4.0 |
| **mod_036** | engineer_9 | 1 | 工具報表遺失: ['RedHawk'] |
| **mod_039** | engineer_5 | 1 | PDK 版本非法: v4.0 |
| **mod_040** | engineer_1 | 11 | 製程不符: 實際為 N12 \| JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| PDK 版本非法: v2.0 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_042** | engineer_3 | 1 | PDK 版本非法: v2.0 |
| **mod_043** | engineer_3 | 1 | 工具報表遺失: ['PrimeTime', 'RedHawk'] |
| **mod_044** | engineer_9 | 1 | PDK 版本非法: v4.0 |
| **mod_045** | engineer_8 | 4 | 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk Power 記憶體不足: 實際僅8GB |
| **mod_047** | engineer_8 | 1 | PDK 版本非法: v4.0 |
| **mod_048** | engineer_7 | 1 | PDK 版本非法: v4.0 |
| **mod_049** | engineer_1 | 1 | PDK 版本非法: v2.0 |
| **mod_050** | engineer_2 | 10 | JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 版本衝突: ['v3.0', 'v2.0'] \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_053** | engineer_10 | 1 | PDK 版本非法: v4.0 |
| **mod_058** | engineer_2 | 1 | PDK 版本非法: v4.0 |
| **mod_059** | engineer_3 | 1 | PDK 版本非法: v2.0 |
| **mod_060** | engineer_5 | 15 | 製程不符: 實際為 N12 \| JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 工具 RedHawk Power 記憶體不足: 實際僅8GB \| PDK 版本非法: v4.0 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_061** | engineer_9 | 2 | 工具報表遺失: ['PrimeTime'] \| PDK 版本非法: v4.0 |
| **mod_063** | engineer_4 | 1 | 工具報表遺失: ['VCS'] |
| **mod_066** | engineer_8 | 1 | 工具報表遺失: ['Formality'] |
| **mod_068** | engineer_3 | 1 | PDK 版本非法: v4.0 |
| **mod_069** | engineer_1 | 1 | PDK 版本非法: v2.0 |
| **mod_070** | engineer_2 | 9 | JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_073** | engineer_1 | 2 | 工具報表遺失: ['VCS', 'RedHawk'] \| PDK 版本非法: v4.0 |
| **mod_074** | engineer_9 | 1 | PDK 版本非法: v4.0 |
| **mod_075** | engineer_3 | 5 | Formal 版本衝突: ['v3.0', 'v2.0'] \| 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk Power 記憶體不足: 實際僅8GB |
| **mod_076** | engineer_5 | 1 | 工具報表遺失: ['PrimeTime'] |
| **mod_080** | engineer_7 | 11 | 製程不符: 實際為 N12 \| JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| PDK 版本非法: v2.0 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_083** | engineer_8 | 1 | PDK 版本非法: v2.0 |
| **mod_088** | engineer_6 | 1 | PDK 版本非法: v4.0 |
| **mod_090** | engineer_3 | 14 | JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 工具 RedHawk Power 記憶體不足: 實際僅8GB \| PDK 版本非法: v4.0 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_092** | engineer_4 | 1 | PDK 版本非法: v2.0 |
| **mod_093** | engineer_10 | 1 | PDK 版本非法: v4.0 |
| **mod_094** | engineer_3 | 1 | PDK 版本非法: v2.0 |
| **mod_096** | engineer_9 | 1 | PDK 版本非法: v2.0 |
| **mod_098** | engineer_7 | 1 | PDK 版本非法: v2.0 |
| **mod_100** | engineer_7 | 11 | 製程不符: 實際為 N12 \| JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 版本衝突: ['v3.0', 'v2.0'] \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_102** | engineer_1 | 1 | PDK 版本非法: v4.0 |
| **mod_103** | engineer_7 | 1 | PDK 版本非法: v2.0 |
| **mod_104** | engineer_6 | 2 | 工具報表遺失: ['PrimeTime'] \| PDK 版本非法: v2.0 |
| **mod_105** | engineer_5 | 4 | 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk Power 記憶體不足: 實際僅8GB |
| **mod_110** | engineer_4 | 9 | JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_111** | engineer_6 | 1 | PDK 版本非法: v2.0 |
| **mod_112** | engineer_10 | 1 | PDK 版本非法: v4.0 |
| **mod_114** | engineer_3 | 1 | PDK 版本非法: v4.0 |
| **mod_115** | engineer_6 | 1 | PDK 版本非法: v2.0 |
| **mod_117** | engineer_8 | 1 | PDK 版本非法: v2.0 |
| **mod_118** | engineer_1 | 2 | 工具報表遺失: ['RedHawk'] \| PDK 版本非法: v4.0 |
| **mod_119** | engineer_6 | 1 | PDK 版本非法: v4.0 |
| **mod_120** | engineer_4 | 15 | 製程不符: 實際為 N12 \| JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 工具 RedHawk Power 記憶體不足: 實際僅8GB \| PDK 版本非法: v2.0 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_122** | engineer_1 | 1 | 工具報表遺失: ['Formality'] |
| **mod_123** | engineer_3 | 1 | PDK 版本非法: v2.0 |
| **mod_125** | engineer_10 | 2 | Formal 版本衝突: ['v3.0', 'v2.0'] \| PDK 版本非法: v4.0 |
| **mod_126** | engineer_1 | 1 | PDK 版本非法: v4.0 |
| **mod_128** | engineer_4 | 1 | 工具報表遺失: ['Formality'] |
| **mod_130** | engineer_1 | 9 | JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_131** | engineer_5 | 1 | 工具報表遺失: ['RedHawk'] |
| **mod_133** | engineer_2 | 1 | 工具報表遺失: ['VCS', 'Formality'] |
| **mod_135** | engineer_1 | 5 | 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk Power 記憶體不足: 實際僅8GB \| PDK 版本非法: v2.0 |
| **mod_137** | engineer_2 | 1 | 工具報表遺失: ['Formality', 'VCS', 'RedHawk'] |
| **mod_138** | engineer_1 | 1 | 工具報表遺失: ['RedHawk', 'VCS', 'PrimeTime'] |
| **mod_139** | engineer_1 | 2 | 工具報表遺失: ['RedHawk'] \| PDK 版本非法: v2.0 |
| **mod_140** | engineer_6 | 11 | 製程不符: 實際為 N12 \| JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| PDK 版本非法: v4.0 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_143** | engineer_1 | 2 | 工具報表遺失: ['RedHawk', 'PrimeTime'] \| PDK 版本非法: v2.0 |
| **mod_145** | engineer_10 | 1 | PDK 版本非法: v2.0 |
| **mod_148** | engineer_1 | 1 | PDK 版本非法: v2.0 |
| **mod_150** | engineer_6 | 15 | JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 版本衝突: ['v3.0', 'v2.0'] \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 工具 RedHawk Power 記憶體不足: 實際僅8GB \| PDK 版本非法: v4.0 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_154** | engineer_8 | 1 | 工具報表遺失: ['RedHawk'] |
| **mod_160** | engineer_7 | 10 | 製程不符: 實際為 N12 \| JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_164** | engineer_10 | 1 | 工具報表遺失: ['Formality', 'PrimeTime', 'VCS'] |
| **mod_165** | engineer_8 | 4 | 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk Power 記憶體不足: 實際僅8GB |
| **mod_166** | engineer_9 | 1 | PDK 版本非法: v2.0 |
| **mod_168** | engineer_8 | 1 | PDK 版本非法: v2.0 |
| **mod_169** | engineer_1 | 1 | PDK 版本非法: v4.0 |
| **mod_170** | engineer_7 | 9 | JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_172** | engineer_2 | 1 | 工具報表遺失: ['VCS'] |
| **mod_173** | engineer_4 | 1 | 工具報表遺失: ['VCS', 'PrimeTime', 'RedHawk'] |
| **mod_175** | engineer_2 | 2 | Formal 版本衝突: ['v3.0', 'v2.0'] \| PDK 版本非法: v4.0 |
| **mod_177** | engineer_6 | 1 | PDK 版本非法: v2.0 |
| **mod_180** | engineer_3 | 15 | 製程不符: 實際為 N12 \| JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 工具 RedHawk Power 記憶體不足: 實際僅8GB \| PDK 版本非法: v2.0 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_181** | engineer_3 | 1 | PDK 版本非法: v2.0 |
| **mod_182** | engineer_1 | 1 | PDK 版本非法: v4.0 |
| **mod_190** | engineer_7 | 10 | JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 腳本日期不符: 2025-05-10 \| 工具 VCS 報告日期偏差: 2025-05-10 \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 Formality 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| PDK 版本非法: v4.0 \| 全域環境日期錯誤: 2025-05-10 |
| **mod_191** | engineer_2 | 1 | PDK 版本非法: v4.0 |
| **mod_193** | engineer_9 | 1 | PDK 版本非法: v2.0 |
| **mod_195** | engineer_5 | 4 | 工具 VCS GLS 記憶體不足: 實際僅8GB \| 工具 PrimeTime STA 記憶體不足: 實際僅8GB \| 工具 Formality Formal 記憶體不足: 實際僅8GB \| 工具 RedHawk Power 記憶體不足: 實際僅8GB |
| **mod_197** | engineer_8 | 1 | PDK 版本非法: v4.0 |
| **mod_199** | engineer_6 | 1 | PDK 版本非法: v2.0 |
| **mod_200** | engineer_5 | 10 | 製程不符: 實際為 N12 \| JSON 日期錯誤: 2025-05-10 \| golden 網表日期過期: 2025-05-10 \| revised 網表日期過期: 2025-05-10 \| Formal 版本衝突: ['v3.0', 'v2.0'] \| Formal 腳本日期不符: 2025-05-10 \| 工具報表遺失: ['VCS', 'Formality'] \| 工具 PrimeTime 報告日期偏差: 2025-05-10 \| 工具 RedHawk 報告日期偏差: 2025-05-10 \| 全域環境日期錯誤: 2025-05-10 |
</details>

###📁Error Information mail(mail_sent.log)

```
==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:00
RECIPIENT: engineer_7@design.com
CC: manager@design.com
BLOCK_ID: mod_103
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================




==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:00
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_104
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['PrimeTime']
  [2] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================
```

<details>
<summary>點此展開查看其餘錯誤資訊郵件</summary>

==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:00
RECIPIENT: engineer_2@design.com
CC: manager@design.com
BLOCK_ID: mod_133
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['VCS', 'Formality']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:00
RECIPIENT: engineer_5@design.com
CC: manager@design.com
BLOCK_ID: mod_105
VIOLATIONS DETECTED:

  [1] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [2] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [3] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [4] 工具 RedHawk Power 記憶體不足: 實際僅8GB

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:00
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_102
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_169
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_135
VIOLATIONS DETECTED:

  [1] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [2] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [3] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [4] 工具 RedHawk Power 記憶體不足: 實際僅8GB
  [5] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_8@design.com
CC: manager@design.com
BLOCK_ID: mod_047
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_5@design.com
CC: manager@design.com
BLOCK_ID: mod_195
VIOLATIONS DETECTED:

  [1] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [2] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [3] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [4] 工具 RedHawk Power 記憶體不足: 實際僅8GB

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_040
VIOLATIONS DETECTED:

  [1] 製程不符: 實際為 N12
  [2] JSON 日期錯誤: 2025-05-10
  [3] golden 網表日期過期: 2025-05-10
  [4] revised 網表日期過期: 2025-05-10
  [5] Formal 腳本日期不符: 2025-05-10
  [6] 工具 VCS 報告日期偏差: 2025-05-10
  [7] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [8] 工具 Formality 報告日期偏差: 2025-05-10
  [9] 工具 RedHawk 報告日期偏差: 2025-05-10
  [10] PDK 版本非法: v2.0
  [11] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_9@design.com
CC: manager@design.com
BLOCK_ID: mod_193
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_9@design.com
CC: manager@design.com
BLOCK_ID: mod_166
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_2@design.com
CC: manager@design.com
BLOCK_ID: mod_070
VIOLATIONS DETECTED:

  [1] JSON 日期錯誤: 2025-05-10
  [2] golden 網表日期過期: 2025-05-10
  [3] revised 網表日期過期: 2025-05-10
  [4] Formal 腳本日期不符: 2025-05-10
  [5] 工具 VCS 報告日期偏差: 2025-05-10
  [6] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [7] 工具 Formality 報告日期偏差: 2025-05-10
  [8] 工具 RedHawk 報告日期偏差: 2025-05-10
  [9] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_5@design.com
CC: manager@design.com
BLOCK_ID: mod_076
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['PrimeTime']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_049
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_8@design.com
CC: manager@design.com
BLOCK_ID: mod_083
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_7@design.com
CC: manager@design.com
BLOCK_ID: mod_160
VIOLATIONS DETECTED:

  [1] 製程不符: 實際為 N12
  [2] JSON 日期錯誤: 2025-05-10
  [3] golden 網表日期過期: 2025-05-10
  [4] revised 網表日期過期: 2025-05-10
  [5] Formal 腳本日期不符: 2025-05-10
  [6] 工具 VCS 報告日期偏差: 2025-05-10
  [7] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [8] 工具 Formality 報告日期偏差: 2025-05-10
  [9] 工具 RedHawk 報告日期偏差: 2025-05-10
  [10] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_7@design.com
CC: manager@design.com
BLOCK_ID: mod_048
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_150
VIOLATIONS DETECTED:

  [1] JSON 日期錯誤: 2025-05-10
  [2] golden 網表日期過期: 2025-05-10
  [3] revised 網表日期過期: 2025-05-10
  [4] Formal 版本衝突: ['v3.0', 'v2.0']
  [5] Formal 腳本日期不符: 2025-05-10
  [6] 工具 VCS 報告日期偏差: 2025-05-10
  [7] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [8] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [9] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [10] 工具 Formality 報告日期偏差: 2025-05-10
  [11] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [12] 工具 RedHawk 報告日期偏差: 2025-05-10
  [13] 工具 RedHawk Power 記憶體不足: 實際僅8GB
  [14] PDK 版本非法: v4.0
  [15] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_7@design.com
CC: manager@design.com
BLOCK_ID: mod_098
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_8@design.com
CC: manager@design.com
BLOCK_ID: mod_168
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_10@design.com
CC: manager@design.com
BLOCK_ID: mod_053
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_015
VIOLATIONS DETECTED:

  [1] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [2] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [3] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [4] 工具 RedHawk Power 記憶體不足: 實際僅8GB

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_9@design.com
CC: manager@design.com
BLOCK_ID: mod_096
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_5@design.com
CC: manager@design.com
BLOCK_ID: mod_025
VIOLATIONS DETECTED:

  [1] Formal 版本衝突: ['v3.0', 'v2.0']
  [2] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_022
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['RedHawk', 'Formality', 'PrimeTime']
  [2] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_180
VIOLATIONS DETECTED:

  [1] 製程不符: 實際為 N12
  [2] JSON 日期錯誤: 2025-05-10
  [3] golden 網表日期過期: 2025-05-10
  [4] revised 網表日期過期: 2025-05-10
  [5] Formal 腳本日期不符: 2025-05-10
  [6] 工具 VCS 報告日期偏差: 2025-05-10
  [7] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [8] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [9] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [10] 工具 Formality 報告日期偏差: 2025-05-10
  [11] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [12] 工具 RedHawk 報告日期偏差: 2025-05-10
  [13] 工具 RedHawk Power 記憶體不足: 實際僅8GB
  [14] PDK 版本非法: v2.0
  [15] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_4@design.com
CC: manager@design.com
BLOCK_ID: mod_120
VIOLATIONS DETECTED:

  [1] 製程不符: 實際為 N12
  [2] JSON 日期錯誤: 2025-05-10
  [3] golden 網表日期過期: 2025-05-10
  [4] revised 網表日期過期: 2025-05-10
  [5] Formal 腳本日期不符: 2025-05-10
  [6] 工具 VCS 報告日期偏差: 2025-05-10
  [7] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [8] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [9] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [10] 工具 Formality 報告日期偏差: 2025-05-10
  [11] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [12] 工具 RedHawk 報告日期偏差: 2025-05-10
  [13] 工具 RedHawk Power 記憶體不足: 實際僅8GB
  [14] PDK 版本非法: v2.0
  [15] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_5@design.com
CC: manager@design.com
BLOCK_ID: mod_006
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['Formality']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_5@design.com
CC: manager@design.com
BLOCK_ID: mod_039
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_143
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['RedHawk', 'PrimeTime']
  [2] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_001
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_8@design.com
CC: manager@design.com
BLOCK_ID: mod_117
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_118
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['RedHawk']
  [2] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_4@design.com
CC: manager@design.com
BLOCK_ID: mod_128
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['Formality']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_111
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_4@design.com
CC: manager@design.com
BLOCK_ID: mod_110
VIOLATIONS DETECTED:

  [1] JSON 日期錯誤: 2025-05-10
  [2] golden 網表日期過期: 2025-05-10
  [3] revised 網表日期過期: 2025-05-10
  [4] Formal 腳本日期不符: 2025-05-10
  [5] 工具 VCS 報告日期偏差: 2025-05-10
  [6] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [7] 工具 Formality 報告日期偏差: 2025-05-10
  [8] 工具 RedHawk 報告日期偏差: 2025-05-10
  [9] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_9@design.com
CC: manager@design.com
BLOCK_ID: mod_031
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_126
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_9@design.com
CC: manager@design.com
BLOCK_ID: mod_036
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['RedHawk']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_119
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_5@design.com
CC: manager@design.com
BLOCK_ID: mod_009
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['VCS']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_008
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_030
VIOLATIONS DETECTED:

  [1] JSON 日期錯誤: 2025-05-10
  [2] golden 網表日期過期: 2025-05-10
  [3] revised 網表日期過期: 2025-05-10
  [4] Formal 腳本日期不符: 2025-05-10
  [5] 工具 VCS 報告日期偏差: 2025-05-10
  [6] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [7] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [8] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [9] 工具 Formality 報告日期偏差: 2025-05-10
  [10] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [11] 工具 RedHawk 報告日期偏差: 2025-05-10
  [12] 工具 RedHawk Power 記憶體不足: 實際僅8GB
  [13] PDK 版本非法: v2.0
  [14] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_8@design.com
CC: manager@design.com
BLOCK_ID: mod_165
VIOLATIONS DETECTED:

  [1] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [2] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [3] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [4] 工具 RedHawk Power 記憶體不足: 實際僅8GB

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_2@design.com
CC: manager@design.com
BLOCK_ID: mod_191
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_181
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_2@design.com
CC: manager@design.com
BLOCK_ID: mod_175
VIOLATIONS DETECTED:

  [1] Formal 版本衝突: ['v3.0', 'v2.0']
  [2] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_2@design.com
CC: manager@design.com
BLOCK_ID: mod_172
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['VCS']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_090
VIOLATIONS DETECTED:

  [1] JSON 日期錯誤: 2025-05-10
  [2] golden 網表日期過期: 2025-05-10
  [3] revised 網表日期過期: 2025-05-10
  [4] Formal 腳本日期不符: 2025-05-10
  [5] 工具 VCS 報告日期偏差: 2025-05-10
  [6] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [7] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [8] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [9] 工具 Formality 報告日期偏差: 2025-05-10
  [10] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [11] 工具 RedHawk 報告日期偏差: 2025-05-10
  [12] 工具 RedHawk Power 記憶體不足: 實際僅8GB
  [13] PDK 版本非法: v4.0
  [14] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_10@design.com
CC: manager@design.com
BLOCK_ID: mod_145
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_8@design.com
CC: manager@design.com
BLOCK_ID: mod_154
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['RedHawk']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_4@design.com
CC: manager@design.com
BLOCK_ID: mod_063
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['VCS']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_4@design.com
CC: manager@design.com
BLOCK_ID: mod_173
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['VCS', 'PrimeTime', 'RedHawk']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_7@design.com
CC: manager@design.com
BLOCK_ID: mod_190
VIOLATIONS DETECTED:

  [1] JSON 日期錯誤: 2025-05-10
  [2] golden 網表日期過期: 2025-05-10
  [3] revised 網表日期過期: 2025-05-10
  [4] Formal 腳本日期不符: 2025-05-10
  [5] 工具 VCS 報告日期偏差: 2025-05-10
  [6] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [7] 工具 Formality 報告日期偏差: 2025-05-10
  [8] 工具 RedHawk 報告日期偏差: 2025-05-10
  [9] PDK 版本非法: v4.0
  [10] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_042
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_10@design.com
CC: manager@design.com
BLOCK_ID: mod_164
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['Formality', 'PrimeTime', 'VCS']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_130
VIOLATIONS DETECTED:

  [1] JSON 日期錯誤: 2025-05-10
  [2] golden 網表日期過期: 2025-05-10
  [3] revised 網表日期過期: 2025-05-10
  [4] Formal 腳本日期不符: 2025-05-10
  [5] 工具 VCS 報告日期偏差: 2025-05-10
  [6] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [7] 工具 Formality 報告日期偏差: 2025-05-10
  [8] 工具 RedHawk 報告日期偏差: 2025-05-10
  [9] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_138
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['RedHawk', 'VCS', 'PrimeTime']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_2@design.com
CC: manager@design.com
BLOCK_ID: mod_137
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['Formality', 'VCS', 'RedHawk']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_075
VIOLATIONS DETECTED:

  [1] Formal 版本衝突: ['v3.0', 'v2.0']
  [2] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [3] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [4] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [5] 工具 RedHawk Power 記憶體不足: 實際僅8GB

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_10@design.com
CC: manager@design.com
BLOCK_ID: mod_016
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['PrimeTime', 'Formality']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_139
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['RedHawk']
  [2] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_7@design.com
CC: manager@design.com
BLOCK_ID: mod_021
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_7@design.com
CC: manager@design.com
BLOCK_ID: mod_100
VIOLATIONS DETECTED:

  [1] 製程不符: 實際為 N12
  [2] JSON 日期錯誤: 2025-05-10
  [3] golden 網表日期過期: 2025-05-10
  [4] revised 網表日期過期: 2025-05-10
  [5] Formal 版本衝突: ['v3.0', 'v2.0']
  [6] Formal 腳本日期不符: 2025-05-10
  [7] 工具 VCS 報告日期偏差: 2025-05-10
  [8] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [9] 工具 Formality 報告日期偏差: 2025-05-10
  [10] 工具 RedHawk 報告日期偏差: 2025-05-10
  [11] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_019
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_4@design.com
CC: manager@design.com
BLOCK_ID: mod_026
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_2@design.com
CC: manager@design.com
BLOCK_ID: mod_010
VIOLATIONS DETECTED:

  [1] JSON 日期錯誤: 2025-05-10
  [2] golden 網表日期過期: 2025-05-10
  [3] revised 網表日期過期: 2025-05-10
  [4] Formal 腳本日期不符: 2025-05-10
  [5] 工具 VCS 報告日期偏差: 2025-05-10
  [6] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [7] 工具 Formality 報告日期偏差: 2025-05-10
  [8] 工具 RedHawk 報告日期偏差: 2025-05-10
  [9] PDK 版本非法: v4.0
  [10] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_018
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['VCS']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_7@design.com
CC: manager@design.com
BLOCK_ID: mod_028
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['RedHawk', 'PrimeTime', 'Formality']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_7@design.com
CC: manager@design.com
BLOCK_ID: mod_027
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_9@design.com
CC: manager@design.com
BLOCK_ID: mod_074
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_9@design.com
CC: manager@design.com
BLOCK_ID: mod_017
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_020
VIOLATIONS DETECTED:

  [1] 製程不符: 實際為 N12
  [2] JSON 日期錯誤: 2025-05-10
  [3] golden 網表日期過期: 2025-05-10
  [4] revised 網表日期過期: 2025-05-10
  [5] Formal 腳本日期不符: 2025-05-10
  [6] 工具 VCS 報告日期偏差: 2025-05-10
  [7] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [8] 工具 Formality 報告日期偏差: 2025-05-10
  [9] 工具 RedHawk 報告日期偏差: 2025-05-10
  [10] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_7@design.com
CC: manager@design.com
BLOCK_ID: mod_080
VIOLATIONS DETECTED:

  [1] 製程不符: 實際為 N12
  [2] JSON 日期錯誤: 2025-05-10
  [3] golden 網表日期過期: 2025-05-10
  [4] revised 網表日期過期: 2025-05-10
  [5] Formal 腳本日期不符: 2025-05-10
  [6] 工具 VCS 報告日期偏差: 2025-05-10
  [7] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [8] 工具 Formality 報告日期偏差: 2025-05-10
  [9] 工具 RedHawk 報告日期偏差: 2025-05-10
  [10] PDK 版本非法: v2.0
  [11] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_043
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['PrimeTime', 'RedHawk']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_035
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_088
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_9@design.com
CC: manager@design.com
BLOCK_ID: mod_044
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_5@design.com
CC: manager@design.com
BLOCK_ID: mod_200
VIOLATIONS DETECTED:

  [1] 製程不符: 實際為 N12
  [2] JSON 日期錯誤: 2025-05-10
  [3] golden 網表日期過期: 2025-05-10
  [4] revised 網表日期過期: 2025-05-10
  [5] Formal 版本衝突: ['v3.0', 'v2.0']
  [6] Formal 腳本日期不符: 2025-05-10
  [7] 工具報表遺失: ['VCS', 'Formality']
  [8] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [9] 工具 RedHawk 報告日期偏差: 2025-05-10
  [10] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_5@design.com
CC: manager@design.com
BLOCK_ID: mod_131
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['RedHawk']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_2@design.com
CC: manager@design.com
BLOCK_ID: mod_032
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['RedHawk', 'Formality']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_2@design.com
CC: manager@design.com
BLOCK_ID: mod_004
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_073
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['VCS', 'RedHawk']
  [2] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_8@design.com
CC: manager@design.com
BLOCK_ID: mod_045
VIOLATIONS DETECTED:

  [1] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [2] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [3] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [4] 工具 RedHawk Power 記憶體不足: 實際僅8GB

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_068
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_199
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_094
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_2@design.com
CC: manager@design.com
BLOCK_ID: mod_058
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_10@design.com
CC: manager@design.com
BLOCK_ID: mod_093
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_2@design.com
CC: manager@design.com
BLOCK_ID: mod_050
VIOLATIONS DETECTED:

  [1] JSON 日期錯誤: 2025-05-10
  [2] golden 網表日期過期: 2025-05-10
  [3] revised 網表日期過期: 2025-05-10
  [4] Formal 版本衝突: ['v3.0', 'v2.0']
  [5] Formal 腳本日期不符: 2025-05-10
  [6] 工具 VCS 報告日期偏差: 2025-05-10
  [7] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [8] 工具 Formality 報告日期偏差: 2025-05-10
  [9] 工具 RedHawk 報告日期偏差: 2025-05-10
  [10] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_059
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_8@design.com
CC: manager@design.com
BLOCK_ID: mod_066
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['Formality']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_4@design.com
CC: manager@design.com
BLOCK_ID: mod_092
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_148
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_177
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_8@design.com
CC: manager@design.com
BLOCK_ID: mod_197
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_182
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_9@design.com
CC: manager@design.com
BLOCK_ID: mod_061
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['PrimeTime']
  [2] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_10@design.com
CC: manager@design.com
BLOCK_ID: mod_002
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_069
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_140
VIOLATIONS DETECTED:

  [1] 製程不符: 實際為 N12
  [2] JSON 日期錯誤: 2025-05-10
  [3] golden 網表日期過期: 2025-05-10
  [4] revised 網表日期過期: 2025-05-10
  [5] Formal 腳本日期不符: 2025-05-10
  [6] 工具 VCS 報告日期偏差: 2025-05-10
  [7] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [8] 工具 Formality 報告日期偏差: 2025-05-10
  [9] 工具 RedHawk 報告日期偏差: 2025-05-10
  [10] PDK 版本非法: v4.0
  [11] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_7@design.com
CC: manager@design.com
BLOCK_ID: mod_170
VIOLATIONS DETECTED:

  [1] JSON 日期錯誤: 2025-05-10
  [2] golden 網表日期過期: 2025-05-10
  [3] revised 網表日期過期: 2025-05-10
  [4] Formal 腳本日期不符: 2025-05-10
  [5] 工具 VCS 報告日期偏差: 2025-05-10
  [6] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [7] 工具 Formality 報告日期偏差: 2025-05-10
  [8] 工具 RedHawk 報告日期偏差: 2025-05-10
  [9] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_114
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_1@design.com
CC: manager@design.com
BLOCK_ID: mod_122
VIOLATIONS DETECTED:

  [1] 工具報表遺失: ['Formality']

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_10@design.com
CC: manager@design.com
BLOCK_ID: mod_125
VIOLATIONS DETECTED:

  [1] Formal 版本衝突: ['v3.0', 'v2.0']
  [2] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_3@design.com
CC: manager@design.com
BLOCK_ID: mod_123
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_6@design.com
CC: manager@design.com
BLOCK_ID: mod_115
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v2.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_10@design.com
CC: manager@design.com
BLOCK_ID: mod_112
VIOLATIONS DETECTED:

  [1] PDK 版本非法: v4.0

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================



==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: 2026-02-08 15:26:01
RECIPIENT: engineer_5@design.com
CC: manager@design.com
BLOCK_ID: mod_060
VIOLATIONS DETECTED:

  [1] 製程不符: 實際為 N12
  [2] JSON 日期錯誤: 2025-05-10
  [3] golden 網表日期過期: 2025-05-10
  [4] revised 網表日期過期: 2025-05-10
  [5] Formal 腳本日期不符: 2025-05-10
  [6] 工具 VCS 報告日期偏差: 2025-05-10
  [7] 工具 VCS GLS 記憶體不足: 實際僅8GB
  [8] 工具 PrimeTime 報告日期偏差: 2025-05-10
  [9] 工具 PrimeTime STA 記憶體不足: 實際僅8GB
  [10] 工具 Formality 報告日期偏差: 2025-05-10
  [11] 工具 Formality Formal 記憶體不足: 實際僅8GB
  [12] 工具 RedHawk 報告日期偏差: 2025-05-10
  [13] 工具 RedHawk Power 記憶體不足: 實際僅8GB
  [14] PDK 版本非法: v4.0
  [15] 全域環境日期錯誤: 2025-05-10

STATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.
==================================================

</details>


---

## 檔案結構:

```
text
EDA Design Environment Audit System/
│
├── .gitignore
├── LICENSE
├── README.md                            # 本說明文件
├── main_auditor.py                      # 主程式
├── gen_data.py                          # 副程式產出待稽核檔案
├── bin                                  
│    └── formality                       # 模擬外部 EDA 執行檔 (LEC 工具)
│ 
├── config
│    └── golden_spec.yaml                # 專案各項環境設定環境規範
│ 
├── input _data                          # 由副程式產出待稽核檔案
│    │
│    ├──mod_001                          ＃ 模組001
│    │   ├──tool_info.csv
│    │   ├──setup.tcl
│    │   ├──project_status.json
│    │   ├──formal_setup.tcl
│    │   ├──mod_001_golden.v
│    │   └──mod_001_revised.v
│    │
│    ├──mod_002                          ＃ 模組002
│    │   ├──tool_info.csv
│    │   ├──setup.tcl
│    │   ├──project_status.json
│    │   ├──formal_setup.tcl
│    │   ├──mod_002_golden.v
│    │   └──mod_002_revised.v
│    │
│    ...
│    │   
│    └──mod_200                          ＃ 模組200
│        ├──tool_info.csv
│        ├──setup.tcl
│        ├──project_status.json
│        ├──formal_setup.tcl
│        ├──mod_200_golden.v
│        └──mod_200_revised.v
│ 
└── output                               # 稽核結果                     
     ├──audit_trace.log
     ├──violation_list.csv
     ├──final_report.html
     └──mail_sent.log

```
---

