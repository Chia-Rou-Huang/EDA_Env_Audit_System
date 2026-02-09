import os
import re
import json
import csv
import yaml
import logging
import argparse
import subprocess
import time
import sys
import pandas as pd
from datetime import datetime
from multiprocessing import Pool, cpu_count

class AuditorConfig:
    PASS = "PASS"
    FAIL = "FAIL"
    SYSTEM_ERROR = "SYSTEM_ERR"
    LOG_DIR = "output"
    REPORT_HTML = "output/final_report.html"
    EMAIL_LOG = "output/mail_sent.log"
    TRACE_LOG = "output/audit_trace.log"
    ERROR_CSV = "output/violation_list.csv"

def init_system_logger():
    if not os.path.exists(AuditorConfig.LOG_DIR):
        os.makedirs(AuditorConfig.LOG_DIR)
    logger = logging.getLogger("IC_CAD_Auditor")
    logger.setLevel(logging.DEBUG)
    if logger.hasHandlers():
        logger.handlers.clear()
    file_handler = logging.FileHandler(AuditorConfig.TRACE_LOG, encoding='utf-8')
    console_handler = logging.StreamHandler(sys.stdout)
    log_format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

class FileParsingEngine:
    def __init__(self, logger):
        self.logger = logger

    def parse_verilog_header(self, file_path):
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                date_ptrn = r"Generated on: (\d{4}-\d{2}-\d{2})"
                mod_ptrn = r"module\s+(\w+)"
                date_res = re.search(date_ptrn, content)
                mod_res = re.search(mod_ptrn, content)
                return {
                    "date": date_res.group(1) if date_res else "NOT_FOUND",
                    "module": mod_res.group(1) if mod_res else "NOT_FOUND",
                    "size": os.path.getsize(file_path)}
        except Exception as e:
            self.logger.error(f"解析 Verilog 失敗: {file_path} -> {e}")
            return None

    def parse_tcl_settings(self, file_path):
        if not os.path.exists(file_path): return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return {
                    "pdk_ver": self._safe_regex(r"set PDK_VER\s+(\S+)", content),
                    "libs": re.findall(r"/libs/N7/(v\d+\.\d+)/", content),
                    "release": self._safe_regex(r"Release:\s+(\d{4}-\d{2}-\d{2})", content),
                    "creation": self._safe_regex(r"Creation Date:\s+(\d{4}-\d{2}-\d{2})", content)
                }
        except Exception as e:
            self.logger.error(f"tcl 讀取異常: {file_path} -> {e}")
            return {}

    def _safe_regex(self, pattern, text):
        match = re.search(pattern, text)
        return match.group(1) if match else "MISSING"

    def read_json_safe(self, file_path):
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"JSON 讀取異常: {file_path} -> {e}")
            return None

    def read_csv_safe(self, file_path):
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except Exception as e:
            self.logger.error(f"CSV 讀取異常: {file_path} -> {e}")
            return []

