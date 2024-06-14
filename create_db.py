from application import app, db
from application.models import Exerciselist

with app.app_context():
    db.create_all()
    exercise = Exerciselist(name = "Push ups")
    db.session.add(exercise)
    exercise = Exerciselist(name = "Pull ups")
    db.session.add(exercise)
    exercise = Exerciselist(name = "Sit ups")
    db.session.add(exercise)
    exercise = Exerciselist(name = "Crunches")
    db.session.add(exercise)
    db.session.commit()
