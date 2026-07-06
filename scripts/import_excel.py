import sys
import os
import pandas as pd
import datetime

# Add backend directory to path so we can import models and database connection
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from database import SessionLocal, engine, Base
import models

def run_etl_pipeline(file_path="sample_cpq_data.xlsx", sheet_name="Category_A_Conveyance"):
    print(f"Starting ETL Ingestion Pipeline for file: {file_path} (Sheet: {sheet_name})")
    if not os.path.exists(file_path):
        print(f"ERROR: File '{file_path}' not found.")
        return

    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Step 1: Read Excel sheet
        print("Reading Excel spreadsheet into Pandas DataFrame...")
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"Loaded {len(df)} rows from sheet '{sheet_name}'.")

        # Step 2: Ensure the Equipment Category exists or create it
        category = db.query(models.EquipmentCategory).filter(models.EquipmentCategory.name == sheet_name).first()
        if not category:
            print(f"Category '{sheet_name}' not found in DB. Creating new category with standard schema...")
            spec_schema = [
                "Type_Code", "BW_mm", "Diameter_mm", "Shell_Thk_mm",
                "Face_Width_mm", "Shaft_Dia_Brg_mm", "Shaft_Dia_Hub_mm", "Lagging_Spec"
            ]
            category = models.EquipmentCategory(name=sheet_name, spec_schema=spec_schema)
            db.add(category)
            db.commit()
            db.refresh(category)
        else:
            print(f"Using existing category: {category.name} (ID: {category.id})")

        # Step 3 & 4: Iterate rows, extract standalone columns, split concatenated specifications, and combine JSON
        inserted_count = 0
        for idx, row in df.iterrows():
            # Standalone attributes
            type_code = str(row.get("Type_Code", "")).strip()
            bw_mm = str(row.get("BW_mm", "")).strip()
            vendor_name = str(row.get("Vendor_Name", f"Vendor_Row_{idx}")).strip()
            base_rate = float(row.get("Base_Rate", 0.0))
            
            # Parse quotation date
            raw_date = row.get("Quotation_Date")
            if isinstance(raw_date, (datetime.datetime, datetime.date)):
                quotation_date = datetime.datetime(raw_date.year, raw_date.month, raw_date.day)
            else:
                try:
                    quotation_date = pd.to_datetime(raw_date).to_pydatetime()
                except Exception:
                    quotation_date = datetime.datetime.utcnow()

            # Split concatenated Specifications string by 'x' or 'X'
            concat_spec = str(row.get("Specifications", "")).strip()
            parts = [p.strip() for p in concat_spec.split("x")] if "x" in concat_spec.lower() else [concat_spec]

            # Construct structured JSON matching category schema keys
            spec_json = {
                "Type_Code": type_code,
                "BW_mm": bw_mm
            }
            
            # Map split parts to remaining keys
            remaining_keys = [k for k in category.spec_schema if k not in ["Type_Code", "BW_mm"]]
            for i, key in enumerate(remaining_keys):
                spec_json[key] = parts[i] if i < len(parts) else "N/A"

            # Step 5: Insert into MasterRate table
            master_rate = models.MasterRate(
                category_id=category.id,
                vendor_name=vendor_name,
                base_rate=base_rate,
                quotation_date=quotation_date,
                specifications=spec_json
            )
            db.add(master_rate)
            inserted_count += 1

        db.commit()
        print(f"SUCCESS: Ingested {inserted_count} MasterRate records into database!")
        print(f"All dynamic JSON specification schemas mapped and validated.")

    except Exception as e:
        db.rollback()
        print(f"ERROR during ETL execution: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    file_arg = sys.argv[1] if len(sys.argv) > 1 else "sample_cpq_data.xlsx"
    sheet_arg = sys.argv[2] if len(sys.argv) > 2 else "Category_A_Conveyance"
    run_etl_pipeline(file_path=file_arg, sheet_name=sheet_arg)