class SignoffAuditManager:
    def __init__(self, spec, logger):
        self.spec = spec
        self.logger = logger
        self.parser = FileParsingEngine(logger)

    def audit_environment(self, mod_dir, mod_name, errors):
        # 1. 檔案存在性
        must_have = {"project_status.json", "setup.tcl", "formal_setup.tcl", "tool_info.csv"}
        current_files = set(os.listdir(mod_dir))
        if not must_have.issubset(current_files):
            missing = must_have - current_files
            errors.append(f"關鍵檔案缺失: {list(missing)}")
        
        # 2. JSON 內容細節校驗
        js_data = self.parser.read_json_safe(os.path.join(mod_dir, "project_status.json"))
        if js_data:
            if js_data.get("process") != self.spec['process']:
                errors.append(f"製程不符: 實際為 {js_data.get('process')}")
            if js_data.get("status") != self.spec['signoff_target']:
                errors.append(f"階段不符: 實際為 {js_data.get('status')}")
            if js_data.get("last_modified") != self.spec['release_date']:
                errors.append(f"JSON 日期錯誤: {js_data.get('last_modified')}")
            if js_data.get("module_name") != mod_name:
                errors.append(f"內部名稱衝突: {js_data.get('module_name')}")
        else:
            errors.append("project_status.json 無法讀取")

    def audit_formal_logic(self, mod_dir, mod_name, errors):
        # 1. 兩份網表的日期與命名檢查
        for v_type in ["golden", "revised"]:
            path = os.path.join(mod_dir, f"{mod_name}_{v_type}.v")
            v_info = self.parser.parse_verilog_header(path)
            if not v_info:
                errors.append(f"無法存取 {v_type} 網表檔案")
            else:
                if v_info.get('date') != self.spec['release_date']:
                    errors.append(f"{v_type} 網表日期過期: {v_info.get('date')}")
                if v_info.get('module') != mod_name:
                    errors.append(f"{v_type} 網表內容名稱錯誤: {v_info.get('module')}")

        # 2. LEC Library 版本對齊
        tcl_data = self.parser.parse_tcl_settings(os.path.join(mod_dir, "formal_setup.tcl"))
        if tcl_data:
            libs = tcl_data.get("libs", [])
            if len(libs) < 2:
                errors.append("Formal 腳本缺失 Library 定義")
            elif len(set(libs)) > 1:
                errors.append(f"Formal 版本衝突: {libs}")
            if tcl_data.get("creation") != self.spec['release_date']:
                errors.append(f"Formal 腳本日期不符: {tcl_data.get('creation')}")
        else:
            errors.append("formal_setup.tcl 無法解析")

    def audit_resources_and_tools(self, mod_dir, errors):
        # 1. 工具完整性
        rows = self.parser.read_csv_safe(os.path.join(mod_dir, "tool_info.csv"))
        present_tools = {r['Tool'] for r in rows if r['Tool']}
        required = set(self.spec['required_tools'])
        if not required.issubset(present_tools):
            errors.append(f"工具報表遺失: {list(required - present_tools)}")

        # 2. 各階段工具細節
        for r in rows:
            try:
                mem_str = r.get('Memory_GB', '0')
                mem = int(mem_str) if mem_str.isdigit() else 0
            except:
                mem = 0
            
            tool = r.get('Tool')
            prio = r.get('Priority')
            date = r.get('Report_Date')

            if date != self.spec['release_date']:
                errors.append(f"工具 {tool} 報告日期偏差: {date}")

            if tool == "PrimeTime":
                if mem < 256: errors.append(f"工具 {tool} STA 記憶體不足: 實際僅{mem}GB")
                if prio != "High": errors.append(f"工具 {tool} 執行優先級錯誤: 目前為{prio}")
            elif tool == "RedHawk":
                if mem < 512: errors.append(f"工具 {tool} Power 記憶體不足: 實際僅{mem}GB")
                if prio != "High": errors.append(f"工具 {tool} 執行優先級錯誤: 目前為{prio}")
            elif tool == "Formality":
                if mem < 64: errors.append(f"工具 {tool} Formal 記憶體不足: 實際僅{mem}GB")
                if prio != "Medium": errors.append(f"工具 {tool} 執行優先級錯誤: 目前為{prio}")
            elif tool == "VCS":
                if mem < 128: errors.append(f"工具 {tool} GLS 記憶體不足: 實際僅{mem}GB")
                if prio != "Low": errors.append(f"工具 {tool} 執行優先級錯誤: 目前為{prio}")
            else:
                if mem < 32: errors.append(f"未知工具 {tool} 資源配置過低")

    def audit_pdk_consistency(self, mod_dir, errors):
        setup_data = self.parser.parse_tcl_settings(os.path.join(mod_dir, "setup.tcl"))
        if setup_data:
            if setup_data.get("pdk_ver") != self.spec['legal_pdk_version']:
                errors.append(f"PDK 版本非法: {setup_data.get('pdk_ver')}")
            if setup_data.get("release") != self.spec['release_date']:
                errors.append(f"全域環境日期錯誤: {setup_data.get('release')}")
        else:
            errors.append("setup.tcl 無法讀取")

class AuditActionTrigger:
    def __init__(self, logger):
        self.logger = logger

    def notify_owner_simulation(self, mod_id, owner, errors):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mail_text = f"""
==================================================
NOTIFICATION: PRE-SIGN-OFF AUDIT FAILED
==================================================
TIME: {timestamp}
RECIPIENT: {owner}@design.com
CC: manager@design.com
BLOCK_ID: {mod_id}
VIOLATIONS DETECTED:
"""
        for i, err in enumerate(errors, 1):
            mail_text += f"\n  [{i}] {err}"
        mail_text += "\n\nSTATUS: BLOCK REJECTED FROM TAPE-OUT FLOW.\n"
        mail_text += "==================================================\n\n\n"
        
        try:
            with open(AuditorConfig.EMAIL_LOG, 'a', encoding='utf-8') as f:
                f.write(mail_text)
            self.logger.warning(f"模組 {mod_id}: 稽核失敗，已將錯誤報告發送至 {owner} 郵箱")
        except Exception as e:
            self.logger.error(f"郵件日誌寫入失敗: {e}")

    def trigger_mock_eda_tool(self, mod_id):
        tool_executable = os.path.abspath("bin/formality")
        if not os.path.exists(tool_executable):
            self.logger.error(f"模組 {mod_id}: 找不到執行檔 {tool_executable}")
            return
        try:
            env_vars = os.environ.copy()
            env_vars["AUDIT_PASS"] = "1"
            result = subprocess.run(
                [tool_executable, "-block", mod_id, "-mode", "verify"],
                capture_output=True, text=True, timeout=5, env=env_vars)
            if result.returncode == 0:
                self.logger.info(f"模組 {mod_id}: 稽核通過，成功觸發工具執行: {result.stdout.strip()}")
            else:
                self.logger.error(f"模組 {mod_id}: 工具啟動回傳異常代碼")
        except subprocess.SubprocessError as e:
            self.logger.error(f"模組 {mod_id}: 動態啟動發生系統級錯誤: {e}")

