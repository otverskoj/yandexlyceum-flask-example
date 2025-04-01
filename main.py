import datetime

from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import reqparse, abort, Api, Resource

from data import db_session, news_api, news_resources
from data.users import User
from data.news import News
from forms.news import NewsForm

from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def orm_example():
    user1 = User()
    user1.name = "Пользователь 1"
    user1.about = "биография пользователя 1"
    user1.email = "email1@email.ru"

    user2 = User()
    user2.name = "Пользователь 2"
    user2.about = "биография пользователя 2"
    user2.email = "email2@email.ru"

    user3 = User()
    user3.name = "Пользователь 3"
    user3.about = "биография пользователя 3"
    user3.email = "email3@email.ru"

    db_sess = db_session.create_session()

    db_sess.add(user1)
    db_sess.add(user2)
    db_sess.add(user3)

    db_sess.commit()


    user = db_sess.query(User).filter(User.id == 1).first()
    user.name = "Измененное имя пользователя"
    user.created_date = datetime.datetime.now()
    db_sess.commit()

    db_sess.query(User).filter(User.id >= 3).delete()
    db_sess.commit()

    user = db_sess.query(User).filter(User.id == 2).first()
    db_sess.delete(user)
    db_sess.commit()

    news = News(title="Первая новость", content="Привет блог!",
                user_id=1, is_private=False)
    db_sess.add(news)
    db_sess.commit()

    user = db_sess.query(User).filter(User.id == 1).first()
    news = News(title="Вторая новость", content="Уже вторая запись!",
                user=user, is_private=False)
    db_sess.add(news)
    db_sess.commit()

    user = db_sess.query(User).filter(User.id == 1).first()
    news = News(title="Личная запись", content="Эта запись личная",
                is_private=True)
    user.news.append(news)
    db_sess.commit()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route("/")
def index():
    db_sess = db_session.create_session()

    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)

    return render_template("index.html", news=news)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        if form.password.data != form.password_again.data:
            return render_template(
                'register.html',
                title='Регистрация',
                form=form,
                message="Пароли не совпадают",
            )

        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                'register.html',
                title='Регистрация',
                form=form,
                message="Такой пользователь уже есть",
            )

        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )

        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        return render_template('login.html', message="Неправильный логин или пароль", form=form)

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data

        current_user.news.append(news)

        db_sess.merge(current_user)
        db_sess.commit()

        return redirect('/')

    return render_template('news.html', title='Добавление новости', form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()

        news = (
            db_sess
            .query(News)
            .filter(News.id == id, News.user == current_user)
            .first()
        )

        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        news = (
            db_sess
            .query(News)
            .filter(News.id == id, News.user == current_user)
            .first()
        )

        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)

    return render_template('news.html', title='Редактирование новости', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()

    news = (
        db_sess
        .query(News)
        .filter(News.id == id, News.user == current_user)
        .first()
    )

    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)

    return redirect('/')


def main():
    db_session.global_init("db/blogs.db")

    # orm_example()

    app.register_blueprint(news_api.blueprint)

    api.add_resource(news_resources.NewsListResource, '/api/v2/news')
    api.add_resource(news_resources.NewsResource, '/api/v2/news/<int:news_id>')

    app.run()


if __name__ == '__main__':
    main()
