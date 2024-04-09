from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string


class Trader:

    LIMIT = {
        'AMETHYSTS': 20,
        'STARFRUIT': 20
    }

    starfruit_price_history = []
    starfruit_initial_price = 5000
    ma_window_size = 10

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
            elif vol > buy_vol_:
                sell_p_, sell_vol_ = p, vol
        return buy_p_, sell_p_

    def run(self, state: TradingState):

        result = {}
        idx = state.timestamp // 100

        for product in state.order_depths:

            current_position = state.position.get(product, 0)
            order_depth = state.order_depths[product]
            orders = []

            if product == "AMETHYSTS":

                sell_capacity = - self.LIMIT[product] - current_position
                buy_capacity = self.LIMIT[product] - current_position

                b, s = self.calculate_barrier_price(order_depth, 1)

                if sell_capacity < 0:
                    orders.append(Order(product, 10001, sell_capacity))
                if buy_capacity > 0:
                    orders.append(Order(product, 9999, buy_capacity))

            if product == "STARFRUIT":

                wavg_price = self.calculate_wavg_midprice(order_depth)
                self.starfruit_price_history.append(wavg_price)

                ll = min(self.ma_window_size, len(self.starfruit_price_history))
                mp = 0
                for i in range(1, ll + 1):
                    mp += self.starfruit_price_history[-i]
                mp = int(mp / ll)

                if idx < 250:
                    sell_capacity = - self.LIMIT[product] - current_position + 15
                    buy_capacity = self.LIMIT[product] - current_position - 15
                    sell_margin, buy_margin = 2, 2
                elif idx <= 9500:
                    if mp <= self.starfruit_initial_price:
                        sell_capacity = - self.LIMIT[product] - current_position
                        buy_capacity = self.LIMIT[product] - current_position - 15
                        sell_margin, buy_margin = 1, 2
                    elif mp >= self.starfruit_initial_price:
                        sell_capacity = - self.LIMIT[product] - current_position + 15
                        buy_capacity = self.LIMIT[product] - current_position
                        sell_margin, buy_margin = 2, 1
                else:
                    if mp <= self.starfruit_initial_price:
                        sell_capacity = - self.LIMIT[product] - current_position
                        buy_capacity = self.LIMIT[product] - current_position - 20
                        sell_margin, buy_margin = 1, 2
                    elif mp >= self.starfruit_initial_price:
                        sell_capacity = - self.LIMIT[product] - current_position + 20
                        buy_capacity = self.LIMIT[product] - current_position
                        sell_margin, buy_margin = 2, 1

                if sell_capacity < 0:
                    orders.append(Order(product, mp + sell_margin, sell_capacity))
                if buy_capacity > 0:
                    orders.append(Order(product, mp - buy_margin, buy_capacity))

            result[product] = orders

        return result, None, "Taeja"