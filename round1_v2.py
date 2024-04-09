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
    def calculate_starfruit_order_amt(capacity):
        return capacity * 0.5

    def run(self, state):

        result = {}
        idx = state.timestamp // 100

        for product in state.order_depths:

            current_position = state.position.get(product, 0)
            order_depth = state.order_depths[product]
            orders = []

            if product == "AMETHYSTS":

                sell_capacity = - self.LIMIT[product] - current_position
                buy_capacity = self.LIMIT[product] - current_position

                if sell_capacity < 0:
                    orders.append(Order(product, 10001, sell_capacity))
                if buy_capacity > 0:
                    orders.append(Order(product, 9999, buy_capacity))

            elif product == "STARFRUIT":

                wavg_price = self.calculate_wavg_midprice(order_depth)

                self.starfruit_price_history.append(wavg_price)

                ll = min(self.ma_window_size, len(self.starfruit_price_history))
                ma_price = 0
                for i in range(1, ll + 1):
                    ma_price += self.starfruit_price_history[-i]
                ma_price = int(ma_price / ll)

                if idx <= self.ma_window_size:
                    sell_capacity = - self.LIMIT[product] - current_position + 15
                    buy_capacity = self.LIMIT[product] - current_position - 15
                    sell_margin, buy_margin = 1, 1
                if idx <= 9500:
                    sell_capacity = - self.LIMIT[product] - current_position + 0
                    buy_capacity = self.LIMIT[product] - current_position
                    sell_margin, buy_margin = 0, 0
                else:
                    sell_capacity = - self.LIMIT[product] - current_position + 0
                    buy_capacity = self.LIMIT[product] - current_position - 0
                    sell_margin, buy_margin = 0, 0

                if sell_capacity < 0:
                    sell_capacity = int(0.5 * sell_capacity) - sell_capacity % 2
                    orders.append(Order(product, ma_price + sell_margin, sell_capacity))
                if buy_capacity > 0:
                    buy_capacity = int(0.5 * buy_capacity) + buy_capacity % 2
                    orders.append(Order(product, ma_price - buy_margin, buy_capacity))

            result[product] = orders

        return result, None, "Taeja"