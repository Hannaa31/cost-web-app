import sys
import os
import datetime
import argparse
import re
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from sqlalchemy.orm import Session

# Add current directory to path so database and models can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal, engine, Base
import models

def parse_x_separated_spec(header: str, val_str: str):
    """
    Parses string values separated by 'x' or 'X'.
    Example header: 'dia x shell thk x lagging x shaft dia'
    Example value:  '630 x 16 x Ceramic x 140'
    """
    val_str = str(val_str).strip()
    header_parts = [h.strip().title() for h in re.split(r'\s*[xX]\s*', header)]
    value_parts = [v.strip() for v in re.split(r'\s*[xX]\s*', val_str)]
    
    parsed = {}
    if len(header_parts) > 1:
        for i, key in enumerate(header_parts):
            parsed[key] = value_parts[i] if i < len(value_parts) else "N/A"
    else:
        if len(value_parts) > 1:
            for i, v in enumerate(value_parts):
                parsed[f"{header} (Part {i+1})"] = v
        else:
            parsed[header] = val_str
            
    return parsed

def detect_domain(name: str) -> models.DomainType:
    n = name.lower()
    if any(k in n for k in ['transformer', 'switchgear', 'cable', 'panel', 'motor', 'electrical', 'substation', 'lighting', 'relay']):
        return models.DomainType.Electrical
    elif any(k in n for k in ['concrete', 'structure', 'civil', 'building', 'foundation', 'excavation', 'steel', 'road', 'drainage', 'shed']):
        return models.DomainType.Civil
    else:
        return models.DomainType.Mechanical

