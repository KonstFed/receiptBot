from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from classes import Receipt
import json


class Group:
    def __init__(self, chat_id):
        self.debts = []
        self.chat_id = chat_id
        self.amount_checks = 0
        self.users_id = []
        self.users_name = {}
        self.unresolved_receipts = []

    def add_user(self, user_id, nick):
        self.users_id.append(user_id)
        self.users_name[user_id] = nick
        tmp = []
        # for i in range(self.users_id):
        #     tmp.append(0)

    def from_json(self, chat_id, users_id, users_name, unresolved_receipts):
        self.chat_id = chat_id
        self.users_id = users_id
        self.users_name = users_name
        self.unresolved_receipts = unresolved_receipts


f = open("config.txt", "r")
TOKEN = f.read()
f.close()

groups = []

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


def save_data():
    tmp = []
    for cur_group in groups:
        s = []
        for i in range(len(cur_group.unresolved_receipts)):
            s.append(cur_group.unresolved_receipts[i].get_save_dict())

        tmp.append({"chat_id": cur_group.chat_id,
                    "amount_checks": cur_group.amount_checks,
                    "users_id": cur_group.users_id,
                    "users_name": cur_group.users_name,
                    "unresolved_receipts": s,
                    })

    js = json.dumps(tmp)
    f = open('data/data.json', 'w')
    f.write(js)
    f.close()


def read_data():
    try:
        with open('data/data.json', 'r') as f:
            js = f.readline()
            raw_data = json.loads(js)
            num_groups = int(len(raw_data))
            for i in range(num_groups):
                cur = raw_data[i]
                unrs_recs = []
                for j in range(len(cur['unresolved_receipts'])):
                    rec = Receipt(0, [])
                    rec.load_from_dict(cur['unresolved_receipts'][j])
                    unrs_recs.append(rec)
                tmp = Group(cur['chat_id'])
                tmp.from_json(cur['chat_id'], cur['users_id'], cur['users_name'], unrs_recs)
                tmp.users_name = dict(map(lambda k, v: (int(k), v), tmp.users_name.keys(), tmp.users_name.values()))
                groups.append(tmp)
    except Exception:
        return


def parse_receipt(raw_str: str):
    answer = []
    strings = raw_str.split("\n")

    if strings[0] == "":
        strings.pop(0)

    date = strings[1][7:]

    for i in range(4, len(strings) - 16, 3):
        product_id, name = strings[i].split(". ", 1)
        product_id = int(product_id) - 1  # Because we want our indexes to start from 0
        cost, other = strings[i + 1].split(" x ")
        cnt, price = other.split(" = ")
        cost, cnt = float(cost), float(cnt)
        answer.append((product_id, name, cnt, cost, date))

    return answer


async def resolve_check(mes, data, receipt: Receipt):
    poll_options = []
    # opt = ["Nothing"]
    opt = []
    for i in range(len(data)):
        if data[i][2] == 1.0:
            opt.append(data[i][1])
            poll_options.append(i)
            if len(opt) == 10:
                msg = await bot.send_poll(mes.chat.id, "За что вкидываешься?", opt, is_anonymous=False,
                                          allows_multiple_answers=True)
                opt = []
                poll_options = []

    cur_poll = await bot.send_poll(mes.chat.id, "За что вкидываешься?", opt, is_anonymous=False,
                                   allows_multiple_answers=True)
    print(cur_poll.poll.id)
    receipt.add_poll(cur_poll.poll.id, poll_options)
    save_data()


async def on_complete(receipt, cur_group):
    s = "You resolved receipt, congrats!!!\n" + receipt.get_debts_str()
    for j in cur_group.users_id:
        s = s.replace('[' + str(j) + ']', "@" + cur_group.users_name[j])
    cur_group.unresolved_receipts = []
    await bot.send_message(cur_group.chat_id, s)


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
                        cur_group.unresolved_receipts[j].add_unit_product(quiz_answer.user.id, goods_id[ind])
                    if len(quiz_answer.option_ids) == 0:
                        for ind in goods_id:
                            cur_group.unresolved_receipts[j].remove_product(quiz_answer.user.id, goods_id[ind])

    save_data()


