from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from cloudipsp import Api, Checkout

MAX_CONTENT_LENGTH = 1024 * 1200

app = Flask(__name__)
app.secret_key = "some secret thing3412324"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "some_key_hides_secret"
db = SQLAlchemy(app)
manager = LoginManager(app)


class Items(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Товар: {self.title}"


class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.login


class AdminView(AdminIndexView):
    @expose('/admin')
    def admin_page(self):
        return self.render_template('admin/index.html')


admin = Admin(app, name='Страница админа', index_view=AdminView(), template_mode='bootstrap4', url='/admin')
admin.add_view(ModelView(User, db.session, name='Пользователи'))
admin.add_view(ModelView(Items, db.session, name='Товары'))
admin.add_view(ModelView(Article, db.session, name='Статьи'))


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title="Страница не найдена", )


@app.route('/login', methods=["GET", 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if request.method == 'POST':
        if login and password:
            user = User.query.filter_by(login=login).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
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


@app.route('/buy/<int:id>')
def buy_item(id):
    item = Items.query.get(id)

    api = Api(merchant_id=1396424,  # тестовый
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "BYN",
        "amount": str(item.price) + "00"
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/add_item', methods=['POST', 'GET'])
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
    db.create_all()
    app.run(debug=True, port=3434)  # дебаг тру для вывода ошибок на страничках сайта