def import_excel_sheets(file_path: str):
    if not os.path.exists(file_path):
        print(f"[Error] File not found at '{file_path}'")
        return

    print(f"Opening Excel workbook: {file_path}")
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    print(f"Found sheets: {', '.join(sheet_names)}\n")

    db: Session = SessionLocal()
    total_added = 0
    total_updated = 0
    total_skipped = 0

    try:
        for sheet_name in sheet_names:
            print(f"--- Processing Sheet: '{sheet_name}' ---")
            df = pd.read_excel(file_path, sheet_name=sheet_name).dropna(how='all')
            if df.empty:
                print(f"[Warning] Sheet '{sheet_name}' is empty. Skipping.")
                continue

            df.columns = [str(c).strip() for c in df.columns]
            col_map = {c.lower(): c for c in df.columns}

            vendor_col = next((col_map[k] for k in ['vendor name', 'vendor', 'supplier', 'make'] if k in col_map), None)
            rate_col = next((col_map[k] for k in ['base rate', 'rate', 'price', 'unit price', 'cost', 'base_rate'] if k in col_map), None)
            date_col = next((col_map[k] for k in ['quote date', 'quotation date', 'date', 'quotation_date'] if k in col_map), None)
            remarks_col = next((col_map[k] for k in ['remarks', 'remark', 'note', 'notes'] if k in col_map), None)

            if not rate_col:
                print(f"[Warning] Could not find a Base Rate/Price column in sheet '{sheet_name}'. Skipping sheet.\n")
                continue

            reserved_cols = {col for col in [vendor_col, rate_col, date_col, remarks_col] if col is not None}
            raw_spec_cols = [c for c in df.columns if c not in reserved_cols]

            rows_data = []
            all_discovered_keys = []

            for idx, row in df.iterrows():
                try:
                    rate_val = float(str(row[rate_col]).replace(',', '').replace('₹', '').strip())
                    if pd.isna(rate_val) or rate_val <= 0:
                        continue
                except (ValueError, TypeError):
                    continue

                vendor_val = str(row[vendor_col]).strip() if vendor_col and not pd.isna(row[vendor_col]) else "Standard Quote"

                if date_col and not pd.isna(row[date_col]):
                    date_val = pd.to_datetime(row[date_col], dayfirst=True, errors='coerce')
                    if pd.isna(date_val):
                        date_val = datetime.datetime.now()
                else:
                    date_val = datetime.datetime.now()

                remark_val = str(row[remarks_col]).strip() if remarks_col and not pd.isna(row[remarks_col]) else ""

                specs_dict = {}
                if remark_val:
                    specs_dict["Remarks"] = remark_val

                for sc in raw_spec_cols:
                    val = row[sc]
                    if pd.isna(val):
                        continue

                    val_str = str(val).strip()
                    if isinstance(val, float) and val.is_integer():
                        val_str = str(int(val))

                    # Automatically parse compound x-separated columns
                    if 'x' in sc.lower() and len(re.split(r'\s*[xX]\s*', sc)) > 1:
                        parsed_sub = parse_x_separated_spec(sc, val_str)
                        for sub_k, sub_v in parsed_sub.items():
                            specs_dict[sub_k] = sub_v
                            if sub_k not in all_discovered_keys:
                                all_discovered_keys.append(sub_k)
                    elif 'x' in val_str.lower() and len(re.split(r'\s*[xX]\s*', val_str)) > 1 and ('spec' in sc.lower() or 'desc' in sc.lower()):
                        parsed_sub = parse_x_separated_spec(sc, val_str)
                        for sub_k, sub_v in parsed_sub.items():
                            specs_dict[sub_k] = sub_v
                            if sub_k not in all_discovered_keys:
                                all_discovered_keys.append(sub_k)
                    else:
                        clean_key = sc.strip()
                        specs_dict[clean_key] = val_str
                        if clean_key not in all_discovered_keys:
                            all_discovered_keys.append(clean_key)

                rows_data.append({
                    "vendor": vendor_val,
                    "rate": rate_val,
                    "date": date_val,
                    "remarks": remark_val,
                    "specs": specs_dict
                })

            # Get or Create Category
            category = db.query(models.EquipmentCategory).filter_by(name=sheet_name.strip()).first()
            if not category:
                domain_val = detect_domain(sheet_name.strip())
                category = models.EquipmentCategory(
                    name=sheet_name.strip(),
                    spec_schema=all_discovered_keys,
                    domain=domain_val
                )
                db.add(category)
                db.commit()
                db.refresh(category)
                print(f"  [Created] New Category: '{category.name}' [{category.domain.value}]")
            else:
                existing_schema = list(category.spec_schema or [])
                updated = False
                for k in all_discovered_keys:
                    if k not in existing_schema:
                        existing_schema.append(k)
                        updated = True
                if updated:
                    category.spec_schema = existing_schema
                    db.commit()
                    db.refresh(category)
                print(f"  [Existing] Found Category: '{category.name}' [{category.domain.value}]")

            # Insert rates with Smart Deduplication
            sheet_added = 0
            sheet_updated = 0
            sheet_skipped = 0

            existing_rates = db.query(models.MasterRate).filter_by(category_id=category.id).all()

            for item in rows_data:
                match_found = False
                for er in existing_rates:
                    if er.vendor_name.lower() == item["vendor"].lower() and abs(er.base_rate - item["rate"]) < 0.01:
                        er_specs = er.specifications or {}
                        item_specs = item["specs"]
                        
                        keys_match = True
                        for k, v in item_specs.items():
                            if str(er_specs.get(k, '')).strip() != str(v).strip():
                                keys_match = False
                                break
                        
                        if keys_match:
                            match_found = True
                            if er.remarks != item["remarks"] or er.quotation_date != item["date"]:
                                er.remarks = item["remarks"]
                                er.quotation_date = item["date"]
                                er.specifications = item["specs"]
                                sheet_updated += 1
                            else:
                                sheet_skipped += 1
                            break

                if not match_found:
                    master_rate = models.MasterRate(
                        category_id=category.id,
                        vendor_name=item["vendor"],
                        base_rate=item["rate"],
                        quotation_date=item["date"],
                        specifications=item["specs"],
                        remarks=item["remarks"]
                    )
                    db.add(master_rate)
                    existing_rates.append(master_rate)
                    sheet_added += 1

            db.commit()
            print(f"  -> Sheet '{sheet_name}': Added {sheet_added} new | Updated {sheet_updated} existing | Skipped {sheet_skipped} identical\n")
            total_added += sheet_added
            total_updated += sheet_updated
            total_skipped += sheet_skipped

        print("==================================================================")
        print("Import Summary Across All Sheets:")
        print(f"   - New Rates Added:        {total_added}")
        print(f"   - Existing Rates Updated: {total_updated}")
        print(f"   - Duplicate Rows Skipped: {total_skipped}")
        print("==================================================================")

    except Exception as e:
        db.rollback()
        print(f"[Error] Database error during import: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import multi-sheet Excel file into PostgreSQL database without duplicates.")
    parser.add_argument("excel_file", help="Path to the Excel (.xlsx) file")
    args = parser.parse_args()

    import_excel_sheets(args.excel_file)
