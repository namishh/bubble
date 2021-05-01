from flask import render_template, url_for, flash, redirect, request, abort
from bubble import app, db, bcrypt, mail
from bubble.models import User, Post
from bubble.forms import RegistrationForm, LoginForm, NewPost, ResetPasswordQuery, PasswordUpdate, UpdateProfile
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/your-bubbles')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=current_user)
    posts_arranged = posts.order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    print(posts)
    print(posts_arranged)
    return render_template('home.html', posts_arranged = posts_arranged)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Already Logged In', 'info')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Login Successful. Logged in as {user.username}', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:

            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return render_template('logout.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfile()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated", "success")
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('profile.html',form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = NewPost()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post Created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form,title="Create")

@app.route('/post/view/<int:post_id>')
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    else:
        return render_template('view_post.html', post=post)

@app.route('/post/view/<int:post_id>/update', methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = NewPost()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('view_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend_value='Update Post')

@app.route('/post/view/<int:post_id>/delete', methods=['GET','POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    return render_template('confirm_delete.html', post=post)

@app.route('/post/view/<int:post_id>/deleted')
@login_required
def post_deleted(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "danger")
    return redirect(url_for('home'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_password_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route('/reset/password',  methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordQuery()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to the given email address', 'info')
        return redirect(url_for('login'))
    return render_template('pass_reset_query.html', form=form)

@app.route('/reset/password/<token>',  methods=['GET', 'POST'])
def reset_password_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid/Expired Token', 'warning')
        return redirect(url_for('reset_password'))
    form = PasswordUpdate()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_pass.html', title="Reset Password", form=form)


