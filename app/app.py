import os
import names

from flask import Flask, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app)
socketio.manage_session = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI", default='sqlite:///:memory:')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("FLASK_COOKIE_SECRET", default="this-default-will-let-anyone-forge-a-cookie")
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24  # 24 hours
db = SQLAlchemy(app)


# # # # # #
# Models  #
# # # # # #


class User(db.Model):
    id = db.Column('user_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    vote = db.Column(db.Integer)
    room = db.Column(db.String(100))

    def __init__(self, name: str, room: str, vote: int):
        self.name = name
        self.room = room
        self.vote = vote


# # # # # # # # #
# API Endpoints #
# # # # # # # # #


@app.route('/')
def random_room():
    import uuid
    uid_str = uuid.uuid4().urn
    room = uid_str[9:]
    return redirect("/" + str(room), code=302)


@app.route('/<room_id>')
def list_members(room_id="default"):  # put application's code here
    user = load_user()
    session['user_room'] = room_id
    user.room = room_id
    db.session.commit()
    return render_template(
        'game.html',
        room=room_id,
        title="Flask Poker",
        votes=["☕️", 1, 2, 3, 5, 8, 13, 21, "?"],
        user=user,
        description="Smarter page templates with Flask & Jinja.",
        players=get_users_in_room(room_id)
    )


@socketio.on('connect')
def connect():
    user = load_user()
    join_room(user.room)
    socketio.emit('name', {"name": user.name, "id": user.id}, room=user.room)


@socketio.on('vote')
def handle_vote(data):
    user = load_user()
    print(user.room)

    if str(session["user_vote"]) == str(data['data']):
        user.vote = None
        session["user_vote"] = None
    else:
        user.vote = data['data']
        session["user_vote"] = user.vote

    emit('vote', [{"user": user.id, "value": "?" if user.vote is not None else ""}], room=user.room)
    db.session.commit()
    print(session)


@socketio.on('name')
def handle_name(data):
    if 'data' not in data or len(data['data']) == 0:
        print("bad name")
        return

    session['user_name'] = data['data']
    user = load_user()
    user.name = data['data']
    db.session.commit()
    emit('name', {"name": user.name, "id": user.id}, room=user.room)
    print(session)


@socketio.on('flip')
def flip(ignored):
    room_id = load_user().room
    votes = []
    for user in get_users_in_room(room_id):
        votes.append({"user": user.id, "value": user.vote})
    emit('vote', votes, room=room_id)


# # # # # # # # # # #
# Helper functions  #
# # # # # # # # # # #


def get_users_in_room(room_id):
    return User.query.filter(User.name.isnot(None)).filter(User.room == room_id)


def load_user():
    user = None

    if 'user_id' in session and session['user_id'] is not None:
        user = User.query.get(session['user_id'])

    if user is None:
        user = User(session['user_name'] if 'user_name' in session else names.get_full_name(),
                    session['user_room'] if 'user_room' in session else None,
                    session['user_vote'] if 'user_vote' in session else None)
        db.session.add(user)
        db.session.commit()
        socketio.emit('name', {"name": user.name, "id": user.id}, room=user.room)
        print(user.id)

    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_vote'] = user.vote
    session['user_room'] = user.room
    return user


# # # # # # # #
# Entrypoint  #
# # # # # # # #


db.create_all()
db.session.commit()

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
