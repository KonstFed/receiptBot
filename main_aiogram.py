from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import pandas as pd
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from classes import Receipt


# surveys = {}
# pathUnresolved = 'data/UnResolvedReceipt.csv'

# unresolved_receipts = pd.read_csv(pathUnresolved)
# tmp = unresolved_receipts['check_id']

# if tmp.size == 0:
#     amount_checks = 0
# else:
#     amount_checks = unresolved_receipts['check_id'].unique().max()

# f = open("config.txt","r")
# TOKEN = f.read()

# bot = Bot(token=TOKEN)
# dp = Dispatcher(bot)

# async def resolve_check(mes,data):
#     global surveys
#     check_id = data['check_id'][0]
#     opt = []
#     for i in range(len(data)):
#         if (data['amount'][i] == 1.0):
#             opt.append(data['name'][i])
#             if (len(opt) == 10):
#                 msg = await bot.send_poll(mes.chat.id,"За что вкидываешься?",opt,is_anonymous=False,allows_multiple_answers=True)
#                 opt = []

    
#     msg = await bot.send_poll(mes.chat.id,"За что вкидываешься?",opt,is_anonymous=False,allows_multiple_answers=True)
# def parse_receipt(raw_str: str):
#     global amount_checks
#     answer = []

#     strings = raw_str.split("\n")

#     date = strings[1][7:]

#     for i in range(4, len(strings) - 16, 3):
#         id, name = strings[i].split(". ", 1)
#         id = int(id)
#         cost, other = strings[i+1].split(" x ")
#         cnt, price = other.split(" = ")
#         cost, cnt = float(cost), float(cnt)

#         answer.append((id, name, cnt, cost,date))

#      # parsing receipt to list of tuples
 

#     data = pd.DataFrame(answer,columns =['goods_id', 'name', 'amount','unit_price','date'])
#     data.insert(loc = 0, column='check_id',value= amount_checks+1)
#     amount_checks += 1
#     return data
# @dp.poll_answer_handler()
# async def handle_poll_answer(quiz_answer: types.PollAnswer):

#     print("answer to poll is ",quiz_answer)
# @dp.message_handler(commands=['start'])
# async def process_start_command(message: types.Message):
#     await message.reply("Hello, It is receipt analyizing bot that will help you divide cash between your roomates!")

# @dp.message_handler()
# async def echo_message(msg: types.Message):
#     global amount_checks,unresolved_receipts
    
#     if not('НДС' in msg.text):  #  receipt condition; need to be done properly later
#         return

#     # button_hi = KeyboardButton('Привет! 👋')

#     # greet_kb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
#     # greet_kb.add(button_hi)
#     # await msg.reply("Привет!", reply_markup= greet_kb)


#     data = parse_receipt(msg.text) # parsing receipt to list of tuples

#     tmp = data.drop('goods_id',inplace=False,axis=1)  


#     unresolved_receipts = pd.concat([unresolved_receipts,tmp],ignore_index=True)

#     # save_unresolved()
#     await resolve_check(msg,data)

# if __name__ == '__main__':
#     executor.start_polling(dp)
class Group():
    def __init__(self,chat_id,):
        self.chat_id = chat_id
        self.amount_checks = 0
        self.users_id = []
        self.users_name = {}
        self.unresolved_receipts = []
        self.unresolved_polls = []
    def add_user(self,user_id,nick):
        self.users_id.append(user_id)
        self.users_name[user_id] = nick
    
f = open("config.txt","r")
TOKEN = f.read()

groups = []

# chats_id = {}
# unresolved_receipts = {}
# unresolved_polls = {} # key в этом словаре poll id, value list id пользователей кто вкинулся и за что
# users_id = []

amount_checks = 0

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

inline_bnt_reg = InlineKeyboardButton("Register", callback_data='register_button')
inline_reg = InlineKeyboardMarkup().add(inline_bnt_reg)


def parse_receipt(raw_str: str):
    answer = []
    strings = raw_str.split("\n")
    date = strings[1][7:]

    for i in range(4, len(strings) - 16, 3):
        id, name = strings[i].split(". ", 1)
        id = int(id) - 1  # Because we want our indexes to start from 0
        cost, other = strings[i+1].split(" x ")
        cnt, price = other.split(" = ")
        cost, cnt = float(cost), float(cnt)
        answer.append((id, name, cnt, cost,date))

    return answer


