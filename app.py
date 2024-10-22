from flask import render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import check_password_hash
from init import create_app, redis_client, db, cache
import os
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User, LoginForm, RegistrationForm, Message, MessageService, OnlineStatus
from flask_jwt_extended import JWTManager, create_access_token
from celery_file import send_telegram_notification
from flasgger import Swagger, swag_from


app = create_app()
swagger = Swagger(app)

app.config.from_object('config.Config')
app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Хранение токена в заголовках
jwt = JWTManager(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для просмотра страницы"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.login == form.login.data.strip()).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash("Неверная пара логин и пароль", 'error')

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Вы уже авторизованы', 'warning')
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(login=form.login.data, name=form.name.data, email=form.email.data, telegram_id=form.telegram_id.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Вы успешно зарегистрированы!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация нового пользователя', form=form)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/api/login', methods=['POST'])
@swag_from('swagger_docs/api_login.yml')
def api_login():
    data = request.json
    login = data.get('login')
    password = data.get('password')

    user = db.session.query(User).filter_by(login=login).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Неверный логин или пароль"}), 401


@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')


def notify_offline_users(message, current_id):
    all_users = db.session.query(User).all()
    status = OnlineStatus()
    for user in all_users:
        if user.id != current_id:
            if not status.is_user_online(user.id):
                send_telegram_notification.apply_async(args=[user.telegram_id, message])
        else:
            continue


@app.route('/update_status', methods=['POST'])
@login_required
def update_status():
    status = OnlineStatus()
    status.set_user_online(current_user.id)
    return jsonify(status='success'), 200


@app.route('/ajax_messages', methods=['GET', 'POST'])
async def ajax_request():
    message_service = MessageService(redis_client, cache)
    if request.method == "POST":
        if request.is_json:
            data = request.json
            new_message = Message(text=data['message'], user_id=current_user.id)
            db.session.add(new_message)
            db.session.commit()

            notify_offline_users(new_message.text, current_user.id)

            # Обновляем кэш после добавления нового сообщения
            messages = message_service.get_messages_from_db(current_user)
            message_service.cache_messages(messages)

            return jsonify(status='success'), 200

        # Пробуем получить сообщения из кэша
    cached_messages = message_service.get_cached_messages()

    if cached_messages:
        # Добавляем информацию о текущем пользователе
        formatted_messages = cached_messages
        formatted_messages.insert(0, {
            "user_real_time": current_user.login,
            'id_user_real_time': current_user.id
        })
        return jsonify(messages=formatted_messages), 200

    # Если в кэше нет сообщений, получаем их из базы данных
    messages = message_service.get_messages_from_db(current_user)

    # Кэшируем новые сообщения
    message_service.cache_messages(messages)

    # Добавляем информацию о текущем пользователе
    messages.insert(0, {
        "user_real_time": current_user.login,
        'id_user_real_time': current_user.id
    })

    return jsonify(messages=messages), 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)