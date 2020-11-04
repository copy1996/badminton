import time
import normal_fun
import pymysql
from flask import json

ip_address = "localhost"
account = "root"
# password = "ustcbadminton"
password = "Fuzhikai1996"
database1 = "badminton"
# 回头写个线程池

# 创建比赛
def create_match(data, openid):
    db = pymysql.connect(ip_address, account, password, database1)
    sql = "insert into `match` (openid, gameType, beginTime, endTime, deadline, address, limitNum, creator," \
          "creatorPhone, participantnum) " \
          "values('%s', '%s', '%s','%s','%s','%s','%s','%s','%s', %d)" % \
          (openid, data['game_type'], data['begin_time'], data['end_time'],
           data['deadline'], data['address'], data['limit_num'], data['creator'], data['creator_phone'], 0)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
        res = {'code': '000000', 'msg': '成功'}
    except Exception as e:
        print(e)
        res = {'code': '600101', 'msg': '创建比赛失败'}
    db.close()
    return json.dumps(res)


# 更新user表信息
def update_user(nick_name, gender, language, city, province, country, avatar_url, openid):
    db = pymysql.connect(ip_address, account, password, database1)
    cursor = db.cursor()
    sql = "update `user` set nickname = '%s', gender = '%s', language = '%s', city = '%s', province = '%s', " \
          "country = '%s', avatarUrl = '%s' where openid = '%s'" % (nick_name, gender, language, city, province,
                                                                    country, avatar_url, openid)
    try:
        cursor.execute(sql)
        db.commit()
        res = {'code': '000000', 'msg': '更新成功'}
    except Exception as e:
        print(e)
        db.rollback()
        res = {'code': '600302', 'msg': '更新失败'}
    db.close()
    return json.dumps(res)


# 删除成员
def delete_member(participant_id):
    db = pymysql.connect(ip_address, account, password, database1)
    cursor = db.cursor()
    sql = "delete from `participant` where id = %d" % participant_id
    sql2 = "update `match` set participantNum = participantNum - 1 where (gameType = '男单' or gameType = '女单') and id in (" \
           "select gameid from `participant` where id = %d)" % participant_id
    sql3 = "update `match` set participantNum = participantNum - 2 where (gameType != '男单' and gameType != '女单') and id in (" \
           "select gameid from `participant` where id = %d)" % participant_id
    try:
        cursor.execute(sql2)
        cursor.execute(sql3)
        cursor.execute(sql)
        db.commit()
        res = {'code': '000000', 'msg': '成功'}
    except Exception as e:
        print(e)
        db.rollback()
        res = {'code': '000001'}
    db.close()
    return json.dumps(res)


# 删除比赛
def delete_match(match_id):
    db = pymysql.connect(ip_address, account, password, database1)
    cursor = db.cursor()
    # 先删除participant里面的相应数据，再删除match里的数据
    sql = "delete from `participant` where gameid = '%s'" % match_id
    sql2 = "delete from `match` where id = '%s'" % match_id
    try:
        cursor.execute(sql)
        cursor.execute(sql2)
        db.commit()
        res = {'code': '000000', 'msg': '删除成功'}
    except Exception as e:
        print(e)
        db.rollback()
        res = {'code': '000001', 'msg': '删除失败'}
    db.close()
    return json.dumps(res)



# 查询比赛对应的人员信息
def get_member_list(match_id, page_num, per_page):
    db = pymysql.connect(ip_address, account, password, database1)
    sql = "select a.gameType, b.* from `match` as a,`participant` as b where a.id = b.gameid and a.id = %d limit %d, %d" \
          % (match_id, (page_num-1)*per_page, per_page)
    sql2 = "select a.gameType, b.* from `match` as a,`participant` as b where a.id = b.gameid and a.id = %d" \
          % (match_id)
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql2)
        dict_len = len(cursor.fetchall())
        cursor.execute(sql)
        results = cursor.fetchall()
        print("results:", results)
        if dict_len % per_page == 0:
            total_page = dict_len // per_page
        else:
            total_page = dict_len // per_page + 1
        res = {'code': '000000', 'msg': '成功', 'result': {'pageNum': page_num, 'data': results, 'totalPage': total_page}}
    except Exception as e:
        print(e)
        res = {'code': '600102', 'msg': '查询失败'}
    print("db.close")
    db.close()
    return json.dumps(res)


