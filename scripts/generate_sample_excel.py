import pandas as pd
import datetime
import os

def generate_sample_excel(output_filename="sample_cpq_data.xlsx"):
    """
    Generates a sample Excel workbook with confidential placeholder engineering specifications
    suitable for testing the ETL pipeline.
    """
    print(f"Generating confidential sample workbook: {output_filename} ...")
    
    # Sheet 1: Category_A_Conveyance (Equivalent to generic pulleys/drives)
    # Standalone columns: Type_Code, BW_mm, Vendor_Name, Base_Rate, Quotation_Date
    # Concatenated string column: Specifications (format: Diameter x Shell Thk x Face Width x Shaft Dia Brg x Shaft Dia Hub x Lagging)
    data_a = [
        {
            "Type_Code": "Type_101",
            "BW_mm": 1000,
            "Vendor_Name": "Vendor_Alpha",
            "Base_Rate": 4300.00,
            "Quotation_Date": "2023-04-10",
            "Specifications": "630x16x1150x120x140xCeramic_Diamond"
        },
        {
            "Type_Code": "Type_101",
            "BW_mm": 1200,
            "Vendor_Name": "Vendor_Beta",
            "Base_Rate": 4850.00,
            "Quotation_Date": "2024-02-15",
            "Specifications": "800x18x1350x140x160xCeramic_Diamond"
        },
        {
            "Type_Code": "Type_202",
            "BW_mm": 1400,
            "Vendor_Name": "Vendor_Gamma",
            "Base_Rate": 6120.00,
            "Quotation_Date": "2024-09-01",
            "Specifications": "800x20x1550x160x180xRubber_Plain"
        },
        {
            "Type_Code": "Type_303",
            "BW_mm": 1600,
            "Vendor_Name": "Vendor_Delta",
            "Base_Rate": 8900.00,
            "Quotation_Date": "2025-01-20",
            "Specifications": "1000x25x1750x180x200xCeramic_Diamond"
        }
    ]
    df_a = pd.DataFrame(data_a)

    with pd.ExcelWriter(output_filename, engine="openpyxl") as writer:
        df_a.to_excel(writer, sheet_name="Category_A_Conveyance", index=False)

    print(f"Workbook '{output_filename}' generated successfully!")

if __name__ == "__main__":
    generate_sample_excel()
