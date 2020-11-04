import datetime
import time
import base64
import hmac


def certify_token(key, token):
    """
    @Args:
        key: str
        token: str
    @Returns:
        boolean
    :param key:
    :param token:
    :return:
    """
    token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split(':')
    if len(token_list) != 2:
        return False
    ts_str = token_list[0]
    if float(ts_str) < time.time():
        return False
    known_sha1_tsstr = token_list[1]
    sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
    calc_sha1_tsstr = sha1.hexdigest()
    if calc_sha1_tsstr != known_sha1_tsstr:
        # token certification failed
        return False
    # token certification success
    return True


def generate_token(key, expire=60):
    """
    @Args:
        key: str (用户给定的key，需要用户保存以便之后验证token,每次产生token时的key 都可以是同一个key)
        expire: int(最大有效时间，单位为s)
    @Return:
        state: str
    :param key:
    :param expire:
    :return:
    """
    ts_str = str(time.time() + expire)
    ts_byte = ts_str.encode("utf-8")
    sha1_tshex_str = hmac.new(key.encode("utf-8"), ts_byte, 'sha1').hexdigest()
    token = ts_str + ':' + sha1_tshex_str
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))

    return b64_token.decode("utf-8")


"""
判断比赛类型
"""


def judge_type(game_type):
    if game_type == '1':
        game_type = "男单"
    elif game_type == '2':
        game_type = "女单"
    elif game_type == '3':
        game_type = '男双'
    elif game_type == '4':
        game_type = '女双'
    else:
        game_type = '混双'
    return game_type


def judge_param(request):
    game_type = judge_type(request.values.get("gameType"))
    begin_time = request.values.get("beginTime")
    end_time = request.values.get("endTime")
    deadline = request.values.get("deadline")
    address = request.values.get("address")
    limit_num = request.values.get("limitNum")
    creator = request.values.get("creator")
    creator_phone = request.values.get("creatorPhone")
    match_id = request.values.get("id")
    information_map = {'game_type': game_type, 'begin_time': begin_time, 'id': match_id,
                       'end_time': end_time, 'deadline': deadline, 'address': address,
                       'limit_num': limit_num, 'creator': creator, 'creator_phone': creator_phone}

    return information_map


# 计算年龄
def calculate_age(birth):
    birth_d = datetime.datetime.strptime(birth, "%Y-%m-%d")
    today_d = datetime.datetime.now()
    birth_t = birth_d.replace(year=today_d.year)
    if today_d > birth_t:
        age = today_d.year - birth_d.year
    else:
        age = today_d.year - birth_d.year - 1
    return age

# 身份证校验
class IdentityCard:
    def __init__(self, identity):
        self.id = identity
        self.birth_year = int(self.id[6:10])
        self.birth_month = int(self.id[10:12])
        self.birth_day = int(self.id[12:14])
        self.code = self.id[0:17]
        self.__Wi = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        self.__Ti = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

    def get_birthday(self):
        # 通过身份证号获取出生日期
        birthday = "{0}-{1}-{2}".format(self.id[6:10], self.id[10:12], self.id[12:14])
        return birthday

    def get_sex(self):
        # 男生：1 女生：0
        num = int(self.id[16:17])
        if num % 2 == 0:
            return 0
        else:
            return 1

    def get_age(self):
        # 获取年龄
        now = (datetime.datetime.now() + datetime.timedelta(days=1))
        year = now.year
        month = now.month
        day = now.day

        if year == self.birth_year:
            return 0
        else:
            if self.birth_month > month or (self.birth_month == month and self.birth_day > day):
                return year - self.birth_year - 1
            else:
                return year - self.birth_year

    def calculate(self):
        sum = 0
        for i in range(17):
            sum += int(self.code[i]) * self.__Wi[i]
        return self.__Ti[sum % 11] == self.id[17:18]
