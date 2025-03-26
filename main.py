import datetime

from flask import Flask, render_template

from data import db_session
from data.users import User
from data.news import News

from forms.user import RegisterForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


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

    user = db_sess.query(User).first()
    print(user.name)

    for user in db_sess.query(User).all():
        print(user)

    for user in db_sess.query(User).filter(User.id > 1, User.email.notilike("%1%")):
        print(user)

    for user in db_sess.query(User).filter((User.id > 1) | (User.email.notilike("%1%"))):
        print(user)

    user = db_sess.query(User).filter(User.id == 1).first()
    print(user)
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

    for news in user.news:
        print(news)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
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


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
