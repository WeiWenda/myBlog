# -*- coding: utf-8 -*- 

from flask import Blueprint, render_template, abort,Flask, request, session, g, redirect, url_for,flash,jsonify
from flask_uploads import UploadSet,IMAGES,configure_uploads,UploadNotAllowed
from datetime import datetime
import MySQLdb as mysql
import sys
import os
import bos_related

gallery_related = Blueprint("gallery_related", __name__, template_folder="templates")

@gallery_related.route('/galleryTravel')
def Gallery_Travel():
    return render_template('Gallery/GalleryTravel.html' )

@gallery_related.route('/gallery/List')
def Gallery_List():
    g.cursor.execute('select name,dir_url from album order by album_id')
    entries = [dict(dir_name=row[0], dir_path=row[1]) for row in g.cursor.fetchall()]
    return render_template('Gallery/GalleryList.html',entries=entries)

@gallery_related.route('/gallery/Manage')
def Gallery_Manage():
    if not session.get('logged_in'):
        return render_template("401.html")
    g.cursor.execute('select name,dir_url from album order by album_id')
    entries = [dict(dir_name=row[0], dir_path=row[1]) for row in g.cursor.fetchall()]
    return render_template('Gallery/GalleryManage.html',entries=entries)

@gallery_related.route("/gallery/Manage/CheckExist", methods=['GET','POST'])
def Gallery_CheckExist():
    if request.method == 'POST':
        album_name = request.form.get('new_dirname')
        g.cursor.execute('select count(*) from album where album.name = "%s"'%(album_name))
        exist = g.cursor.fetchone()[0]
        if exist == 0:
            return jsonify(dict(valid=True))
        else:
            return jsonify(dict(valid=False))
    return jsonify(dict(valid=False))

@gallery_related.route("/gallery/Manage/AddDir", methods=['GET','POST'])
def Gallery_AddDir():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method == 'POST':
        new_dirname = request.form.get('new_dirname')
        dir = 'img_travel/'+new_dirname+'/'
        g.cursor.execute('insert into album(name,dir_url) values (%s,%s)',(new_dirname,dir))
        g.db.commit()
    return redirect(url_for('.Gallery_Manage'))

@gallery_related.route('/gallery/Detail')
def Gallery_Detail():
    path = str(request.args.get("looking"))
    g.cursor.execute('select picture_name,picture_url from album,picture where album.album_id = picture.album_id and dir_url = "%s"'%(path))
    photos = [dict(title=row[0], url=row[1]) for row in g.cursor.fetchall()]
    return jsonify(photos)

@gallery_related.route("/gallery/Manage/Detail",methods=['GET','POST'])
def Gallery_ManageDetail():
    path = str(request.args.get("looking"))
    g.cursor.execute('select picture_name,picture_url,picture_size,picture_object from album,picture where album.album_id = picture.album_id and dir_url = "%s"'%(path))
    pictures = g.cursor.fetchall()
    urls = map(lambda item: item[1],pictures)
    configs = map (lambda (index,file): dict(caption=file[0],key=index,extra=dict(key=file[3]),size= int(file[2])),enumerate(pictures))
    ret = dict(urls=urls,configs= configs)
    # ret['photos']=photos
    return jsonify(ret)

@gallery_related.route("/gallery/Manage/Upload", methods=['GET','POST'])
def Gallery_Upload():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method == 'POST':
        # subfolder = "/".join(request.args.get('folder_name').split('/')[1:])
        subfolder = str(request.args.get('folder_name'))
        g.cursor.execute('select album_id from album where dir_url = "%s"'%(subfolder))
        album_id = int(g.cursor.fetchone()[0])
        urls = []
        configs = []
        # g.md_photos.url(filename)也可以，但是返回的是188:5000的地址
        for file in  request.files.getlist('input-pa[]'):
            (url,key,content_length) = bos_related.save(file,folder=subfolder)
            g.cursor.execute('insert into picture(album_id,picture_name,picture_size,picture_url,picture_object) values (%d,"%s",%d,"%s","%s")'%(album_id,file.filename,content_length,url,key))
            urls.append(url)
            configs.append(dict(caption=file.filename,extra=dict(key=key),size=content_length))
        g.db.commit()
        ret = dict(initialPreview=urls,initialPreviewConfig= configs)
        return jsonify(ret)

@gallery_related.route("/gallery/Manage/Delete", methods=['GET','POST'])
def Gallery_Delete():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method == 'POST':
        key = request.form.get('key')
        g.cursor.execute('delete from picture where picture_object = "%s"'%key)
        bos_related.delete(key)
        g.db.commit()
        return '{}'

@gallery_related.route("/gallery/Manage/DelDir", methods=['GET','POST'])
def Gallery_DelDir():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method == 'GET':
        toDel = request.args.get('path')
        bos_related.rmdir(toDel)
        g.cursor.execute('delete from album where dir_url = "%s"'%toDel)
        g.db.commit()
    return redirect(url_for('.Gallery_Manage'))

