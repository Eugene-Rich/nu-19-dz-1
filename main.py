from flask import Flask, render_template, request
from api_hh02 import getvkans

from sqlalchemy import Column, Integer, String, DECIMAL, create_engine, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///orm_sqlite.db', echo=True)
Base = declarative_base()

class Region(Base): # Регионы
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f'{self.id}) {self.name}'

class Vacancy(Base): # Вакансии
    __tablename__ = 'vacancy'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f'{self.id}) {self.name}'

class Tseek(Base): # Вакансии
    __tablename__ = 'tseek'
    id = Column(Integer, primary_key=True)
    k_region = Column(Integer, ForeignKey(Region.id))
    k_vacancy = Column(Integer, ForeignKey(Vacancy.id))
    def __init__(self, k_region, k_vacancy):
        self.k_region = k_region
        self.k_vacancy = k_vacancy


class Listvac(Base): # Вакансии
    __tablename__ = 'listvac'
    id = Column(Integer, primary_key=True)
    organiz = Column(String)
    zarplata = Column(DECIMAL)
    idzap = Column(Integer)
    def __init__(self, organiz, zarplata, idzap):
        self.organiz = organiz
        self.zarplata = zarplata
        self.idzap = idzap

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)

@app.route("/")
def index():
   return render_template('index.html')

@app.route('/instrp/')
def instrp():
    return render_template('instrp.html')

@app.route('/ftbl/')
def results():
    return render_template('ftbl.html')


@app.route('/vvod/', methods=['GET', 'POST'])
def vvod():

    if request.method == 'GET':
        return render_template('vvod.html')
    else:

        # Обрабатываем регион
        reg = request.form['region']

        #cursor.execute('SELECT * FROM region WHERE name = ?', (reg,))
        #rezreg = cursor.fetchall()
        #if len(rezreg) == 0: # Добавим в базу регион
        #    cursor.execute('INSERT INTO region (name) VALUES (?)', (reg,))
        #    conn.commit()
        #    cursor.execute('SELECT * FROM region WHERE name = ?', (reg,))
        #    rezreg = cursor.fetchall()
        #k_region = rezreg[0][0]

        kolrezreg = session.query(Region).filter(Region.name == reg).count()
        if kolrezreg == 0:
            session.add(Region(reg))
            session.commit()
        rezreg = session.query(Region).filter(Region.name == reg).first()
        k_region = rezreg.id

        print('k_region=', k_region)

        # Обрабатываем наименование вакансии
        naimvac = request.form['naimvac']

        #cursor.execute('SELECT * FROM vacancy WHERE name = ?', (naimvac,))
        #rezvac = cursor.fetchall()
        #if len(rezvac) == 0: # Добавим в базу наименование вакансии
        #    cursor.execute('INSERT INTO vacancy (name) VALUES (?)', (naimvac,))
        #    conn.commit()
        #    cursor.execute('SELECT * FROM vacancy WHERE name = ?', (naimvac,))
        #    rezvac = cursor.fetchall()
        #k_vacancy = rezvac[0][0]

        kolrezvac = session.query(Vacancy).filter(Vacancy.name == naimvac).count()
        if kolrezvac == 0:
            session.add(Vacancy(naimvac))
            session.commit()
        rezvac = session.query(Vacancy).filter(Vacancy.name == naimvac).first()
        k_vacancy = rezvac.id

        print('k_vacancy=', k_vacancy)

        # Ищем запись в таблице поиска.
        #cursor.execute('SELECT id FROM tseek WHERE k_region = ? and k_vacancy = ?', (k_region, k_vacancy,))
        #rezts = cursor.fetchall()
        #if len(rezts) == 0: # При отсутствии этой записи создаем ее.
        #    cursor.execute('INSERT INTO tseek (k_region, k_vacancy) VALUES (?,? )', (k_region, k_vacancy))
        #    conn.commit()
        #    cursor.execute('SELECT id FROM tseek WHERE k_region = ? and k_vacancy = ?', (k_region, k_vacancy,))
        #    rezts = cursor.fetchall()
        #k_ts = rezts[0][0]

        kolrezts = session.query(Tseek).filter(Tseek.k_region == k_region and Tseek.k_vacancy == k_vacancy).count()
        if kolrezts == 0:
            session.add(Tseek(k_region, k_vacancy))
            session.commit()
        rezts = session.query(Tseek).filter(Tseek.k_region == k_region and Tseek.k_vacancy == k_vacancy).first()
        k_ts = rezts.id

        print('k_ts=', k_ts)

        # Ищем записи в таблице вакансий.
        #cursor.execute('SELECT organiz, zarplata FROM listvac WHERE idzap = ?', (k_ts,))
        #rezlsvc = cursor.fetchall()
        #if len(rezlsvc) == 0: # Не найден такой запрос в нашей базе. Будем запрашивать с hh.
        #    lstvac = getvkans(naimvac, reg)

        kolrezlsvc = session.query(Listvac).filter(Listvac.idzap == k_ts).count()
        if kolrezlsvc == 0:  # Не найден такой запрос в нашей базе. Будем запрашивать с hh.
            lstvac = getvkans(naimvac, reg)
            # Сохраним в нашей базе ответ HH
            for vac in lstvac:
                session.add(Listvac(vac[0], vac[1], k_ts))
                session.commit()

            print('Выполнен запрос к НН')

        else:
            lstvac = []
            rezlsvc = session.query(Listvac).filter(Listvac.idzap == k_ts).all()
            for rz in rezlsvc:
                print(rz)
                stls = [rz.organiz, rz.zarplata]
                lstvac.append(stls)

            print('Выданы данные из нашей базы.')


        return render_template('ftbl.html', msvac = lstvac, reg=reg, naimvac=naimvac)


if __name__ == "__main__":
    app.run(debug=True)