async def resolve_check(mes,data,receipt: Receipt):
    poll_options = []
    # opt = ["Nothing"]
    opt = []
    for i in range(len(data)):
        if (data[i][2] == 1.0):
            opt.append(data[i][1])
            poll_options.append(i)
            if (len(opt) == 10):
                
                msg = await bot.send_poll(mes.chat.id,"За что вкидываешься?",opt,is_anonymous=False,allows_multiple_answers=True)
                opt = []
                poll_options = []

    
    cur_poll = await bot.send_poll(mes.chat.id,"За что вкидываешься?",opt,is_anonymous=False,allows_multiple_answers=True)
    print(cur_poll.poll.id)
    receipt.add_poll(cur_poll.poll.id,poll_options)


# def resolve_goods(receipt: Receipt,poll_id):
#     products_id = receipt.poll_options_id[poll_id] # index from poll to goods id
#     goods = [0]*len(products_id)
#     for key_user_id in unresolved_polls[poll_id]:
#         for j in (unresolved_polls[poll_id][key_user_id]):
#             goods[unresolved_polls[poll_id][key_user_id][j]] += 1
#     for i in range(len(goods)):
#         ratio = 1/goods[i]
#         for key_user_id in unresolved_polls[poll_id]:
#             if i in unresolved_polls[poll_id][key_user_id]:
#                 receipt.add_product(key_user_id, products_id[i], ratio)
#         receipt.add_product(user_id, products_id[i], ratio)

def save_data():
    pass # TODO save all server in case of backup

def on_complete(receipt,cur_group):
    
    s = "You resolved receipt, congrats!!!\n" + receipt.get_debts_str()
    for j in cur_group.users_id:
        s = s.replace('[' + str(j) + ']',"@" + cur_group.users_name[j])

    bot.send_message(cur_group.chat_id, text)
@dp.poll_answer_handler()
async def handle_poll_answer(quiz_answer: types.PollAnswer):
    cur_poll_id = quiz_answer.poll_id
    cur_group = -1

    for i in range(len(groups)):
        for j in range(len(groups[i].unresolved_receipts)):
            for k in range(len(groups[i].unresolved_receipts[j].poll_id_list)):
                if groups[i].unresolved_receipts[j].poll_id_list[k] == cur_poll_id:
                    cur_group = groups[i]
                    goods_id = cur_group.unresolved_receipts[j].poll_options_id[cur_poll_id]
                    for ind in quiz_answer.option_ids:
                        cur_group.unresolved_receipts[j].add_unit_product(quiz_answer.user.id,goods_id[ind])
                    if len(quiz_answer.option_ids) == 0:
                        for ind in goods_id:
                            cur_group.unresolved_receipts[j].remove_product(quiz_answer.user.id,goods_id[ind])
                    
                    # if cur_group.unresolved_receipts[j].is_complete():
                    #     on_complete(cur_group.unresolved_receipts[j], cur_group)

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    print("start command ",message.chat.id)
    gr = Group(message.chat.id)
    groups.append(gr)
    await message.reply("Hello, It is receipt analyizing bot that will help you divide cash between your roomates! To start /register")

def getGroup(group_id):
    for i in range(len(groups)):
        if (groups[i].chat_id == group_id):
            return groups[i]
    return None

@dp.message_handler(commands=['register'])
async def process_callback_button1(message: types.Message):
    cur_group = getGroup(message.chat.id)
    cur_group.add_user(message.from_user.id,message.from_user.username)

    await message.reply('You was registered')

@dp.message_handler(commands=['receipt'])
async def findReceipt(msg: types.Message):
    global amount_checks
    if not("НДС" in msg.text):
        return
    # try:    
    cur_group = getGroup(msg.chat.id)
    if len(cur_group.unresolved_receipts)!=0:
        await bot.send_message(msg.chat.id, "Sorry, but you need to resolve your previous receipt first")
        return 
    
    data = parse_receipt(msg.text[10:])
    # except Exception:
    #     return
    cur_receipt = Receipt(msg.from_user.id, data)
    cur_group.unresolved_receipts.append(cur_receipt)
    cur_group.amount_checks += 1
    await resolve_check(msg, data,cur_receipt)


@dp.message_handler(commands=['status'])
async def give_status(msg: types.Message):
    cur_group = getGroup(msg.chat.id)
    s = ""
    for i in range(len(cur_group.unresolved_receipts)):
        f_part = cur_group.unresolved_receipts[i].get_status()
        s_part = cur_group.unresolved_receipts[i].get_debts_str()
        print(f_part+ "\n" + s_part)
        for j in cur_group.users_id:
            s_part = s_part.replace('[' + str(j) + ']',"@" + cur_group.users_name[j])
            f_part = f_part.replace('[' + str(j) + ']',"@" + cur_group.users_name[j])
        # for i in range() 
        s += f_part + "\n" + s_part + "\n\n"
    await bot.send_message(msg.chat.id, s)



if __name__ == '__main__':
    executor.start_polling(dp)
