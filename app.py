from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import random
import os
import webbrowser
import threading
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

DATA_FILE = 'quiz_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"folders": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    data = load_data()
    folders = list(data["folders"].keys())
    return render_template('index.html', folders=folders)

@app.route('/create_folder', methods=['POST'])
def create_folder():
    name = request.form['name']
    data = load_data()
    if name and name not in data["folders"]:
        data["folders"][name] = {"quizzes": {}}
        save_data(data)
        flash('Folder created successfully!', 'success')
    else:
        flash('Folder name is empty or already exists.', 'error')
    return redirect(url_for('index'))

@app.route('/delete_folder/<folder_name>')
def delete_folder(folder_name):
    data = load_data()
    if folder_name in data["folders"]:
        del data["folders"][folder_name]
        save_data(data)
        flash('Folder deleted.', 'success')
    return redirect(url_for('index'))

@app.route('/folder/<folder_name>')
def folder(folder_name):
    data = load_data()
    if folder_name not in data["folders"]:
        flash('Folder not found.', 'error')
        return redirect(url_for('index'))
    quizzes = list(data["folders"][folder_name]["quizzes"].keys())
    session['current_folder'] = folder_name
    return render_template('folder.html', folder_name=folder_name, quizzes=quizzes)

@app.route('/create_quiz', methods=['POST'])
def create_quiz():
    name = request.form['name']
    folder_name = session.get('current_folder')
    if not folder_name:
        return redirect(url_for('index'))
    data = load_data()
    if name and name not in data["folders"][folder_name]["quizzes"]:
        data["folders"][folder_name]["quizzes"][name] = []
        save_data(data)
        session['current_quiz'] = name
        return redirect(url_for('add_terms'))
    else:
        flash('Quiz name is empty or already exists.', 'error')
        return redirect(url_for('folder', folder_name=folder_name))

@app.route('/add_terms', methods=['GET', 'POST'])
def add_terms():
    folder_name = session.get('current_folder')
    quiz_name = session.get('current_quiz')
    if not folder_name or not quiz_name:
        return redirect(url_for('index'))
    if request.method == 'POST':
        term = request.form['term']
        definition = request.form['definition']
        if term and definition:
            data = load_data()
            data["folders"][folder_name]["quizzes"][quiz_name].append({"term": term, "def": definition})
            save_data(data)
            flash('Term added.', 'success')
        else:
            flash('Both term and definition are required.', 'error')
    return render_template('add_terms.html', folder_name=folder_name, quiz_name=quiz_name)

@app.route('/finish_adding_terms')
def finish_adding_terms():
    session.pop('current_quiz', None)
    folder_name = session.get('current_folder')
    return redirect(url_for('folder', folder_name=folder_name))

@app.route('/delete_quiz/<quiz_name>')
def delete_quiz(quiz_name):
    folder_name = session.get('current_folder')
    if not folder_name:
        return redirect(url_for('index'))
    data = load_data()
    if quiz_name in data["folders"][folder_name]["quizzes"]:
        del data["folders"][folder_name]["quizzes"][quiz_name]
        save_data(data)
        flash('Quiz deleted.', 'success')
    return redirect(url_for('folder', folder_name=folder_name))

@app.route('/take_quiz/<quiz_name>')
def take_quiz(quiz_name):
    folder_name = session.get('current_folder')
    if not folder_name:
        return redirect(url_for('index'))
    data = load_data()
    if quiz_name not in data["folders"][folder_name]["quizzes"]:
        flash('Quiz not found.', 'error')
        return redirect(url_for('folder', folder_name=folder_name))
    quiz_data = data["folders"][folder_name]["quizzes"][quiz_name]
    if len(quiz_data) < 4:
        flash('Quiz must have at least 4 terms.', 'error')
        return redirect(url_for('folder', folder_name=folder_name))
    questions = []
    for item in quiz_data:
        correct = item["def"]
        wrongs = [i["def"] for i in quiz_data if i != item]
        options = [correct] + random.sample(wrongs, 3)
        random.shuffle(options)
        questions.append({"term": item["term"], "correct": correct, "options": options})
    session['questions'] = questions
    session['current_question'] = 0
    session['score'] = 0
    session['incorrect'] = []
    return redirect(url_for('quiz_question'))

@app.route('/quiz_question', methods=['GET', 'POST'])
def quiz_question():
    questions = session.get('questions')
    current = session.get('current_question', 0)
    if not questions or current >= len(questions):
        return redirect(url_for('quiz_results'))
    q = questions[current]
    if request.method == 'POST':
        selected = request.form.get('option')
        if selected == q["correct"]:
            session['score'] = session.get('score', 0) + 1
        else:
            incorrect = session.get('incorrect', [])
            incorrect.append({"term": q["term"], "correct": q["correct"], "selected": selected})
            session['incorrect'] = incorrect
        session['current_question'] = current + 1
        return redirect(url_for('quiz_question'))
    return render_template('quiz_question.html', question=q, current=current+1, total=len(questions))

@app.route('/quiz_results')
def quiz_results():
    score = session.get('score', 0)
    total = len(session.get('questions', []))
    incorrect = session.get('incorrect', [])
    session.pop('questions', None)
    session.pop('current_question', None)
    session.pop('score', None)
    session.pop('incorrect', None)
    return render_template('quiz_results.html', score=score, total=total, incorrect=incorrect)

def open_browser():
    time.sleep(1)  # Wait for server to start
    try:
        webbrowser.get('chrome').open('http://127.0.0.1:5000/')
    except webbrowser.Error:
        webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(debug=True)