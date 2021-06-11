from wsgiref.simple_server import make_server
from flask import Flask, render_template, request, redirect, url_for
import pymysql
import time

pymysql.install_as_MySQLdb()
app = Flask(__name__)

movies = []
usr_current = []   # 这里保存了当前登录的用户的信息
admin_current = [] # 这里保存了当前登录的管理员信息
cars = []          # 这里保存了所有车辆的信息
car_current = []   # 这里保存了当前处理的车辆的信息
person_log = []    # 这里保存了用户的订单信息
conn = pymysql.Connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='123123',
    db='car',
    charset='utf8')

''' 多个sql语句一起执行的调用函数'''
def split_sql(sql):
    sql_list = sql.split(';')
    return sql_list[0:-1]
def exe_sql(sql, cursor):
    sql_list = split_sql(sql)
    for i in sql_list:
        print(i)
        #cursor.execute(i)


'''
    这是管理员的登录界面
        登录失败就刷新本页面，显示提示框
        登录成功就跳转到 管理员的首页（未实现）
'''
@app.route('/login/', methods=['POST', 'GET'])
def login():
    nm = request.args.get('name')
    pwd = request.args.get('psd')
    global conn
    conn.autocommit(True)
    cursor = conn.cursor()
    sql = "select * from employee where fullname = '%s' and passwd = '%s'" % (nm, pwd)
    cursor.execute(sql)
    results = cursor.fetchall()
    if cursor.rowcount == 0:
        admin_login_sign = 1
        # 弹出密码错误的消息框，提示重新输入
        return render_template('login.html', admin_login_sign=admin_login_sign)
    else:
        admin_current.clear()
        admin_current.append(list(results[0]))
        return home_page()


'''
    跳转到用户登录界面
'''
@app.route('/usr_login_index/')
def usr_log_in_index():
    usr_login_sign = 0
    usr_logup_sign = 0
    return render_template('usr_login.html', usr_login_sign=usr_login_sign, usr_logup_sign=usr_logup_sign)


'''
    跳转到用户注册界面
'''
@app.route('/usr_logup_index/')
def usr_log_up_index():
    usr_fail_logup_sign = 0
    usr_miss_passwd_sign = 0
    return render_template('usr_logup.html', usr_fail_logup_sign=usr_fail_logup_sign, \
                           usr_miss_passwd_sign=usr_miss_passwd_sign)


'''
    用户登录界面
        如果用户名和密码都正确，就跳转到用户信息首页
        如果有错误，就刷新页面
'''
@app.route('/usr_login/', methods=['POST', 'GET'])
def usr_log_in():
    global conn
    conn.autocommit(True)
    usr_name = request.args.get('usr_name')
    usr_pwd = request.args.get('usr_psd')
    return usr_log_in_extra(conn, usr_name, usr_pwd)
def usr_log_in_extra(conn=None, uer_name=None, usr_pwd=None):
    cursor = conn.cursor()
    sql = "select * from person where username = '%s' and passwd = '%s'" % (uer_name, usr_pwd)
    cursor.execute(sql)
    results = cursor.fetchall()
    if len(results) == 0:
        usr_login_sign = 1
        usr_logup_sign = 0
        return render_template('usr_login.html', usr_login_sign=usr_login_sign, usr_logup_sign=usr_logup_sign)
    else:
        # cursor.close()   #做完一个sql语句之后记得执行关闭游标的操作
        usr_current.clear()
        usr_current.append(list(results[0]))
        return usr_home_page()


'''
    用户注册界面
'''
@app.route('/usr_logup/', methods=['POST', 'GET'])
def usr_log_up():
    global conn
    usr_name = request.args.get('usr_name')
    true_name = request.args.get('true_name')
    usr_passwd = request.args.get('usr_passwd')
    usr_confirm_passwd = request.args.get('usr_confirm_passwd')
    conn.autocommit(True)  # 可以使SQL语句对数据库的改变进行随时更新
    cursor = conn.cursor()
    sql = "select * from person where username = '%s' " % usr_name
    cursor.execute(sql)
    if cursor.rowcount != 0:
        #  rowcount()：最近一次执行数据库查询命令后，返回数据的行数
        usr_fail_logup_sign = 1
        usr_miss_passwd_sign = 0
        return render_template('usr_logup.html', \
                               usr_fail_logup_sign=usr_fail_logup_sign, \
                               usr_miss_passwd_sign=usr_miss_passwd_sign)
    elif usr_passwd != usr_confirm_passwd:
        usr_fail_logup_sign = 0
        usr_miss_passwd_sign = 1
        return render_template('usr_logup.html', usr_fail_logup_sign=usr_fail_logup_sign, \
                               usr_miss_passwd_sign=usr_miss_passwd_sign)
    else:
        sql = "select * from person"
        cursor.execute(sql)
        results = cursor.fetchall()
        usr_id = results[-1][0] + 1
        sql = "insert into person values ( %d , '%s' , '%s' , '%s' , 0 , 0 )" % (
        usr_id, true_name, usr_name, usr_passwd)
        cursor.execute(sql)
        sql = "select * from person"
        cursor.execute(sql)
        usr_logup_sign = 1
    usr_login_sign = 0
    return render_template('usr_login.html', usr_login_sign=usr_login_sign, usr_logup_sign=usr_logup_sign)


