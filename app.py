# нав бар изменить
# сделать форму регистрации и логина
# сделать тёмную тему и кнопку для именения языка

import random
import string

import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS, cross_origin
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room, send
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_babel import Babel, gettext


app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
babel = Babel(app)

app.config['LANGUAGES'] = {
    'uk': 'Ukrainian',
    'ru': 'Russian',
    'en': 'English'
}

app.config['SECRET_KEY'] = 'secretic'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'  # Здесь 'en' - это код языка по умолчанию (например, английский).
cors = CORS(app, resources={r"/*": {"origins": "*"}})
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
socketio = SocketIO(app)
api_key = '3ce55d8a27933676dcba27c03414b5f3'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def get_id(self):
        return self.id


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True, nullable=False)
    members = db.Column(db.Integer, default=0)
    is_playing = db.Column(db.Boolean, default=False)
    messages = db.relationship("Message", backref="room", lazy=True)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(200), nullable=False)


login_manager = LoginManager()
login_manager.init_app(app)


@babel.localeselector
def get_locale():
    user_locale = request.accept_languages.best_match(app.config['LANGUAGES'].keys())
    if user_locale is None:
        user_locale = app.config['BABEL_DEFAULT_LOCALE']
    return user_locale


@app.route('/')
def movies():
    page = request.args.get('page', default=1, type=int)
    # Здесь вы можете использовать библиотеку requests, чтобы получить данные с TMDB API
    response = requests.get(f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language={get_locale()}&page={page}&include_adult=false')

    data = response.json()
    # Обработка данных и создание списка фильмов
    movies = []
    for movie_data in data['results']:
        movie = {
            'adult': movie_data['adult'],
            'id': movie_data['id'],
            'title': movie_data['title'],
            'overview': movie_data['overview'],
            'vote_average': movie_data['vote_average'],
            'poster_path': f'https://image.tmdb.org/t/p/w500/{movie_data["poster_path"]}'
        }
        movies.append(movie)

    total_pages = data['total_pages']
    return render_template('index.html', movies=movies, current_page=page, total_pages=total_pages)


@app.route('/tv')
def serials():
    page = request.args.get('page', default=1, type=int)
    # Здесь вы можете использовать библиотеку requests, чтобы получить данные с TMDB API
    response = requests.get(f'https://api.themoviedb.org/3/tv/top_rated?api_key={api_key}&language={get_locale()}&page={page}&include_adult=false')

    data = response.json()
    # Обработка данных и создание списка фильмов
    movies = []
    for movie_data in data['results']:
        movie = {
            'id': movie_data['id'],
            'title': movie_data['name'],
            'overview': movie_data['overview'],
            'vote_average': movie_data['vote_average'],
            'poster_path': f'https://image.tmdb.org/t/p/w500/{movie_data["poster_path"]}'
        }
        movies.append(movie)

    total_pages = data['total_pages']

    return render_template('tv.html', movies=movies, current_page=page, total_pages=total_pages)


@app.route('/<int:genre>/<string:type>')
def with_genres(genre, type_video):

    page = request.args.get('page', default=1, type=int)
    genre = request.args.get('genre', default=genre, type=int)
    if type_video == 'movies':
        response = requests.get(f'https://api.themoviedb.org/3/discover/movie/?&language={get_locale()}&with_genres={genre}&api_key={api_key}&page={page}&include_adult=false')
    else:
        response = requests.get(f'https://api.themoviedb.org/3/discover/tv/?&language={get_locale()}&with_genres={genre}&api_key={api_key}&page={page}&include_adult=false')
    data = response.json()
    total_pages = data['total_pages']

    return render_template('genres.html', movies=data, current_page=page, total_pages=total_pages, genre=genre, type=type_video)


@app.route('/genre')
def genres_list():
    movie_url = requests.get(f"https://api.themoviedb.org/3/genre/movie/list?&language={get_locale()}&api_key={api_key}&include_adult=false")
    tv_url = requests.get(f"https://api.themoviedb.org/3/genre/tv/list?&language={get_locale()}&api_key={api_key}&include_adult=false")

    movie = movie_url.json()

    tv = tv_url.json()


    return render_template('genre.html', movie=movie, tv=tv)


@app.route('/<string:content_type>/<int:movie_id>')
def movie_details(content_type, movie_id):
    url = f'https://api.themoviedb.org/3/{content_type}/{movie_id}?api_key={api_key}&language={get_locale()}&include_adult=false&append_to_response=release_dates'
    response = requests.get(url)
    movie_data = response.json()

    url = f'https://api.themoviedb.org/3/{content_type}/{movie_id}?api_key={api_key}&language=ru-RU&include_adult=false&append_to_response=release_dates'
    response = requests.get(url)
    movie_data_for_name = response.json()

    url = f'https://api.themoviedb.org/3/{content_type}/{movie_id}/videos?api_key={api_key}'
    response = requests.get(url)
    movie_data_for_video = response.json()
    print(movie_data_for_video['results'])
    return render_template('film.html', movie_video=movie_data_for_video['results'][0]['key'], movie_data=movie_data, content_type=content_type, movie_name=movie_data_for_name)


def get_first_two_digits(number):
    return str(number)[:3]


app.jinja_env.filters['get_first_two_digits'] = get_first_two_digits


@app.route('/search', methods=['POST', 'GET'])
def search_movie():
    try:
        if request.method == 'POST':
            query = request.form['query']
        else:
            query = request.args.get('query', '')  # Обратите внимание на 'query' здесь

        page = request.args.get('page', default=1, type=int)

        url = f"https://api.themoviedb.org/3/search/multi?query={query}&include_adult=false&language={get_locale()}&page={page}&include_adult=false"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzY2U1NWQ4YTI3OTMzNjc2ZGNiYTI3YzAzNDE0YjVmMyIsInN1YiI6IjY0ZjFhYTBkZGJiYjQyMDEzYTIzM2ZmMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.pQYaSsFmAFEnrdfJWoaXc5c2t75z_L8OdK38-QQmUQw"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            results = data['results']
            total_pages = data['total_pages']
            print(data)
            return render_template('search.html', results=results, current_page=page, total_pages=total_pages, query=query)  # Передайте параметр query в шаблон
        else:
            return gettext('Error fetching data from TMDb')
    except ConnectionError:
        return gettext('Error fetching data from TMDb')


@cross_origin()
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        if current_user.is_authenticated:
            name = current_user.username
            code = request.form.get("code")
            join = request.form.get("join", False)
            create = request.form.get("create", False)

            if not name:
                return render_template("index.html", error=gettext("Please enter a name."), code=code, name=name)

            if join and not code:
                return render_template("index.html", error=gettext("Please enter a room code."), code=code, name=name)

            room = None
            if create != False:
                room = Room(code=generate_unique_code(8), members=0)
                db.session.add(room)
                db.session.commit()
            elif code:
                room = Room.query.filter_by(code=code).first()

            if room is None:
                return render_template("index.html", error=gettext("Room does not exist."), code=code, name=name)

            session["room"] = room.code
            session["name"] = name
            return redirect(url_for("room", code=room.code))
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")


@app.route("/room/<string:code>")
def room(code):
    room = Room.query.filter_by(code=code).first()
    if room is None:
        return redirect(url_for("home"))

    messages = Message.query.filter_by(room_id=room.id).all()
    return render_template("room.html", code=room.code, messages=messages, room_mem=room.members)


@socketio.on("connect")
def connect(auth):
    room_code = session.get("room")
    name = session.get("name")
    if room_code and name:
        room = Room.query.filter_by(code=room_code).first()
        if room:
            join_room(room_code)
            send({"name": name, "message": "has join to the room"}, to=room_code)
            room.members += 1
            db.session.commit()


@socketio.on("disconnect")
def disconnect():
    room_code = session.get("room")
    name = session.get("name")

    if room_code and name:
        room = Room.query.filter_by(code=room_code).first()

        if room:
            leave_room(room_code)
            room.members -= 1
            db.session.commit()

            if room.members <= 0:
                messages = Message.query.filter_by(room_id=room.id).all()
                db.session.delete(room)
                db.session.commit()

                for message in messages:
                    db.session.delete(message)


@socketio.on("message")
def message(data):
    room_code = session.get("room")
    name = session.get("name")

    if room_code and name:
        room = Room.query.filter_by(code=room_code).first()

        if room:
            content = Message(name=name, content=data["data"], room_id=room.id)
            db.session.add(content)
            db.session.commit()
            send({"name": name, "message": data["data"]}, to=room_code)


@socketio.on('play_video')
def handle_play_video():
    room_code = session.get('room')
    room = Room.query.filter_by(code=room_code).first()

    if room:
        room.is_playing = True
        db.session.commit()
        socketio.emit('play_video', room=room_code)


@socketio.on('pause_video')
def handle_pause_video():
    room_code = session.get('room')
    room = Room.query.filter_by(code=room_code).first()

    if room:
        room.is_playing = False
        db.session.commit()
        socketio.emit('pause_video', room=room_code)


def generate_unique_code(length):
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(length))
    return code


