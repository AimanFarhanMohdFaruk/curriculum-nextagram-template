from models.base_model import BaseModel
import peewee as pw
from playhouse.hybrid import hybrid_property
from models.user import User




class UserImages(BaseModel):
    user_image_path = pw.TextField(null=True)
    user = pw.ForeignKeyField(User, backref='images', on_delete="CASCADE")


    @hybrid_property
    def full_image_path(self):
            from app import app
            return app.config.get("S3_LOCATION") + self.user_image_path
     




