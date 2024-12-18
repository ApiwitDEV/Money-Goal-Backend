from pydantic import BaseModel
from datetime import datetime

class TransactionRequestBody(BaseModel):
    id: str | None = None
    name: str
    create_at: str | None = None
    update_at: str | None = None
    category_id: str
    type: str
    money_amount: float
    remark: str | None = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "create_at": self.create_at,
            "update_at": self.update_at,
            "category_id": self.category_id,
            "type": self.type,
            "money_amount": self.money_amount,
            "remark": self.remark
        }
    
    def set_id(self, id: str):
        self.id = id

    def set_create_time(self):
        current_time = datetime.now().astimezone().isoformat()
        self.create_at = current_time

    def set_update_time(self):
        current_time = datetime.now().astimezone().isoformat()
        self.update_at = current_time