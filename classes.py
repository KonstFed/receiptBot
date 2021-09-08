class Receipt:
    def __init__(self, owner_id: int, products: list):
        self.owner_id = owner_id
        self.products = {}
        for product in products:
            self.products[product[0]] = product
        self.poll_id_list = []
        self.participants = {}  # key - user_id, value - list of goods with ratios (product_id, ratio)

    def add_poll(self, poll_id: int):
        self.poll_id_list.append(poll_id)

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
        pass  # TODO

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
