from flask_migrate import Migrate
from application import app, db
from application.models import User, Workout, ExerciseSet, Exerciselist

migrate = Migrate(app, db)


with app.app_context():
    db.create_all()

    # Create users
    easyfitness = User(firstname = "Admin",lastname = "Admin",username="EasyFitness",password = 321, weight = 100000,height=10000)
    user1 = User(firstname="Bog", lastname="God", username="admin", password="123", weight=100, height=200)
    user2 = User(firstname="user", lastname="userovich", username="user", password="1234", weight=60, height=160)
    db.session.add(easyfitness)
    db.session.add(user1)
    db.session.add(user2)

    # Create workouts
    fullbody = Workout(name="Full Body Workout", creator_id=user1.id, likes=10, dislikes=2)
    upper_body = Workout(name="Upper Body Workout", creator_id=user1.id, likes=8, dislikes=1)
    legs = Workout(name="Legs Workout", creator_id=user1.id, likes=12, dislikes=0)
    db.session.add(fullbody)
    db.session.add(upper_body)
    db.session.add(legs)

    # Create exercises
    exercise_names = ["Push ups", "Pull ups", "Sit ups", "Bicep curls", "Bench press", 
                      "Squat", "Deadlift", "Lunges", "Leg Press", "Shoulder Press"]

    exercises = {}
    for name in exercise_names:
        exercise = Exerciselist(name=name)
        db.session.add(exercise)
        db.session.commit()
        exercises[name] = exercise

    # Commit the session to set the id attributes of the User, Workout, and Exerciselist instances
    db.session.commit()

    # Add exercise sets to the workouts
    fullbody_exercises = ["Push ups", "Pull ups", "Sit ups", "Bicep curls", "Squat"]
    upper_body_exercises = ["Push ups", "Pull ups", "Bench press", "Shoulder Press", "Bicep curls"]
    legs_exercises = ["Squat", "Deadlift", "Lunges", "Leg Press", "Sit ups"]

    for exercise_name in fullbody_exercises:
        exercise_set = ExerciseSet(workout_id=fullbody.id, exercise_id=exercises[exercise_name].id, sets=3, weight=0, reps=12)
        db.session.add(exercise_set)

    for exercise_name in upper_body_exercises:
        exercise_set = ExerciseSet(workout_id=upper_body.id, exercise_id=exercises[exercise_name].id, sets=3, weight=0, reps=12)
        db.session.add(exercise_set)

    for exercise_name in legs_exercises:
        exercise_set = ExerciseSet(workout_id=legs.id, exercise_id=exercises[exercise_name].id, sets=3, weight=0, reps=12)
        db.session.add(exercise_set)

    db.session.commit()