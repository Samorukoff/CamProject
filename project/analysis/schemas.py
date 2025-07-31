from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Схема вывода общей инфомрации о точках
class PointOut(BaseModel):
    id: int
    name: str
    address: str
    company: int

    model_config = ConfigDict(
        from_attributes=True
    )


class AnalysisRow(BaseModel):
    point_id: int
    point_name: str
    camera_name: str
    traffic: int
    useful_traffic: int
    recommendations: str
    period: datetime

    model_config = ConfigDict(
        json_encoders={datetime: lambda dt: dt.strftime("%d.%m.%Y")},
        from_attributes=True
    )

class AnalysisSummary(BaseModel):
    subscription: str
    price: int
    remaining_days: int
    total_cameras: int
    last_updated: datetime
