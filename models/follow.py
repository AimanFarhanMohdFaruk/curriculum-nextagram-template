from models.base_model import BaseModel
from models.user import User
import peewee as pw


class Follow(BaseModel):
    follower = pw.ForeignKeyField(User, backref= 'followings', on_delete='CASCADE')
    following = pw.ForeignKeyField(User, backref= 'followers', on_delete='CASCADE')
    is_approved = pw.BooleanField(default=False)

