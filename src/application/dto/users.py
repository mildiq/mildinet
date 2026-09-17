from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    email: str
    name: str
    password_hash: str
    created_at: datetime