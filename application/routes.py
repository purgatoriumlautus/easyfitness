from application import app
from application import db
from flask import render_template, redirect, url_for, flash, request,session,abort
from flask_login import login_user,logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from .models import User, Exerciselist, Workout, ExerciseSet,UserReaction,CompletedWorkout,CompletedExerciseSet


@app.route('/')
def index():
    return render_template('index.html')



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
            return redirect(url_for('workout_history'))
        
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


@app.route("/workouts", methods=["GET", "POST"])
@login_required
def all_workouts():
    sort_order = request.args.get('sort', 'newest')

    base_query = Workout.query.filter_by(privacy='public')

    if sort_order == 'newest':
        workouts = base_query.order_by(Workout.created_at.desc()).all()
    elif sort_order == 'oldest':
        workouts = base_query.order_by(Workout.created_at).all()
    elif sort_order == 'likes':
        workouts = base_query.order_by(Workout.likes.desc()).all()
    else:
        workouts = base_query.order_by(Workout.name.asc()).all()

    return render_template('workouts.html', workouts=workouts)



@app.route('/create_workout', methods=['POST', 'GET'])
@login_required
def create_workout():
    exercises = Exerciselist.query.filter_by(creator_id=None).all()
    
    if request.method == 'POST':
        name = request.form["name"]
        privacy = request.form["privacy"]  # Get the privacy setting
        exercise_ids = request.form.getlist('exercise[]')
        reps = request.form.getlist('reps[]')
        sets = request.form.getlist('sets[]')

        workout = Workout(name=name, creator_id=current_user.id, privacy=privacy)  # Save the privacy setting
        db.session.add(workout)
        db.session.commit()

        for i, exercise_id in enumerate(exercise_ids):
            if exercise_id == 'other':
                new_exercise_name = request.form.get(f'new_exercise_{i}')
                if new_exercise_name:
                    new_exercise = Exerciselist(name=new_exercise_name, creator_id=current_user.id)
                    db.session.add(new_exercise)
                    db.session.flush()
                    exercise_id = new_exercise.id

            try:
                rep = int(reps[i])
                set_count = int(sets[i])
            except ValueError:
                flash(f"Incorrect input for reps or sets: {reps[i]}, {sets[i]}", category="error")
                return redirect(url_for('create_workout'))

            exerciseset = ExerciseSet(
                workout_id=workout.id,
                exercise_id=int(exercise_id),
                reps=rep,
                sets=set_count
            )
            db.session.add(exerciseset)

        db.session.commit()

        flash("Workout Added!", category="success")
        return redirect(url_for('all_workouts'))

    return render_template('create_workout.html', exercises=exercises)


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
    

@app.route('/workouts/<int:workout_id>/favorite', methods=['POST'])
@login_required
def favorite_workout(workout_id):
    workout = Workout.query.get(workout_id)
    
    if request.form.get('_method') == 'DELETE':
        current_user.favorite_workouts.remove(workout)
        db.session.commit()
        flash("Workout unfavored successfully", category="warning")
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
    
    
    # print(current_user.created_workouts)  # Debug print statement
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




@app.route("/workouts/<int:workout_id>", methods=["GET", "POST"])
@login_required
def workout(workout_id):
    workout = Workout.query.filter_by(id=workout_id).first()
    
    if workout is None:
        flash("Workout not found!", category="danger")
        return redirect(url_for('all_workouts'))
    
    exercise_sets = ExerciseSet.query.filter_by(workout_id=workout.id).all()
    
    # print("Exercise Sets:", exercise_sets)  # debug if exercise_sets contains data
    
    workout.exercisesets = exercise_sets
    
    # print("Workout:", workout)  # debug if workout object is correctly fetched
    
    return render_template('workout.html', workout=workout)


