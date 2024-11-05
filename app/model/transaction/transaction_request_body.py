from pydantic import BaseModel

class TransactionRequestBody(BaseModel):
    id: str | None = None
    name: str
    category_id: str
    type: str
    value: float
    remark: str | None = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category_id": self.category_id,
            "type": self.type,
            "value": self.value,
            "remark": self.remark
        }
    
    def set_id(self, id: str):
        self.id = id