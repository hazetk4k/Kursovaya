from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "some secret thing3412324"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "some_key_hides_secret"
db = SQLAlchemy(app)
manager = LoginManager(app)


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Товар: {self.title}"


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login', methods=["GET", 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if request.method == 'POST':
        if login and password:
            user = User.query.filter_by(login=login).first()
            if user and check_password_hash(user.password, password):
                login_user(user)

                # next_page = request.args.get('next')

                # return redirect(next_page)
                return redirect(url_for('index'))
            else:
                flash("Логин или пароль введены неверно!", category='error')
        else:
            flash("Не указаны логин и пароль!", category='error')

    return render_template('login.html')


@app.route('/logout', methods=["GET", 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/register', methods=["GET", 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not login or not password or not password2:
            flash("Нужно заполнить все поля!", category='error')
        elif password2 != password:
            flash("Введенные пароли должны быть одинаковыми!", category='error')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route('/')  # отслеживание главной странички
@app.route('/home')
@login_required
def index():
    items = Items.query.order_by(Items.price).all()
    return render_template("index.html", items=items)


@app.route('/about')  # отслеживание главной странички
def about():
    return render_template("about.html")


@app.route('/add_item', methods=['POST', 'GET'])  # отслеживание главной странички
@login_required
def add_item():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        text = request.form['text']
        if title == "" or price == "":
            flash('При добавлении товара не были указаны ключевые элементы!', category='error')
            return render_template("add_item.html")
        item = Items(title=title, price=price, text=text)

        try:
            db.session.add(item)
            db.session.commit()
            flash('Успешно добавлен новый товар!', category='success')
            return render_template("add_item.html")
        except:
            return "При добавлении товара что-то пошло не так..."
    else:
        return render_template("add_item.html")


@app.route('/index/<int:id>/delete')
@login_required
def item_delete(id):
    item = Items.query.get_or_404(id)

    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/home')
    except:
        return "При удалении товара произошла ошибка"


@app.route('/index/<int:id>')
@login_required
def item_detail(id):
    item = Items.query.get(id)
    return render_template("item_detail.html", item=item)


@app.route('/posts')
@login_required
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("posts.html", articles=articles)


@app.route('/posts/<int:id>')
@login_required
def post_detail(id):
    article = Article.query.get(id)
    return render_template("post_detail.html", article=article)


@app.route('/posts/<int:id>/delete')
@login_required
def post_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return "При удалении статьи произошла ошибка"


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])  # отслеживание главной странички
@login_required
def post_update(id):
    article = Article.query.get(id)
    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return "При редактировании статьи произошла ошибка"
    else:
        return render_template("post_update.html", article=article)


@app.route('/create-article', methods=['POST', 'GET'])  # отслеживание главной странички
@login_required
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']
        if title == "" or intro == "" or text == "":
            flash('При добавлении статьи не были указаны ключевые элементы!', category='error')
            return render_template("create-article.html")
        article = Article(title=title, intro=intro, text=text)

        try:
            db.session.add(article)
            db.session.commit()
            flash('Успешно добавлена новыя статья!', category='success')
            return render_template("create-article.html")
        except:
            return "При добавлении статьи произошла ошибка"
    else:
        return render_template("create-article.html")


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response


if __name__ == "__main__":
    app.run(debug=True)  # дебаг тру для вывода ошибок на страничках сайта
