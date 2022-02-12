import uuid


class User:
    users = {}

    def __init__(self, telegram_id):
        self.telegram_id = telegram_id
        self.allowed = True

    @classmethod
    def get(cls, telegram_id):
        return cls.users.get(telegram_id)

    @classmethod
    def create(cls, telegram_id):
        user = User(telegram_id)
        cls.users[telegram_id] = user
        return user

    @classmethod
    def get_or_create(cls, telegram_id):
        user = cls.get(telegram_id)
        if user is None:
            user = cls.create(telegram_id)
        return user

    def block(self):
        self.allowed = False

    def allow(self):
        self.allowed = True


id = 1


class Item:
    items = {}

    def __init__(self, name, url, item_id):
        self.url = url
        self.name = name
        self.item_id = item_id

    @classmethod
    def get(cls, name):
        return cls.items.get(name)

    @classmethod
    def create(cls, name, url):
        global id
        item_id = id
        id += 1
        item = Item(name, url, item_id)
        cls.items[name] = item
        return item


Item.create("Мандарин", "https://m.dom-eda.com/uploads/images/catalog/item/53275a4f46/c4f7252f9e_1000.jpg")
Item.create("Яблоко",
            "https://static9.depositphotos.com/1011549/1208/i/600/depositphotos_12089121-stock-photo-green-apple-with-leaf.jpg")
