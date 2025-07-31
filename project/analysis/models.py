from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Float
from sqlalchemy.orm import relationship
from project.database import Base
from datetime import datetime

class AnalysisData(Base):
    __tablename__ = "analysis_data"

    id = Column(Integer, primary_key=True)
    point_id = Column(Integer, ForeignKey("points.id"), nullable=False)
    camera = Column(String, nullable=False)  # Имя или ID камеры
    traffic = Column(Integer, nullable=False)  # Общая проходимость
    useful_traffic = Column(Integer, nullable=False)  # Полезная проходимость
    recommendations = Column(String, nullable=True)  # Рекомендации
    period = Column(DateTime, default=datetime.utcnow, nullable=False)

    point = relationship("Point", back_populates="analysis_data")


# Таблица с общей информацией по всем точкам
class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    company = Column(Integer, ForeignKey("companies.id"), nullable=False)

    analysis_data = relationship("AnalysisData", back_populates="point")