# 更新比赛
def update_match(data):
    db = pymysql.connect(ip_address, account, password, database1)
    sql = "update `match` set gameType = '%s', beginTime = '%s', endTime = '%s', deadline = '%s', address = '%s', " \
          "limitNum = '%s', creator = '%s', creatorPhone = '%s' where id = %d" % \
          (data['game_type'], data['begin_time'], data['end_time'], data['deadline'], data['address'],
           data['limit_num'], data['creator'], data['creator_phone'], int(data['id']))
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
        res = {'code': '000000', 'msg': '成功'}
    except Exception as e:
        print(e)
        db.rollback()
        res = {'code': '600101', 'msg': '更新比赛失败'}
    print("db.close")
    db.close()
    return json.dumps(res)


# 查询比赛列表
def get_match_list(page_num, per_page, orderType):
    db = pymysql.connect(ip_address, account, password, database1)
    sql = "select * from `match` limit %d, %d" % ((page_num - 1) * per_page, per_page)
    sql2 = "select * from `match`"
    print(sql)
    # 将结果作为字典返回游标
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql2)
        dict_len = len(cursor.fetchall())
        cursor.execute(sql)
        results = cursor.fetchall()
        print("get_match_list results:", results)
        localtime = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        for row in results:
            row['localtime'] = localtime
            if localtime <= row['deadline']:
                row['progress'] = '报名中'
            elif row['deadline'] < localtime < row['beginTime']:
                row['progress'] = '已截止'
            elif row['beginTime'] <= localtime <= row['endTime']:
                row['progress'] = '进行中'
            else:
                row['progress'] = '已结束'
        if dict_len % per_page == 0:
            total_page = dict_len // per_page
        else:
            total_page = dict_len // per_page + 1
        print("total_page:", total_page)
        res = {'code': '000000', 'msg': '成功', 'result': {'pageNum': page_num, 'data': results, 'totalPage': total_page}}
    except Exception as e:
        print(e)
        res = {'code': '600102', 'msg': '比赛查询失败'}
    print("db.close")
    db.close()
    return json.dumps(res)


# 比赛详情查询(按比赛ID)
def query_by_id(match_id):
    """
    :param match_id: 比赛id
    :return:
    """
    db = pymysql.connect(ip_address, account, password, database1)
    sql = "select * from `match` where id = %s" % match_id
    # 将结果作为字典返回游标
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql)
        # 查询一条数据
        result = cursor.fetchone()
        dict = {'男单': '1', '女单': '2', '男双': '3', '女双': '4', '混双': '5'}
        result['gameType'] = dict[result['gameType']]
        localtime = time.strftime("%Y-%m-%d", time.localtime())
        result['localtime'] = localtime
        res = {'code': '000000', 'msg': '成功', 'result': {'data': result}}
        print(res)
    except Exception as e:
        print(e)
        res = {'code': '600102', 'msg': '比赛详情查询失败'}
    print("db.close")
    db.close()
    return json.dumps(res)


