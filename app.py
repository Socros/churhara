import os
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm,LoginForm



app = Flask(__name__)


# from flask import RegistrationForm, LoginForm
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)






SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), index=True, unique=True)
  email = db.Column(db.String(150), unique = True, index = True)
  password_hash = db.Column(db.String(150))
  joined_at = db.Column(db.DateTime(), default = datetime.utcnow, index = True)

  def set_password(self, password):
        self.password_hash = generate_password_hash(password)

  def check_password(self,password):
      return check_password_hash(self.password_hash,password)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

#Take the last tasks from jsron file
def getTodos():
    with open('todos.json', encoding="utf8") as json_file:
        return json.load(json_file)

#Giving at task an id
def getTodo(id):
    todos = getTodos()
    return next(filter(lambda x: x['id'] == int(id), todos))

#Add a task to json file
def addTodo(todo):
    todos = getTodos()
    todos.append(todo)
    with open('todos.json', 'w', encoding="utf8") as json_file:
        return json.dump(todos, json_file, ensure_ascii = False)

#When you create a new task, this, convert your task to a js which is our DB.
def toggleTodo(id):
    todos = getTodos()
    todo = next(filter(lambda x: x['id'] == int(id), todos))
    todo['status'] = abs(todo['status'] - 1)
    with open('todos.json', 'w', encoding="utf8") as json_file:
        return json.dump(todos, json_file, ensure_ascii = False)

#When you delete a task, it delete from json file.
def deleteTodo(id):
    todos = getTodos()
    # todos = list(filter(lambda x: x['id'] != int(id), todos))
    todos = list([x for x in todos if x['id'] != int(id)])
    with open('todos.json', 'w', encoding="utf8") as json_file:
        return json.dump(todos, json_file, ensure_ascii = False)

#When you update task, this, convert your task to a js which is our DB.
def updateTodo(todo_toedit):
    todos = getTodos()
    todo = next(filter(lambda x: x['id'] == int(todo_toedit['id']), todos))
    todo['name'] = todo_toedit['name']
    with open('todos.json', 'w', encoding="utf8") as json_file:
        return json.dump(todos, json_file, ensure_ascii = False)


#app
@app.route('/home', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index2.html')

#This is for complete tasks
@app.route('/toggle/<id>')
def toggle(id):
    toggleTodo(id)
    return redirect(url_for('tasks'))

#Delete a task
@app.route('/delete/<id>')
def delete(id):
    deleteTodo(id)
    return redirect(url_for('tasks'))

#Contact page url
@app.route('/contacts', methods=['GET', 'POST'])
def contact():
    return render_template('contacts.html')

#profile page
@app.route('/profile')
def profile():
    return render_template('profile.html', name=current_user.name)


#task page
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'POST':
        now = datetime.now()
        todo_name = request.form.get('todo_name')
        todoDict = {
            'id': int(datetime.timestamp(now)),
            'name' : todo_name,
            'status': 0,
            'create_at': now.strftime("%d-%m-%Y %H:%M:%S"),
            'deadline': None
        }
        addTodo(todoDict)
    return render_template('tasks.html', todos=getTodos())


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    todo = getTodo(id)
    if request.method == 'POST':
        todo_name = request.form.get('todo_name')
        todo['name'] = todo_name
        updateTodo(todo)
        return redirect(url_for('tasks'))
    return render_template('edit.html', todo=todo)

#######################
@app.route('/register', methods = ['POST','GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username =form.username.data, email = form.email.data)
        user.set_password(form.password1.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registration.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get("next")
            return redirect(next or url_for('/home'))
        flash('Invalid email address or Password.')    
    return render_template('login.html', form=form)


@app.route("/forbidden",methods=['GET', 'POST'])
@login_required
def protected():
    return redirect(url_for('forbidden.html'))

@app.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
