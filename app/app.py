import typing

from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)
socketio.manage_session = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "random string"
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column('user_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    vote = db.Column(db.Integer)

    def __init__(self, name: str, vote: typing.Optional[int]):
        self.name = name
        self.vote = vote


@app.route('/')
def list_members():  # put application's code here
    user = load_user()
    return render_template(
        'game.html',
        title="Flask Poker",
        votes=["☕️", 1, 2, 3, 5, 8, 13, 21, "?"],
        user=user,
        description="Smarter page templates with Flask & Jinja.",
        players=User.query.all()
    )


@socketio.on('connect')
def connect():
    print(session)

    # print(request.cookies)
    load_user()


def load_user():
    user = None

    if 'user_id' in session and session['user_id'] is not None:
        user = User.query.get(session['user_id'])

    if user is None:
        user = User(session['user_name'] if 'user_name' in session else "Unknown User",
                    session['user_vote'] if 'user_vote' in session else None)
        db.session.add(user)
        db.session.commit()
        socketio.emit('name', {"name": user.name, "id": user.id}, broadcast=True)
        print(user.id)

    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_vote'] = user.vote
    return user


@socketio.on('vote')
def handle_vote(data):
    user = load_user()
    if str(session["user_vote"]) == str(data['data']):
        user.vote = None
        session["user_vote"] = None
        emit('vote', [{"user": user.id, "value": None}], broadcast=True)
    else:
        user.vote = data['data']
        session["user_vote"] = user.vote
        emit('vote', [{"user": user.id, "value": "?"}], broadcast=True)
    db.session.commit()
    print(session)


@socketio.on('name')
def handle_name(data):
    user = load_user()
    user.name = data['data']
    session['user_name'] = user.name
    db.session.commit()
    emit('name', {"name": data['data'], "id": user.id}, broadcast=True)
    print(session)


@socketio.on('flip')
def flip(ignored):
    voting_users = User.query.filter(User.vote.isnot(None))
    votes = []
    for user in voting_users:
        votes.append({"user": user.id, "value": user.vote})
    emit('vote', votes, broadcast=True)


db.create_all()
db.session.commit()

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
