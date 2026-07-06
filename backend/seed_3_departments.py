import os
import sys
import pandas as pd

# Ensure we can import database and models from backend directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from import_excel_sheets import import_excel_sheets

def create_and_seed_3_departments():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("==================================================================")
    print("   ENTERPRISE CPQ - 3 DEPARTMENT EXCEL SEED & IMPORT TOOL")
    print("==================================================================\n")

    # -------------------------------------------------------------------------
    # 1. Mechanical Department Excel
    # -------------------------------------------------------------------------
    mech_file = os.path.join(root_dir, "Mechanical_Department_Input.xlsx")
    print(f"[1/3] Generating Mechanical Department Workbook: {mech_file}")
    
    mech_data = {
        "Pulleys": pd.DataFrame([
            {
                "dia x shell thk x lagging x shaft dia": "630 x 16 x Ceramic x 140",
                "Belt Width": "1200 mm",
                "Vendor Name": "Fenner India",
                "Base Rate": 85000,
                "Quote Date": "2024-03-15",
                "Remarks": "Heavy duty drive pulley with diamond ceramic lagging"
            },
            {
                "dia x shell thk x lagging x shaft dia": "500 x 12 x Rubber x 110",
                "Belt Width": "1000 mm",
                "Vendor Name": "David Brown",
                "Base Rate": 62000,
                "Quote Date": "2024-04-10",
                "Remarks": "Tail pulley with 10mm rubber lagging"
            },
            {
                "dia x shell thk x lagging x shaft dia": "800 x 20 x Ceramic x 180",
                "Belt Width": "1400 mm",
                "Vendor Name": "Elecon Engineering",
                "Base Rate": 145000,
                "Quote Date": "2024-02-20",
                "Remarks": "High tension head pulley"
            }
        ]),
        "Belts": pd.DataFrame([
            {
                "Spec (Width x Ply x Grade)": "1200 x 4 x M-Grade",
                "Belt Type": "EP-800",
                "Vendor Name": "Continental Belting",
                "Base Rate": 3200,
                "Quote Date": "2024-05-01",
                "Remarks": "Fire resistant mining conveyor belt per meter"
            },
            {
                "Spec (Width x Ply x Grade)": "1000 x 3 x N-Grade",
                "Belt Type": "EP-600",
                "Vendor Name": "Fenner India",
                "Base Rate": 2400,
                "Quote Date": "2024-03-25",
                "Remarks": "General purpose abrasion resistant belt"
            },
            {
                "Spec (Width x Ply x Grade)": "1400 x 5 x HR-Grade",
                "Belt Type": "EP-1000",
                "Vendor Name": "Bridgestone",
                "Base Rate": 4800,
                "Quote Date": "2024-01-15",
                "Remarks": "Heat resistant up to 180 deg C"
            }
        ]),
        "Idlers": pd.DataFrame([
            {
                "dia x len x shaft dia": "133 x 450 x 25",
                "Idler Type": "Troughing Carrying",
                "Vendor Name": "Precismeca",
                "Base Rate": 1850,
                "Quote Date": "2024-04-12",
                "Remarks": "Sealed for life bearings SKF make"
            },
            {
                "dia x len x shaft dia": "114 x 380 x 20",
                "Idler Type": "Return Roller",
                "Vendor Name": "Elecon Engineering",
                "Base Rate": 1350,
                "Quote Date": "2024-03-10",
                "Remarks": "Heavy wall steel tube"
            }
        ]),
        "Drive Units": pd.DataFrame([
            {
                "Motor Power x Gearbox Ratio": "75 kW x 25:1",
                "Mounting Type": "Foot Mounted",
                "Vendor Name": "Siemens India",
                "Base Rate": 340000,
                "Quote Date": "2024-05-10",
                "Remarks": "IE3 premium efficiency motor with helical bevel gearbox"
            },
            {
                "Motor Power x Gearbox Ratio": "45 kW x 20:1",
                "Mounting Type": "Flange Mounted",
                "Vendor Name": "SEW Eurodrive",
                "Base Rate": 265000,
                "Quote Date": "2024-04-18",
                "Remarks": "Heavy duty outdoor conveyor drive unit"
            }
        ])
    }
    with pd.ExcelWriter(mech_file, engine='openpyxl') as writer:
        for sheet_name, df in mech_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print("  -> Created Mechanical workbook successfully!\n")

    # -------------------------------------------------------------------------
    # 2. Electrical Department Excel
    # -------------------------------------------------------------------------
    elec_file = os.path.join(root_dir, "Electrical_Department_Input.xlsx")
    print(f"[2/3] Generating Electrical Department Workbook: {elec_file}")
    
    elec_data = {
        "Transformers": pd.DataFrame([
            {
                "Rating x Voltage Ratio x Cooling": "2.5 MVA x 33kV/415V x ONAN",
                "Transformer Type": "Oil Immersed",
                "Vendor Name": "ABB India",
                "Base Rate": 1850000,
                "Quote Date": "2024-04-05",
                "Remarks": "Copper wound distribution transformer with OLTC"
            },
            {
                "Rating x Voltage Ratio x Cooling": "1.6 MVA x 11kV/415V x ONAN",
                "Transformer Type": "Oil Immersed",
                "Vendor Name": "Schneider Electric",
                "Base Rate": 1250000,
                "Quote Date": "2024-03-20",
                "Remarks": "Low loss Tier-3 energy efficient transformer"
            },
            {
                "Rating x Voltage Ratio x Cooling": "800 kVA x 11kV/415V x AN",
                "Transformer Type": "Dry Type Resin Cast",
                "Vendor Name": "Siemens India",
                "Base Rate": 1450000,
                "Quote Date": "2024-05-02",
                "Remarks": "Indoor substation resin cast dry type"
            }
        ]),
        "Switchgears": pd.DataFrame([
            {
                "Voltage x Fault Rating x Incomer": "33 kV x 25kA x 1250A",
                "Panel Type": "VCB Incomer Panel",
                "Vendor Name": "Siemens India",
                "Base Rate": 950000,
                "Quote Date": "2024-03-15",
                "Remarks": "Indoor vacuum circuit breaker panel with numerical relay"
            },
            {
                "Voltage x Fault Rating x Incomer": "415 V x 50kA x 2500A",
                "Panel Type": "PCC Incomer Panel",
                "Vendor Name": "L&T Electrical",
                "Base Rate": 680000,
                "Quote Date": "2024-04-10",
                "Remarks": "Power control centre with ACB incomer and bus duct"
            },
            {
                "Voltage x Fault Rating x Incomer": "415 V x 50kA x 800A",
                "Panel Type": "MCC Feeder Panel",
                "Vendor Name": "Schneider Electric",
                "Base Rate": 450000,
                "Quote Date": "2024-02-25",
                "Remarks": "Motor control centre drawout type feeder"
            }
        ]),
        "Power Cables": pd.DataFrame([
            {
                "Size x Cores x Insulation": "300 sqmm x 3.5 Core x XLPE",
                "Conductor Type": "Aluminium Armoured",
                "Vendor Name": "Polycab India",
                "Base Rate": 1850,
                "Quote Date": "2024-05-12",
                "Remarks": "11kV HT armoured cable per meter"
            },
            {
                "Size x Cores x Insulation": "185 sqmm x 3.5 Core x XLPE",
                "Conductor Type": "Aluminium Armoured",
                "Vendor Name": "Havells India",
                "Base Rate": 1250,
                "Quote Date": "2024-04-20",
                "Remarks": "1.1kV LT power cable per meter"
            },
            {
                "Size x Cores x Insulation": "16 sqmm x 4 Core x XLPE",
                "Conductor Type": "Copper Armoured",
                "Vendor Name": "Finolex Cables",
                "Base Rate": 650,
                "Quote Date": "2024-03-18",
                "Remarks": "Heavy duty copper control cable per meter"
            }
        ]),
        "Control Panels": pd.DataFrame([
            {
                "PLC Spec x I/O Count x Enclosure": "Siemens S7-1500 x 256 I/O x IP65",
                "System Type": "Redundant PLC Panel",
                "Vendor Name": "Siemens India",
                "Base Rate": 1450000,
                "Quote Date": "2024-04-15",
                "Remarks": "Hot standby redundant PLC system with HMI and UPS"
            },
            {
                "PLC Spec x I/O Count x Enclosure": "Allen Bradley ControlLogix x 128 I/O x IP54",
                "System Type": "Conveyor Automation Panel",
                "Vendor Name": "Rockwell Automation",
                "Base Rate": 1150000,
                "Quote Date": "2024-03-10",
                "Remarks": "Plant wide SCADA integrated control station"
            }
        ])
    }
    with pd.ExcelWriter(elec_file, engine='openpyxl') as writer:
        for sheet_name, df in elec_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print("  -> Created Electrical workbook successfully!\n")

    # -------------------------------------------------------------------------
    # 3. Civil Department Excel
    # -------------------------------------------------------------------------
    civil_file = os.path.join(root_dir, "Civil_Department_Input.xlsx")
    print(f"[3/3] Generating Civil Department Workbook: {civil_file}")
    
    civil_data = {
        "RCC Foundations": pd.DataFrame([
            {
                "Grade x Depth x Rebar Density": "M35 x 3.5m x 120kg/m3",
                "Foundation Type": "Heavy Equipment Foundation",
                "Vendor Name": "L&T Construction",
                "Base Rate": 8500,
                "Quote Date": "2024-04-01",
                "Remarks": "Rate per cu.m including excavation, shuttering, steel rebar and curing"
            },
            {
                "Grade x Depth x Rebar Density": "M25 x 2.0m x 80kg/m3",
                "Foundation Type": "Conveyor Trestle Foundation",
                "Vendor Name": "Shapoorji Pallonji",
                "Base Rate": 6200,
                "Quote Date": "2024-03-15",
                "Remarks": "Isolated column footing per cu.m"
            },
            {
                "Grade x Depth x Rebar Density": "M40 x 4.5m x 150kg/m3",
                "Foundation Type": "Crusher Building Raft",
                "Vendor Name": "Afcons Infrastructure",
                "Base Rate": 10500,
                "Quote Date": "2024-05-05",
                "Remarks": "High strength raft foundation with waterproofing"
            }
        ]),
        "Structural Steelwork": pd.DataFrame([
            {
                "Section Type x Grade x Fabrication": "ISMB 500 x E250 x Welded & Bolted",
                "Application": "Conveyor Gallery Trestle",
                "Vendor Name": "Tata Bluescope",
                "Base Rate": 98000,
                "Quote Date": "2024-04-18",
                "Remarks": "Rate per MT including epoxy primer and 2 coats polyurethane paint"
            },
            {
                "Section Type x Grade x Fabrication": "Tubular Section x E350 x Prefabricated",
                "Application": "Transfer Tower Structure",
                "Vendor Name": "Jindal Steel & Power",
                "Base Rate": 115000,
                "Quote Date": "2024-03-22",
                "Remarks": "High tensile tubular lattice bridge structure per MT"
            },
            {
                "Section Type x Grade x Fabrication": "ISMC 300 x E250 x Standard",
                "Application": "Equipment Support Grid",
                "Vendor Name": "Steel Authority (SAIL)",
                "Base Rate": 88000,
                "Quote Date": "2024-02-14",
                "Remarks": "Standard structural channel grid per MT"
            }
        ]),
        "Industrial Sheds": pd.DataFrame([
            {
                "Span x Eave Height x Roof Sheeting": "30m x 12m x Galvalume 0.5mm",
                "Shed Structure Type": "PEB Portal Frame Shed",
                "Vendor Name": "Kirby Building Systems",
                "Base Rate": 4500,
                "Quote Date": "2024-05-10",
                "Remarks": "Pre-engineered building structure rate per sq.m floor area"
            },
            {
                "Span x Eave Height x Roof Sheeting": "24m x 9m x Color Coated Steel",
                "Shed Structure Type": "Warehouse Shed",
                "Vendor Name": "Interarch Building",
                "Base Rate": 3800,
                "Quote Date": "2024-04-05",
                "Remarks": "Standard industrial storage shed per sq.m"
            }
        ]),
        "Excavation & Roads": pd.DataFrame([
            {
                "Road Type x Width x Crust Thickness": "Rigid RCC Road x 7.5m x 300mm",
                "Civil Infrastructure": "Heavy Duty Plant Road",
                "Vendor Name": "L&T Construction",
                "Base Rate": 3200,
                "Quote Date": "2024-04-12",
                "Remarks": "Rate per sq.m including DLC sub-base and M40 pavement quality concrete"
            },
            {
                "Road Type x Width x Crust Thickness": "Flexible Bitumen Road x 6.0m x 250mm",
                "Civil Infrastructure": "Peripheral Access Road",
                "Vendor Name": "Dilip Buildcon",
                "Base Rate": 1800,
                "Quote Date": "2024-03-18",
                "Remarks": "Rate per sq.m including WMM and bituminous macadam"
            }
        ])
    }
    with pd.ExcelWriter(civil_file, engine='openpyxl') as writer:
        for sheet_name, df in civil_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print("  -> Created Civil workbook successfully!\n")

    # -------------------------------------------------------------------------
    # 4. Import all 3 into the single database using smart deduplication
    # -------------------------------------------------------------------------
    print("==================================================================")
    print("   IMPORTING ALL 3 WORKBOOKS INTO UNIFIED DATABASE")
    print("==================================================================\n")
    
    print(">>> Seeding Mechanical Department...")
    import_excel_sheets(mech_file)
    
    print(">>> Seeding Electrical Department...")
    import_excel_sheets(elec_file)
    
    print(">>> Seeding Civil Department...")
    import_excel_sheets(civil_file)
    
    print("\n[SUCCESS] All 3 department Excel sheets have been generated and seeded into your database!")

if __name__ == "__main__":
    create_and_seed_3_departments()