# 報表彙整與平行處理
def multiprocessing_worker(args):
    target_dir, spec_dict = args
    module_name = os.path.basename(target_dir)
    log = logging.getLogger("IC_CAD_Auditor")
    module_errors = []
    
    # 執行稽核
    manager = SignoffAuditManager(spec_dict, log)
    manager.audit_environment(target_dir, module_name, module_errors)
    manager.audit_formal_logic(target_dir, module_name, module_errors)
    manager.audit_resources_and_tools(target_dir, module_errors)
    manager.audit_pdk_consistency(target_dir, module_errors)
    
    js = FileParsingEngine(log).read_json_safe(os.path.join(target_dir, "project_status.json"))
    owner_info = js.get("owner", "Admin") if js else "Unknown"
    
    trigger = AuditActionTrigger(log)
    audit_status = AuditorConfig.PASS if not module_errors else AuditorConfig.FAIL
    if audit_status == AuditorConfig.FAIL:
        trigger.notify_owner_simulation(module_name, owner_info, module_errors)
    else:
        trigger.trigger_mock_eda_tool(module_name)
    
    return {
        "Module_ID": module_name,
        "Engineer": owner_info,
        "Status": audit_status,
        "Total_Issues": len(module_errors),
        "Issue_Summary": " | ".join(module_errors) if module_errors else "All Correct" }

