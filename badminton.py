import requests
import dbfunction
import normal_fun
import importlib
import sys

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    importlib.reload(sys)
    sys.setdefaultencoding(defaultencoding)
from flask import Flask, render_template, request, json

app = Flask(__name__)

@app.route('/')
def index():
    user_agent = request.headers.get('User_Agent')
    return 'user_agent is %s' % user_agent


# 创建比赛
@app.route('/wx/game/create', methods=['POST'])
def create_match():
    data = normal_fun.judge_param(request)
    token = request.cookies.get("token")
    token_json = dbfunction.token_query(token)
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '400001', 'msg': '签名验证未通过'}
        return json.dumps(res)
    openid = token_map['openid']
    return dbfunction.create_match(data, openid)


# 我创建的比赛里面删除成员
@app.route('/wx/game/delete_member', methods=['POST'])
def delete_member():
    token = request.cookies.get("token")
    token_json = dbfunction.token_query(token)
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '600003', 'msg': '签名验证未通过'}
        return json.dumps(res)
    participant_id = int(request.values.get("id"))
    return dbfunction.delete_member(participant_id)


# 删除比赛
@app.route('/wx/game/delete_match', methods=['POST'])
def delete_match():
    token = request.cookies.get("token")
    token_json = dbfunction.token_query(token)
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '600003', 'msg': '签名验证未通过'}
        return json.dumps(res)
    match_id = request.values.get("id")
    return dbfunction.delete_match(match_id)


# 取消报名
@app.route('/wx/participant/cancel', methods=['POST'])
def participant_cancel():
    token = request.cookies.get("token")
    token_json = dbfunction.token_query(token)
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '600003', 'msg': '签名验证未通过'}
        return json.dumps(res)
    # participant里面的id，非match_id，唯一标识一个参赛者记录
    match_id = int(request.values.get("id"))
    return dbfunction.cancel_participant(match_id)


@app.route('/wx/game/memberList', methods=['POST'])
def member_list():
    token = request.cookies.get("token")
    token_json = dbfunction.token_query(token)
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '600003', 'msg': '签名验证未通过'}
        return json.dumps(res)
    match_id = int(request.values.get("matchId"))
    page_num = int(request.values.get("pageNum"))
    per_page = int(request.values.get("perPage"))
    return dbfunction.get_member_list(match_id, page_num, per_page)


# 获取参赛者详细信息
@app.route('/wx/game/memberDetails', methods=['POST'])
def get_member_details():
    token = request.cookies.get("token")
    token_json = dbfunction.token_query(token)
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '400001', 'msg': '签名验证未通过'}
        return json.dumps(res)
    member_id = int(request.values.get('id'))
    return dbfunction.member_details(member_id)


@app.route('/wx/game/update', methods=['POST'])
def match_update():
    data = normal_fun.judge_param(request)
    token = request.cookies.get("token")
    token_json = dbfunction.token_query(token)
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '600003', 'msg': '签名验证未通过'}
        return json.dumps(res)
    return dbfunction.update_match(data)


@app.route('/wx/game/list', methods=['POST'])
def get_match_list():
    print("list begin to work")
    page_num = int(request.values.get("pageNum"))
    per_page = int(request.values.get("perPage"))
    order_type = request.values.get("orderType")
    return dbfunction.get_match_list(page_num, per_page, order_type)


# 比赛详情查询(按比赛ID)
@app.route('/wx/game/query_by_id', methods=['POST'])
def query_by_id():
    print("query_by_id begin to work")
    match_id = request.values.get("id")
    token = request.cookies.get("token")
    print("query_by_id:", token)
    return dbfunction.query_by_id(match_id)


