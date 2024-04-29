from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_wtf import CSRFProtect
from DataBase import DataBaseOperations as DB
from SmartyPantsOperations import Operations as OP
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from datetime import timedelta, datetime
import speech_recognition as sr
import json

import pytz

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
            word_dict["status"] = "wrong"
        word_status_list.append(word_dict)
    for word, count in given_word_count.items():
        for _ in range(count):
            word_dict = {"word": word, "status": "missing"}
            word_status_list.append(word_dict)

    correct_count = sum(1 for word_dict in word_status_list if word_dict["status"] == "correct")
    missing_count = sum(1 for word_dict in word_status_list if word_dict["status"] == "missing")
    wrong_count = sum(1 for word_dict in word_status_list if word_dict["status"] == "wrong")
    total_words = correct_count + missing_count + wrong_count

    accuracy = round((correct_count / total_words) * 100, 2)
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
        return redirect(url_for('home'))
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
                session['user'] = True
                session['age'] = OP.calculateAge(record[1])
                return redirect(url_for("home"))
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
            DB.initTime(ID)
            user = User(ID)
            session['user'] = True
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
    time = DB.getTime(current_user.userId)
    mins = []
    for sec in time:
        mins.append(round(sec/ 60, 2))
    script1, div1 = OP.generateTimeGraph(mins)
    scores = DB.getTScores(current_user.userId)
    modifiedScores = [0 if x == -1 else x for x in scores]
    script2, div2 = OP.generateProfileGraph(scores = modifiedScores)
    return render_template("profile.html", record = record, script1 = script1, div1 = div1, script2 = script2, div2 = div2)

@app.route('/learn')
@login_required
def learn():
    records = DB.getLearn()
    scores = DB.getTScores(current_user.userId)
    age = session.get('age')
    return render_template("learn.html", records = records, scores = scores, age = age)

@app.route("/learn/<string:contentName>/<int:contentPos>", methods=['POST', 'GET'])
@login_required
def learnContent(contentName, contentPos):
    if contentPos == -1:
        return redirect(url_for('learn'))
    contentId = request.args.get('id')
    records = DB.getLearnContent(contentId)
    if 0 <= contentPos < len(records):
        lastContent = True if((contentPos + 1) == len(records)) else False
        record = records[contentPos]
        return render_template("contentLearn.html", record=record, contentPos=contentPos, contentId = contentId, contentName = contentName, 
                               lastContent = lastContent)
    elif contentPos == len(records):
        return redirect(url_for("results", contentName = contentName, contentId = contentId))
    else:
        return redirect(url_for('learn'))

@app.route("/results/<string:contentName>")
@login_required
def results(contentName):
    contentId = request.args.get('contentId')
    scores = session.get(contentId)
    if scores == None:
        return redirect(url_for('learn'))
    texts = DB.getContentText(contentId)
    x, y  = [], []
    for text in texts:
        x.append(text[1].split()[0])
    for learnId in texts:
        if str(learnId[0] - 1) not in scores.keys():
            y.append(0)
        else:
            y.append(scores[str(learnId[0] - 1)])
    totalScore = sum(y)
    avgAcc = round(totalScore / len(x), 2)
    script, div = OP.generateGraph(x, y)
    highScore = DB.getHighScore(contentId, current_user.userId)
    return render_template("results.html", script=script, div=div, totalScore = round(totalScore, 2), highScore = highScore,
                           contentName = contentName, contentId = contentId, scores = scores, texts = texts, avgAcc = avgAcc)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        audio_file = request.files['audio']
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise()
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
        overallScore = 0
        if contentId not in session or session[contentId] is None:
            session[contentId] = dict()
        if score == -1:
            score = dict()
        score[contentPos] = max(score.get(contentPos, 0), accuracy)
        session[contentId][contentPos] = max(session[contentId].get(contentPos, 0), accuracy)
        
        for individualScore in session[contentId]:
            totalScore += session[contentId][individualScore]
        for individualScore in score:
            overallScore += score[individualScore]
        maxScore = round(overallScore, 2)
        DB.updateScore(json.dumps(score), maxScore, contentId, current_user.userId)
        return jsonify({'result': result, 'accuracy': accuracy, 'score': round(totalScore, 2)})
    except Exception as e:
        app.logger.error(f'An error occurred: {str(e)}')
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/play')
@login_required
def play():
    return render_template('play.html')

@app.route('/play/<string:game>')
@login_required
def playGame(game):
    return render_template('game/' + game + '.html')

@app.route('/read')
@login_required
def read():
    return render_template('read.html')

@app.route('/read/<string:story>')
@login_required
def readStory(story):
    return render_template('story/' + story + '.html')

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
    session.permanent = True
    session.modified = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    
@app.after_request
def after_request(response):
    utc = pytz.timezone('UTC')
    startTime = session.pop('startTime', None)
    pageName = request.path
    if startTime is not None:
        user_id = session.get('user')
        if user_id is not None:
            endTime = datetime.now(utc)
            if 'learn' in pageName:
                DB.updateTime('learn', (endTime - startTime).total_seconds(), current_user.userId)
            elif 'play' in pageName:
                DB.updateTime('play', (endTime - startTime).total_seconds(), current_user.userId)
            elif 'read' in pageName:
                DB.updateTime('read', (endTime - startTime).total_seconds(), current_user.userId)
        session['startTime'] = datetime.now(utc)
    else:
        session['startTime'] = datetime.now(utc)
    return response

if __name__ == '__main__':
    app.run(debug=True)