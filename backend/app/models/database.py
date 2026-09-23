from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./agni_pariksha.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class PartResult(Base):
    __tablename__ = "part_results"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(String, index=True)
    lot_id = Column(String, index=True)
    verdict = Column(String)
    cri_score = Column(Float)
    a_score = Column(Float)
    d_score = Column(Float)
    highest_attr_param = Column(String)
    
    # Ground truth (for synthetic data)
    is_defective_gt = Column(Boolean, nullable=True)
    defect_type_gt = Column(String, nullable=True)

class PartReading(Base):
    __tablename__ = "part_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(String, index=True)
    lot_id = Column(String, index=True)
    parameter_name = Column(String)
    timepoint_hours = Column(Float)
    value = Column(Float)

Base.metadata.create_all(bind=engine)