# 单人赛添加报名信息
def add_participant_single(game_id, openid, name, sex, phone, salary_id, cloth_num, pants_num, birthday, identification):
    db = pymysql.connect(ip_address, account, password, database1)
    # 验证是否已报名过
    # sql4 = "select a.gameType as game_type, b.* from `match` as a, `participant` as b where a.id = b.gameid " \
    #        "and (b.name = '%s' and b.salaryid = '%s'" \
    #        " and b.identification = '%s' or b.partnername = '%s'" \
    #        " and b.partnersalaryid = '%s' and b.partnerIdentification = '%s') " % (name, salary_id, identification,
    #                                                                                name, salary_id, identification)
    sql4 = "select a.gameType as game_type, b.* from `match` as a, `participant` as b where a.id = b.gameid " \
           "and (b.identification = '%s' or b.partnerIdentification = '%s') " % (identification, identification)
    # 检查是否报名者已满以及性别是否对应
    sql3 = "select participantnum as participant_num, limitNum as limit_num, gameType as game_type from `match` " \
           "where id = '%s'" % game_id
    # 插入报名者信息
    sql = "insert into `participant` (gameid, openid, name, sex, phone, salaryid, clothnum, pantsnum, birthday, identification) " \
          "values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
          (game_id, openid, name, sex, phone, salary_id, cloth_num, pants_num, birthday, identification)
    # 更新match表中participantnum字段
    sql2 = "update `match` set participantnum = participantnum + 1 where id = '%s'" % game_id
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql3)
        result = cursor.fetchone()
        game_type = result['game_type']
        if result['game_type'] == '女单' and sex == '1':
            res = {'code': '600201', 'msg': '性别错误，不能报名女赛'}
            db.close()
            return json.dumps(res)

        if result['game_type'] == '男单' and sex == '2':
            res = {'code': '600201', 'msg': '性别错误，不能报名男赛'}
            db.close()
            return json.dumps(res)

        if result['limit_num'] == result['participant_num']:
            res = {'code': '600201', 'msg': '人数已满'}
            db.close()
            return json.dumps(res)
        cursor.execute(sql4)
        results = cursor.fetchall()
        count = len(results)

        if sex == '1' and count > 0:
            for row in results:
                if row['game_type'] == '男单':
                    res = {'code': '600201', 'msg': '无法报名，已报名一场男单'}
                    db.close()
                    return json.dumps(res)
                else:
                    if name == row['name'] and salary_id == row['salaryid'] and identification == row['identification']:
                        res = {'code': '600202',
                               'result': {'data': {'name': row['partnername'], 'salaryid': row['partnersalaryid'],
                                                   'identification': row['partnerIdentification']}}}
                        db.close()
                        return json.dumps(res)
                    else:
                        res = {'code': '600202',
                               'result': {'data': {'name': row['name'], 'salaryid': row['salaryid'], 'identification':
                                   row['identification']}}}
                        db.close()
                        return json.dumps(res)
        if sex == '2' and count > 1:
            new_list1 = []
            new_list2 = []
            count = 0
            for row in results:
                if row['game_type'] == '女双':
                    if name == row['name'] and salary_id == row['salaryid'] and identification == row['identification']:
                        new_list1.append({'name': row['partnername'], 'salaryid': row['partnersalaryid'],
                                                   'identification': row['partnerIdentification']})
                    else:
                        new_list1.append({'name': row['name'], 'salaryid': row['salaryid'], 'identification':
                                   row['identification']})
                elif row['game_type'] == '混双':
                    if name == row['name'] and salary_id == row['salaryid'] and identification == row['identification']:
                        new_list2.append({'name': row['partnername'], 'salaryid': row['partnersalaryid'],
                                         'identification': row['partnerIdentification']})
                    else:
                        new_list2.append({'name': row['name'], 'salaryid': row['salaryid'], 'identification':
                            row['identification']})
                else:
                    count = count + 1
            if count == 2:
                res = {'code': '600201', 'msg': '无法报名，已报名两场女单'}
            else:
                res = {'code': '600203', 'result': {'data1': new_list1, 'data2': new_list2}}
            db.close()
            return json.dumps(res)

        cursor.execute(sql)
        cursor.execute(sql2)
        db.commit()
        res = {'code': '000000', 'msg': '成功'}
    except Exception as e:
        print(e)
        db.rollback()
        res = {'code': '600201', 'msg': '报名失败'}
    db.close()
    return json.dumps(res)


