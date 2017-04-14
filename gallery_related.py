# -*- coding: utf-8 -*- 

from flask import Blueprint, render_template, abort,Flask, request, session, g, redirect, url_for,flash,jsonify
from flask_uploads import UploadSet,IMAGES,configure_uploads,UploadNotAllowed
from datetime import datetime
import MySQLdb as mysql
import sys
import os

gallery_related = Blueprint("gallery_related", __name__, template_folder="templates")

@gallery_related.route('/galleryTravel')
def Gallery_Travel():
    return render_template('Gallery/GalleryTravel.html' )

@gallery_related.route('/gallery/List')
def Gallery_List():
    dirs = os.listdir('static/img_travel')
    entries = [dict(dir_name='My Honey',dir_path='static/img_honey')]
    map(lambda file:entries.append(dict(dir_name=file,dir_path=os.path.join('static/img_travel',file))),dirs)
    return render_template('Gallery/GalleryList.html',entries=entries)

@gallery_related.route('/gallery/Manage')
def Gallery_Manage():
    if not session.get('logged_in'):
        return render_template("401.html")
    dirs = os.listdir('static/img_travel')
    entries = [dict(dir_name='My Honey',dir_path='static/img_honey')]
    map(lambda file:entries.append(dict(dir_name=file,dir_path=os.path.join('static/img_travel',file))),dirs)
    return render_template('Gallery/GalleryManage.html',entries=entries)

@gallery_related.route('/gallery/Detail')
def Gallery_Detail():
    path = str(request.args.get("looking"))
    pictures = os.listdir(path)
    photos = map(lambda file:dict(url=os.path.join("../"+path,file),title=file),pictures)
    # ret['photos']=photos
    return jsonify(photos)

@gallery_related.route("/gallery/Manage/Upload", methods=['GET','POST'])
def Gallery_Upload():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method == 'POST':
        # subfolder = "/".join(request.args.get('folder_name').split('/')[1:])
        subfolder = request.args.get('folder_name')
        urls = []
        configs = []
        # g.md_photos.url(filename)也可以，但是返回的是188:5000的地址
        for file in  request.files.getlist('input-pa[]'):
            filename = g.travel_photos.save(file,folder=subfolder)
            # urlstr= '\'<img src=\''+filename+'\' class=\'file-preview-image\' alt=\'Desert\' title=\'Desert\'>\''
            urlstr= "../"+filename
            urls.append(urlstr)
            configs.append(dict(caption=filename.split('/')[-1],key=len(os.listdir(subfolder))+1,extra=dict(filename=filename),size=os.path.getsize(filename)))
        ret = dict(initialPreview=urls,initialPreviewConfig= configs)
        return jsonify(ret)

@gallery_related.route("/gallery/Manage/Detail",methods=['GET','POST'])
def Gallery_ManageDetail():
    path = str(request.args.get("looking"))
    pictures = os.listdir(path)
    urls = map(lambda file: os.path.join('../'+path,file),pictures)
    configs = map (lambda (index,file): dict (caption=file,key=index,extra=dict(filename=os.path.join(path,file)),size= os.path.getsize(os.path.join(path,file))),enumerate(pictures))
    ret = dict(urls=urls,configs= configs)
    # ret['photos']=photos
    return jsonify(ret)

@gallery_related.route("/gallery/Manage/Delete", methods=['GET','POST'])
def Gallery_Delete():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method == 'POST':
        filename = request.form.get('filename')
        os.remove(filename)
        return '{}'

@gallery_related.route("/gallery/Manage/DelDir", methods=['GET','POST'])
def Gallery_DelDir():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method == 'GET':
        toDel = request.args.get('path')
        if (len(os.listdir(toDel)) == 0):
            os.rmdir(toDel)
    return redirect(url_for('.Gallery_Manage'))

@gallery_related.route("/gallery/Manage/CheckExist", methods=['GET','POST'])
def Gallery_CheckExist():
    if request.method == 'POST':
        dir = os.path.join('static/img_travel',request.form.get('new_dirname'))
        if not os.path.isdir(dir):
            return jsonify(dict(valid=True))
        else:
            return jsonify(dict(valid=False))
    return jsonify(dict(valid=False))

@gallery_related.route("/gallery/Manage/AddDir", methods=['GET','POST'])
def Gallery_AddDir():
    if not session.get('logged_in'):
        return render_template("401.html")
    if request.method == 'POST':
        dir = os.path.join('static/img_travel',request.form.get('new_dirname'))
        if not os.path.isdir(dir):
            os.mkdir(dir)
    return redirect(url_for('.Gallery_Manage'))