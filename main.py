from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string


class Trader:

    LIMIT = {
        'AMETHYSTS': 20,
        'STARFRUIT': 20
    }

    price_history = dict()
    ma_window_size = 5
    current_sum = 0

    def run(self, state: TradingState):

        result = {}

        for product in state.order_depths:

            current_position = state.position.get(product, 0)
            orders = []

            sell_capacity = - self.LIMIT[product] - current_position
            buy_capacity = self.LIMIT[product] - current_position

            if product == "AMETHYSTS":

                if sell_capacity < 0:
                    orders.append(Order(product, 10001, sell_capacity))
                if buy_capacity > 0:
                    orders.append(Order(product, 9999, buy_capacity))

            # if product == "STARFRUIT":
            #
            #     order_depth = state.order_depths[product]
            #     sorted_buy_orders = sorted(order_depth.buy_orders.items(), reverse=True)
            #     print(sorted_buy_orders)

            #     sorted_sell_orders = sorted(order_depth.sell_orders.items(), reverse=False)
            #     total_volume = 0
            #     wavg_price = 0
            #
            #     for p, vol in sorted_buy_orders:
            #         wavg_price = p * vol
            #         total_volume += vol
            #     for p, vol in sorted_sell_orders:
            #         wavg_price = p * vol
            #         total_volume += vol
            #
            #     wavg_price /= total_volume
            #     self.price_history.append(wavg_price)
            #
            #     idx = state.timestamp // 100
            #     if idx < self.ma_window_size:
            #         self.current_sum += self.price_history[-1]
            #         mp = self.current_sum / (idx + 1)
            #     else:
            #         self.current_sum += self.price_history[-1] - self.price_history[idx - self.ma_window_size]
            #         mp = self.current_sum / self.ma_window_size
            #
            #     orders.append(Order(product, mp + 1, sell_capacity))
            #     orders.append(Order(product, mp - 1, buy_capacity))

            result[product] = orders

        return result, None, "Taeja"