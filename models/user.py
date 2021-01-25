from models.base_model import BaseModel
import peewee as pw
import re
from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from playhouse.hybrid import hybrid_property



class User(BaseModel, UserMixin):
    email = pw.CharField(unique=True, null=False)
    username = pw.CharField(unique=False, null = False)
    password_hash = pw.TextField(null=False)
    password = None
    image_path=pw.TextField(null=True)
    private = pw.BooleanField(default=False)

    @hybrid_property
    def full_image_path(self):
        if self.image_path:
            from app import app
            return app.config.get("S3_LOCATION") + self.image_path
        else:
            return ""

    def follow(self,following):
        from models.follow import Follow

        if self.follow_status(following) == None:
            relationship = Follow(follower = self.id, following = following)
            if not following.private:
                relationship.is_approved  = True
            return relationship.save()
        else:
            return 0

    def unfollow(self,following):
        from models.follow import Follow
        return Follow.delete().where(Follow.follower == self.id, Follow.following == following).execute()

    def follow_status(self, following):
        from models.follow import Follow
        return Follow.get_or_none(Follow.follower == self.id , Follow.following == following.id )

    @hybrid_property    
    def get_followers(self):
        from models.follow import Follow
        followers = Follow.select(Follow.follower).where(Follow.following == self.id, Follow.is_approved == True)
        return User.select().where(User.id.in_(followers))

    @hybrid_property
    def get_followings(self):
        from models.follow import Follow
        followings = Follow.select(Follow.following).where(Follow.follower == self.id, Follow.is_approved == True)
        return User.select().where(User.id.in_(followings))

    @hybrid_property
    def following_requests(self):
        from models.follow import Follow
        followings = Follow.select(Follow.following).where(Follow.follower == self.id, Follow.is_approved == False)
        return User.select().where(User.id.in_(followings))
    
    @hybrid_property
    def follower_requests(self):
        from models.follow import Follow
        followers = Follow.select(Follow.follower).where(Follow.following == self.id, Follow.is_approved == False)
        return User.select().where(User.id.in_(followers))

    
    def approve_requests(self, follower):
        from models.follow import Follow
        # GET the relationship. This would return the follow relationship between follower and following. Direct get to that database, then set is_approved = True to accept
        relationship = follower.follow_status(self)
        relationship.is_approved = True
        return relationship.save()

    
    def validate(self):
        existing_user_email = User.get_or_none(User.email == self.email)
        if existing_user_email and existing_user_email.id != self.id:
            self.errors.append(f"User with {self.email} already exists")

        existing_user_username = User.get_or_none(User.username == self.username)
        if existing_user_username and existing_user_username.id != self.id:
            self.errors.append(f"User with {self.username} already exists.")

        #Passwords
        if self.password:
            if len(self.password) <= 6:
                self.errors.append(f"Password must at least have six characters")

            has_lower = re.search(r"[a-z]", self.password)
            has_upper = re.search(r"[A-Z]",self.password)
            has_special = re.search(r"[\[ \] \@ \$ \* \^ \# \%]", self.password)

            if has_lower and has_upper and has_special:
                self.password_hash = generate_password_hash(self.password)
            else:
                self.errors.append(f"Password requires changes")