import pandas as pd
import telebot
pathUnresolved = 'data/UnResolvedReceipt.csv'
# 1951390501:AAHdfgn9-EjD1-DKT4Jv_KKwwV9De4ma6io ; Name of bot is ReceiptBot
bot = telebot.TeleBot('1951390501:AAHdfgn9-EjD1-DKT4Jv_KKwwV9De4ma6io')

unresolved_receipts = pd.read_csv(pathUnresolved)
tmp = unresolved_receipts['check_id']
if tmp.size == 0:
    amount_checks = 0
else:
    amount_checks = unresolved_receipts['check_id'].unique().max()



def save_unresolved():
    global unresolved_receipts,pathUnresolved
    unresolved_receipts.to_csv(pathUnresolved,sep=',',index=False)
def parse_receipt(raw_str: str):
    global amount_checks
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

     # parsing receipt to list of tuples
 

    data = pd.DataFrame(answer,columns =['goods_id', 'name', 'amount','unit_price','date'])
    data.insert(loc = 0, column='check_id',value= amount_checks+1)
    amount_checks += 1
    return data
def resolve_check(message,data):
    bot.send_poll(message.chat.id,  options)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Hello, It is receipt analyizing bot that will help you divide cash between your roomates!")

@bot.message_handler(content_types=['text'])
def check_receipt(message):
    global amount_checks,unresolved_receipts

    text = message.text
    bot.send_message(message.chat.id, "I saw a message")

    if not('НДС' in text):  #  receipt condition; need to be done properly later
        return
    data = parse_receipt(text) # parsing receipt to list of tuples

    tmp = data.drop('goods_id',inplace=False,axis=1)

    unresolved_receipts = pd.concat([unresolved_receipts,tmp],ignore_index=True)

    save_unresolved()


bot.polling()