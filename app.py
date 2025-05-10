from flask import Flask, redirect, url_for, request, abort
from faker import Faker
import random

app = Flask(__name__)
fake = Faker()

news = []
for _ in range(10):
    news.append({
        'title': fake.word(part_of_speech='adjective') + ' ' + fake.company(),
        'text': fake.text(),
        'img': fake.image_url(),
        'tags': [fake.word(part_of_speech='noun') for el in range(random.randint(1,10))]
    })


@app.route('/')
def index():
    return redirect(url_for('news_get'))


# Read
@app.get('/news', defaults={'news_id': 0})
@app.get('/news/<int:news_id>')
def news_get(news_id):
    if news_id > 0:
        try:
            return news[news_id - 1]
        except IndexError:
            abort(404, "News not found")
    else:
        return news


# Create
@app.post('/news')
def news_post():
    if not all(key in request.form for key in ['title', 'text','img', 'tags']):
        abort(400, "Missing required fields")
    else:
        title = request.form['title']
        text = request.form['text']
        img = request.form['img']
        tags = request.form['tags'].split()
        news.append({
            'title': title,
            'text': text,
            'img': img,
            'tags': tags,
        })
        return news


# Update
@app.patch('/news/<int:news_id>')
def news_patch(news_id):
    try:
        if news_id == 0:
            raise IndexError
        for item in request.form.keys():
            if item in news[news_id - 1].keys():
                news[news_id - 1][item] = request.form[f"{item}"]
            else:
                abort(400, f"Invalid field: {item}")
    except IndexError:
        abort(404, "News not found")
    return news


# Delete
@app.delete('/news/<int:news_id>')
def news_delete(news_id):
    try:
        if news_id == 0:
            raise IndexError
        news.pop(news_id - 1)
    except IndexError:
        abort(404, "News not found")
    return '', 204