'''
    用户登录成功的界面（还有要添加的功能）
        1.跳转到个人信息查询与修改
        2.跳转到车辆信息查询，并且实现了下订单的操作
        3.查看我的订单
'''
@app.route('/usr_homepage/')
def usr_home_page():
    return render_template('usr_homepage.html', finish_sign=0)


'''
    管理员登录成功的首页（还没想好做什么）
        1.
'''
@app.route('/homepage/')
def home_page():
    return render_template('admin_homepage.html')


'''
    用户访问：个人信息的显示（与更改）
'''
@app.route('/usr_privateinfo/')
def usr_private_info():
    if usr_current[0][5] == 0:
        (usr_current[0]).append("否")
    else:
        (usr_current[0]).append("是")
    return render_template('usr_private_info.html', usr_info=usr_current[0])


'''
    用户访问：显示车辆信息
'''
@app.route('/usr_showcars')
def usr_show_cars():
    global conn
    cursor = conn.cursor()
    sql = "select * from cars"
    cursor.execute(sql)
    results = cursor.fetchall()
    cars.clear()
    for row in results:
        license = row[0]
        cost = row[1]
        brand = row[2]
        status = row[3]
        rent = row[4]
        dirt = {'license': license, 'cost': cost, 'brand': brand, 'status': status, 'rent': rent}
        cars.append(dirt)
    return render_template('usr_show_cars.html', cars=cars)


'''
    用户访问：租车
'''
@app.route('/usr_rentcar/', methods=['POST', 'GET'])
def usr_rent_car():
    global conn
    cursor = conn.cursor()
    license_need = request.args.get('rent_license')
    #sql = "begin ; select * from cars where license = '%s' and rent_info = 0 ; rollback ;" % license_need
    #exe_sql(sql, cursor)
    #这里考虑过用事务，但是不知道该怎么用，就放弃了
    sql = "select * from cars where license = '%s' and rent_info = 0" % license_need
    cursor.execute(sql)
    results = cursor.fetchall()
    if cursor.rowcount == 0:
        #要显示当前车辆不可用的信息
        return render_template('usr_show_cars.html', cars=cars)
    else:
        car_current.clear()
        car_current.append(list(results[0]))
        sql = "select * from log"
        cursor.execute(sql)
        results = cursor.fetchall()
        log_id_cur = results[-1][0] + 1
        sql = "INSERT INTO log VALUES ( %d , %d , '%s' , '%s' , NULL , 0 , 0 , 0 , NULL , NULL , 0) ;" \
              % (log_id_cur, usr_current[0][0], car_current[0][0], time.strftime("%Y-%m-%d", time.localtime()) )
        print(sql)
        cursor.execute(sql)
    return render_template('usr_homepage.html', finish_sign=1)   # finish用来显示一个弹窗，说明已经提交订单



'''
    用户访问：个人订单    未完成
'''
@app.route('/usr_log')
def usr_log():
    current_id = usr_current[0][0]
    global conn
    cursor = conn.cursor()
    sql = "select * from log where p_id = %d" % current_id
    cursor.execute(sql)
    results = cursor.fetchall()
    person_log.clear()
    for row in results:
        license = row[2]
        start_time = row[3]
        finish_time = row[4]
        cost = row[5]
        rent_e = row[8]
        back_e = row[9]
        if row[10] == 0:
            status='未完成'
        else:
            status='结束'
        dirt = {'license': license, 'start_time': start_time, 'finish_time': finish_time,\
                'cost': cost, 'rent_e': rent_e, 'back_e': back_e, 'status': status }
        person_log.append(dirt)
    return render_template('usr_log.html', person_log=person_log)


'''
    跳转到管理员注册界面（该界面还没实现）
'''
@app.route('/logup_index/')
def log_up():
    return render_template('')


'''
    这只是一个查询功能的demo
'''
@app.route('/a/')
def person_list():
    global conn
    cursor = conn.cursor()
    sql = "select * from person"
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        username = row[1]
        email = row[2]
        dirt = {'title': username, 'year': email}
        movies.append(dirt)
    return render_template('index.html', movies=movies)


'''
    最初的界面
    跳转到管理员登录界面
'''
@app.route('/')
def index():
    admin_login_sign = 0
    return render_template('login.html', admin_login_sign=admin_login_sign)


@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码


if __name__ == '__main__':
    server = make_server('127.0.0.1', 3306, app)
    server.serve_forever()
    app.run()
