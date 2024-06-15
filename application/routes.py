from application import app
from application import db
from flask import render_template, redirect, url_for, flash, request,session,abort
from flask_login import login_user,logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from .models import User, Exerciselist, Workout, ExerciseSet,UserReaction



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

@app.route("/favorite", methods=["GET", "POST"])
@login_required
def favorite_workouts():
    if request.method == "POST":
        workout_id = request.form.get('workout_id')
        workout = Workout.query.get(workout_id)
        if workout in current_user.favorite_workouts:
            current_user.favorite_workouts.remove(workout)
            db.session.commit()

    return render_template('favorite.html', workouts=current_user.favorite_workouts)
    
@app.route("/favorite/", methods=["GET", "POST"])

@app.route("/workouts",methods = ["GET","POST"])
@login_required
def all_workouts():
    sort_order = request.args.get('sort', 'newest')  
    if sort_order == 'newest': #does not work for some reason(
        workouts = Workout.query.all()
    elif sort_order == 'oldest':
        workouts = Workout.query.order_by(Workout.created_at).all()
    elif sort_order == 'likes':
        workouts = Workout.query.order_by(Workout.likes.desc()).all()
    else:
        workouts = Workout.query.all()  

    return render_template('workouts.html', workouts=workouts)

@app.route('/workouts/<int:workout_id>/favorite', methods=['POST'])
@login_required
def favorite_workout(workout_id):
    workout = Workout.query.get(workout_id)
    if request.form.get('_method') == 'DELETE':
        current_user.favorite_workouts.remove(workout)
        db.session.commit()
        flash("Workout unfavored successfully.", category="warning")
        return redirect(url_for('favorite_workouts'))

    if workout not in current_user.favorite_workouts:
        current_user.favorite_workouts.append(workout)
        flash("Workout favored successfully.", category="success")
    else:
        current_user.favorite_workouts.remove(workout)
        flash("Workout unfavored successfully.", category="warning")
    db.session.commit()
    return redirect(url_for('workout', workout_id=workout_id))

@app.route("/myworkouts",methods = ["GET","POST"])
@login_required
def created_workouts():
    if request.form.get('_method') == 'DELETE':
        current_user.favorite_workouts.remove(workout)
        db.session.commit()
        return redirect(url_for('favorite_workouts'))
    print(current_user.created_workouts)  # Debug print statement
    return render_template('myworkouts.html')


@app.route("/workouts/<int:workout_id>/delete", methods=["POST"])
@login_required
def delete_workout(workout_id):
    workout = Workout.query.get(workout_id)
    
    if workout is None or workout.creator != current_user:
        flash("Unauthorized action.", category="danger")
        return redirect(url_for('all_workouts'))

    # Delete the workout
    db.session.delete(workout)
    db.session.commit()

    flash("Workout deleted successfully.", category="success")
    return redirect(url_for('created_workouts'))

@app.route("/workouts/<int:workout_id>", methods=["GET","POST"])
@login_required
def workout(workout_id):
    workout = Workout.query.filter_by(id=workout_id).first()
    
    if workout is None:
        flash("Workout not found!", category="danger")
        return redirect(url_for('all_workouts'))
    return render_template('workout.html', workout=workout)


@app.route("/workouts/<int:workout_id>/edit", methods=["GET","POST"])
@login_required
def edit_workout(workout_id):
    workout = Workout.query.get(workout_id)
    exercises = Exerciselist.query.all()
    
    if workout is None or workout.creator != current_user:
        flash("Unauthorized action.", category="danger")
        return redirect(url_for('all_workouts'))

    if request.method == 'POST':
   
        name = request.form.get('name')
        weights = request.form.getlist('weight[]')
        reps = request.form.getlist('reps[]')
        sets = request.form.getlist('sets[]')


        workout.name = name        
        for i in range(len(weights)):
            if i < len(workout.exercisesets):
                exercise_set = workout.exercisesets[i]
                exercise_set.weight = weights[i]
                exercise_set.reps = reps[i]
                exercise_set.sets = sets[i]
            else:
        
                exercise_set = ExerciseSet(weight=weights[i], reps=reps[i], sets=sets[i])
                workout.exercisesets.append(exercise_set)

     
        while len(workout.exercisesets) > len(weights):
            workout.exercisesets.pop()


        db.session.commit()

        flash("Workout updated successfully.", category="success")
        return redirect(url_for('all_workouts'))
    return render_template('edit_workout.html', workout=workout, exercises=exercises)


@app.route('/workouts/<int:workout_id>/like', methods=['POST'])
@login_required
def like_workout(workout_id):
    workout = Workout.query.get(workout_id)
    user_reaction = UserReaction.query.filter_by(user_id=current_user.id, workout_id=workout_id).first()
    if user_reaction:
        if user_reaction.reaction == 'like':
            flash('You have already liked this workout.', category='danger')
        else:
            user_reaction.reaction = 'like'
            workout.likes += 1
            workout.dislikes -= 1
            db.session.commit()
    elif workout:
        workout.likes += 1
        db.session.add(UserReaction(user_id=current_user.id, workout_id=workout_id, reaction='like'))
        db.session.commit()
    return redirect(url_for('workout', workout_id=workout_id))

@app.route('/workouts/<int:workout_id>/dislike', methods=['POST'])
@login_required
def dislike_workout(workout_id):
    workout = Workout.query.get(workout_id)
    user_reaction = UserReaction.query.filter_by(user_id=current_user.id, workout_id=workout_id).first()
    if user_reaction:
        if user_reaction.reaction == 'dislike':
            flash('You have already disliked this workout.', category='danger')
        else:
            user_reaction.reaction = 'dislike'
            workout.likes -= 1
            workout.dislikes += 1
            db.session.commit()
    elif workout and workout.likes > 0:
        workout.dislikes += 1
        db.session.add(UserReaction(user_id=current_user.id, workout_id=workout_id, reaction='dislike'))
        db.session.commit()
    return redirect(url_for('workout', workout_id=workout_id))

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