@app.route("/workouts/<int:workout_id>/edit", methods=["GET","POST"])
@login_required
def edit_workout(workout_id):
    workout = Workout.query.get(workout_id)
    exercises = Exerciselist.query.filter(
        (Exerciselist.creator_id == None) | (Exerciselist.creator_id == current_user.id)
    ).order_by(Exerciselist.name).all()

    if workout is None or workout.creator != current_user:
        flash("Unauthorized action.", category="danger")
        return redirect(url_for('all_workouts'))

    if request.method == 'POST':
        name = request.form.get('name')
        privacy = request.form.get('privacy')  
        exercise_ids = request.form.getlist('exercise[]')
        new_exercise_names = request.form.getlist('new_exercise[]')
        reps = request.form.getlist('reps[]')
        sets = request.form.getlist('sets[]')
        workout.name = name
        workout.privacy = privacy  
        
        # adding a new exercise 
        for i in range(len(exercise_ids)):
            if exercise_ids[i] == 'other' and new_exercise_names[i].strip():
                new_exercise = Exerciselist(name=new_exercise_names[i].strip(), creator_id=current_user.id)
                db.session.add(new_exercise)
                db.session.flush()  # new exercise has an ID
                exercise_id = new_exercise.id
            else:
                exercise_id = exercise_ids[i]

            if i < len(workout.exercisesets):
                exercise_set = workout.exercisesets[i]
                exercise_set.exercise_id = exercise_id
                exercise_set.reps = reps[i]
                exercise_set.sets = sets[i]
            else:
                exercise_set = ExerciseSet(workout_id=workout.id, exercise_id=exercise_id, reps=reps[i], sets=sets[i])
                workout.exercisesets.append(exercise_set)

        while len(workout.exercisesets) > len(exercise_ids):
            workout.exercisesets.pop()

        db.session.commit()

        flash("Workout updated successfully", category="success")
        return redirect(url_for('all_workouts'))

    return render_template('edit_workout.html', workout=workout, exercises=exercises)




@app.route('/workouts/<int:workout_id>/like', methods=['POST'])
@login_required
def like_workout(workout_id):
    workout = Workout.query.get(workout_id)
    user_reaction = UserReaction.query.filter_by(user_id=current_user.id, workout_id=workout_id).first()
    
    if user_reaction:
        if user_reaction.reaction == 'like':
            # already liked the workout remove the like
            workout.likes -= 1
            db.session.delete(user_reaction)
            db.session.commit()
            flash('You removed your like from this workout.', category='success')
        else:
            #  change to like
            user_reaction.reaction = 'like'
            workout.likes += 1
            workout.dislikes -= 1
            db.session.commit()
            flash('You changed your reaction to like.', category='success')
    else:
        # jsut add a like
        workout.likes += 1
        db.session.add(UserReaction(user_id=current_user.id, workout_id=workout_id, reaction='like'))
        db.session.commit()
        flash('You liked this workout.', category='success')
    
    return redirect(url_for('workout', workout_id=workout_id))

@app.route('/workouts/<int:workout_id>/dislike', methods=['POST'])
@login_required
def dislike_workout(workout_id):
    workout = Workout.query.get(workout_id)
    user_reaction = UserReaction.query.filter_by(user_id=current_user.id, workout_id=workout_id).first()
    
    if user_reaction:
        if user_reaction.reaction == 'dislike':
            # already disliked the workout remove the dislike
            workout.dislikes -= 1
            db.session.delete(user_reaction)
            db.session.commit()
            flash('You removed your dislike from this workout.', category='success')
        else:
            # liked the workout change to dislike
            user_reaction.reaction = 'dislike'
            workout.likes -= 1
            workout.dislikes += 1
            db.session.commit()
            flash('You changed your reaction to dislike.', category='success')
    else:
        # just add a dislike
        workout.dislikes += 1
        db.session.add(UserReaction(user_id=current_user.id, workout_id=workout_id, reaction='dislike'))
        db.session.commit()
        flash('You disliked this workout.', category='success')
    
    return redirect(url_for('workout', workout_id=workout_id))











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


@app.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        height = request.form.get('height')
        weight = request.form.get('weight')
        
       
        if firstname and lastname and height and weight:
            current_user.firstname = firstname
            current_user.lastname = lastname
            current_user.height = height
            current_user.weight = weight
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        else:
            flash('All fields need to be filled', 'danger')
        return redirect(url_for('profile'))
    
    return render_template('myprofile.html')


@app.route('/workout_history', methods=['GET'])
@login_required
def workout_history():
    completed_workouts = CompletedWorkout.query.filter_by(user_id=current_user.id).order_by(CompletedWorkout.date.desc()).all()
    return render_template('workout_history.html', completed_workouts=completed_workouts)



