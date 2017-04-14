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

reload(sys)
sys.setdefaultencoding('utf-8')

calendar_related = Blueprint("calendar_related", __name__, template_folder="templates")

@calendar_related.route('/calendar/index')
def Calendar_Index():
    if request.method=='GET':
        g.cursor.execute('select event_id,title,start,backgroundColor,borderColor,long_term from event where end is null or long_term = true order by long_term,start')
        entries = [dict(id=row[0], title=row[1],start=row[2].isoformat(" "),backgroundColor=row[3],borderColor=row[4],long_term=row[5]) for row in g.cursor.fetchall()]
        return render_template('Calendar/CalendarIndex.html',entries=entries)

    
@calendar_related.route('/calendar/Add',methods=['POST','GET'])
def Calendar_Add():
    if not session.get('logged_in'):
        return jsonify(dict(status="1"))
    if request.method == 'POST':
        bg_color=request.form['backgroundColor']
        bd_color=request.form['borderColor']
        title=request.form['title']
        long_term = request.form.get('long_term','false')
        allDay = request.form.get('allDay','true')
        start = request.form.get("start",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        end = request.form.get("end")
        g.cursor.execute('insert into event(title,start,end,allDay,long_term,backgroundColor,borderColor) values (%s,%s,%s,%s,%s,%s,%s)',(title,start,end,allDay,long_term,bg_color,bd_color))
        g.db.commit()
        g.cursor.execute('select max(event_id) from event')
        return jsonify(dict(status="0",newid=g.cursor.fetchone()[0]))
    return jsonify(dict(status="1"))

@calendar_related.route('/calendar/getEvent',methods=['GET'])
def Calendar_GetEvent():
    if request.method=='GET':
        start = request.args.get('start')
        end = request.args.get('end')
        g.cursor.execute('select event_id,title,allDay,start,end,backgroundColor,borderColor from event where end is not null and start between %s and %s',(start,end))
        ret = [dict(id=row[0], title=row[1],start=row[3].isoformat(" "),end=row[4].isoformat(" "),allDay=(row[2] == 'true'),backgroundColor=row[5],borderColor=row[6]) for row in g.cursor.fetchall()]
        return jsonify(ret)
    return redirect(url_for ('.Calendar_Index'))

@calendar_related.route('/calendar/Edit',methods=['POST','GET'])
def Calendar_Edit():
    if not session.get('logged_in'):
        return jsonify(dict(status="1"))
    if request.method == 'POST':
        if request.form.get('longTerm') == 'false':
            event_id=request.form['id']
            end=request.form['end']
            allDay=request.form['allDay']
            g.cursor.execute('update event set end= %s ,allDay=%s where event_id =%s',(end,allDay,event_id))
            g.db.commit()
            return jsonify(dict(status="0"))
        elif request.form.get('longTerm') == 'true':
            bg_color=request.form['backgroundColor']
            bd_color=request.form['borderColor']
            title=request.form['title']
            long_term = 'false'
            allDay = request.form['allDay']
            start = request.form['start']
            end = request.form['end']
            g.cursor.execute('insert into event(title,start,end,allDay,long_term,backgroundColor,borderColor) values (%s,%s,%s,%s,%s,%s,%s)',(title,start,end,allDay,long_term,bg_color,bd_color))
            g.db.commit()
            return jsonify(dict(status="0"))
    return jsonify(dict(status="1"))

@calendar_related.route('/calendar/eventDropOrResize',methods=['POST','GET'])
def Calendar_EventDropOrResize():
    if not session.get('logged_in'):
        return jsonify(dict(status="1"))
    if request.method == 'POST':
            allDay = request.form['allDay']
            start = request.form['start']
            end = request.form['end']
            event_id = request.form['id']
            g.cursor.execute('update event set start= %s ,end= %s ,allDay=%s where event_id =%s',(start,end,allDay,event_id))
            g.db.commit()
            return jsonify(dict(status="0"))
    return jsonify(dict(status="1"))

@calendar_related.route('/calendar/remove',methods=['POST','GET'])
def Calendar_Remove():
    if not session.get('logged_in'):
        return jsonify(dict(status="1"))
    if request.method == 'POST':
        event_id = request.form['id']
        g.cursor.execute('delete from event where event_id = %d'% int(event_id))
        g.db.commit()
        return jsonify(dict(status="0"))