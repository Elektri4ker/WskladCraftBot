class DataBaseProxy:
    db = None

    @staticmethod
    def setDb(db):
        DataBaseProxy.db = db

class Resources(DataBaseProxy):

    @staticmethod
    def resetResource(name, cost):
        res = DataBaseProxy.db.Resources.find_one({'name': name})
        if not res:
            DataBaseProxy.db.Resources.insert_one({'name': name, 'cost': cost})
            return 2

        if res['cost'] != cost:
            DataBaseProxy.db.Resources.update_one({'name': name}, {'$set': {'cost': cost}})
            return 1

        return 0

    @staticmethod
    def getResource(name):
        return DataBaseProxy.db.Resources.find_one({'name': name})

    @staticmethod
    def getAll():
        a_res = []
        for res in DataBaseProxy.db.Resources.find():
            a_res.append(res)

        return a_res

class Users(DataBaseProxy):

    @staticmethod
    def getUserStock(name, user_stock, unknown_res_names):
        user = DataBaseProxy.db.Users.find_one('name')
        if not user:
            return False

        unknown_res_names = []
        #add 'cost' field to all stock entries
        for stock_entry in user['stock']:
            res = Resources.getResource(stock_entry['name'])
            if not res:
                unknown_res_names.append(stock_entry['name'])
            else:
                stock_entry['cost'] = res['cost']

        user_stock = user['stock']
        return True

    @staticmethod
    def resetUserStock(name, new_stock):
        DataBaseProxy.db.Users.update({'name': name}, {'$set': {'stock': new_stock}}, True)

    @staticmethod
    def calcStockCost(user_stock):
        cost = 0
        for stock_entry in user_stock:
            if user_res['cost']:
                cost += stock_entry['cost']

        return cost