@app.route("/workout_history_add", methods=["GET", "POST"])
@login_required
def add_completed_workout():
    workouts = Workout.query.filter(
        (Workout.creator_id == current_user.id) | 
        (Workout.id.in_([w.id for w in current_user.favorite_workouts]))
    ).all()
    
    selected_workout = None
    exercises = Exerciselist.query.filter(
        (Exerciselist.creator_id == None) | (Exerciselist.creator_id == current_user.id)
    ).order_by(Exerciselist.name).all()
    
    if request.method == "POST":
        workout_id = request.form.get("workout_id")
        selected_workout = Workout.query.get(workout_id)
        
        if not selected_workout:
            flash("Invalid workout selected", "danger")
            return redirect(url_for("add_completed_workout"))

    return render_template("add_completed_workout.html", workouts=workouts, selected_workout=selected_workout, exercises=exercises)




@app.route('/save_completed_workout', methods=['POST'])
@login_required
def save_completed_workout():
    try:
        workout_id = request.form.get('workout_id')
        workout = Workout.query.get(workout_id)

        if not workout:
            flash("Invalid workout selected.", "danger")
            return redirect(url_for('add_completed_workout'))

        total_sets = 0
        exercise_logs = []

        # get the forms data and create CompletedExerciseSet for existing exercises
        for exercise_set in workout.exercisesets:
            if request.form.get(f'delete_exercise_{exercise_set.exercise.id}') == 'true':
                continue

            exercise_id = exercise_set.exercise.id
            weight = request.form.get(f'weight_{exercise_id}')
            sets = request.form.get(f'sets_{exercise_id}')
            reps = request.form.get(f'reps_{exercise_id}')

            if not sets or not reps:
                flash("Please fill out all fields for sets and reps.", "danger")
                return redirect(url_for('add_completed_workout'))

            total_sets += int(sets)
            exercise_logs.append(
                CompletedExerciseSet(
                    exercise_id=exercise_id,
                    weight=weight if weight else None,  #  weight is optional
                    sets=sets,
                    reps=reps
                )
            )

        #  newly added exercises
        for key in request.form:
            if key.startswith('exercise_new_'):
                new_exercise_id = key.split('_')[-1]
                if request.form.get(f'delete_exercise_{new_exercise_id}') == 'true':
                    continue

                exercise_id = request.form.get(f'exercise_new_{new_exercise_id}')
                weight = request.form.get(f'weight_new_{new_exercise_id}')
                sets = request.form.get(f'sets_new_{new_exercise_id}')
                reps = request.form.get(f'reps_new_{new_exercise_id}')

                if not sets or not reps:
                    flash("Please fill out all fields for sets and reps", "danger")
                    return redirect(url_for('add_completed_workout'))

                total_sets += int(sets)
                exercise_logs.append(
                    CompletedExerciseSet(
                        exercise_id=exercise_id,
                        weight=weight if weight else None,  # weight is optoinal
                        sets=sets,
                        reps=reps
                    )
                )

        # new CompletedWorkout 
        completed_workout = CompletedWorkout(
            user_id=current_user.id,
            workout_id=workout_id,
            total_sets=total_sets
        )
        db.session.add(completed_workout)
        db.session.commit() 

        # link each CompletedExerciseSet with the completed_workout
        for log in exercise_logs:
            log.completed_workout_id = completed_workout.id
            db.session.add(log)

        db.session.commit()

        flash("Completed workout saved successfully!", "success")
        return redirect(url_for('workout_history'))

    except Exception as e:
       
        flash("An error occurred while saving the completed workout. Please try again.", "danger")
        return redirect(url_for('add_completed_workout'))


@app.route('/manage_workout_history', methods=['POST'])
@login_required
def manage_workout_history():
    action = request.form.get('action')
    
    try:
        if action == 'delete':
            workout_id = request.form.get('workout_id')
            completed_workout = CompletedWorkout.query.get(workout_id)
            if not completed_workout or completed_workout.user_id != current_user.id:
                flash("Invalid workout selected.", "danger")
                return redirect(url_for('workout_history'))
            
            # delete particular completed workout
            db.session.delete(completed_workout)
            db.session.commit()
            flash("Workout deleted successfully.", "success")
        
        elif action == 'clear':
            # delete all completed workouts 
            CompletedWorkout.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
            flash("Workout history cleared successfully.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash("An error occurred. Please try again.", "danger")

    return redirect(url_for('workout_history'))







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