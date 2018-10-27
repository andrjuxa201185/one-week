import os
from flask import Flask, redirect, render_template, jsonify, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
# from flask_session import Session
# from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from werkzeug.exceptions import RequestEntityTooLarge
from flask_uploads import UploadSet, IMAGES

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# app.config["SESSION_FILE_DIR"] = mkdtemp()
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

photos = UploadSet('photos', IMAGES)
UPLOAD_FOLDER = 'static/foto/'
LIST_OF_RUBRIC = ['недвижимость','транспорт','работа','отдам_даром','детский_мир','животные','строительство','электроника','услуги']
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
LIMIT_OF_ADS = 12

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

class Register(db.Model):
   id = db.Column('student_id', db.Integer, primary_key = True)
   name = db.Column(db.String(100), nullable=True)
   email = db.Column(db.String(100), unique = True, nullable=False)
   password = db.Column(db.String, unique = True, nullable=False)

class Ads(db.Model):
    ads_id = db.Column('ads_id', db.Integer, primary_key = True)
    header = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(50), nullable = False)
    text = db.Column(db.String(501), nullable = False)
    path = db.Column(db.String(30), nullable = False)
    rubric = db.Column(db.String(20), nullable = False)
    city = db.Column(db.String(20), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    phone = db.Column(db.String(20), nullable = False)
    date = db.Column(db.String(20), nullable = False)

class Bookmark(db.Model):
    id = db.Column('bookmark', db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, nullable = False)
    ads_id = db.Column(db.Integer, nullable = False)

from appl import db
from appl import Register, Ads, Bookmark
db.create_all()

def check_date():
    now = datetime.now()
    ads = Ads.query.all()
    ads_c = Ads.query.count()

    for i in range(ads_c):
        date_ad = datetime.strptime(ads[i].date , '%Y-%m-%d %H:%M:%S')
        delta = now - date_ad

        if delta.days > 6:
            db.session.delete(ads[i])
            db.session.commit()

def isYourAd(ads_id):
    if 'user_id' in session:
        user_id = session['user_id']
        user = Register.query.filter(Register.id == user_id).first()
        if user:
            user_email = user.email

        ad = Ads.query.filter_by(ads_id = ads_id).first()
        if ad:
            if user_email == ad.email:
                return True
        return False

def getBookmarks():
    bm = []

    user_id = session['user_id']
    bookmarks = Bookmark.query.filter_by(user_id = user_id).all()
    count_bookmarks = Bookmark.query.filter_by(user_id = user_id).count()

    for i in range(count_bookmarks):
        ad = Ads.query.filter_by(ads_id = bookmarks[i].ads_id).first()
        if ad:
            bm.append(bookmarks[i].ads_id)
        else:
            bm_to_del = Bookmark.query.filter_by(ads_id = bookmarks[i].ads_id).first()
            db.session.delete(bm_to_del)
            db.session.commit()

    return bm

@app.route("/")
def index():
    check_date()
    count_ads = {}
    count_all = 0

    for i in LIST_OF_RUBRIC:
        c = Ads.query.filter(Ads.rubric == i).count()
        count_all = count_all + c
        count_ads[i] = c

    # if 'user_id' in session:


    return render_template('index.html', count_ads = count_ads, count_all = count_all)

@app.route("/registration", methods = ["GET", "POST"])
def registration():
    if request.method == "GET":
        return render_template("registration.html")
    else:
        session.pop('user_id', None)
        name = request.form.get('name').strip()
        email = request.form.get('email').strip()
        password = request.form.get("password").strip()
        password2 = request.form.get("password2").strip()
        if password != password2:
            return render_template('alert.html', message = 'Пароли не совпадают', clas = 'alert-danger')
        hash_password = generate_password_hash(password)

        if not name or not email or not password:
            return render_template('alert.html', message = 'Заполните все поля', clas = 'alert-danger')
        
        if Register.query.filter_by(email = email).first():
            return render_template('alert.html', message = 'Этот email уже зарегистрирован', clas = 'alert-danger')

        user = Register(name = name, email = email, password = hash_password)

        db.session.add(user)
        db.session.commit()

        row = Register.query.filter_by(email = email).first()
        session['user_id'] = row.id

        return redirect('/')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        session.pop('user_id', None)
        email = request.form.get('email').strip()
        password = request.form.get("password").strip()

        if email == 'admin@com' and password == 'admin':
            return redirect('/admin')

        user = Register.query.filter_by(email = email).first()
        if not user:
            return render_template('alert.html', message = 'Не верный email', clas = 'alert-danger')
        
        if not check_password_hash(user.password, password):
            return render_template('alert.html', message = 'Не верный пароль', clas = 'alert-danger')

        session['user_id'] = user.id
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/add', methods = ['GET', 'POST'])
def add():
    if request.method == 'GET':
        user = None
        if 'user_id' in session:
            user = Register.query.filter_by(id = session['user_id']).first()
        return render_template('add.html', user = user)
    else:
        header = request.form.get('header').strip()
        rubric = request.form.get('rubric')
        email = request.form.get('email').strip()
        text = request.form.get('text').strip()
        city = request.form.get('city')
        price = request.form.get('price')
        phone = request.form.get('phone')
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not header or not rubric or not email or not text or not city or not phone:
            return render_template("alert.html", message = 'Заполните все поля со звездочкой', clas = 'alert-danger')
        if not price:
            price = 0

        count_ads_of_rubric = Ads.query.filter(Ads.email==email).filter(Ads.rubric==rubric).count()
        if count_ads_of_rubric >= LIMIT_OF_ADS:
            return render_template('alert.html', message ='вы достигли лимита в этой рубрике', clas = 'alert-danger')

        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = photos.resolve_conflict(UPLOAD_FOLDER,filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                path = UPLOAD_FOLDER + filename
            else:
                path = 'static/img/nofoto.png'
        else:
            path = 'static/img/nofoto.png'

        
        obj = Ads(header = header.lower(), rubric = rubric, text = text, email = email, city = city, price = price, phone = phone, path = path, date = date)
        db.session.add(obj)

        if not 'user_id' in session:
            if Register.query.filter_by(email = email).first():
                db.session.commit()
                return render_template('alert.html', message = 'Этот email уже зарегистрирован. Объявление добавлено. Войдите в систему', clas = 'alert-secondary')
            password = request.form.get("password").strip()
            if not password:
                return render_template('alert.html', message ='Введите пароль', clas = 'alert-danger')
            hash_password = generate_password_hash(password)
            user = Register(email = email, password = hash_password)
            db.session.add(user)
                
        db.session.commit()
        
        return render_template('alert.html', message = 'Ваше обьявление принято, вскоре оно появится на сайте', clas = 'alert-success')

# @app.errorhandler(413)
# def page_not_found(e):
#     print('erhandlerrrrrr-------')
#     return render_template('alert.html', message='file', clas='alert-danger'),413

@app.route('/show/<param>')
def show(param):
    check_date()
    sort = request.args.get('sort')
    city = request.args.get('city')
    count_ads = {}
    count_all = 0

    for i in LIST_OF_RUBRIC:
        c = Ads.query.filter(Ads.rubric == i).count()
        count_all = count_all + c
        count_ads[i] = c

    if param == 'все_объявления':
        if city != None and city != 'None':
            ads = Ads.query.filter(Ads.city == city).order_by(Ads.date).all()
        else:
            ads = Ads.query.order_by(Ads.date).all()
    else:
        if city != None and city != 'None':
            ads = Ads.query.filter(or_(Ads.rubric == param, Ads.city == param)).filter(Ads.city == city).order_by(Ads.date).all()
        else:
            ads = Ads.query.filter(or_(Ads.rubric == param, Ads.city == param)).order_by(Ads.date).all()

    ads_revers = list(reversed(ads))
    bookmarks = None
    if 'user_id' in session:
        bookmarks = getBookmarks()
        
    if sort == 'old-new':
        return render_template('show.html',ads=ads,param=param,sort=sort,city=city,bookmarks=bookmarks,count_ads=count_ads,count_all=count_all)
    return render_template('show.html',ads=ads_revers,param=param,sort=sort,city=city,bookmarks=bookmarks,count_ads=count_ads,count_all=count_all)
   
@app.route('/show_ad/<param>')
def show_ad(param):
    check_date()
    p = int(param)
    ad = Ads.query.filter(Ads.ads_id == p).first()
    bookmarks = None
    if 'user_id' in session:
        bookmarks = getBookmarks()
    if ad:
        return render_template('show_ad.html', ad = ad, bookmarks = bookmarks)
    else:
        return render_template('alert.html', message = 'не найдено', clas = 'alert-danger')

@app.route('/my_ads')
def my_ads():
    if 'user_id' in session:
        check_date()
        id = session['user_id']
        user = Register.query.filter(Register.id == id).first()
        email = user.email

        ads = Ads.query.filter(Ads.email == email).order_by(Ads.date).all()
        if ads:
            ads_revers = list(reversed(ads))
        else:
            return render_template('alert.html', message = 'у вас пока нет объявлений', clas = 'alert-info')
          
    return render_template('my_ads.html', ads = ads_revers)

@app.route('/update/<id>')
def update_ad(id):
    check_date()
    id_ad = int(id)

    if isYourAd(id_ad):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ad = Ads.query.filter(Ads.ads_id == id_ad).first()
        ad.date = date
        db.session.commit()
    
    return redirect('/my_ads')

@app.route('/delete/<id>')
def delete_ad(id):
    check_date()

    id_ad = int(id)
    if isYourAd(id_ad):
        ad_Ads = Ads.query.filter(Ads.ads_id == id_ad).first()
        ad_Bookmark = Bookmark.query.filter_by(ads_id = id_ad).first()
        db.session.delete(ad_Ads)
        db.session.delete(ad_Bookmark)
        db.session.commit()

    return redirect('/my_ads')

@app.route('/edit/<id>', methods = ['GET', 'POST'])
def edit(id):
    check_date()
    id_ad = int(id)

    if request.method == 'GET':
        if isYourAd(id_ad):
            ad = Ads.query.filter(Ads.ads_id == id_ad).first()
            return render_template('edit.html', ad = ad)
    else:
        if isYourAd(id_ad):
            id_ad = int(id)
            ad = Ads.query.filter(Ads.ads_id == id_ad).first()
            header = request.form.get('header').strip()
            rubric = request.form.get('rubric')
            text = request.form.get('text').strip()
            city = request.form.get('city')
            price = request.form.get('price')
            phone = request.form.get('phone')
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if not header or not rubric or not text or not city or not phone:
                return render_template("alert.html", message = 'Заполните все поля со звездочкой', clas = 'alert-danger')
            if not price:
                price = 0

            count_ads_of_rubric = Ads.query.filter(Ads.rubric == rubric).count()
            if count_ads_of_rubric >= LIMIT_OF_ADS:
                return render_template('alert.html', message = 'вы достигли лимита в этой рубрике', clas = 'alert-danger')

            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = photos.resolve_conflict(UPLOAD_FOLDER,filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    path = UPLOAD_FOLDER + filename
            else:
                path = ad.path

            ad.header = header.lower()
            ad.rubric = rubric
            ad.price = price
            ad.date = date
            ad.city = city
            ad.phone = phone
            ad.text = text
            ad.path = path   
            db.session.commit()

    return redirect('/my_ads')

@app.route('/search')
def search():
    check_date()
    q = "%" + request.args.get("q").lower() + "%"
    ads = Ads.query.filter(Ads.header.like(q)).all()
    ads_count = int(Ads.query.filter(Ads.header.like(q)).count())

    headers =[]
    dic = {}

    for i in range(ads_count):
        dic["header"] = ads[i].header
        headers.append(dic.copy())
        dic.clear()
    if len(headers) >= 10:
        return(headers[0], headers[1],headers[2],headers[3],headers[4],headers[5],headers[6],headers[7],headers[8],headers[9])
    return jsonify(headers)

@app.route('/show_search')
def show_search():
    check_date()
    q = "%" + request.args.get("q") + "%"
    ads = Ads.query.filter(Ads.header.like(q)).all()
    bookmarks = None
    if 'user_id' in session:
        bookmarks = getBookmarks()
    if ads:
        return render_template('show_search.html', ads = ads, bookmarks = bookmarks,header = 'Результаты поиска')
    else:
        return render_template('alert.html', message = 'по вашему запросу ничего не найдено', clas = 'alert-info')

@app.route('/bookmarks')
def bookmarks():
    if 'user_id' in session:
        add_bm = request.args.get('add')
        del_bm = request.args.get('del')
        user_id = session['user_id']
        count_bm = {"count": 0}

        if add_bm:
            add_bm = int(add_bm)
            if_exist = Bookmark.query.filter(Bookmark.user_id == user_id).filter(Bookmark.ads_id == add_bm).first()
            if not if_exist:
                obj = Bookmark(user_id = user_id, ads_id = add_bm)
                db.session.add(obj)
                db.session.commit()

        if del_bm:
            del_bm = int(del_bm)
            row = Bookmark.query.filter_by(ads_id = del_bm).first()
            if row:
                db.session.delete(row)
                db.session.commit()
        getBookmarks()
        count_bm["count"] = Bookmark.query.filter(Bookmark.user_id == user_id).count()
        return jsonify(count_bm)
    return jsonify({})

@app.route('/show_bookmarks')
def show_bookmarks():
    if 'user_id' in session:
        bookmarks = getBookmarks()

        if bookmarks:
            ads_bm = []
            for i in bookmarks:
                ad = Ads.query.filter_by(ads_id = i).first()
                if ad:
                    ads_bm.append(ad)
        else:
            return render_template('alert.html', message = 'у вас пока нет закладок', clas = 'alert-info')
        
        return render_template('show_search.html', ads = ads_bm, bookmarks = bookmarks,header = 'Мои закладки')


# @app.route('/admin_ads')
# def admin_ads():
#     rows_ads = Ads.query.all()
#     return render_template('admin_ads.html', ads = rows_ads)

# @app.route('/admin_users')
# def admin_register():
#     rows_users = Register.query.all()
#     return render_template('admin_register.html', users = rows_users)

@app.route('/admin', methods = ["GET", "POST"])
def a():
    if request.method == 'POST':
        name = request.form.get('email')
        password = request.form.get('password')
        if name == 'andrey@com' and password == '123':
            rows_ads = Ads.query.all()
            return render_template('admin_ads.html', ads = rows_ads)
        else:
            return render_template('alert.html', message = 'error', clas = 'alert-info')
    else:
        return render_template('login_admin.html')



if __name__ == '__main__':
    app.run()