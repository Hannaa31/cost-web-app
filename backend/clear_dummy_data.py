import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from database import SessionLocal
import models

def clear_dummy_data():
    db = SessionLocal()
    try:
        print("Clearing dummy data from database...")
        
        # Delete Estimate Line Items
        deleted_items = db.query(models.EstimateLineItem).delete()
        
        # Delete Projects
        deleted_projects = db.query(models.Project).delete()
        
        # Delete Master Rates
        deleted_rates = db.query(models.MasterRate).delete()
        
        # Delete Equipment Categories
        deleted_cats = db.query(models.EquipmentCategory).delete()
        
        db.commit()
        print("Cleaned up successfully!")
        print(f"   - Removed Line Items:        {deleted_items}")
        print(f"   - Removed Projects:          {deleted_projects}")
        print(f"   - Removed Master Rates:      {deleted_rates}")
        print(f"   - Removed Categories:        {deleted_cats}")
        print("\nNote: User accounts (admin@enterprise.local and estimator@enterprise.local) were preserved so you can stay logged in.")
        
    except Exception as e:
        db.rollback()
        print(f"Error clearing data: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_dummy_data()
