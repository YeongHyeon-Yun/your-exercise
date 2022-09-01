from ast import arg
from flask import Flask, Response, render_template, request, redirect, session, url_for, flash
from load_db import get_logininfo, get_userinfo, register
import cv2
import numpy as np
import pose_detector
from PIL import ImageFont, ImageDraw, Image
import time
from datetime import datetime
import os
import argparse

app = Flask(__name__)
app.secret_key = 'abcdefghijzlmnopqrstuvwxyz'
video = cv2.VideoCapture(0)

video.set(cv2.CAP_PROP_FRAME_WIDTH, 800) # 가로
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 600) # 세로

i = 0
user = None
today_now = datetime.now().strftime('%Y%m%d_%H%M%S')

@app.route('/')
def main():
    if user == None:
        return render_template('main.html', state='LOGIN')
    else:
        return render_template('main.html', state='LOGOUT')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    user = None
    if request.method == 'POST':
        userid = request.form['ID']
        password = request.form['PW']
        print(userid, password)
        res = get_logininfo(userid, password)
    try:
        if res != ():
            for row in res:
                user_id = row[0]
            if res:
                session['user'] = user_id
                user = session['user']
                return render_template('main.html', state='LOGOUT')
        else:
            flash('아이디나 비밀번호를 확인해주세요')
            return render_template('login.html', state='LOGIN')
    except:
        return render_template('login.html', state='LOGIN')
    return render_template('login.html', state='LOGIN')

@app.route('/side_lunge')
def side_lunge():
    global i
    i = 1
    if user == None:
        return render_template('side_lunge.html', state='LOGIN')
    else:
        return render_template('side_lunge.html', state='LOGOUT')

@app.route('/squat')
def squat():
    global i
    i = 2
    if user == None:
        return render_template('squat.html', state='LOGIN')
    else:
        return render_template('squat.html', state='LOGOUT')

@app.route('/tree')
def tree():
    global i
    i = 3
    if user == None:
        return render_template('tree.html', state='LOGIN')
    else:
        return render_template('tree.html', state='LOGOUT')

def gen(video):
    global i
    cat_list = ['side_lunge', 'squat', 'tree', 'standing', 'nothing']
    capture_on = True
    while True:
        success, image = video.read()
        det = pose_detector.detect(image)
        if det is not None:
            cats = []
            confs = []
            for *xyxy, conf, cls in reversed(det):
                c = int(cls)  # integer class
                cats.append(cat_list[c])
                confs.append(float(conf))
            show_index = np.argmax(confs)
            pose_rate = str(int(confs[show_index]*100))
            if i == 1 and round(confs[show_index],4)*100 >= 95 and cats[show_index] == 'side_lunge':
                dst = cv2.putText(image, cats[show_index] +'  ' + pose_rate + '%', (300, 40), 0, 1, (255, 50, 0), 3, cv2.LINE_AA)
                if capture_on and user != None:
                    cv2.imwrite(f"./static/pose_capture/{user}_{cats[show_index]}_{today_now}" + ".jpg", image)
                    capture_on = False
            elif i == 2 and round(confs[show_index],4)*100 >= 95 and cats[show_index] == 'squat':
                dst = cv2.putText(image, cats[show_index] +'  ' + pose_rate + '%', (300, 40), 0, 1, (255, 50, 0), 3, cv2.LINE_AA)
                if capture_on and user != None:
                    cv2.imwrite(f"./static/pose_capture/{user}_{cats[show_index]}_{today_now}" + ".jpg", image)
                    capture_on = False
            elif i == 3 and round(confs[show_index],4)*100 >= 95 and cats[show_index] == 'tree':
                dst = cv2.putText(image, cats[show_index] +'  ' + pose_rate + '%', (300, 40), 0, 1, (255, 50, 0), 3, cv2.LINE_AA)
                if capture_on and user != None:
                    cv2.imwrite(f"./static/pose_capture/{user}_{cats[show_index]}_{today_now}" + ".jpg", image)
                    capture_on = False
            elif i == 1 and round(confs[show_index],4)*100 >= 90 and cats[show_index] == 'side_lunge':
                dst = cv2.putText(image, cats[show_index] +'  ' + pose_rate + '%', (300, 40), 0, 1, (0, 255, 0), 3, cv2.LINE_AA)
            elif i == 2 and round(confs[show_index],4)*100 >= 90 and cats[show_index] == 'squat':
                dst = cv2.putText(image, cats[show_index] +'  ' + pose_rate + '%', (300, 40), 0, 1, (0, 255, 0), 3, cv2.LINE_AA)
            elif i == 3 and round(confs[show_index],4)*100 >= 90 and cats[show_index] == 'tree':
                dst = cv2.putText(image, cats[show_index] +'  ' + pose_rate + '%', (300, 40), 0, 1, (0, 255, 0), 3, cv2.LINE_AA)
            elif i == 1 and round(confs[show_index],4)*100 < 90 and cats[show_index] == 'side_lunge':
                dst = cv2.putText(image, cats[show_index] +'  ' + pose_rate + '%', (300, 40), 0, 1, (0, 150, 255), 3, cv2.LINE_AA)
            elif i == 2 and round(confs[show_index],4)*100 < 90 and cats[show_index] == 'squat':
                dst = cv2.putText(image, cats[show_index] +'  ' + pose_rate + '%', (300, 40), 0, 1, (0, 150, 255), 3, cv2.LINE_AA)
            elif i == 3 and round(confs[show_index],4)*100 < 90 and cats[show_index] == 'tree':
                dst = cv2.putText(image, cats[show_index] +'  ' + pose_rate + '%', (300, 40), 0, 1, (0, 150, 255), 3, cv2.LINE_AA)
            elif cats[show_index] != 'standing':
                dst = cv2.putText(image, 'Please follow the picture', (300, 40), 0, 1, (0, 0, 255), 3, cv2.LINE_AA)
                capture_on = True
        ret, jpeg = cv2.imencode('.jpg', image)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    global video
    return Response(gen(video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/mypage')
def mypage():
    global user
    root = 'static\pose_capture'
    if user != None:
        for _, _, filenames in os.walk(root):
            for filename in filenames:
                if user in filename:
                    if 'squat' in filename:
                        squat = os.path.join(root, filename)
                    elif 'side_lunge' in filename:
                        side_lunge = os.path.join(root, filename)
                    elif 'tree' in filename:
                        tree = os.path.join(root, filename)
        return render_template('mypage.html', side_lunge_path=side_lunge, squat_path=squat, tree_path=tree, user_name=user, state='LOGOUT')
    else:
        flash('로그인 후 이용해주세요')
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2204, threaded=True, debug=True)