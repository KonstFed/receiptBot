import json


class Receipt:
    def __init__(self, owner_id: int, products: list):
        self.owner_id = owner_id
        self.products = {}
        for product in products:
            self.products[product[0]] = product
        self.poll_id_list = []
        self.participants = {}  # key - user_id, value - list of goods with ratios (product_id, ratio)
        self.poll_options_id = {}
        self.unit_products = {}  # key - product_id, value - list of users who will by it

    def add_poll(self, poll_id: int, poll_options):
        self.poll_id_list.append(poll_id)
        self.poll_options_id[poll_id] = poll_options

    def add_unit_product(self, user_id: int, product_id: int):  # For unit(единичных) products
        if product_id not in self.unit_products:
            self.unit_products[product_id] = []

        if user_id not in self.unit_products[product_id]:
            self.unit_products[product_id].append(user_id)
            self.calculate_unit_product(product_id)

    def calculate_unit_product(self, product_id: int):
        ratio = 1 / len(self.unit_products[product_id])
        for user in self.unit_products[product_id]:
            self.add_product(user, product_id, ratio)

    def add_product(self, user_id: int, product_id: int, ratio: float):
        if product_id not in self.products:
            # ERROR
            return

        if user_id not in self.participants:
            self.participants[user_id] = []

        # Check if we already have product in list (if so, delete it, so we can overwrite it)
        for product_id_in_list, _ in self.participants[user_id]:
            if product_id_in_list == product_id:
                self.participants[user_id].remove((product_id_in_list, _))
                break

        self.participants[user_id].append((product_id, ratio))

    def get_debts(self):
        answer = {}

        for user_id in self.participants:
            debt = 0
            for product_id, ratio in self.participants[user_id]:
                product = self.products[product_id]
                debt += product[2] * product[3] * ratio  # cnt * cost * ratio
            answer[user_id] = debt

        return answer

    def remove_product(self, user_id: int, product_id: int):
        if user_id not in self.participants:
            return

        for product, ratio in self.participants[user_id]:
            if product_id == product:
                self.participants[user_id].remove((product, ratio))
                break

        if product_id in self.unit_products and user_id in self.unit_products[product_id]:
            self.unit_products[product_id].remove(user_id)
            if len(self.unit_products[product_id]) == 0:
                self.unit_products.pop(product_id)
            else:
                self.calculate_unit_product(product_id)

        if len(self.participants[user_id]) == 0:
            self.participants.pop(user_id)

    def is_complete(self):
        remaining_products = {}
        for product_id in self.products:
            remaining_products[product_id] = 1

        for user_id in self.participants:
            for product_id, ratio in self.participants[user_id]:
                remaining_products[product_id] -= ratio

        for ratio in remaining_products.values():
            if abs(ratio) > 0.05:
                return False

        return True

    def get_product_ratios(self):
        answer = {}
        for product_id, ratio in self.participants.values():
            if product_id not in answer:
                answer[product_id] = 0
            answer[product_id] += ratio

        return answer

    def get_status(self):
        answer = "Owner: [{}]\n".format(self.owner_id)

        for product_id in self.products:  # product: id, name, cnt, cost, date
            answer += "(" + str(self.products[product_id]) + ") " + self.products[product_id][1] + ":"
            found = False
            for participant in self.participants:
                for product in self.participants[participant]:
                    if product[0] == product_id:
                        answer += " [{}] - {},".format(participant, product[1])
                        found = True

            if not found:
                answer += " no one bought this;\n"
            else:
                answer = answer[:-1] + ";\n"

            answer += "\n"

        return answer

    def get_debts_str(self):
        answer = "Following persons should give [{}] some money:".format(self.owner_id)

        debts = self.get_debts()
        flag = False
        for user_id in debts:
            if user_id == self.owner_id:
                continue
            flag = True
            answer += " [{}] - {},".format(user_id, debts[user_id])

        if not flag:
            answer += " no one\n"
        else:
            answer = answer[:-1] + "\n"

        return answer

    def get_save_json(self):
        return json.dumps({"owner_id": self.owner_id,
                           "products": self.products,
                           "poll_id_list": self.poll_id_list,
                           "participants": self.participants,
                           "poll_options_id": self.poll_options_id,
                           "unit_products": self.unit_products})

    def get_save_dict(self):
        return {"owner_id": self.owner_id,
                "products": self.products,
                "poll_id_list": self.poll_id_list,
                "participants": self.participants,
                "poll_options_id": self.poll_options_id,
                "unit_products": self.unit_products}

    def fix_keys(self):
        # This function changes keys from str to dict
        # It is needed after loading data

        self.participants = dict(map(lambda k, v: (int(k), v), self.participants.keys(), self.participants.values()))
        self.products = dict(map(lambda k, v: (int(k), v), self.products.keys(), self.products.values()))
        self.unit_products = dict(map(lambda k, v: (int(k), v), self.unit_products.keys(), self.unit_products.values()))

    def load_from_json(self, json_str: str):
        values = json.loads(json_str)
        self.owner_id = values["owner_id"]
        self.products = values["products"]
        self.poll_id_list = values["poll_id_list"]
        self.participants = values["participants"]
        self.poll_options_id = values["poll_options_id"]
        self.unit_products = values["unit_products"]

        self.fix_keys()

    def load_from_dict(self, values: dict):
        self.owner_id = values["owner_id"]
        self.products = values["products"]
        self.poll_id_list = values["poll_id_list"]
        self.participants = values["participants"]
        self.poll_options_id = values["poll_options_id"]
        self.unit_products = values["unit_products"]

        self.fix_keys()


if __name__ == "__main__":
    receipt = Receipt(126, [(7, "Name", 67, 32, "date"), (9, "AbobA", 44, 2, "date")])
    receipt.add_unit_product(4, 9)
    receipt.add_unit_product(4, 7)
    receipt.remove_product(4, 7)

    d = receipt.get_save_dict()
    print(d)
    receipt.load_from_dict(d)
    d = receipt.get_save_dict()
    print(d)

    print(d == d)