# 单人比赛报名
@app.route('/wx/participant_single/add', methods=['POST'])
def add_participant_single():
    print("add_participant begin to work")
    # 获取token
    token = request.cookies.get("token")
    token_json = dbfunction.token_query(token)
    # 是否在数据库中查询到token
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '600201', 'msg': '签名验证未通过'}
        return json.dumps(res)
    openid = token_map['openid']

    game_id = request.values.get("gameId")  # 比赛id，对应match数据表中的id
    name = request.values.get("name")
    phone = request.values.get("phone")
    # birthday = request.values.get("birthday")
    salary_id = request.values.get("salaryID")
    cloth_num = request.values.get("clothNum")
    pants_num = request.values.get("pantsNum")
    identification = request.values.get("identification")
    # 默认已经等于18位
    identification_17 = identification[0:17]
    print("identi17:", identification_17)
    print("typeiden17:", type(identification_17))
    if not identification_17.isdigit():
        res = {'code': '600201', 'msg': '身份证号码输入错误'}
        return json.dumps(res)
    identity_card = normal_fun.IdentityCard(identification)
    if not identity_card.calculate():
        res = {'code': '600201', 'msg': '身份证号码输入错误'}
        return json.dumps(res)
    sex = identity_card.get_sex()
    birthday = identity_card.get_birthday()
    # 女
    if sex == 0:
        sex = '2'
    # 男
    else:
        sex = '1'
    return dbfunction.add_participant_single(game_id, openid, name, sex, phone, salary_id, cloth_num, pants_num, birthday,
                                             identification)


# 双人比赛报名
@app.route('/wx/participant_double/add', methods=['POST'])
def add_participant_double():
    print("add_participant_double begin to work")
    # 获取token
    token = request.cookies.get("token")
    token_json = dbfunction.token_query(token)
    # 是否在数据库中查询到token
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '600003', 'msg': '签名验证未通过'}
        return json.dumps(res)
    openid = token_map['openid']

    game_id = request.values.get("gameId")  # 比赛id，对应match数据表中的id

    name = request.values.get("name")
    phone = request.values.get("phone")
    salary_id = request.values.get("salaryID")
    cloth_num = request.values.get("clothNum")
    pants_num = request.values.get("pantsNum")
    identification = request.values.get("identification")
    # 默认已经等于18位
    identification_17 = identification[0:17]
    if not identification_17.isdigit():
        res = {'code': '600003', 'msg': '身份证号码输入错误'}
        return json.dumps(res)
    identity_card = normal_fun.IdentityCard(identification)
    if not identity_card.calculate():
        res = {'code': '600003', 'msg': '身份证号码输入错误'}
        return json.dumps(res)
    sex = identity_card.get_sex()
    # 女
    if sex == 0:
        sex = '2'
    # 男
    else:
        sex = '1'
    birthday = identity_card.get_birthday()
    age = identity_card.get_age()
    # 搭档
    partner_name = request.values.get("partnerName")
    partner_phone = request.values.get("partnerPhone")
    partner_salary_id = request.values.get("partnerSalaryID")
    partner_cloth_num = request.values.get("partnerClothNum")
    partner_pants_num = request.values.get("partnerPantsNum")
    partner_identification = request.values.get("partnerIdentification")
    # 默认已经等于18位
    identification_17 = partner_identification[0:17]
    if not identification_17.isdigit():
        res = {'code': '600003', 'msg': '身份证号码输入错误'}
        return json.dumps(res)
    identity_card = normal_fun.IdentityCard(partner_identification)
    partner_age = identity_card.get_age()
    if age + partner_age < 80:
        res = {'code': '600003', 'msg': '年龄之和小于80，无法报名'}
        return json.dumps(res)
    if not identity_card.calculate():
        res = {'code': '600003', 'msg': '身份证号码输入错误'}
        return json.dumps(res)
    partner_sex = identity_card.get_sex()
    # 女
    if partner_sex == 0:
        partner_sex = '2'
    # 男
    else:
        partner_sex = '1'
    partner_birthday = identity_card.get_birthday()
    return dbfunction.add_participant_double(game_id, openid, name, sex, phone, salary_id, cloth_num, pants_num, birthday, identification,
                                             partner_name, partner_sex, partner_phone, partner_salary_id,
                                             partner_cloth_num, partner_pants_num, partner_birthday, partner_identification)


