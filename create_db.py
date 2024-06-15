from application import app, db
from application.models import User, Workout, ExerciseSet, Exerciselist

with app.app_context():
    db.create_all()

    # Create users
    user1 = User(firstname="Bog", lastname="God", username="admin", password="123", weight=100, height=200)
    user2 = User(firstname="user", lastname="userovich", username="user", password="1234", weight=60, height=160)
    db.session.add(user1)
    db.session.add(user2)

    # Create workouts
    workout1 = Workout(name="Workout 1", creator_id=user1.id, likes=10, dislikes=2)
    workout2 = Workout(name="Workout 2", creator_id=user2.id, likes=5, dislikes=1)
    db.session.add(workout1)
    db.session.add(workout2)

    # Create exercises
    exercise1 = Exerciselist(name="Push ups")
    exercise2 = Exerciselist(name="Pull ups")
    exercise3 = Exerciselist(name="Sit ups")
    exercise4 = Exerciselist(name="Bicep curls")
    exercise5 = Exerciselist(name="Bench press")
    db.session.add(exercise1)
    db.session.add(exercise2)
    db.session.add(exercise3)
    db.session.add(exercise4)
    db.session.add(exercise5)

    # Commit the session to set the id attributes of the User, Workout, and Exerciselist instances
    db.session.commit()

    # Create exercise sets and add them to the workouts
    exerciseset1 = ExerciseSet(workout_id=workout1.id, exercise_id=exercise1.id, sets=3, weight=10, reps=10)
    exerciseset2 = ExerciseSet(workout_id=workout2.id, exercise_id=exercise2.id, sets=3, weight=10, reps=10)
    db.session.add(exerciseset1)
    db.session.add(exerciseset2)

    db.session.commit()