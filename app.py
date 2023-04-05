import psycopg2
from flask import *
import bcrypt
import datetime
import os



app = Flask(__name__)
app.secret_key = 'secret_key' # задаем секретный ключ для работы с сессиями

  
# регистрация пользователя
@app.route('/registration', methods=['GET', 'POST'])
def registration():

    conn = psycopg2.connect( 
                            host="Ваш хост", # localhost если локально
                            port="Ваш порт", # 5432 локально
                            database="Имя базы данных",
                            user="Имя пользователя в postrgesql",
                            password="Пароль")

    cursor = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        login = request.form['login']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        # хешируем пароль
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        

        # Проверяем, что все поля заполнены
        if not username or not login or not password or not confirm_password:
            return render_template('registration.html', error='Все поля должны быть заполнены')

        # Проверяем, что пароли совпадают
        if password != confirm_password:
            return render_template('registration.html', error='Пароли не совпадают')

        # Добавляем пользователя в базу данных
        try:
            cursor.execute("INSERT INTO Имя_вашей_таблицы (user_name, login, password) VALUES (%s, %s, %s)", (username, login, hashed_password.decode('utf-8')))
            conn.commit()

            cursor.close()
            conn.close()
        except:
            conn.rollback()
            return render_template('registration.html', error='Ошибка при добавлении пользователя в базу данных, обратитесь к разработчикам')

        return render_template('registration.html', message='Регистрация прошла успешно')

    # Отображаем страницу регистрации
    return render_template('registration.html')   


@app.route('/index')  
def index():    
    # проверяем вошел ли пользователь в сессию
    if 'login' in session:
        return render_template("index.html")
    else:
        return redirect(url_for('login'))  


# функция для проверки пользователя в бд, существует ли пользователь с таким login
def check_user(login, password):
    conn = psycopg2.connect( 
                            host="Ваш хост", # localhost если локально
                            port="Ваш порт", # 5432 локально
                            database="Имя базы данных",
                            user="Имя пользователя в postrgesql",
                            password="Пароль")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Имя_вашей_таблицы WHERE login=%s", (login,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8'))    
    return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # получаем данные из формы авторизации
        login = request.form['login']
        password = request.form['password']
        # проверяем, что пользователь с таким логином и паролем существует в базе данных
        if check_user(login, password):
            conn = psycopg2.connect( 
                            host="Ваш хост", # localhost если локально
                            port="Ваш порт", # 5432 локально
                            database="Имя базы данных",
                            user="Имя пользователя в postrgesql",
                            password="Пароль")

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Имя_вашей_таблицы WHERE login=%s", (login,))
            user = cursor.fetchone()
            # сохраняем имя пользователя в сессии
            session['username'] = user[0]
            session['login'] = user[1]

            cursor.close()
            conn.close()
            
            # перенаправляем пользователя на главную страницу
            return render_template('index.html')
        else:
            return render_template('login.html', error='Неверный логин или пароль')

    # показываем форму авторизации
    return render_template('login.html')


@app.route('/logout')
def logout():
    # выход из сессии
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Сохраняем данные из сессии
        audiofile = request.files['audiofile']
        filename = request.form['filename']
        name = request.form['voice']
        login = session.get('login')
        # текущее время
        now = datetime.datetime.now()
        # получаем путь к текущей дериктории
        url = os.getcwd() + '\\'
        # Проверяем, что файл был выбран
        if audiofile:
            # Получаем расширение файла
            ext = audiofile.filename.split('.')[-1]
            # Сохраняем файл под другим именем
            audiofile.save(url + 'static/' + filename + '.' + ext)
             # Получаем ссылку на файл из static
            file_url = url_for('static', filename= filename + '.' + ext)
            
            # проводим нужные изменения над файлом и сохраняем его 
            # .save(url + 'static/' + name + '_' + filename + '.' + ext, format="png")
           
            # Получаем ссылку на файл из static
            new_file_url = url_for('static', filename= name + '_' + filename + '.' + ext)
            
            
            conn = psycopg2.connect( 
                            host="Ваш хост", # localhost если локально
                            port="Ваш порт", # 5432 локально
                            database="Имя базы данных",
                            user="Имя пользователя в postrgesql",
                            password="Пароль")

            cursor = conn.cursor()
            cursor.execute("INSERT INTO Имя_вашей_таблицы (login, name_file, link_orig, link_oz, name_oz, date_time, name) VALUES (%s, %s, %s, %s, %s, %s, %s)", (login, filename, file_url, new_file_url, name+'_'+filename, now, name))
            conn.commit()

            cursor.close()
            conn.close()
            flash('Файл был успешно загружен!')
            return render_template('index.html')
    # Отображаем страницу загрузки файла
    return render_template('index.html')


# удаление строк из таблицы на странице
@app.route('/delete_row', methods=['POST'])
def delete_row():
    # параметры запроса
    row_id = request.json["row_id"]
    conn = psycopg2.connect( 
                            host="Ваш хост", # localhost если локально
                            port="Ваш порт", # 5432 локально
                            database="Имя базы данных",
                            user="Имя пользователя в postrgesql",
                            password="Пароль")

    cur = conn.cursor()
    cur.execute("DELETE FROM Имя_вашей_таблицы WHERE id_audio=%s", (row_id,))
    conn.commit()
    cur.close()
    conn.close()
    return "OK"



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # отображение данных в таблице на странице
    conn = psycopg2.connect( 
                            host="Ваш хост", # localhost если локально
                            port="Ваш порт", # 5432 локально
                            database="Имя базы данных",
                            user="Имя пользователя в postrgesql",
                            password="Пароль")

    context = {}
    cur = conn.cursor()
    cur.execute("SELECT link_orig, link_oz, name, date_time, id_audio FROM Имя_вашей_таблицы")
    rows = cur.fetchall()
    context['rows'] = rows
    return render_template('profile.html', context=context)


if __name__ == '__main__':
    app.run(port=5500, debug=True)
