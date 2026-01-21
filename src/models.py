from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# --------------------------
# MODELOS (Instagram-like)
# --------------------------

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    firstname = db.Column(db.String(80), nullable=True)
    lastname = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Relaciones
    posts = db.relationship(
        "Post", back_populates="author", cascade="all, delete-orphan")
    comments = db.relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan")

    following = db.relationship(
        "Follower",
        foreign_keys="Follower.user_from_id",
        back_populates="from_user",
        cascade="all, delete-orphan",
    )
    followers = db.relationship(
        "Follower",
        foreign_keys="Follower.user_to_id",
        back_populates="to_user",
        cascade="all, delete-orphan",
    )

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            # opcional: listas rápidas (ids)
            "following_ids": [f.user_to_id for f in self.following],
            "follower_ids": [f.user_from_id for f in self.followers],
        }


class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    caption = db.Column(db.String(2200), nullable=True)

    author = db.relationship("User", back_populates="posts")
    media_items = db.relationship(
        "Media", back_populates="post", cascade="all, delete-orphan")
    comments = db.relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "caption": self.caption,
            "media": [m.serialize() for m in self.media_items],
            "comments": [c.serialize() for c in self.comments],
        }


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # "image" | "video"
    url = db.Column(db.String(255), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

    post = db.relationship("Post", back_populates="media_items")

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type,
            "url": self.url,
            "post_id": self.post_id,
        }


class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    comment_text = db.Column(db.String(1000), nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

    author = db.relationship("User", back_populates="comments")
    post = db.relationship("Post", back_populates="comments")

    def serialize(self):
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "author_id": self.author_id,
            "post_id": self.post_id,
        }


class Follower(db.Model):
    __tablename__ = "follower"

    id = db.Column(db.Integer, primary_key=True)

    user_from_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False)
    user_to_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_from_id", "user_to_id",
                            name="uq_follow_pair"),
    )

    from_user = db.relationship(
        "User",
        foreign_keys=[user_from_id],
        back_populates="following",
    )
    to_user = db.relationship(
        "User",
        foreign_keys=[user_to_id],
        back_populates="followers",
    )

    def serialize(self):
        return {
            "id": self.id,
            "user_from_id": self.user_from_id,
            "user_to_id": self.user_to_id,
        }
