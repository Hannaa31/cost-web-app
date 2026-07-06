import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Enum as SAEnum, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum
from database import Base

# Strict JSONB type that falls back to JSON when running against SQLite in local demo mode
JSONBType = JSONB().with_variant(JSON(), "sqlite")

class UserRole(str, enum.Enum):
    admin = "admin"
    estimator = "estimator"

class DomainType(str, enum.Enum):
    Mechanical = "Mechanical"
    Electrical = "Electrical"
    Civil = "Civil"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.estimator, nullable=False)
    is_active = Column(Boolean, default=True)

    projects = relationship("Project", back_populates="creator", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False, index=True)
    client = Column(String, nullable=False)
    global_margin_pct = Column(Float, default=0.15)  # e.g. 0.15 for 15%
    global_erection_pct = Column(Float, default=0.10) # e.g. 0.10 for 10%
    default_annual_escalation_pct = Column(Float, default=0.045) # e.g. 0.045 for 4.5% annual inflation/escalation
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    creator = relationship("User", back_populates="projects")
    line_items = relationship("EstimateLineItem", back_populates="project", cascade="all, delete-orphan")

class EquipmentCategory(Base):
    __tablename__ = "equipment_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    domain = Column(SAEnum(DomainType), default=DomainType.Mechanical, nullable=False, index=True)
    # spec_schema defines list of specification parameter keys expected for this category
    # e.g., ["Pulley Type", "BW (mm)", "Diameter", "Shell Thk", "Face Width", "Shaft Dia Brg", "Shaft Dia Hub", "Lagging"]
    spec_schema = Column(JSONBType, nullable=False)

    master_rates = relationship("MasterRate", back_populates="category", cascade="all, delete-orphan")
    line_items = relationship("EstimateLineItem", back_populates="category")

class MasterRate(Base):
    __tablename__ = "master_rates"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("equipment_categories.id", ondelete="CASCADE"), nullable=False)
    vendor_name = Column(String, nullable=False, index=True) # Placeholders like "Vendor_Alpha", "Vendor_Beta"
    base_rate = Column(Float, nullable=False)
    quotation_date = Column(DateTime, nullable=False)
    specifications = Column(JSONBType, nullable=False)
    remarks = Column(String, nullable=True)

    category = relationship("EquipmentCategory", back_populates="master_rates")
    line_items = relationship("EstimateLineItem", back_populates="selected_rate")

class EstimateLineItem(Base):
    __tablename__ = "estimate_line_items"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("equipment_categories.id"), nullable=False)
    selected_rate_id = Column(Integer, ForeignKey("master_rates.id"), nullable=False)
    domain = Column(SAEnum(DomainType), default=DomainType.Mechanical, nullable=False, index=True)
    quantity = Column(Float, nullable=False, default=1.0)
    calculated_escalated_rate = Column(Float, nullable=False)
    total_item_cost = Column(Float, nullable=False)

    project = relationship("Project", back_populates="line_items")
    category = relationship("EquipmentCategory", back_populates="line_items")
    selected_rate = relationship("MasterRate", back_populates="line_items")