# 双人赛添加报名信息
def add_participant_double(game_id, openid, name, sex, phone, salary_id, cloth_num, pants_num, birthday, identification,
                           partner_name, partner_sex, partner_phone, partner_salary_id, partner_cloth_num,
                           partner_pants_num, partner_birthday, partner_identification):
    db = pymysql.connect(ip_address, account, password, database1)
    # 查询是否报名过比赛
    # sql4 = "select a.gameType as game_type, b.* from `match` as a, `participant` as b where a.id = b.gameid " \
    #        "and (b.name = '%s' and b.salaryid = '%s' and b.identification = '%s' " \
    #        "or b.partnername = '%s'" \
    #        " and b.partnersalaryid = '%s' and b.partnerIdentification = '%s')" % (name, salary_id, identification,
    #                                                                          name, salary_id, identification)
    sql4 = "select a.gameType as game_type, b.* from `match` as a, `participant` as b where a.id = b.gameid " \
           "and (b.identification = '%s' or b.partnerIdentification = '%s')" % (identification, identification)
    # 查询搭档是否报名过比赛
    # sql5 = "select a.gameType as game_type, b.* from   `match` as a,`participant` as b where a.id = b.gameid " \
    #        "and (b.name = '%s' and b.salaryid = '%s' and b.identification = '%s' " \
    #        "or b.partnername = '%s' and b.partnersalaryid = '%s' and b.partnerIdentification = '%s')" % \
    #        (partner_name, partner_salary_id, partner_identification,
    #         partner_name, partner_salary_id, partner_identification)
    sql5 = "select a.gameType as game_type, b.* from   `match` as a,`participant` as b where a.id = b.gameid " \
           "and (b.identification = '%s' or b.partnerIdentification = '%s')" % \
           (partner_identification, partner_identification)
    # 检查是否报名者已满
    sql3 = "select participantnum as participant_num, limitNum as limit_num, gameType as game_type from `match` " \
           "where id = '%s'" % game_id
    # 插入报名者信息
    sql = "insert into `participant` (gameid, openid, name, sex, phone, salaryid, clothnum, pantsnum, birthday, identification," \
          "partnername, partnersex, partnerphone, partnersalaryid, partnerclothnum,partnerpantsnum, partnerbirthday, " \
          "partnerIdentification) " \
          "values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
          (game_id, openid, name, sex, phone, salary_id, cloth_num, pants_num, birthday, identification, partner_name,
           partner_sex, partner_phone, partner_salary_id, partner_cloth_num, partner_pants_num, partner_birthday, partner_identification)
    # 更新match表中participantnum字段
    sql2 = "update `match` set participantnum = participantnum + 2 where id = '%s'" % game_id
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql3)
        result = cursor.fetchone()
        if result['game_type'] == '女双' and (sex == '1' or partner_sex == '1'):
            res = {'code': '600201', 'msg': '性别错误，不能报名女赛'}
            db.close()
            return json.dumps(res)

        if result['game_type'] == '男双' and (sex == '2' or partner_sex == '2'):
            res = {'code': '600201', 'msg': '性别错误，不能报名男赛'}
            db.close()
            return json.dumps(res)

        if result['limit_num'] == result['participant_num'] or result['limit_num'] == result['participant_num']+1:
            res = {'code': '600201', 'msg': '人数已满，无法报名'}
            db.close()
            return json.dumps(res)
        cursor.execute(sql4)
        results = cursor.fetchall()
        count = len(results)
        if sex == '1' and count > 0:
            for row in results:
                if row['game_type'] == '男单':
                    res = {'code': '600201', 'msg': '无法报名，已报名一场男单'}
                    db.close()
                    return json.dumps(res)
                else:
                    if name == row['name'] and salary_id == row['salaryid'] and identification == row['identification']:
                        res = {'code': '600202',
                               'result': {'data': {'name': row['partnername'], 'salaryid': row['partnersalaryid'],
                                                   'identification': row['partnerIdentification']}}}
                        db.close()
                        return json.dumps(res)
                    else:
                        res = {'code': '600202',
                               'result': {'data': {'name': row['name'], 'salaryid': row['salaryid'], 'identification':
                                   row['identification']}}}
                        db.close()
                        return json.dumps(res)
        if sex == '2' and count > 1:
            new_list1 = []
            new_list2 = []
            count = 0
            for row in results:
                if row['game_type'] == '女双':
                    if name == row['name'] and salary_id == row['salaryid'] and identification == row['identification']:
                        new_list1.append({'name': row['partnername'], 'salaryid': row['partnersalaryid'],
                                          'identification': row['partnerIdentification']})
                    else:
                        new_list1.append({'name': row['name'], 'salaryid': row['salaryid'], 'identification':
                            row['identification']})
                elif row['game_type'] == '混双':
                    if name == row['name'] and salary_id == row['salaryid'] and identification == row['identification']:
                        new_list2.append({'name': row['partnername'], 'salaryid': row['partnersalaryid'],
                                          'identification': row['partnerIdentification']})
                    else:
                        new_list2.append({'name': row['partnername'], 'salaryid': row['partnersalaryid'], 'identification':
                            row['partneridentification']})
                else:
                    count = count + 1
            if count == 2:
                res = {'code': '600201', 'msg': '无法报名，已报名两场女单'}
            else:
                res = {'code': '600203', 'result': {'data1': new_list1, 'data2': new_list2}}
            db.close()
            return json.dumps(res)
        cursor.execute(sql5)
        results = cursor.fetchall()
        count = len(results)
        if partner_sex == '1' and count > 0:
            for row in results:
                if row['game_type'] == '男单':
                    res = {'code': '600201', 'msg': '无法报名，搭档已报名一场男单'}
                    db.close()
                    return json.dumps(res)
                else:
                    if name == row['name'] and salary_id == row['salaryid'] and identification == row['identification']:
                        res = {'code': '600204',
                               'result': {'data': {'name': row['partnername'], 'salaryid': row['partnersalaryid'],
                                                   'identification': row['partnerIdentification']}}}
                        db.close()
                        return json.dumps(res)
                    else:
                        res = {'code': '600204',
                               'result': {'data': {'partnername': row['name'], 'salaryid': row['salaryid'], 'identification':
                                   row['identification']}}}
                        db.close()
                        return json.dumps(res)
        if partner_sex == '2' and count > 1:
            new_list1 = []
            new_list2 = []
            count = 0
            for row in results:
                if row['game_type'] == '女双':
                    if name == row['name'] and salary_id == row['salaryid'] and identification == row['identification']:
                        new_list1.append({'name': row['partnername'], 'salaryid': row['partnersalaryid'],
                                          'identification': row['partnerIdentification']})
                    else:
                        new_list1.append({'name': row['name'], 'salaryid': row['salaryid'], 'identification':
                            row['identification']})
                elif row['game_type'] == '混双':
                    if name == row['name'] and salary_id == row['salaryid'] and identification == row['identification']:
                        new_list2.append({'name': row['partnername'], 'salaryid': row['partnersalaryid'],
                                          'identification': row['partnerIdentification']})
                    else:
                        new_list2.append({'name': row['name'], 'salaryid': row['salaryid'], 'identification':
                            row['identification']})
                else:
                    count = count + 1
            if count == 2:
                res = {'code': '600201', 'msg': '无法报名，搭档已报名两场女单'}
            else:
                res = {'code': '600205', 'result': {'data1': new_list1, 'data2': new_list2}}
            db.close()
            return json.dumps(res)

        cursor.execute(sql)
        cursor.execute(sql2)
        db.commit()
        res = {'code': '000000', 'msg': '成功'}
    except Exception as e:
        print(e)
        db.rollback()
        res = {'code': '600201', 'msg': '报名失败'}
    db.close()
    return json.dumps(res)


