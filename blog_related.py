# -*- coding: utf8 -*-

from flask import Blueprint, render_template, abort,Flask, request, session, g, redirect, url_for,flash,jsonify
from flask_uploads import UploadSet,IMAGES,configure_uploads,UploadNotAllowed
from datetime import datetime
import MySQLdb as mysql
import sys
from extract_abstract import extract
import shutil,os
import string
import bos_related

reload(sys)
sys.setdefaultencoding('utf-8')

blog_related = Blueprint("blog_related", __name__, template_folder="templates")

@blog_related.route('/blog/Index')
def Blog_Index():
    cur = g.cursor.execute('select type_desc,count(*) as counts,icon_string,bg_string,type_id from blog,blog_type where blog.type_L = blog_type.type_id and blog_type.type_id < 10 group by type_id order by type_id')
    entries = [dict(type_desc=row[0], counts=row[1],icon_string=row[2],bg_string=row[3],type_id=row[4]) for row in g.cursor.fetchall()]
    return render_template('Blog/BlogIndex.html',entries=entries )

@blog_related.route('/blog/List')
def Blog_List():
    BlogLType=int(request.args.get('type',3))
    ThisSType=int(request.args.get('SType',BlogLType*10+1))
    g.cursor.execute('select distinct(type_id),type_desc from blog_type where type_id between %s and %s',(BlogLType*10,BlogLType*10+9))
    STypes = [dict(type_id=row[0],type_desc=row[1]) for row in g.cursor.fetchall()]
    for SType in STypes:
        g.cursor.execute("select blog_id,title,substring(abstract,1,150),create_date from blog where type_S = %d order by create_date desc" %SType['type_id'])
        Tmpblogs = [dict(blog_id=row[0], title=row[1],abstract=row[2].split('\n'),date=row[3]) for row in g.cursor.fetchall()]
        SType['blogs']=Tmpblogs
    return render_template('Blog/BlogList.html',entries=STypes,SType=ThisSType,LType=BlogLType)

@blog_related.route('/blog/View')    
def Blog_View():
    blog_id=request.args.get('blog_id')
    ThisSType=int(request.args.get('SType',21))
    ThisLType=ThisSType/10
    return render_template('Blog/BlogView.html',blog_id=blog_id,SType=ThisSType,LType=ThisLType)

@blog_related.route('/blog/AddType',methods=['POST','GET'])
def Blog_AddType():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method=='GET':
        cur = g.cursor.execute('select distinct(type_id),type_desc from blog_type where blog_type.type_id < 10 order by type_id')
        entries = [dict(type_id=row[0], type_desc=row[1]) for row in g.cursor.fetchall()]
        return render_template("Blog/BlogAddType.html",entries=entries)
    else:
        isLType = request.form['isLType']
        if isLType == 'yes':
            icon_string =  request.form['icon_string']
            bg_string = request.form['bg_string']
            g.cursor.execute('select max(type_id) from blog_type where type_id < 10')
            maxid=g.cursor.fetchone()[0]
            g.cursor.execute('insert into blog_type(type_id,type_desc,icon_string,bg_string) values (%s,%s,%s,%s)',(maxid+1,request.form['type_desc'],icon_string,bg_string))
            g.db.commit()
        else:
            type_L=int(request.form['type_L'])
            g.cursor.execute('select max(type_id) from blog_type where type_id between %s and %s',(type_L*10,type_L*10+9))
            maxid=g.cursor.fetchone()[0]
            NextId=0
            if maxid is None:
                NextId = type_L*10+1
            else:
                NextId = maxid+1
            g.cursor.execute('insert into blog_type(type_id,type_desc) values (%s,%s)',(NextId,request.form['type_desc']))
            g.db.commit()
    return redirect(url_for('.Blog_Index'))
    
@blog_related.route('/blog/Add',methods=['POST','GET'])
def Blog_Add():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method=='GET':
        blog_title='新的笔记标题'
        type_S= int(request.args.get('SType'))
        type_L= type_S/10
        content= '<p>请输入内容...</p><p><br></p>'
        abstract=extract(content)
        if len(abstract)>500:
            abstract=abstract[:500]
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        g.cursor.execute('insert into blog(title,content,create_date,author,type_L,type_S,abstract) values (%s,%s,%s,%s,%s,%s,%s)',(blog_title,content,time,"vivid",type_L,type_S,abstract))
        g.db.commit()
        g.cursor.execute('select blog_id from blog where create_date = "%s"'%(time))
        blog_id =  g.cursor.fetchone()[0]
        return redirect(url_for('.Blog_Edit',blog_id=blog_id,SType=type_S))
    return redirect(url_for('.Blog_List',SType=type_S))

