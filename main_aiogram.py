from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import pandas as pd
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import classes


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
unresolved_receipts = {}
amount_checks = 0
users_id = [] 
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
    opt = []
    for i in range(len(data)):
        if (data[i][2] == 1.0):
            opt.append(data[i][1])
            if (len(opt) == 10):
                receipt.add_poll()
                msg = await bot.send_poll(mes.chat.id,"За что вкидываешься?",opt,is_anonymous=False,allows_multiple_answers=True)
                opt = []

    
    msg = await bot.send_poll(mes.chat.id,"За что вкидываешься?",opt,is_anonymous=False,allows_multiple_answers=True)

@dp.poll_answer_handler()
async def handle_poll_answer(quiz_answer: types.PollAnswer):
    for i in range(len(unresolved_receipts)):
        for j in range(len(unresolved_receipts[i].poll_id_list)):
            if unresolved_receipts[i].poll_id_list[j] == quiz_answer.poll_id:
                quiz_answer.option_ids
                unresolved_receipts[i].
    print("answer to poll is ",quiz_answer)

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Hello, It is receipt analyizing bot that will help you divide cash between your roomates!",reply_markup=inline_reg)

@dp.callback_query_handler(text='register_button')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if not(callback_query.from_user.id in users_id):
        users_id.append(callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, 'You was registered')
    print(users_id)

@dp.message_handler()
async def findReceipt(msg: types.Message):
    
    if not("НДС" in msg.text):
        return
    
    data = parse_receipt(msg.text)
    cur_receipt = Receipt(msg.from_user.id, data)
    unresolved_receipts[amount_checks] = cur_receipt
    amount_checks += 1
    await resolve_check(msg, data)

if __name__ == '__main__':
    executor.start_polling(dp)
