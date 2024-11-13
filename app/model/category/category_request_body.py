from pydantic import BaseModel
from datetime import datetime

class CategoryRequestBody(BaseModel):
    id: str | None = None
    name: str
    create_at: str | None = None
    update_at: str | None = None

    def to_dict(self):
        return {
            'name': self.name,
            'create_at': self.create_at,
            'update_at': self.update_at
        }
    
    def set_create_time(self):
        current_time = datetime.now().astimezone().isoformat()
        self.create_at = current_time

    def set_update_time(self):
        current_time = datetime.now().astimezone().isoformat()
        self.update_at = current_time