@blog_related.route('/blog/Edit',methods=['POST','GET'])
def Blog_Edit():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method=='GET':
        g.cursor.execute('select distinct(type_id),type_desc from blog_type where blog_type.type_id < 10 order by type_id')
        LTypes = [dict(type_id=row[0], type_desc=row[1]) for row in g.cursor.fetchall()]
        ThisSType = int(request.args.get('SType'))
        ThisLType = ThisSType/10
        g.cursor.execute('select distinct(type_id),type_desc from blog_type where type_id between %s and %s',(ThisLType*10,ThisLType*10+9))
        STypes = [dict(type_id=row[0],type_desc=row[1]) for row in g.cursor.fetchall()]
        entries = dict(STypes=STypes, LTypes=LTypes,TSType=ThisSType,TLType=ThisLType,blog_id=request.args.get('blog_id'))
        return render_template("Blog/BlogEdit.html",entries=entries)
    else:
        blog_id=request.form['blog_id']
        blog_title=request.form['blog_title']
        type_L=request.form['type_L']
        type_S=request.form['type_S']
        content=request.form['content']
        abstract=extract(content)
        if len(abstract)>500:
            abstract=abstract[:500]
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        g.cursor.execute('update blog set title = %s,content =%s,create_date= %s,type_L=%s,type_S=%s,abstract=%s where blog_id =%s ',(blog_title,content,time,type_L,type_S,abstract,blog_id))
        g.db.commit()
    return redirect(url_for('.Blog_List',type=type_L,Stype=type_S))

@blog_related.route("/blog/Del", methods=['GET','POST'])
def Blog_Del():
    if not session.get('logged_in'):
        return render_template("401.html")
    blog_ids = list(request.form.get('blog_ids').split(","))
    for blog_id in blog_ids:
        file_path=g.ck_photos.config.destination+"/"+blog_id
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        bos_related.rmdir('img_wangeditor/'+blog_id)
        g.cursor.execute('delete from blog where blog_id = %d'% int(blog_id))
    g.db.commit()
    return "删除成功!"

@blog_related.route("/blog/getSType", methods=['GET','POST'])
def Blog_getSType():
    LType = int(request.form.get('LType'))
    g.cursor.execute('select distinct(type_id),type_desc from blog_type where type_id between %s and %s',(LType*10,LType*10+9))
    STypes = [dict(type_id=row[0],type_desc=row[1]) for row in g.cursor.fetchall()]
    return jsonify(dict(STypes=STypes))

@blog_related.route("/blog/Detail", methods=['GET','POST'])
def Blog_Detail():
    BlogID = int(request.form.get('blog_id'))
    g.cursor.execute('select title,content,create_date from blog where blog_id = %d'% BlogID)
    row = g.cursor.fetchone()
    date=row[2].isoformat(" ")
    Content =dict(title=row[0],content=row[1],create_date=date)
    return jsonify(Content)
@blog_related.route("/blog/BosUpload", methods=['GET','POST'])
def Blog_BosUpload():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method == 'POST':
        subfolder = str(request.args.get('blog_id'))
        returnString,key,length = bos_related.save(request.files['upload'],'img_wangeditor/'+subfolder+'/')
        return returnString
@blog_related.route("/blog/CkeditorUpload", methods=['GET','POST'])
def Blog_CkeditorUpload():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method == 'POST':
        subfolder = request.args.get('blog_id')
        returnString=""
        # g.md_photos.url(filename)也可以，但是返回的是188:5000的地址
        try:
            filename = g.ck_photos.save(request.files['upload'],folder=subfolder)
        except UploadNotAllowed:
            returnString += "error|文件格式不正确（必须为.jpg/.jpe/.jpeg/.png/.gif/.svg/.bmp文件）"
            return returnString
        returnString = "../"+string.replace(g.ck_photos.path(filename),'\\','/')
        return returnString