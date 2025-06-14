from app.models.base_model import BaseModel
from app.db import db

class StockImage(BaseModel):
    __tablename__ = "stock_image"

    istock_name = db.Column(db.String)
    istock_id = db.Column(db.Integer)
    uses = db.Column(db.String)