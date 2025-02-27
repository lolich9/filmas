from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sqlite3
import plotly.express as px
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
DB_NAME = 'movies.db'
CSV_FILE = 'movies.csv'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS movies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        genre TEXT,
                        rating REAL,
                        year INTEGER)''')
    conn.commit()
    conn.close()

def load_csv():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        conn = sqlite3.connect(DB_NAME)
        df.to_sql('movies', conn, if_exists='replace', index=False)
        conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM movies", conn)
    conn.close()
    fig = px.histogram(df, x='rating', title='Movie Ratings Distribution')
    graph = fig.to_html(full_html=False)
    return render_template('index.html', graph=graph, movies=df.to_dict(orient='records'))

@app.route('/filter', methods=['GET'])
def filter_movies():
    genre = request.args.get('genre', '')
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM movies WHERE genre=?" if genre else "SELECT * FROM movies"
    df = pd.read_sql_query(query, conn, params=(genre,) if genre else None)
    conn.close()
    fig = px.scatter(df, x='year', y='rating', color='genre', title='Movies by Year and Rating')
    graph = fig.to_html(full_html=False)
    return render_template('index.html', graph=graph, movies=df.to_dict(orient='records'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            df = pd.read_csv(filepath)
            conn = sqlite3.connect(DB_NAME)
            df.to_sql('movies', conn, if_exists='replace', index=False)
            conn.close()
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/top_movies')
def top_movies():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM movies ORDER BY rating DESC LIMIT 10", conn)
    conn.close()
    fig = px.bar(df, x='title', y='rating', title='Top 10 Highest Rated Movies')
    graph = fig.to_html(full_html=False)
    return render_template('top_movies.html', graph=graph, movies=df.to_dict(orient='records'))

if __name__ == '__main__':
    init_db()
    load_csv()
    app.run(debug=True)
