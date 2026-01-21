"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import Comment, Follower, Media, Post, db, User
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


@app.route("/users", methods=["POST"])
def create_user():
    body = request.get_json(silent=True) or {}

    if not body.get("username") or not body.get("email"):
        return jsonify({"msg": "username y email son obligatorios"}), 400

    user = User(
        username=body["username"],
        email=body["email"],
        firstname=body.get("firstname"),
        lastname=body.get("lastname"),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201


@app.route("/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()
    return jsonify([p.serialize() for p in posts]), 200


@app.route("/posts", methods=["POST"])
def create_post():
    body = request.get_json(silent=True) or {}
    user_id = body.get("user_id")

    if not user_id:
        return jsonify({"msg": "user_id es obligatorio"}), 400

    # Opcional: validar usuario existe
    if not User.query.get(user_id):
        return jsonify({"msg": "User no existe"}), 404

    post = Post(
        user_id=user_id,
        caption=body.get("caption"),
    )
    db.session.add(post)
    db.session.commit()
    return jsonify(post.serialize()), 201


@app.route("/posts/<int:post_id>/media", methods=["POST"])
def add_media_to_post(post_id):
    body = request.get_json(silent=True) or {}

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"msg": "Post no existe"}), 404

    if not body.get("type") or not body.get("url"):
        return jsonify({"msg": "type y url son obligatorios"}), 400

    media = Media(
        type=body["type"],
        url=body["url"],
        post_id=post_id,
    )
    db.session.add(media)
    db.session.commit()
    return jsonify(media.serialize()), 201


@app.route("/posts/<int:post_id>/comments", methods=["POST"])
def add_comment(post_id):
    body = request.get_json(silent=True) or {}

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"msg": "Post no existe"}), 404

    if not body.get("author_id") or not body.get("comment_text"):
        return jsonify({"msg": "author_id y comment_text son obligatorios"}), 400

    if not User.query.get(body["author_id"]):
        return jsonify({"msg": "Author no existe"}), 404

    comment = Comment(
        author_id=body["author_id"],
        post_id=post_id,
        comment_text=body["comment_text"],
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.serialize()), 201


@app.route("/follow", methods=["POST"])
def follow_user():
    body = request.get_json(silent=True) or {}

    user_from_id = body.get("user_from_id")
    user_to_id = body.get("user_to_id")

    if not user_from_id or not user_to_id:
        return jsonify({"msg": "user_from_id y user_to_id son obligatorios"}), 400

    if user_from_id == user_to_id:
        return jsonify({"msg": "No puedes seguirte a ti mismo"}), 400

    if not User.query.get(user_from_id) or not User.query.get(user_to_id):
        return jsonify({"msg": "User(s) no existen"}), 404

    exists = Follower.query.get((user_from_id, user_to_id))
    if exists:
        return jsonify({"msg": "Ya lo sigues"}), 409

    follow = Follower(user_from_id=user_from_id, user_to_id=user_to_id)
    db.session.add(follow)
    db.session.commit()
    return jsonify(follow.serialize()), 201


@app.route("/follow", methods=["DELETE"])
def unfollow_user():
    body = request.get_json(silent=True) or {}

    user_from_id = body.get("user_from_id")
    user_to_id = body.get("user_to_id")

    if not user_from_id or not user_to_id:
        return jsonify({"msg": "user_from_id y user_to_id son obligatorios"}), 400

    follow = Follower.query.get((user_from_id, user_to_id))
    if not follow:
        return jsonify({"msg": "No existe esa relación"}), 404

    db.session.delete(follow)
    db.session.commit()
    return jsonify({"msg": "Unfollow OK"}), 200