# 向token表里插入包含token和tokenjson的数据
def create_token(token, token_json):
    db = pymysql.connect(ip_address, account, password, database1)
    sql = "insert into `token` values('%s','%s')" % (token, token_json)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
        res = cursor.rowcount
        if res == 1:
            res = {'code': '000000', 'msg': '成功', 'session': token}
        else:
            res = {'code': '600002', 'msg': '登录失败'}
    except:
        print("error")
        res = {'code': '600002', 'msg': '登录失败'}
    print("db.close")
    db.close()
    return json.dumps(res)


# token表根据id查询包含了sessionkey和openid的tokenjson，进行校验
def token_query(token):
    """
    :param token:
    :return:
    """
    db = pymysql.connect(ip_address, account, password, database1)
    sql = "select * from `token` where id = '%s'" % token
    # 将结果作为字典返回游标
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql)
        # 查询一条数据
        result = cursor.fetchone()
        print("db.close")
        db.close()
        if result:
            return result['tokenjson']
    except Exception as e:
        print(e)
        return ""


# 向user表中添加一条只包含了openid的数据
def user_add_openid_only(openid):
    db = pymysql.connect(ip_address, account, password, database1)
    # 判断有没有这个openid，查询成功返回2
    sql_judge = "select * from `user` where openid = '%s'" % openid
    sql = "insert into `user` (openid) values ('%s')" % openid
    cursor = db.cursor()
    success = False
    try:
        # 查询openid的数据项
        cursor.execute(sql_judge)
        res = cursor.fetchall()
        # 查询成功，不必插入，直接返回
        if res:
            db.close()
            return 1
        else:
            cursor.execute(sql)
            db.commit()
            count = cursor.rowcount
            print("db.close")
            db.close()
            return count
    except Exception as e:
        print(e)
        db.rollback()
        print("db.close")
        db.close()
        # count = 3表明出现了错误
        return 0


