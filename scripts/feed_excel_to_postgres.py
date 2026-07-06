import sys
import os
import pandas as pd
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path to reuse existing SQLAlchemy models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
import models

# ==============================================================================
# CONFIGURATION: Set your PostgreSQL database connection string here
# Example: "postgresql://postgres:mysecretpassword@localhost:5432/cpq_enterprise"
# ==============================================================================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../cpq_enterprise.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def import_custom_excel(excel_file_path: str, category_name: str, specification_columns: list):
    """
    Ingests any custom Excel file into PostgreSQL MasterRate table.
    
    :param excel_file_path: Path to your .xlsx file (e.g. 'my_pulleys.xlsx')
    :param category_name: Name of the Equipment Category (e.g. 'Pulleys & Conveyors')
    :param specification_columns: List of column names in your Excel that represent dynamic technical specs
                                  (e.g. ['Diameter', 'Face Width', 'Shaft Dia', 'Lagging'])
    """
    print(f"Connecting to database: {DATABASE_URL}")
    print(f"Reading file: '{excel_file_path}' for category: '{category_name}'...")
    
    if not os.path.exists(excel_file_path):
        print(f"❌ ERROR: Excel file '{excel_file_path}' not found!")
        return

    # Ensure tables exist
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Load workbook
        df = pd.read_excel(excel_file_path)
        print(f"Loaded {len(df)} rows from Excel spreadsheet.")

        # Step 1: Find or create the Equipment Category
        category = db.query(models.EquipmentCategory).filter(models.EquipmentCategory.name == category_name).first()
        if not category:
            print(f"Creating new Equipment Category '{category_name}' with schema: {specification_columns}")
            category = models.EquipmentCategory(
                name=category_name,
                spec_schema=specification_columns
            )
            db.add(category)
            db.commit()
            db.refresh(category)
        else:
            print(f"Found existing category '{category_name}' (ID: {category.id}). Updating schema...")
            category.spec_schema = specification_columns
            db.commit()

        # Step 2: Iterate through Excel rows and insert into MasterRate
        inserted = 0
        for idx, row in df.iterrows():
            # Standard fields (fallback defaults provided if column name slightly differs)
            vendor = str(row.get("Vendor_Name", row.get("Vendor", f"Vendor_{idx+1}"))).strip()
            base_rate = float(row.get("Base_Rate", row.get("Rate", row.get("Price", 0.0))))
            
            # Handle quotation date
            raw_date = row.get("Quotation_Date", row.get("Quote_Date", row.get("Date")))
            if isinstance(raw_date, (datetime.datetime, datetime.date)):
                qdate = datetime.datetime(raw_date.year, raw_date.month, raw_date.day)
            else:
                try:
                    qdate = pd.to_datetime(raw_date).to_pydatetime()
                except Exception:
                    qdate = datetime.datetime.utcnow()

            # Build dynamic JSONB specifications dictionary from the specified columns
            specs_dict = {}
            for col in specification_columns:
                val = row.get(col, "N/A")
                # Clean up float values that are whole numbers (e.g. 1000.0 -> "1000")
                if isinstance(val, float) and val.is_integer():
                    val = int(val)
                specs_dict[col] = str(val).strip() if pd.notna(val) else "N/A"

            # Create record
            rate_record = models.MasterRate(
                category_id=category.id,
                vendor_name=vendor,
                base_rate=base_rate,
                quotation_date=qdate,
                specifications=specs_dict
            )
            db.add(rate_record)
            inserted += 1

        db.commit()
        print(f"✅ SUCCESS: Successfully fed {inserted} records into PostgreSQL table 'master_rates'!")

    except Exception as e:
        db.rollback()
        print(f"❌ ERROR during database insertion: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # ==========================================================================
    # HOW TO RUN:
    # Modify the parameters below to match your Excel file name and column names!
    # ==========================================================================
    EXCEL_FILE = sys.argv[1] if len(sys.argv) > 1 else "sample_cpq_data.xlsx"
    CATEGORY = sys.argv[2] if len(sys.argv) > 2 else "Heavy Pulleys (India)"
    
    # Specify the columns in your Excel file that make up the technical specs
    SPEC_COLUMNS = [
        "Diameter_mm", 
        "Shell_Thk_mm", 
        "Face_Width_mm", 
        "Shaft_Dia_Brg_mm", 
        "Shaft_Dia_Hub_mm", 
        "Lagging_Spec"
    ]
    
    import_custom_excel(EXCEL_FILE, CATEGORY, SPEC_COLUMNS)