@dp.message_handler(commands=['done'])
async def process_start_command(message: types.Message):
    try:
        cur_group = getGroup(message.chat.id)
        if cur_group.unresolved_receipts[0].is_complete():
            await on_complete(cur_group.unresolved_receipts[0], cur_group)
        else:
            await bot.send_message(message.chat.id, "You have not finished your receipt")
    except Exception:
        await send_message_fuck(message)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    try:
        print("start command ", message.chat.id)
        for gr in groups:
            if gr.chat_id == message.chat.id:
                return
        gr = Group(message.chat.id)
        groups.append(gr)
        read_data()
        await message.reply(
            "Hello, It is receipt analyizing bot that will help you divide cash between your roomates! To start "
            "/register")
    except Exception:
        await send_message_fuck(message)


def getGroup(group_id):
    for i in range(len(groups)):
        if groups[i].chat_id == group_id:
            return groups[i]
    return None


@dp.message_handler(commands=['register'])
async def process_callback_button1(message: types.Message):
    try:
        cur_group = getGroup(message.chat.id)
        if message.from_user.id in cur_group.users_id:
            await message.reply("You are already registered")
            return
        cur_group.add_user(message.from_user.id, message.from_user.username)
        save_data()
        await message.reply('You were registered')
    except Exception:
        await send_message_fuck(message)


@dp.message_handler(commands=['receipt'])
async def findReceipt(msg: types.Message):
    try:

        if not ("НДС" in msg.text):
            return

        cur_group = getGroup(msg.chat.id)
        if len(cur_group.unresolved_receipts) != 0:
            await bot.send_message(msg.chat.id, "Sorry, but you need to resolve your previous receipt first")
            return

        data = msg.text.replace("/receipt", "")
        data = parse_receipt(data)
        cur_receipt = Receipt(msg.from_user.id, data)
        cur_group.unresolved_receipts.append(cur_receipt)
        cur_group.amount_checks += 1
        save_data()
        await resolve_check(msg, data, cur_receipt)
    except Exception:
        await send_message_fuck(msg)
        return


@dp.message_handler(commands=['status'])
async def give_status(msg: types.Message):
    try:
        cur_group = getGroup(msg.chat.id)
        s = ""
        for i in range(len(cur_group.unresolved_receipts)):
            f_part = cur_group.unresolved_receipts[i].get_status()
            s_part = cur_group.unresolved_receipts[i].get_debts_str()
            print(f_part + "\n" + s_part)
            for j in cur_group.users_id:
                s_part = s_part.replace('[' + str(j) + ']', "@" + cur_group.users_name[j])
                f_part = f_part.replace('[' + str(j) + ']', "@" + cur_group.users_name[j])
            # for i in range() 
            s += f_part + "\n" + s_part + "\n\n"
        await bot.send_message(msg.chat.id, s)
    except Exception:
        await send_message_fuck(msg)
        return


async def send_message_fuck(msg):
    s = "Wrong command, go fuck yourself"
    await msg.reply(s)


@dp.message_handler(commands=['add'])
async def addRatio(msg: types.Message):
    try:
        data = msg.text.split()
        cur_group = getGroup(msg.chat.id)
        cur_rec = cur_group.unresolved_receipts[0]
        s = data[2]
        if '%' in data[2]:
            s = s.replace('%', '')
            ratio = int(s) / 100
        else:
            ratio = float(s)
        cur_rec.add_product(msg.from_user.id, int(data[1]), ratio)
        save_data()
    except Exception:
        await send_message_fuck(msg)
        return


if __name__ == '__main__':
    read_data()
    executor.start_polling(dp)
