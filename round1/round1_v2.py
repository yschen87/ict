import datamodel
from datamodel import OrderDepth, UserId, TradingState, Order

class Trader:

    LIMIT = {
        'AMETHYSTS': 20,
        'STARFRUIT': 20
    }

    starfruit_price_history = []
    starfruit_initial_price = 5000
    ma_window_size = 1

    @staticmethod
    def calculate_wavg_midprice(order_depth):
        sorted_buy_orders = sorted(order_depth.buy_orders.items(), reverse=True)
        sorted_sell_orders = sorted(order_depth.sell_orders.items(), reverse=False)
        total_volume = 0
        wavg_price = 0

        for p, vol in sorted_buy_orders:
            wavg_price += p * vol
            total_volume += vol
        for p, vol in sorted_sell_orders:
            vol = abs(vol)
            wavg_price += p * vol
            total_volume += vol
        wavg_price /= total_volume
        return wavg_price

    @staticmethod
    def calculate_barrier_price(order_depth, barrier=10):
        sorted_buy_orders = sorted(order_depth.buy_orders.items(), reverse=True)
        sorted_sell_orders = sorted(order_depth.sell_orders.items(), reverse=False)
        buy_p_, sell_p_ = -1, -1
        buy_vol_, sell_vol_ = 0, 0
        for p, vol in sorted_buy_orders:
            if vol >= barrier:
                buy_p_, buy_vol_ = p, vol
                break
            elif vol > buy_vol_:
                buy_p_, buy_vol_ = p, vol
        for p, vol in sorted_sell_orders:
            vol = abs(vol)
            if vol >= barrier:
                sell_p_, sell_vol_ = p, vol
                break
            elif vol > sell_vol_:
                sell_p_, sell_vol_ = p, vol
        return buy_p_, sell_p_

    @staticmethod
    def hit_the_book(product, order_depth, buy_capacity, buy_price, sell_capacity, sell_price):
        sorted_buy_orders = sorted(order_depth.buy_orders.items(), reverse=True)
        sorted_sell_orders = sorted(order_depth.sell_orders.items(), reverse=False)
        orders = []
        for p, vol in sorted_buy_orders:
            vol = abs(vol)
            if p >= sell_price:
                s_amt = min(sell_capacity, vol)
                if s_amt > 0:
                    sell_capacity -= s_amt
                    orders.append(Order(product, p, -s_amt))
        for p, vol in sorted_sell_orders:
            vol = abs(vol)
            if p <= buy_price:
                b_amt = min(buy_capacity, vol)
                if b_amt > 0:
                    buy_capacity -= b_amt
                    orders.append(Order(product, p, b_amt))
        return orders, buy_capacity, sell_capacity

    def run(self, state):

        result = {}
        idx = state.timestamp // 100

        for product in state.order_depths:

            current_position = state.position.get(product, 0)
            order_depth = state.order_depths[product]
            orders = []

            if product == "AMETHYSTS":
                sell_capacity = self.LIMIT[product] + current_position
                buy_capacity = self.LIMIT[product] - current_position
                _orders, buy_capacity, sell_capacity = self.hit_the_book(product, order_depth, buy_capacity, 9999,
                                                                         sell_capacity, 10001)
                orders.extend(_orders)
                amethysts_buy_price = 9998 if sell_capacity <= 5 else 9996
                amethysts_sell_price = 10002 if buy_capacity <= 5 else 10004
                if sell_capacity > 0:
                    orders.append(Order(product, amethysts_sell_price, -sell_capacity))
                if buy_capacity > 0:
                    orders.append(Order(product, amethysts_buy_price, buy_capacity))

            elif product == "STARFRUIT":

                wavg_price = self.calculate_wavg_midprice(order_depth)

                sell_capacity = self.LIMIT[product] + current_position
                buy_capacity = self.LIMIT[product] - current_position

                _orders, buy_capacity, sell_capacity = self.hit_the_book(product, order_depth,
                                                                         buy_capacity, wavg_price - 0.5,
                                                                         sell_capacity, wavg_price + 0.5)
                orders.extend(_orders)
                print(idx, wavg_price, buy_capacity, sell_capacity)
                if sell_capacity <= 5:
                    sell_margin, buy_margin = 4, 1
                if sell_capacity <= 10:
                    sell_margin, buy_margin = 3, 1
                elif buy_capacity <= 5:
                    sell_margin, buy_margin = 1, 4
                elif buy_capacity <= 10:
                    sell_margin, buy_margin = 1, 3
                else:
                    sell_margin, buy_margin = 2, 2

                wavg_price = int(round(wavg_price, 0))
                if sell_capacity > 0:
                    orders.append(Order(product, wavg_price + sell_margin, -sell_capacity))
                if buy_capacity > 0:
                    orders.append(Order(product, wavg_price - buy_margin, buy_capacity))

            result[product] = orders

        return result, None, "Taeja"