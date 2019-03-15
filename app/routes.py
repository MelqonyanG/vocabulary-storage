from app import app, db
from flask import render_template, flash, redirect, url_for, request, send_file, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, TestForm, AddNewWordsForm
from app.models import User, Word
import os
from  sqlalchemy.sql.expression import func
from flask import jsonify
from werkzeug.utils import secure_filename

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    print(len(current_user.words))
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    form = TestForm()
    if form.validate_on_submit():
        direct = form.direct.data
        sorted_by = form.sort.data
        return redirect(url_for('ask_words', direct=direct, sorted_by=sorted_by))
    return render_template('test.html', title='Test your vocabulary', form=form)

@app.route('/ask_words/<direct>/<sorted_by>', methods=['GET', 'POST'])
@login_required
def ask_words(direct, sorted_by):
    rowId = Word.query.order_by(func.random()).first().id
    rnd_word = Word.query.get(rowId)
    word = rnd_word.english if direct == 'english' else rnd_word.armenian
    return render_template('ask_word.html', title='Test your vocabulary', word=word, direct=direct, sorted_by=sorted_by)

@app.route('/check_word', methods=['POST'])
@login_required
def check_word():
    word = request.form['word'].strip()
    response = request.form['response'].strip()
    direct = request.form['direct'].strip()

    if direct == 'english':
        correct_word = Word.query.filter_by(english=word).first()
        if correct_word is not None:
            correct_word = correct_word.armenian
        else:
            correct_word = ''
    else:
        correct_word = Word.query.filter_by(armenian=word).first()
        if correct_word is not None:
            correct_word = correct_word.english
        else:
            correct_word = ''
    return jsonify({
        'result': correct_word == response
    })

@app.route('/vocabulary', methods=['GET', 'POST'])
@login_required
def vocabulary():
    page = request.args.get('page', 1, type=int)
    words = current_user.words.paginate(page, app.config['WORDS_PER_PAGE'], False)
    next_url = url_for('vocabulary', page=words.next_num) if words.has_next else None
    prev_url = url_for('vocabulary', page=words.prev_num) if words.has_prev else None
    return render_template('vocabulary.html', title='Vocabulary', words=words.items, next_url=next_url, prev_url=prev_url)

@app.route('/all_words')
@login_required
def all_words():
    page = request.args.get('page', 1, type=int)
    words = Word.query.filter_by(private=False).paginate(page, app.config['WORDS_PER_PAGE'], False)
    next_url = url_for('all_words', page=words.next_num) if words.has_next else None
    prev_url = url_for('all_words', page=words.prev_num) if words.has_prev else None
    return render_template('all_words.html', title='Vocabulary', words=words.items, next_url=next_url, prev_url=prev_url)

@app.route('/add_new_words', methods=['GET', 'POST'])
@login_required
def add_new_words():
    form = AddNewWordsForm()
    if form.validate_on_submit():
        word = Word(english=form.english.data, armenian=form.armenian.data, private=form.private.data, user_id=current_user.id)
        db.session.add(word)
        db.session.commit()
        flash('Word is added')
        return redirect(url_for('add_new_words'))
    return render_template('add_new_words.html', title='Add New Words', form=form)

@app.route('/remove_word/<word_id>')
@login_required
def remove_word(word_id):
    word = Word.query.get(word_id)
    db.session.delete(word)
    db.session.commit()
    return redirect(url_for('vocabulary'))

@app.route('/edit_word/<word_id>', methods=['GET', 'POST'])
@login_required
def edit_word(word_id):
    word = Word.query.get(word_id)
    en = word.english
    am = word.armenian
    private = word.private
    form = AddNewWordsForm()
    if form.validate_on_submit():
        word.english = form.english.data
        word.armenian = form.armenian.data
        word.private = form.private.data
        db.session.commit()
        return redirect(url_for('vocabulary'))
    elif request.method == 'GET':
        form.english.data = en
        form.armenian.data = am
        form.private.data = private
    return render_template('add_new_words.html', title='Edit Words', form=form)

@app.route('/download', methods=['GET', 'POST'])
@login_required
def download():
    with open('app/download.txt', 'w') as file:
        words = list(current_user.words)
        for i in words:
            file.write(str(i))
            file.write('\n')
    return send_file('download.txt', as_attachment=True)

@app.route('/upload_file', methods=['POST', 'GET'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_words', filename=filename))
    return render_template('upload_file.html', title='Upload words')

@app.route('/upload_words/<filename>', methods=['POST', 'GET'])
@login_required
def upload_words(filename):
    with open(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) as f:
        for word in f:
            if '*' in word:
                english = word.split('*')[0].strip()
                armenian = word.split('*')[1].strip()
                word_translation = Word(user_id=current_user.id, english=english, armenian=armenian, private=False)
                db.session.add(word_translation)
        db.session.commit()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('vocabulary'))
