# -*- coding: utf8 -*-
import os
from flask import Blueprint, render_template, abort,Flask, request, session, g, redirect, url_for,flash,jsonify,request 
from flask_uploads import UploadSet,IMAGES,configure_uploads
from werkzeug import secure_filename
from datetime import datetime
import MySQLdb as mysql
import sys
from extract_abstract import extract
import shutil
import string

reload(sys)
sys.setdefaultencoding('utf-8')

doc_related = Blueprint("doc_related", __name__, template_folder="templates")

@doc_related.route('/doc/List')
def Doc_List():
    g.cursor.execute("select doc_id,title,substring(abstract,1,150),create_date from doc order by create_date desc")
    Tmpblogs = [dict(doc_id=row[0], title=row[1],abstract=row[2].split('\n'),date=row[3]) for row in g.cursor.fetchall()]
    ret=dict(docs=Tmpblogs)
    return render_template('Doc/DocList.html',entries=ret)

@doc_related.route('/doc/View')
def Doc_View():
    doc_id=request.args.get('doc_id')
    return render_template('Doc/DocView.html',doc_id=doc_id)
    
@doc_related.route('/doc/Add',methods=['POST','GET'])
def Doc_Add():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method=='GET':
        return render_template("Doc/DocAdd.html")
    else:
        doc_title=request.form['doc_title']
        content_md=request.form['editormd-markdown-doc']
        content=request.form['editormd-html-code']
        abstract=extract(content)
        if len(abstract)>500:
            abstract=abstract[:500]
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        g.cursor.execute('insert into doc(title,content,abstract,create_date,author) values (%s,%s,%s,%s,%s)',(doc_title,content_md,abstract,time,"vivid"))
        g.db.commit()
    return redirect(url_for('.Doc_List'))

@doc_related.route('/doc/Edit',methods=['POST','GET'])
def Doc_Edit():
    if not session.get('logged_in'): 
        return render_template("401.html")
    if request.method=='GET':
        doc_id=request.args.get('doc_id')
        return render_template("Doc/DocEdit.html",doc_id=doc_id)
    else:
        doc_title=request.form['doc_title']
        content_md=request.form['editormd-markdown-doc']
        content=request.form['editormd-html-code']
        abstract=extract(content)
        if len(abstract)>500:
            abstract=abstract[:500]
        doc_id =request.form['doc_id']
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        g.cursor.execute('update doc set title = %s,content =%s,abstract=%s,create_date= %s where doc_id =%s ',(doc_title,content_md,abstract,time,doc_id))
        g.db.commit()
    return redirect(url_for('.Doc_List'))

@doc_related.route("/doc/Del", methods=['GET','POST'])
def Doc_Del():
    if not session.get('logged_in'):
        return render_template("401.html")
    doc_ids = list(request.form.get('doc_ids').split(","))
    for doc_id in doc_ids:
        file_path=g.md_photos.config.destination+"/"+doc_id
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        g.cursor.execute('delete from doc where doc_id = %d'% int(doc_id))
    g.db.commit()
    return "删除成功!"

@doc_related.route("/doc/Detail", methods=['GET','POST'])
def Doc_Detail():
    docID = int(request.form.get('doc_id'))
    g.cursor.execute('select title,content,create_date from doc where doc_id = %d'% docID)
    row = g.cursor.fetchone()
    date=row[2].isoformat(" ")
    Content =dict(title=row[0],content=row[1],create_date=date)
    return jsonify(Content)

@doc_related.route("/doc/MardownUpload", methods=['GET','POST'])
def Doc_MardownUpload():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method == 'POST':
        subfolder = request.args.get('doc_id')
        # g.md_photos.url(filename)也可以，但是返回的是188:5000的地址
        filename = g.md_photos.save(request.files['editormd-image-file'],folder=subfolder)
        ret = dict(success=1,message="上传成功！",url='../'+string.replace(g.md_photos.path(filename),'\\','/'))
        return jsonify(ret)
    ret = dict(success=0,message="格式有误！")
    return jsonify(ret)