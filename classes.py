class Receipt:
    def __init__(self,check_id ,id_who_bought, goods ,users): # data is 2d array where first index is good name, second is amount, users is array of id of users
        self.check_id = check_id
        self.id_who_bought = id_who_bought
        self.raw_goods = data
        self.users = users
        tmp = {}
        for i in range(len(users)):
            tmp[users[i]] = [0 for i in range(len(goods))]