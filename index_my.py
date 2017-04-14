#coding:utf-8
# all the imports
import logging
import logging.config
from bae_log import handlers
import MySQLdb as mysql
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash,jsonify, send_from_directory
from flask_uploads import UploadSet,IMAGES,configure_uploads,patch_request_class
import datetime
import sys
from blog_related import blog_related
from doc_related import doc_related
from gallery_related import gallery_related
from calendar_related import calendar_related

logging.config.fileConfig("logging.conf")
reload(sys)
sys.setdefaultencoding('utf-8')

# configuration
DATABASE = 'YTFHdiMflxHpJTeIfQdw'
DEBUG = True
HOST='sqld.duapp.com'
SECRET_KEY = 'e9fcb9a1fc6e4f0884a9ee67f471b447'
USERNAME = 'a7e801ba0d2b4eb5b446e6a4746cd1bc'
PASSWORD = 'e9fcb9a1fc6e4f0884a9ee67f471b447'
M_USERNAME = 'vivid'
M_PASSWORD = 'root'
PORT=4050
UPLOADED_MDPHOTOS_DEST = 'static/img_md'
UPLOADED_MDPHOTOS_ALLOW = IMAGES
UPLOADED_CKPHOTOS_DEST = 'static/img_ckeditor'
UPLOADED_CKPHOTOS_ALLOW = IMAGES
UPLOADED_TRAVELPHOTOS_DEST = ''
UPLOADED_TRAVELPHOTOS_ALLOW = IMAGES

app = Flask(__name__,static_folder = 'static')
app.config.from_object(__name__)
patch_request_class(app, 32 * 1024 * 1024)
md_photos = UploadSet('mdphotos')
ck_photos = UploadSet('ckphotos')
travel_photos = UploadSet('travelphotos')
configure_uploads(app, (md_photos,ck_photos,travel_photos))


# Register Pages
app.register_blueprint(blog_related)
app.register_blueprint(doc_related)
app.register_blueprint(gallery_related)
app.register_blueprint(calendar_related)
app.secret_key = app.config['SECRET_KEY']

def connect_db():
    return mysql.connect(host=app.config['HOST'],user=app.config['USERNAME'],\
        passwd=app.config['PASSWORD'],db=app.config['DATABASE'],charset='utf8',port=4050)

def get_cursor():
    return g.db.cursor()

@app.before_request
def before_request():
    g.travel_photos = travel_photos
    g.md_photos = md_photos
    g.ck_photos = ck_photos
    g.db = connect_db()
    g.cursor = get_cursor()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
        g.cursor.close()


@app.route('/Video')
def Video():
    return render_template('gotoIFrame.html',entry=dict(url="http://video.1024cloud.com",page_title="影视库"))
@app.route('/OurRecipe')
def OurRecipe():
    return render_template('gotoIFrame.html',entry=dict(url="http://58.206.124.13/",page_title="九楼的秘籍"))
@app.route('/OurTpin')
def OurTpin():
    return render_template('gotoIFrame.html',entry=dict(url="http://tpin.1024cloud.com/TPIN/tpin/pages/lyglwl.html",page_title="TPIN Demo"))
@app.route('/MyFtp')
def MyFtp():
    return render_template('gotoIFrame.html',entry=dict(url="ftp://ftpUser:ftpUser@202.117.16.35",page_title="我的FTP"))

@app.route('/MessageBoard')
def MessageBoard():
    return render_template('MessageBoard.html')

# def add_entry():
#     if not session.get('logged_in'):
#         abort(401)
#     g.cursor.execute('insert into blog (title, content) values (?, ?)',
#                  [request.form['title'], request.form['content']])
#     g.db.commit()
#     flash('New content was successfully posted')
#     return redirect(url_for('show_entries'))

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    g.cursor.execute('SELECT substring(blog.abstract,1,20), blog.blog_id, blog.type_L, blog.type_S, blog.title, bt1.type_desc, bt2.type_desc,blog.create_date FROM blog, blog_type AS bt1, blog_type AS bt2 WHERE blog.type_L = bt1.type_id AND blog.type_S = bt2.type_id ORDER BY blog.create_date DESC LIMIT 0, 2') 
    blogs = [dict(title=row[4],abstract=row[0],typeL=row[2],typeS=row[3],typeLDesc=row[5],typeSDesc=row[6],blog_id=row[1],create_date=row[7]) for row in g.cursor.fetchall()]
    g.cursor.execute('SELECT doc.doc_id, doc.title,substring(doc.abstract,1,20),doc.create_date FROM doc ORDER BY doc.create_date DESC LIMIT 0, 2')
    docs = [dict(title=row[1],abstract=row[2],typeDesc="团队文档",doc_id=row[0],create_date=row[3]) for row in g.cursor.fetchall()]
    return render_template('index.html',blogs=blogs,docs=docs)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.args.get('user') is not None:
        if request.args.get('user') != app.config['M_USERNAME']:
            ret=dict(valid=False)
            return jsonify(ret)
        else:
            ret=dict(valid=True)
            return jsonify(ret) 
    if request.args.get('password') is not None:
        if request.args.get('password') != app.config['M_PASSWORD']:
            ret=dict(valid=False)
            return jsonify(ret)
        else:
            ret=dict(valid=True)
            return jsonify(ret)  
    if request.method=='POST' and request.form.get('user','') == app.config['M_USERNAME'] and request.form.get('password','') == app.config['M_PASSWORD']:
        session['logged_in'] = 'vivid'
        ret=dict(success='true')
        return jsonify(ret)
    else:
        return render_template('login.html')

from bae.core.wsgi import WSGIApplication  
application  = WSGIApplication(app)  
# if __name__ == '__main__':
# 	app.run(host=app.config['HOST'])