import pandas as pd
import telebot


pathUnresolved = 'data/UnResolvedReceipt.csv'
# 1951390501:AAHdfgn9-EjD1-DKT4Jv_KKwwV9De4ma6io ; Name of bot is ReceiptBot
bot = telebot.TeleBot('TOKEN')

unresolved_receipts = pd.read_csv(pathUnresolved)
tmp = unresolved_receipts['check_id']
isCheckResolved = True
if tmp.size == 0:
    amount_checks = 0
else:
    amount_checks = unresolved_receipts['check_id'].unique().max()

polls = []

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
def receive_quiz_answer(message):
    print(message.text)
def resolve_check(message,data):
    global polls
    opt = []
    for i in range(len(data)):
        if (data['amount'][i] == 1.0):
            opt.append(data['name'][i])
    message = bot.send_poll(message.chat.id,"Choose what you have bought", opt,is_anonymous=False,allows_multiple_answers=True)
    polls.append(message)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Hello, It is receipt analyizing bot that will help you divide cash between your roomates!")
@bot.message_handler(commands=['resolve'])
def resolved(message):
    for 
@bot.message_handler(content_types=['text'])
def check_receipt(message):
    global amount_checks,unresolved_receipts

    text = message.text
    bot.send_message(message.chat.id, "I saw a message")

    if not('НДС' in text):  #  receipt condition; need to be done properly later
        return
    if isCheckResolved:
        isCheckResolved = False
        data = parse_receipt(text) # parsing receipt to list of tuples

        tmp = data.drop('goods_id',inplace=False,axis=1)

        unresolved_receipts = pd.concat([unresolved_receipts,tmp],ignore_index=True)

        save_unresolved()
        resolve_check(message,data)
    


<<<<<<< HEAD
updater = bot.Updater(TOKEN)
dispatcher = updater.dispatcher
dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
=======
>>>>>>> 6d890959516e470c353f82d5a220b9d8b803de63
bot.polling()
