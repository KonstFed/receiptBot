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

        if user_id in self.unit_products[product_id]:
            self.unit_products[product_id].remove(user_id)
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
            answer += self.products[product_id][1] + ":"
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

        return answer

    def get_debts_str(self):
        answer = "Following persons should give [{}] some money:".format(self.owner_id)

        debts = self.get_debts()
        for user_id in debts:
            answer += " [{}] - {},".format(user_id, debts[user_id])

        if len(debts) == 0:
            answer += " no one\n"
        else:
            answer = answer[:-1] + "\n"

        return answer
