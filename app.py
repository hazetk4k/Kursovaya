from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "some_key_hides_secret"
db = SQLAlchemy(app)


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


@app.route('/')  # отслеживание главной странички
@app.route('/home')
def index():
    items = Items.query.order_by(Items.price).all()
    return render_template("index.html", items=items)


@app.route('/about')  # отслеживание главной странички
def about():
    return render_template("about.html")


@app.route('/add_item', methods=['POST', 'GET'])  # отслеживание главной странички
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
def item_delete(id):
    item = Items.query.get_or_404(id)

    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/home')
    except:
        return "При удалении товара произошла ошибка"


@app.route('/index/<int:id>')
def item_detail(id):
    item = Items.query.get(id)
    return render_template("item_detail.html", item=item)


@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("posts.html", articles=articles)


@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get(id)
    return render_template("post_detail.html", article=article)


@app.route('/posts/<int:id>/delete')
def post_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return "При удалении статьи произошла ошибка"


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])  # отслеживание главной странички
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


if __name__ == "__main__":
    app.run(debug=True)  # дебаг тру для вывода ошибок на страничках сайта