# 用户登录
@app.route('/wx/auth/login', methods=['POST'])
def auth_login():
    print("auth_login begin to work")
    code = request.values.get("code")
    url = "https://api.weixin.qq.com/sns/jscode2session?appid=wxea3b22cabe162900&" \
          "secret=567b3db8b1ea42ea930ff7012471165c&js_code=" \
          + code + "&grant_type=authorization_code"
    print("url:", url)
    response = requests.get(url)
    result = response.json()
    session_key = result['session_key']
    openid = result['openid']
    print("session_key:", session_key)
    print("openid:", openid)
    token_dict = {'session_key': session_key, "openid": openid}
    token_json = json.dumps(token_dict)

    token = normal_fun.generate_token(token_json)
    print("token:", token)
    # 在redis中将token，token_json作为键值对存储
    # 先存在mysql中
    # 把openid放入user表，在check函数中添加user具体信息
    count = dbfunction.user_add_openid_only(openid)
    if count == 0:
        res = {'code': '700002', 'msg': '数据库操作异常'}

    return dbfunction.create_token(token, token_json)


# 查看我创建的比赛
@app.route('/wx/game/creator/query', methods=['POST'])
def creator_query():
    print("ssss")
    per_page = int(request.values.get('perPage'))
    page_num = int(request.values.get('pageNum'))
    token = request.cookies.get('token')
    token_json = dbfunction.token_query(token)
    # 是否在数据库中查询到token
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '600003', 'msg': '签名验证未通过'}
        return json.dumps(res)
    openid = token_map['openid']
    return dbfunction.my_create_matches(page_num, per_page, openid)


# 查看我参加的比赛
@app.route('/wx/game/participant/query', methods=['POST'])
def my_attend_matches():
    print("request.values.get('pageNum'):", request.values.get('pageNum'))
    page_num = int(request.values.get('pageNum'))
    per_page = int(request.values.get('perPage'))
    token = request.cookies.get('token')
    token_json = dbfunction.token_query(token)
    # 是否在数据库中查询到token
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '600003', 'msg': '签名验证未通过'}
        return json.dumps(res)
    openid = token_map['openid']
    return dbfunction.my_attend_matches(page_num, per_page, openid)


@app.route('/wx/user/check', methods=['POST'])
def user_check():
    print("user check begin to work")
    token = request.cookies.get("token")
    token_json = dbfunction.token_query(token)
    # 是否在数据库中查询到token
    if token_json:
        token_map = eval(token_json)
    else:
        res = {'code': '600003', 'msg': '签名验证未通过'}
        return json.dumps(res)
    # 校验"{"openid:": "oFpnZ5et2lnqMvKoVSDyrdtPyIAU", "session_key": "/YuizxZZn0F7UuLSo8Ev9A=="}
    print("token_map:", token_map)
    # openid 用于更新user表的nickname之类的
    openid = token_map['openid']
    session_key = token_map['session_key']

    nick_name = request.values.get("nickName")
    gender = request.values.get("gender")
    language = request.values.get("language")
    city = request.values.get("city")
    province = request.values.get("province")
    country = request.values.get("country")
    avatar_url = request.values.get("avatarUrl")

    # TODO sha1校验，比较signature和signature2，来确保数据的完整性
    # signature = request.values.get("signature")
    # raw_data = request.values.get("rawData")
    # sha = hashlib.sha1((raw_data + session_key).encode('utf-8'))
    # signature2 = sha.hexdigest()
    # print("signature2:", signature2)

    # encrypted_data = request.values.get("encryptedData")
    # iv = request.values.get("iv")
    # TODO 进行校验
    # appID = 'wxea3b22cabe162900'  # 开发者关于微信小程序的appID
    # pc = WXBizDataCrypt(appID, session_key)
    #
    # print(pc.decrypt(encrypted_data, iv))
    # encryptedData = request.values.get('encryptedData')
    # iv = request.values.get('iv')
    # pc = WXBizDataCrypt(appID, session_key)  # 对用户信息进行解密
    # userinfo = pc.decrypt(encryptedData, iv)  # 获得用户信息
    # print("userinfo:", userinfo)
    return dbfunction.update_user(nick_name, gender, language, city, province, country, avatar_url, openid)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(
        host='192.168.2.101',
        port=5000,
        debug=True
    )
