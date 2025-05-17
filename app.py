from flask import Flask, redirect, url_for, request, abort
from sqlalchemy import desc
from dotenv import load_dotenv
from model import db, News, NewsHistory
from flasgger import Swagger
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/news?user=postgres&password=123')
app.config['SWAGGER'] = {
    'title': 'News API',
    'version': '1.0',
    'description': 'Документация для API новостей',
}


swagger = Swagger(app)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    """
    Перенаправляет с корневого URL на /news
    ---
    tags:
      - System
    responses:
      302:
        description: Перенаправление на /news
        headers:
          Location:
            type: string
            description: URL назначения
            example: /news
    """
    return redirect(url_for('news_get'))


# Read
@app.get('/news', defaults={'news_id': -1})
@app.get('/news/<int:news_id>')
def news_get(news_id):
    """
    Получить новости
    ---
    tags:
      - News
    parameters:
      - name: news_id
        in: path
        type: integer
        required: false
        description: ID новости
    responses:
      200:
        description: Новость получена
        schema:
          type: array
          items:
            type: object
            properties:
              title:
                type: string
                example: "Заголовок"
              text:
                type: string
                example: "Текст"
              tags:
                type: array
                items:
                  type: string
                example: ["тег1", "тег2"]
      404:
        description: Новость не найдена
    """
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
    """
    Создать новость
    ---
    tags:
      - News
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              example: "Заголовок"
            text:
              type: string
              example: "Текст"
            tags:
              type: array
              items:
                type: string
              example: ["тег1", "тег2"]
    responses:
      200:
        description: Новость обновлена
      400:
        description: Неверные введённые поля
    """
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
    """
    Обновление новости с сохранением в истории
    ---
    tags:
      - News
    parameters:
      - name: news_id
        in: path
        type: integer
        required: true
        description: ID новости
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              example: "Новый заголовок"
            text:
              type: string
              example: "Обновлённый текст"
            tags:
              type: array
              items:
                type: string
              example: ["тег1", "тег2"]
    responses:
      200:
        description: Новость обновлена
      400:
        description: Неверные поля
      404:
        description: Новость не найдена
    """
    res_json = request.get_json()
    try:
        old_data = db.session.execute(db.select(News).where(News.id == news_id)).all()
        old_news = {
            'title': old_data[0][0].title,
            'text': old_data[0][0].text,
            'img': old_data[0][0].img,
            'tags': old_data[0][0].tags,
        }
        for item in res_json.keys():
            if item in ['title', 'img', 'text', 'tags']:
                # Правильнее было бы сделать это одним запросом и не нагружать базу данных
                data = db.session.query(News).filter(News.id == news_id).update({item: res_json[item]})
                if data == 0:
                    raise IndexError
            else:
                abort(400, f"Invalid field: {item}")
    except IndexError:
        db.session.rollback()
        abort(404, "News not found")
    news_history = NewsHistory(
        news_id=news_id,
        og_data={k:v for (k,v) in zip(res_json.keys(),[old_news[key] for key in res_json.keys()])}
    )
    db.session.add(news_history)
    db.session.commit()
    return {'message': 'Updated'}, 200


@app.patch('/news/<int:news_id>/rollback')
def news_rollback(news_id):
    """
    Откат новости к предыдущей версии из истории
    ---
    tags:
      - News
    parameters:
      - name: news_id
        in: path
        type: integer
        required: true
        description: ID новости
    responses:
      200:
        description: Успешный откат
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Updated"
      404:
        description: Новость или изменения не найдены
    """
    try:
        old_data = db.session.execute(db.select(NewsHistory).where(NewsHistory.news_id == news_id).order_by(desc(NewsHistory.change_date)).limit(1)).all()
        if not old_data:
            raise IndexError
        else:
            db.session.query(News).filter(News.id == news_id).update(old_data[0][0].og_data)
            db.session.commit()
    except IndexError:
        abort(404, "News not found")
    return {'message': 'Updated'}, 200


# Delete
@app.delete('/news/<int:news_id>')
def news_delete(news_id):
    """
    Удалить новость
    ---
    tags:
      - News
    parameters:
      - name: news_id
        in: path
        type: integer
        required: true
        description: ID новости
    responses:
      204:
        description: Новость удалена
      404:
        description: Новость не найдена
    """
    try:
        data = db.session.query(News).filter(News.id == news_id).delete()
        if data == 0:
            raise IndexError
        else:
            db.session.query(NewsHistory).filter(NewsHistory.news_id == news_id).delete()
            db.session.commit()
    except IndexError:
        db.session.rollback()
        abort(404, "News not found")
    return '', 204