class Receipt:
    def __init__(self, owner_id: int, products: list):
        self.owner_id = owner_id
        self.products = {}
        for product in products:
            self.products[product[0]] = product
        self.poll_id_list = []
        self.participants = {}  # key - user_id, value - list of goods with ratios (product_id, ratio)
        self.poll_options_id = {}

    def add_poll(self, poll_id: int, poll_options):
        self.poll_id_list.append(poll_id)
        self.poll_options_id[poll_id] = poll_options

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
                if self.participants[participant][0] == product_id:
                    answer += " [{}] - {},".format(participant, self.participants[participant][1])
                    found = True

            if not found:
                answer += " no one bought this;\n"
            else:
                answer = answer[:-1] + ";\n"

        return answer
