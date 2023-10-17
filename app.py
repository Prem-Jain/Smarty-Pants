from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_wtf import CSRFProtect
from DataBase import DataBaseOperations as DB
from SmartyPantsOperations import Operations as OP
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from datetime import timedelta
import speech_recognition as sr
import json

app = Flask(__name__)

app.config.update(
    DEBUG = True,
    SECRET_KEY = 'SmartyPants_P_N_M#801')
csrf = CSRFProtect(app) 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = u"Login to access this page." 

def compare_text(original_text, given_text):
    original_words = original_text.split()
    given_words = given_text.split()
    word_status_list = []
    given_word_count = {}
    for word in given_words:
        given_word_count[word.lower()] = given_word_count.get(word.lower(), 0) + 1
    for original_word in original_words:
        word_dict = {}
        lowercase_original_word = original_word.lower()
        if lowercase_original_word in given_word_count and given_word_count[lowercase_original_word] > 0:
            word_dict["word"] = original_word
            word_dict["status"] = "correct"
            given_word_count[lowercase_original_word] -= 1
        else:
            word_dict["word"] = original_word
            word_dict["status"] = "missing"
        word_status_list.append(word_dict)
    for word, count in given_word_count.items():
        for _ in range(count):
            word_dict = {"word": word, "status": "wrong"}
            word_status_list.append(word_dict)

    correct_count = sum(1 for word_dict in word_status_list if word_dict["status"] == "correct")
    missing_count = sum(1 for word_dict in word_status_list if word_dict["status"] == "missing")
    wrong_count = sum(1 for word_dict in word_status_list if word_dict["status"] == "wrong")
    total_words = correct_count + missing_count + wrong_count

    accuracy = (correct_count / total_words) * 100
    return word_status_list, accuracy

class User(UserMixin):
    def __init__(self, userId):
        self.userId = userId

    def get_id(self):
        return self.userId
    
    def is_active(self):
        return True

@app.route('/', methods=['post', 'get'])
@app.route('/login', methods=['post', 'get'])
def login():
    if current_user.is_active:
        return redirect('/home')
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['pwd']
        exists = DB.checkEmailExists(email)
        if not exists:
            flash("No " + email + " Email exists!")
            return render_template("login.html")
        else:
            record = DB.getUserDetails(email)
            if pwd != record[2]:
                flash("Passwword does not match!")
                return render_template("login.html")
            else:
                user = User(record[0])
                login_user(user)
                session['age'] = OP.calculateAge(record[1])
                return redirect("/home")
    return render_template("login.html")

@app.route('/signup', methods=['post', 'get'])
def signup():
    if current_user.is_active:
        return redirect('/home')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        dob = request.form['dob']
        pwd = request.form['pwd']
        confPwd = request.form['confPwd']
        if pwd != confPwd:
            flash("Password does not match!")
            return render_template("login.html")
        else:
            ID = DB.addUser(name, email, dob, pwd)
            DB.initScores(ID)
            user = User(ID)
            session['age'] = OP.calculateAge(dob)
            login_user(user)
        return redirect("/home")
    return render_template("login.html")

@app.route('/home')
@login_required
def home():
    return render_template("home.html")

@app.route('/profile')
@login_required
def profile():
    record = DB.getUser(current_user.userId)
    return render_template("profile.html", record = record)

@app.route('/learn')
@login_required
def learn():
    records = DB.getLearn()
    return render_template("learn.html", records = records)

@app.route("/learn/<string:contentName>/<int:contentPos>", methods=['POST', 'GET'])
@login_required
def learnContent(contentName, contentPos):
    if contentPos == -1:
        return redirect(url_for('learn'))
    contentId = request.args.get('id')
    records = DB.getLearnContent(contentId)
    if 0 <= contentPos < len(records):
        record = records[contentPos]
        return render_template("contentLearn.html", record=record, contentPos=contentPos, contentId = contentId, contentName = contentName)
    else:
        return redirect(url_for('learn'))

@app.route('/ryhme', methods=['GET', 'POST'])
def rhyme():
    return render_template('ryhme.html', og = "this is a test")

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        audio_file = request.files['audio']
        recognizer = sr.Recognizer()
        audio_data = recognizer.record(audio_file)
        text = recognizer.recognize_google(audio_data)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/compare', methods=['POST'])
def compare():
    try:
        speech_text = request.form.get('text')
        original_text = request.form.get('og')
        contentId = request.form.get('contentId')
        contentPos = request.form.get('contentPos')
        result, accuracy = compare_text(speech_text, original_text)
        score = json.loads(DB.getScore(contentId, current_user.userId))
        totalScore = 0
        if contentId not in session or session[contentId] == None:
            session[contentId] = dict()
        if score == -1:
            score = dict()
            score[contentPos] = accuracy
            session[contentId][contentPos] = accuracy
        else:
            if contentPos in score:
                score[contentPos] = max(score[contentPos], accuracy)
                if contentPos in session[contentId]:
                    session[contentId][contentPos] = max(session[contentId][contentPos], accuracy)
                else:
                    session[contentId][contentPos] = accuracy
            else:
                score[contentPos] = accuracy
            for individualScore in session[contentId]:
                totalScore += session[contentId][individualScore]
        DB.updateScore(json.dumps(score), contentId, current_user.userId)
        return jsonify({'result': result, 'accuracy':accuracy, 'score':totalScore})
    except Exception as e:
        return jsonify({'error': str(e)}), e

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(userId):
    return User(userId)

@app.before_request
def before_request():
    app.permanent_session_lifetime = timedelta(minutes=30)
    session.permanent = True
    session.modified = True

if __name__ == '__main__':
    app.run(debug=True)