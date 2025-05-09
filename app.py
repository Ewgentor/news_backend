from flask import Flask, redirect, url_for, request, abort

app = Flask(__name__)

news = [
    {
        'title': "Lorem Ipsum1",
        'text': "",
        'img': "",
        'tags': []
    },
    {
        'title': "Lorem Ipsum2",
        'text': "",
        'img': "",
        'tags': []
    },
    {
        'title': "Lorem Ipsum3",
        'text': "",
        'img': "",
        'tags': []
    },
]


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
            return abort(406, "Error: IndexError")
    else:
        return news


# Create
@app.post('/news')
def news_post():
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
        for item in request.form.keys():
            if item in news[news_id - 1].keys():
                news[news_id - 1][item] = request.form[f"{item}"]
            else:
                return abort(406, "Error: KeyError")
    except IndexError:
        return abort(406, "Error: IndexError")
    return news
