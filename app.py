from flask import Flask, redirect, url_for, request, abort
from sqlalchemy import desc
from dotenv import load_dotenv
from model import db, News
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/news?user=postgres&password=123')

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return redirect(url_for('news_get'))


# Read
@app.get('/news', defaults={'news_id': -1})
@app.get('/news/<int:news_id>')
def news_get(news_id):
    if news_id != -1:
        try:
            data = db.session.execute(db.select(News).where(News.id == news_id)).all()
            news = [{
                'title': row[0].title,
                'text': row[0].text,
                'img': row[0].img,
                'tags': row[0].tags,
            } for row in data]
            if news:
                return news
            else:
                raise IndexError
        except IndexError:
            abort(404, "News not found")
    else:
        data = db.session.execute(db.select(News).order_by(News.id)).all()
        news = [{
            'id': row[0].id,
            'title': row[0].title,
            'text': row[0].text,
            'img': row[0].img,
            'tags': row[0].tags,
        } for row in data]
        return news


# Create
@app.post('/news')
def news_post():
    res_json = request.get_json()
    if not all(key in res_json for key in ['title', 'text','img', 'tags']):
        abort(400, "Missing required fields")
    else:
        title = res_json['title']
        if not title or len(title) > 100:
            abort(400, "Title must be 1-100 characters long")
        text = res_json['text']
        img = res_json['img']
        tags = res_json['tags']
        if not tags:
            abort(400, "Tags must not be empty")

        news = News(
            title=title,
            text=text,
            img=img,
            tags=tags
        )
        db.session.add(news)
        db.session.commit()
        data = db.session.execute(db.select(News).order_by(desc(News.id)).limit(1)).all()
        return {'message': 'Created', 'id': data[0][0].id}, 201


# Update
@app.patch('/news/<int:news_id>')
def news_patch(news_id):
    res_json = request.get_json()
    try:
        for item in res_json.keys():
            if item in ['title', 'img', 'text', 'tags']:
                data = db.session.query(News).filter(News.id == news_id).update({item: res_json[item]})
                if data == 0:
                    db.session.rollback()
                    raise IndexError
                else:
                    db.session.commit()
            else:
                abort(400, f"Invalid field: {item}")
    except IndexError:
        abort(404, "News not found")
    return {'message': 'Updated'}, 200


# Delete
@app.delete('/news/<int:news_id>')
def news_delete(news_id):
    try:
        data = db.session.query(News).filter(News.id == news_id).delete()
        if data == 0:
            db.session.rollback()
            raise IndexError
        else:
            db.session.commit()
    except IndexError:
        db.session.rollback()
        abort(404, "News not found")
    return '', 204