class MainAuditorCLI:
    def __init__(self):
        self.logger = init_system_logger()
        self.args = self._parse_cmd_args()

    def _parse_cmd_args(self):
        desc_text = "Digital IC Design Pre-Signoff Environment Audit Tool.\n針對簽核階段前的環境一致性、PDK版本及資源配置進行自動化稽核。"
        epilog_text = """
        使用範例 (Usage Examples):
        --------------------------------------------------
        1. 執行標準稽核 (使用預設路徑):
        python3 main_auditor.py

        2. 指定特定專案的Golden Spec與數據目錄:
        python3 main_auditor.py --config ./config/project_spec.yaml --input ./design_blocks

        3. 設定平行處理執行緒數量 (例如限制使用 4 核心):
        python3 main_auditor.py --jobs 4

        4. 呼叫此說明選單:
        python3 main_auditor.py --help
        --------------------------------------------------
        作者: IC CAD Team
        """
        
        # 使用 RawDescriptionHelpFormatter 以保留範例文字的換行格式
        parser = argparse.ArgumentParser(
            description=desc_text,
            epilog=epilog_text,
            formatter_class=argparse.RawDescriptionHelpFormatter)
        
        # 詳細定義每一個參數及其幫助說明
        parser.add_argument(
            "--config", 
            default="config/golden_spec.yaml", 
            help="指定Golden Spec 檔案的路徑。系統將依據此檔案定義的日期、版本進行比對。")
        parser.add_argument(
            "--input", 
            default="input_data", 
            help="指定模組數據源路徑。系統會自動掃描該目錄下所有 mod_ 開頭的子資料夾。")
        parser.add_argument(
            "--jobs", 
            type=int, 
            default=cpu_count(), 
            help="平行稽核任務的執行緒數量。預設將使用本機電腦的所有 CPU 核心以實現最高效能。")
        
        return parser.parse_args()

    def create_dashboard(self, results):
        if not results:
            self.logger.error("無稽核數據，跳過報表生成")
            return

        df = pd.DataFrame(results)
        df = df.sort_values(by='Module_ID').reset_index(drop=True)
        df.index = df.index + 1

        total_count = len(df)
        passed_count = len(df[df['Status'] == AuditorConfig.PASS])
        failed_count = total_count - passed_count
        pass_rate = format((passed_count / total_count) * 100, ".1f") if total_count > 0 else "0.0"
        fail_rate = format((failed_count / total_count) * 100, ".1f") if total_count > 0 else "0.0"


        def apply_status_color(val):
            bg = '#28a745' if val == AuditorConfig.PASS else '#dc3545'
            return f'background-color: {bg}; color: white; font-weight: bold; text-align: center;'

        try:
            final_styler = df.style.map(apply_status_color, subset=['Status'])
            html_table = final_styler.to_html(index=True)
        except Exception as e:
            self.logger.error(f"HTML 渲染失敗(可能缺少 jinja2): {e}")
            html_table = df.to_html(index=True) 
        
        html_template = f"""
        <html><head><meta charset="UTF-8"><style>
            body {{ font-family: 'Helvetica Neue', sans-serif; margin: 50px; background: #f0f2f5; }}
            .container {{ background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
            h1 {{ color: #1a73e8; border-bottom: 3px solid #1a73e8; padding-bottom: 15px; }}
            
            .dashboard-header {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            
            /* 綠框樣式：從上往下排列 */
            .count-zone {{ display: flex; flex-direction: column; gap: 10px; flex: 1; }}
            .count-item {{ background: #fff; border: 2px solid #e8f0fe; padding: 15px; border-radius: 10px; text-align: center; }}
            
            /* 紅框樣式：從左往右排列 */
            .rate-zone {{ display: flex; flex-direction: row; gap: 15px; flex: 2; align-items: stretch; }}
            .rate-card {{ background: #e8f0fe; padding: 20px; border-radius: 10px; flex: 1; text-align: center; display: flex; flex-direction: column; justify-content: center; }}
            
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #1a73e8; color: white; padding: 15px; text-align: center; }}
            td {{ padding: 12px; border: 1px solid #ddd; }}
            /* 黃框樣式：表格第一欄編號加粗 */
            table td:first-child {{ font-weight: bold; background: #f8f9fa; text-align: center; color: #1a73e8; }}
    </style></head><body>
        <div class="container">
                <h1>Pre-Sign-off Audit System</h1>
                <div class="dashboard-header">
                <!-- 綠框區域 -->
                <div class="count-zone">
                    <div class="count-item"><strong>總模組數：</strong> {total_count}</div>
                    <div class="count-item" style="color:green"><strong>通過數量：</strong> {passed_count}</div>
                    <div class="count-item" style="color:red"><strong>違規數量：</strong> {failed_count}</div>
                </div>
                
                <!-- 紅框區域 -->
                <div class="rate-zone">
                    <div class="rate-card"><h3>總通過率</h3><p style="font-size: 24px; font-weight: bold;">{pass_rate}%</p></div>
                    <div class="rate-card"><h3>總違規率</h3><p style="font-size: 24px; font-weight: bold; color:red;">{fail_rate}%</p></div>
                </div>
            </div>

            {html_table}
            
            <p style="color: #888; margin-top: 30px;">Generated by CAD AutoAudit System at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </body></html>
    """
        with open(AuditorConfig.REPORT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_template)

    def run_process(self):
        try:
            with open(self.args.config, 'r') as f:
                spec = yaml.safe_load(f)
        except Exception as e:
            self.logger.critical(f"Golden Spec 載入崩潰: {e}")
            return

        self.logger.info(f"掃描模組目錄: {self.args.input}")
        if not os.path.exists(self.args.input):
            self.logger.error("錯誤: 指定的輸入路徑不存在。")
            return

        # 使用 List Comprehension 篩選目標資料夾
        target_dirs = [os.path.join(self.args.input, d) for d in os.listdir(self.args.input) 
                       if os.path.isdir(os.path.join(self.args.input, d)) and d.startswith("mod_")]
        
        self.logger.info(f"偵測到 {len(target_dirs)} 個專案，啟動平行處理執行緒 (Jobs={self.args.jobs})")
        
        pool_inputs = [(d, spec) for d in target_dirs]
        with Pool(processes=self.args.jobs) as p:
            results = p.map(multiprocessing_worker, pool_inputs)

        self.create_dashboard(results)
        
        failed_results = [r for r in results if r['Status'] == AuditorConfig.FAIL]
        error_df = pd.DataFrame(failed_results)

        if not error_df.empty:
            error_df = error_df.sort_values(by='Module_ID', ascending=True)
            error_df = error_df.drop(columns=['Status'])

        error_df.to_csv(AuditorConfig.ERROR_CSV, index=False)
        self.logger.info(f"任務完成。報表：{AuditorConfig.REPORT_HTML}，錯誤清單：{AuditorConfig.ERROR_CSV}")

if __name__ == "__main__":
    start_watch = time.time()
    Auditor = MainAuditorCLI()
    Auditor.run_process()
    stop_watch = round(time.time() - start_watch, 4)
    print(f"\n[SYSTEM] 稽核引擎總運行耗時: {stop_watch}s")