from application import db, login_manager
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


favorite_workouts_users = db.Table('favorite_workouts_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),  
    db.Column('workout_id', db.Integer, db.ForeignKey('workout.id')) 
)


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    exercisesets = db.relationship('ExerciseSet', backref='workout', lazy=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    creator = db.relationship('User', backref='created_workouts', lazy=True)
    likes = db.Column(db.Integer, default = 0)
    dislikes = db.Column(db.Integer,default = 0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
  
    @hybrid_property
    def duration(self):
        return sum(exerciseset.sets for exerciseset in self.exercisesets) * 3

class UserReaction(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), primary_key=True)
    reaction = db.Column(db.String(10))

class CompletedWorkout(db.Model):
    id = id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    date = db.Column(db.Date())
    duration = db.Column(db.Numeric(precision=2, asdecimal=False, decimal_return_scale=None))


workouts_users = db.Table('workouts_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),  
    db.Column('workout_id', db.Integer, db.ForeignKey('workout.id')) 
)

completed_workouts_users = db.Table('completed_workouts_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),  
    db.Column('completed_workout_id', db.Integer, db.ForeignKey('completed_workout.id')) 
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20))
    lastname = db.Column(db.String(20))
    username = db.Column(db.String(15), unique=True)
    weight = db.Column(db.Numeric(precision=1, asdecimal=False, decimal_return_scale=None))
    height = db.Column(db.Numeric(precision=2, asdecimal=False, decimal_return_scale=None))
    password = db.Column(db.String(80))

    completed_workouts = db.relationship('CompletedWorkout', secondary=completed_workouts_users, backref=db.backref('users', lazy='dynamic'))
    favorite_workouts = db.relationship('Workout', secondary=favorite_workouts_users, backref=db.backref('favorited_by', lazy='dynamic'))
    


class Exerciselist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


class ExerciseSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))
    exercise_id = db.Column(db.Integer, db.ForeignKey('exerciselist.id'))
    exercise = db.relationship('Exerciselist', backref='exercisesets')
    sets = db.Column(db.Integer)
    weight = db.Column(db.Numeric(precision=1, asdecimal=False, decimal_return_scale=None))
    reps = db.Column(db.Integer)