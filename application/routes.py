from application import app
from application import db
from flask import render_template, redirect, url_for, flash, request,session,abort
from flask_login import login_user,logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from .models import User, Exerciselist, Workout, ExerciseSet



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/workout_log')
@login_required
def workout_log():
    # workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()
    return render_template('workout_log.html') #workouts=workouts)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
         
        if user and password == user.password:
            login_user(user)
            flash("Login Successful!", category="success")
            session['username'] = username
            return redirect(url_for('workout_log'))
        
        else:
            flash("Invalid username or password! Please try again.", category="danger")
            return redirect(url_for('login'))
        
    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        weight = request.form['weight']
        height = request.form['height']

        user_username = User.query.filter_by(username=username).first()
        if user_username:
            flash("Username already exists!", category="danger")
            return redirect(url_for('register'))

        user = User(
            firstname=firstname,
            lastname=lastname,
            username=username, 
            password=password,
            weight = weight,
            height = height
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration Successful!", category="success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route("/workouts",methods = ["GET"])
@login_required
def all_workouts():
    workouts = Workout.query.all()
    return render_template('workouts.html', workouts=workouts)



@app.route('/create_workout', methods=['POST', 'GET'])
@login_required
def create_workout():
    if request.method == 'POST':
        name = request.form["name"]
        
        exercise_ids = request.form.getlist('exercise[]')
        weights = request.form.getlist('weight[]')
        reps = request.form.getlist('reps[]')
        sets = request.form.getlist('sets[]')

        exercises = list(zip(exercise_ids, weights, reps, sets))
        print(current_user.id)
        workout = Workout(name=name,creator_id = current_user.id )
        db.session.add(workout)
        db.session.commit()

        for exercise in exercises:
            exerciseset = ExerciseSet(workout_id=workout.id, exercise_id=exercise[0], weight=exercise[1], reps=exercise[2], sets=exercise[3])
            workout.exercisesets.append(exerciseset)
        
        
        db.session.commit()
        

        flash("Workout Added!", category="success")
        return redirect(url_for('all_workouts'))

    exercises = Exerciselist.query.all()
    return render_template('create_workout.html', exercises=exercises)



@app.route('/edit', methods=['POST','GET'])
@login_required
def edit():
    if request.method == 'POST':
        workout_id = int(request.form['workout_id'])
        workout = Workout.query.filter_by(id = workout_id).first()
        for exercise in workout.exercises:
            for set in exercise.sets:
                set.weight = request.form['weight' + str(set.id)]
                set.reps = request.form['reps' + str(set.id)]
        db.session.commit()
        flash("Workout updated!", category="success")
        return redirect(url_for('workout_log'))


@app.route('/myprofile',methods=['POST','GET'])
@login_required
def profile():
    user = User.query.filter_by(username=current_user.username).first()
    return render_template('myprofile.html', user=user)





@app.route('/delete', methods=['POST','GET'])
@login_required
def delete():
    if request.method == 'POST':
        workout_id = int(request.form['workout_id'])
        workout = Workout.query.filter_by(id = workout_id).first()
        db.session.delete(workout)
        db.session.commit()
        flash("Workout deleted!", category="warning")
        return redirect(url_for('workout_log'))




@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", category="warning")
    return redirect(url_for('index'))



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404




@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'),500