from flask import Flask, request, render_template, url_for, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import colorama
# Меня зовут Илья я учусь пользоваться GitHub
colorama.init(autoreset=True)

app = Flask(__name__)

# Конфигурация БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///search_work.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'


db = SQLAlchemy(app)


# Создание двух таблиц Рабочие и Отклики нанимателей
class Workers(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    lastname = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50)) 
    salary = db.Column(db.Integer)
    profession = db.Column(db.String(100))
    education = db.Column(db.String(50))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    def __repr__(self) -> str:
        return f'{self.id}'
 
        
class Offers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100))
    time_offer = db.Column(db.DateTime, default=datetime.utcnow)
    
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))
    
    def __repr__(self) -> str:
        return f'{self.id}'


# Главная страница
@app.route('/')
def index():
    return render_template('index.html')


# Форма с заявкой Работника
@app.route('/worker_register', methods=['POST', 'GET'])
def worker_register():
    
    if request.method == 'POST':
        try:
            print(request.form['name'])
            print(request.form['age'])
            print(request.form['profession'])
            print(request.form['gender'])
            print(request.form['education'])
            print(request.form['salary'])

            worker_name_lastname = request.form['name'].split()
            print('get name and lastname')
            
            # проверка коректности ввода данных
            print('test input data')
            if len(worker_name_lastname) != 2:
                flash(message='Неправильно поле "Фамилия Имя"', category='bad')
            

            elif not 0 <= int(request.form['age']) <= 100:
                flash(message='Неправильное поле "Возраст"')


            elif request.form['gender'].lower() not in ['мужской', 'женский']:
                flash(message='Неправильное поле "Пол"')
            

            elif request.form['profession'].lower() not in ['программист', 'менеджер', 'дизайнер', 'администратор', 'сетевой инженер', 'тестировщик']:
                flash(message='Выберете другую проффесию', category='bad')

            
            elif request.form['education'].lower() not in ['школа', 'среднее', 'высшее']:
                flash(message='Неправильное поле "Образование"', category='bad')

            
            else:

                print('pass input data')

                print('start query check')
                worker_exist = Workers.query.filter(
                        Workers.name == worker_name_lastname[0],
                        Workers.lastname == worker_name_lastname[1],
                        Workers.age == request.form['age'],
                        Workers.gender == request.form['gender'],
                        Workers.profession == request.form['profession'],
                        Workers.education == request.form['education']
                        ).first()
                print('end query check')
                print(worker_exist is None)

                
                if worker_exist is None:
                    print('start add worker in database')
                    worker_create = Workers(name=worker_name_lastname[0].lower(), lastname=worker_name_lastname[1].lower(),
                                            age=request.form['age'], gender=request.form['gender'].lower(),
                                            profession=request.form['profession'].lower(), education=request.form['education'].lower(),
                                            salary=request.form['salary'])
                    
                    
                    

                    db.session.add(worker_create)
                    db.session.commit()
                    print('end add worker in database. success')
                    return redirect(url_for('success'))
                else:
                    flash(message='Такой пользователь уже оставлял заявку', category='bad')

    
        except:
            print('database error')
            db.session.rollback()

    return render_template('worker_register.html')


# страница с успешной отправкой
@app.route('/success')
def success():
    return render_template('success.html')


# Старница с формой для Нанимателя
@app.route('/search', methods=['GET', 'POST'])
def search():
    print(colorama.Fore.GREEN + 'search')

    if request.method == 'POST':
        print(colorama.Fore.GREEN + 'search POST method')
        session['searchGender'] = request.form['gender'].lower()
        session['searchAge'] = request.form['age']
        session['searchAgeEnd'] = request.form['age_end']
        session['searchProfession'] = request.form['profession'].lower()
        session['searchEducation'] = request.form['education'].lower()
        session['searchSalary'] = request.form['salary']
        session['searchCompany'] = request.form['company'].lower()
        print(session['searchCompany'])

        return redirect(url_for('search_result'))

    return render_template('search.html')


# страница с результатом
@app.route('/search_result', methods=['GET', 'POST'])
def search_result():
    query_workers = Workers.query.filter(
        Workers.gender == session['searchGender'],
        Workers.age >= session['searchAge'],
        Workers.age <= session['searchAgeEnd'],
        Workers.profession == session['searchProfession'],
        Workers.education == session['searchEducation'],
        Workers.salary <= session['searchSalary']).all()
        

    if request.method == 'POST':
        try:
            print('start add offer')
            print(session['searchCompany'])
            print(request.form['offer_id'])
            offer = Offers(company=session['searchCompany'], worker_id=request.form['offer_id'])
            print('pass add offer')

            db.session.add(offer)
            db.session.commit()
        except:
            print(colorama.Fore.RED + 'offer error')
            db.session.rollback()

    return render_template('search_result.html', workers=query_workers)


if __name__ == '__main__':
    app.run(debug=True)
