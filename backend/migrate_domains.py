import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from sqlalchemy import text
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

def detect_domain(name: str) -> models.DomainType:
    n = name.lower()
    if any(k in n for k in ['transformer', 'switchgear', 'cable', 'panel', 'motor', 'electrical', 'substation', 'lighting', 'relay']):
        return models.DomainType.Electrical
    elif any(k in n for k in ['concrete', 'structure', 'civil', 'building', 'foundation', 'excavation', 'steel', 'road', 'drainage', 'shed']):
        return models.DomainType.Civil
    else:
        return models.DomainType.Mechanical

def migrate_domains():
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE equipment_categories ADD COLUMN IF NOT EXISTS domain VARCHAR DEFAULT 'Mechanical';"))
            conn.execute(text("ALTER TABLE estimate_line_items ADD COLUMN IF NOT EXISTS domain VARCHAR DEFAULT 'Mechanical';"))
            conn.commit()
    except Exception:
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE equipment_categories ADD COLUMN domain VARCHAR DEFAULT 'Mechanical';"))
                conn.commit()
        except Exception:
            pass
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE estimate_line_items ADD COLUMN domain VARCHAR DEFAULT 'Mechanical';"))
                conn.commit()
        except Exception:
            pass

    db: Session = SessionLocal()
    try:
        print("Starting Domain Architecture migration...")
        categories = db.query(models.EquipmentCategory).all()
        print(f"Found {len(categories)} equipment categories.")

        updated_cats = 0
        for cat in categories:
            new_domain = detect_domain(cat.name)
            if cat.domain != new_domain:
                cat.domain = new_domain
                updated_cats += 1
            print(f"   - Category '{cat.name}' -> Domain: [{cat.domain.value}]")

        line_items = db.query(models.EstimateLineItem).all()
        updated_items = 0
        for item in line_items:
            if item.category and item.domain != item.category.domain:
                item.domain = item.category.domain
                updated_items += 1
            elif not item.domain:
                item.domain = models.DomainType.Mechanical
                updated_items += 1

        db.commit()
        print("\nDomain migration completed successfully!")
        print(f"   - Updated Categories: {updated_cats}")
        print(f"   - Updated Line Items: {updated_items}")
        print("==================================================================")
    except Exception as e:
        db.rollback()
        print(f"[Error] Migration failed: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_domains()