# Страница входа
@app.route('/login')
def login():
    return render_template("login.html")


# код для входа
@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()

    if user:
        stored_hashed_password = user.password
        if bcrypt.check_password_hash(stored_hashed_password, password):
            login_user(user)
            return jsonify({'status': 'success', 'redirect': url_for('index')})
        else:
            return jsonify({'status': 'error', 'message': 'Неверный пароль'})
    else:
        return jsonify({'status': 'error', 'message': 'Пользователь не найден'})


# Ваш серверный код (например, views.py)
@socketio.on('current_time')
def current_time(current_time):
    room_code = session.get('room')
    socketio.emit('current_time', current_time, room=room_code)


# Страница профиля пользователя
@app.route('/profile')
def profile():
    username = ''
    if current_user.is_authenticated:
        # Пользователь залогинен, можно выполнять защищенные действия
        username = current_user.username
    # Далее выполните логику, связанную с профилем пользователя
    return render_template('profile.html', username=username)


@app.route("/remove")
def remove():
    a = current_user.username
    id_user = User.query.filter_by(username=a).first()
    # Проверьте, что пользователь существует
    if id_user:
        # Удалите пользователя
        db.session.delete(id_user)
        db.session.commit()

    return redirect(url_for('index'))


# код для выхода
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Страница регистрации
@app.route('/register')
def register():
    return render_template('register.html')


# код для регистрации
@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')

    # Проверка, существует ли уже пользователь с таким именем
    existing_user = User.query.filter_by(username=username).first()
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    if existing_user:
        return jsonify({'status': 'error', 'message': 'Пользователь с таким именем уже существует'})
    if len(password) < 8:
        return jsonify({'status': 'error', 'message': 'Слишком маленький пароль | минимальная длина 8 символов'})

    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Вы можете выполнить вход пользователя сразу после регистрации, если это необходимо

    return jsonify({'status': 'success', 'redirect': url_for('index')})


@login_manager.user_loader
def load_user(user_id):
    # Загрузка пользователя по его идентификатору (user_id)
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return render_template('index.html', current_user=current_user)


if __name__ == '__main__':
    socketio.run(app, debug=True)

