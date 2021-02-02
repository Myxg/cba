import os
import pymysql
import requests
import shutil


db = pymysql.connect('cba-db.hbang.com.cn', 'admin', 'Passw0rd235', 'cba')
cursor = db.cursor()
sql = "select distinct videoid from video_route"
cursor.execute(sql)
result = cursor.fetchall()
db.commit()
db.close()

for i in result:
    db = pymysql.connect('cba-db.hbang.com.cn', 'admin', 'Passw0rd235', 'cba')
    cursor = db.cursor()
    sql = "insert into finish(videoid) values('" + i[0] + "')"
    try:
        cursor.execute(sql)
    except Exception as e:
        pass
    db.commit()
    db.rollback()
    db.close()

db = pymysql.connect('cba-db.hbang.com.cn', 'admin', 'Passw0rd235', 'cba')
cursor = db.cursor()
name_sql = "select * from finish where result is null"
cursor.execute(name_sql)
result = cursor.fetchone()
db.commit()
db.close()
videoid = result[0]

v1 = videoid.split('-')

p1 = '/cbavideo/' + videoid
os.system('mkdir ' + p1)
score_path = '/cbavideo/' + videoid + '/' + v1[0] + '/' + v1[1] + '/' + v1[2] + '/score'
os.system('mkdir ' + score_path)
route_path = '/cbavideo/' + videoid + '/' + v1[0] + '/' + v1[1] + '/' + v1[2] + '/route'
os.system('mkdir ' + route_path)
win_lost_path = '/cbavideo/' + videoid + '/' + v1[0] + '/' + v1[1] + '/' + v1[2] + '/win_lost'
os.system('mkdir ' + win_lost_path)

db = pymysql.connect('video.hbang.com.cn', 'video', 'P@ssw0rd235', 'video')
cursor = db.cursor()
sql = "select Url from form_ShiPin_Report where videoid='" + videoid + "'"
cursor.execute(sql)
result = cursor.fetchone()
db.commit()
db.close()
url = result[0]
res = requests.get(url, stream=True)

video_path = p1 + '/' + videoid + '.mp4'

with open(video_path, 'wb') as f:
    for chunk in res.iter_content(chunk_size=10240):
        f.write(chunk)

img_path = p1 + '/images'
os.system('mkdir ' + img_path)

split_img = 'ffmpeg -i ' + video_path + ' -f image2 -vf fps=24 -qscale:v 2 ' + img_path + '\%07d.jpeg'
os.system(split_img)

db = pymysql.connect('cba-db.hbang.com.cn', 'admin', 'Passw0rd235', 'cba')
cursor = db.cursor()
name_sql = "update finish set result='图片分解完成' where videoid='" + videoid + "'"
cursor.execute(name_sql)
# result = cursor.fetchall()
db.commit()
db.close()

db = pymysql.connect('cba-db.hbang.com.cn', 'admin', 'Passw0rd235', 'cba')
cursor = db.cursor()
name_sql = "select * from video_score where videoid='" + videoid + "'"
cursor.execute(name_sql)
result = cursor.fetchall()
db.commit()
db.close()

for i in result:
    score_tem = p1 + '/score_tem'
    os.system('mkdir ' + score_tem)
    ll = []
    video = score_path + '/' + videoid + '-' + str(i[1]).zfill(7) + '-' + str(i[2]).zfill(7) + '-' + str(i[3]) + '-' +\
            str(i[4]) + '-' + str(i[5]) + '-' + str(i[6]) + '.mp4'
    video1 = win_lost_path + '/' + videoid + '-' + str(i[1]).zfill(7) + '-' + str(i[2]).zfill(7) + '-' + str(i[3]) + '-' + \
            str(i[4]) + '-' + str(i[5]) + '-' + str(i[6]) + '-得分：' + str(i[8]) + '-' + str(i[9]) + '.mp4'
    for j in range(int(i[1]), int(i[2])+1):
        ll.append(j)
    for iframe in ll:
        o_img = img_path + '/' + str(iframe).zfill(7) + '.jpeg'
        n_img = score_tem + '/' + str(ll.index(iframe)).zfill(7) + '.jpeg'
        try:
            shutil.copyfile(o_img, n_img)
        except Exception as e:
            pass
    score_video = 'ffmpeg -f image2 -i ' + score_tem + '/%07d.jpeg -vcodec libx264 -r 24 ' + video
    win_lost_video = 'ffmpeg -f image2 -i ' + score_tem + '/%07d.jpeg -vcodec libx264 -r 24 ' + video1
    os.system(score_video)
    os.system(win_lost_video)
    shutil.rmtree(score_tem)

db = pymysql.connect('cba-db.hbang.com.cn', 'admin', 'Passw0rd235', 'cba')
cursor = db.cursor()
name_sql = "select * from video_route where videoid='" + videoid + "'"
cursor.execute(name_sql)
result = cursor.fetchall()
db.commit()
db.close()

db = pymysql.connect('cba-db.hbang.com.cn', 'admin', 'Passw0rd235', 'cba')
cursor = db.cursor()
name_sql = "update finish set result='score&win_lost处理完成' where videoid='" + videoid + "'"
cursor.execute(name_sql)
# result = cursor.fetchall()
db.commit()
db.close()

for i in result:
    route_tem = p1 + '/route_tem'
    os.system('mkdir ' + route_tem)
    ll = []
    c_frame = int(i[1])
    video = route_path + '/' + videoid + '-' + str(c_frame-72).zfill(7) + '-' + str(c_frame).zfill(7) + '-' +\
            str(c_frame+72).zfill(7) + '-' + i[2] + '-' + i[3] + '-' + i[4] + '-' + i[5] + '-' + i[6] + '.mp4'
    for j in range(c_frame-72, c_frame+73):
        ll.append(j)
    for iframe in ll:
        o_img = img_path + '/' + str(iframe).zfill(7) + '.jpeg'
        n_img = route_tem + '/' + str(ll.index(iframe)).zfill(7) + '.jpeg'
        try:
            shutil.copyfile(o_img, n_img)
        except Exception as e:
            pass
    route_video = 'ffmpeg -f image2 -i ' + route_tem + '/%07d.jpeg -vcodec libx264 -r 24 ' + video
    os.system(route_video)
    shutil.rmtree(route_tem)

os.remove(video_path)
shutil.rmtree(img_path)
score_zip = '/cbavideo/' + videoid + '/' + v1[0] + '/' + v1[1] + '/' + v1[2] + '/score'
shutil.make_archive(score_zip, 'zip', score_path)
route_zip = '/cbavideo/' + videoid + '/' + v1[0] + '/' + v1[1] + '/' + v1[2] + '/route'
shutil.make_archive(route_zip, 'zip', route_path)

upload = 'aws s3 cp ' + '/cbavideo/' + videoid + ' s3://cba.hbang.com.cn --recursive'
os.system(upload)

db = pymysql.connect('cba-db.hbang.com.cn', 'admin', 'Passw0rd235', 'cba')
cursor = db.cursor()
name_sql = "update finish set result='全部处理完成' where videoid='" + videoid + "'"
cursor.execute(name_sql)
# result = cursor.fetchall()
db.commit()
db.close()

shutil.rmtree(p1)



