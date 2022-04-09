import typing

from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "random string"

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
    return render_template(
        'game.html',
        title="Flask Poker",
        description="Smarter page templates with Flask & Jinja.",
        players=User.query.all(),
        is_revealed=False
    )


@socketio.on('connect')
def register():
    user = User("Unknown User", None)
    session['user'] = user
    db.session.add(user)
    db.session.commit()


@socketio.on('vote')
def handle_vote(data):
    user = session['user']
    session['user'].vote = data['data']
    db.session.add(user)
    db.session.commit()

    if user.id is None:
        print("missing uid")
        return

    emit('vote', [{"user": user.id, "value":  "?"}], broadcast=True)


@socketio.on('name')
def handle_name(data):
    user = session['user']
    user.name = data['data']
    db.session.add(user)
    db.session.commit()
    emit('name', {"name": data['data'], "id": user.id}, broadcast=True)


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
