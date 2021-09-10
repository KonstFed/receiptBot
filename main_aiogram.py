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

f = open("config.txt","r")
TOKEN = f.read()

chat_groups = []

'''
chats_id = {}
unresolved_receipts = {}
unresolved_polls = {} # key в этом словаре poll id, value list id пользователей кто вкинулся и за что
users_id = []
'''
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
        id = int(id)
        cost, other = strings[i+1].split(" x ")
        cnt, price = other.split(" = ")
        cost, cnt = float(cost), float(cnt)
        answer.append((id, name, cnt, cost,date))

    return answer

async def resolve_check(mes,data,receipt: Receipt):
    poll_options = []
    opt = ["Nothing"]
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


def resolve_goods(receipt: Receipt,poll_id):
    products_id = receipt.poll_options_id[poll_id] # index from poll to goods id
    goods = [0]*len(products_id)
    for key_user_id in unresolved_polls[poll_id]:
        # cur_product_ids = [products_id[i] for i in unresolved_polls[poll_id][key_user_id]]
        for j in (unresolved_polls[poll_id][key_user_id]):
            goods[unresolved_polls[poll_id][key_user_id][j]] += 1
    for i in range(len(goods)):
        ratio = 1/goods[i]
        for key_user_id in unresolved_polls[poll_id]:
            if i in unresolved_polls[poll_id][key_user_id]:
                receipt.add_product(key_user_id, products_id[i], ratio)
        receipt.add_product(user_id, products_id[i], ratio)
    

@dp.poll_answer_handler()
async def handle_poll_answer(quiz_answer: types.PollAnswer):

    for i in range(len(unresolved_receipts)):
        for j in range(len(unresolved_receipts[i].poll_id_list)):
            if unresolved_receipts[i].poll_id_list[j] == quiz_answer.poll_id:
                if len(unresolved_polls) == len(users_id):

                    resolve_goods(unresolved_receipts[i],quiz_answer.poll_id)

                if quiz_answer.user.id not in unresolved_polls[quiz_answer.poll_id]:
                    tmp = {
                        quiz_answer.user.id: quiz_answer.option_ids
                    }
                    unresolved_polls[quiz_answer.poll_id].append(tmp)
                

    print("answer to poll is ",quiz_answer.poll_id)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    print("start command ",message.chat.id)
    await message.reply("Hello, It is receipt analyizing bot that will help you divide cash between your roomates! To start /register")


@dp.message_handler(commands=['register'])
async def process_callback_button1(message: types.Message):

    if message.chat.id in chats_id:
        if message.from_user.id not in chats_id[message.chat.id]:
            chats_id[message.chat.id].append(message.from_user.id)
    else:
        chats_id[message.chat.id] = [message.from_user.id]
        
    await message.reply('You was registered')

@dp.message_handler(commands=['receipt'])
async def findReceipt(msg: types.Message):
    global amount_checks
    if not("НДС" in msg.text):
        return
    
    data = parse_receipt(msg.text)
    cur_receipt = Receipt(msg.from_user.id, data)
    unresolved_receipts[amount_checks] = cur_receipt
    amount_checks += 1
    await resolve_check(msg, data,cur_receipt)

if __name__ == '__main__':
    executor.start_polling(dp)