# 根据openid查询某人所创建的比赛
def my_create_matches(page_num, per_page, openid):
    sql = "select * from `match` where openid = '%s' ORDER BY beginTime DESC limit %d, %d " % (openid, (page_num - 1) * per_page, per_page)
    sql2 = "select * from `match` where openid = '%s' ORDER BY beginTime DESC" % (openid)
    db = pymysql.connect(ip_address, account, password, database1)
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql2)
        dict_len = len(cursor.fetchall())
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            localtime = time.strftime("%Y-%m-%d %H:%M", time.localtime())
            if localtime <= row['deadline']:
                row['progress'] = '报名中'
            elif row['deadline'] < localtime < row['beginTime']:
                row['progress'] = '已截止'
            elif row['beginTime'] <= localtime <= row['endTime']:
                row['progress'] = '进行中'
            else:
                row['progress'] = '已结束'
        if dict_len % per_page == 0:
            total_page = dict_len // per_page
        else:
            total_page = dict_len // per_page + 1
        res = {'code': '000000', 'msg': '成功', 'result': {'pageNum': page_num, 'data': results}, 'totalPage': total_page}
    except Exception as e:
        print(e)
        res = {'code': '600101', 'msg': '比赛查询失败'}
    db.close()
    return json.dumps(res)


# 根据openid查询某人所参加的比赛
def my_attend_matches(page_num, per_page, openid):
    db = pymysql.connect(ip_address, account, password, database1)
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)

    sql = "select a.id as id, b.id as gameid, b.gameType, b.beginTime, b.endTime, b.openid, b.deadline, " \
           "b.address, b.limitNum, b.creator, b.participantNum from `participant` as a, `match` as b where " \
           "b.id = a.gameid and a.openid = '%s' limit %d, %d" % (openid, (page_num - 1) * per_page, per_page)
    sql2 = "select a.id as id, b.id as gameid, b.gameType, b.beginTime, b.endTime, b.openid, b.deadline, " \
           "b.address, b.limitNum, b.creator, b.participantNum from `participant` as a, `match` as b where " \
           "b.id = a.gameid and a.openid = '%s'" % (openid)
    # sql = "SELECT * FROM `match` where id in (SELECT gameid from `participant` where openid = '%s') limit %d, %d" \
    #       % (openid, (page_num - 1) * per_page, per_page)
    try:
        cursor.execute(sql2)
        dict_len = len(cursor.fetchall())
        cursor.execute(sql)
        results = cursor.fetchall()
        print("results:", results)
        if dict_len % per_page == 0:
            total_page = dict_len // per_page
        else:
            total_page = dict_len // per_page + 1
        res = {'code': '000000', 'msg': '成功', 'result': {'pageNum': page_num, 'data': results}, 'totalPage': total_page}
    except Exception as e:
        print(e)
        res = {'code': '600101', 'msg': '比赛查询失败'}
    db.close()
    return json.dumps(res)


# 查询参赛者详情
def member_details(member_id):
    db = pymysql.connect(ip_address, account, password, database1)
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "select * from `participant` where id = %d" % member_id
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        print("member_details result:", result)
        age = normal_fun.calculate_age(result['birthday'])
        if result['partnerbirthday'] != '':
            partner_age = normal_fun.calculate_age(result['partnerbirthday'])
        else:
            partner_age = ''
        if result['sex'] == '1':
            sex = '男'
        else:
            sex = '女'
        if result['partnersex'] == '1':
            partner_sex = '男'
        else:
            partner_sex = '女'
        result['age'] = age
        result['partnerage'] = partner_age
        result['sex'] = sex
        result['partnersex'] = partner_sex
        print("result:", result)
        res = {'code': '000000', 'msg': '成功', 'result': {'data': result}}
    except Exception as e:
        print(e)
        res = {'code': '400001', 'msg': '查询失败'}
    db.close()
    return json.dumps(res)


# 取消报名
def cancel_participant(match_id):
    db = pymysql.connect(ip_address, account, password, database1)
    cursor = db.cursor()
    sql = "delete from `participant` where id = %d" % match_id
    sql2 = "update `match` set participantNum = participantNum - 1 where (gameType = '男单' or gameType = '女单') " \
           "and id in (select gameid from `participant` where id = %d)" % match_id
    sql3 = "update `match` set participantNum = participantNum - 2 where (gameType != '男单' and gameType != '女单') " \
           "and id in (select gameid from `participant` where id = %d)" % match_id
    print("sql:", sql)
    print("sql2:", sql2)
    try:
        cursor.execute(sql2)
        cursor.execute(sql3)
        cursor.execute(sql)
        db.commit()
        res = {'code': '000000', 'msg': '成功'}
    except Exception as e:
        print(e)
        db.rollback()
        res = {'code': '600101', 'msg': '删除失败'}
    db.close()
    return json.dumps(res)



def list123():
    db = pymysql.connect(ip_address, account, password, database1)
    cursor = db.cursor()
    sql = "select * from `match`"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            print(row)
    except Exception as e:
        print("error:", e)
    db.close()
