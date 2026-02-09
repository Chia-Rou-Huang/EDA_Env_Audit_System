import os
import json
import csv
import yaml
import random

def generate_project_eda_data():
    folders = ["input_data", "config", "bin", "output"]
    for folder in folders: 
        os.makedirs(folder, exist_ok=True)
    
    # 1. Golden Spec.yaml
    target_date = "2025-05-13"
    golden_spec = {
        "process": "N7",
        "release_date": target_date,
        "signoff_target": "layout_done",
        "legal_pdk_version": "v3.0",
        "required_tools": ["VCS", "PrimeTime", "Formality", "RedHawk"]
    }
    with open("config/golden_spec.yaml", 'w') as f: 
        yaml.dump(golden_spec, f, sort_keys=False)

    print(f"--- 開始生成 200 個模組資料 (規範日期: {target_date}) ---")
    for i in range(1, 201):
        proj_name = f"mod_{i:03d}"
        proj_path = os.path.join("input_data", proj_name)
        os.makedirs(proj_path, exist_ok=True)

        current_mod_date = target_date if i % 10 != 0 else "2025-05-10"

        # 2. Netlist.v
        netlist_types = ["golden", "revised"]
        
        for n_type in netlist_types:
            filename = f"{proj_name}_{n_type}.v"
            with open(os.path.join(proj_path, filename), 'w') as f:
                f.write(f"// Generated on: {current_mod_date}\n")
                f.write(f"module {proj_name} (clk, rst, in, out);\n")
                f.write(f"  // {n_type.capitalize()} Netlist for {proj_name}\n")
                for j in range(20):
                    f.write(f"  AND2X1 g{j} (.A(n{j}), .B(n{j+1}), .Y(n{j+2}));\n")
                    f.write(f"  DFFQX1 f{j} (.D(n{j+2}), .CK(clk), .Q(out_s{j}));\n")
                f.write("endmodule\n")

        # 3. formal_setup.tcl
        golden_lib_v = "v3.0"
        revised_lib_v = "v3.0" if i % 25 != 0 else "v2.0" 

        with open(os.path.join(proj_path, "formal_setup.tcl"), 'w') as f:
            f.write(f"# Formal Verification Setup for {proj_name}\n")
            f.write(f"# Creation Date: {current_mod_date}\n") 
            f.write(f"read_db /tools/libs/N7/{golden_lib_v}/std_cell.db\n")
            f.write(f"read_verilog -golden {proj_name}_golden.v\n")
            f.write(f"read_db /tools/libs/N7/{revised_lib_v}/std_cell.db\n")
            f.write(f"read_verilog -revised {proj_name}_revised.v\n")

        # 4.project_status.json
        mod_process = "N7" if i % 20 != 0 else "N12"
        with open(os.path.join(proj_path, "project_status.json"), 'w') as f:
            json.dump({
                "module_name": proj_name,
                "process": mod_process,   
                "owner": f"engineer_{random.randint(1, 10)}",
                "status": "layout_done",
                "last_modified": current_mod_date 
            }, f, indent=4)

        # 5. setup.tcl
        pdk_versions = ["v3.0", "v3.0", "v3.0", "v3.0", "v2.0", "v4.0"]
        pdk_v = random.choice(pdk_versions)

        with open(os.path.join(proj_path, "setup.tcl"), 'w') as f:
            f.write(f"# Environment Script (Release: {current_mod_date})\n")
            f.write(f"set PDK_VER {pdk_v}\n")
            f.write(f"set SEARCH_PATH \"/tools/pdk/N7/$PDK_VER/std_cell/db\"\n")

        # 6. tool_info.csv
        all_signoff_tools = ["VCS", "PrimeTime", "Formality", "RedHawk"]
        standard_prio = {"PrimeTime": "High", "RedHawk": "High", "Formality": "Medium", "VCS": "Low"}
        standard_mem = {"PrimeTime": "256", "RedHawk": "512", "Formality": "64", "VCS": "128"}
        
        prob = random.random()
        if prob < 0.85:
            tools_in_this_mod = all_signoff_tools 
        elif prob < 0.95:
            tools_in_this_mod = random.sample(all_signoff_tools, 3)
        else:
            tools_in_this_mod = random.sample(all_signoff_tools, random.randint(1, 2))

        with open(os.path.join(proj_path, "tool_info.csv"), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Tool", "Server", "Memory_GB", "Priority","Report_Date"])
        
            for tool in tools_in_this_mod:

                prio = standard_prio[tool]
                mem = standard_mem[tool] if i % 15 != 0 else "8"
                server_id = random.randint(1, 500)
                server_name = f"node_{server_id:03d}"
                
                writer.writerow([tool, server_name, mem, prio, current_mod_date])

    print(f"成功！已在 input_data/ 下生成 200 個模組的 Pre-Sign-off 稽核資料。")

if __name__ == "__main__":
    generate_project_eda_data()