import peewee as pw
from models.base_model import BaseModel
from models.user_images import UserImages


class Donate(BaseModel):
    amount = pw.DecimalField(decimal_places=2)
    image = pw.ForeignKeyField(UserImages, backref="donations")