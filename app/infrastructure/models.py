

from sqlalchemy import JSON, Column, Integer, String

from app.infrastructure.database import Base


class TerritorialDataModel(Base):
    #modelo de  tabla
    __tablename__="territorial_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(String, index=True, nullable=False) # Para saber de qué corrida son estos datos
    zone_code = Column(String, nullable=False)
    zone_name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    metrics = Column(JSON, nullable=False) #guardamos la metricas