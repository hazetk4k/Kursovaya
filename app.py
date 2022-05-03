from flask import Flask

app = Flask(__name__)


@app.route('/')  # отслеживание главной странички
def index():
    return "Hello World"


@app.route('/about')  # отслеживание главной странички
def about():
    return "About page"


if __name__ == "__main__":
    app.run(debug=True)  # дебаг тру для вывода ошибок на страничках сайта
