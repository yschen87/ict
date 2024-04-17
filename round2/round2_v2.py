import datamodel
from datamodel import OrderDepth, UserId, TradingState, Order
import jsonpickle
import numpy as np


DEBUG_MODE = True

class Trader:

    LIMIT = {
        'AMETHYSTS': 20,
        'STARFRUIT': 20,
        "ORCHIDS": 100
    }
    attributes = {}

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
        if total_volume == 0:
            return -1
        else:
            return wavg_price / total_volume

    @staticmethod
    def calculate_barrier_price(order_depth, mid, barrier=10):
        sorted_buy_orders = sorted(order_depth.buy_orders.items(), reverse=True)
        sorted_sell_orders = sorted(order_depth.sell_orders.items(), reverse=False)

        buy_p_, sell_p_ = -1, -1
        buy_vol_, sell_vol_ = 0, 0
        for p, vol in sorted_buy_orders:
            if p >= mid:
                continue
            if vol >= barrier:
                buy_p_, buy_vol_ = p, vol
                break
            elif vol > buy_vol_:
                buy_p_, buy_vol_ = p, vol
        for p, vol in sorted_sell_orders:
            if p <= mid:
                continue
            vol = abs(vol)
            if vol >= barrier:
                sell_p_, sell_vol_ = p, vol
                break
            elif vol > sell_vol_:
                sell_p_, sell_vol_ = p, vol
        return buy_p_, buy_vol_, sell_p_, sell_vol_

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

    def simulate_lambda_reset(self):
        self.attributes = {}

    def run(self, state):

        # if np.random.uniform(0, 1) >= 0.9:
        #     self.simulate_reset()

        result = {}
        idx = state.timestamp // 100
        if idx >= 1 and not self.attributes:
            self.attributes = jsonpickle.decode(state.traderData)
        conversions = 0

        for product in state.order_depths:

            current_position = state.position.get(product, 0)
            order_depth = state.order_depths[product]
            sell_capacity = self.LIMIT[product] + current_position
            buy_capacity = self.LIMIT[product] - current_position
            orders = []

            if product == "AMETHYSTS":

                _orders, buy_capacity, sell_capacity = self.hit_the_book(product, order_depth,
                                                                         buy_capacity, 9999,
                                                                         sell_capacity, 10001)
                orders.extend(_orders)

                ext_buy_price, ext_buy_volume, ext_sell_price, ext_sell_volume = self.calculate_barrier_price(order_depth, 10000, 1)

                sell_price, buy_price = max(10001, ext_sell_price -1), min(9999, ext_buy_price + 1)
                if sell_capacity > 0:
                    orders.append(Order(product, sell_price, -sell_capacity))
                if buy_capacity > 0:
                    orders.append(Order(product, buy_price, buy_capacity))

            elif product == "STARFRUIT":

                prev_price = self.attributes.get("starfruit_price", None)
                if idx == 0:
                    prev_price = self.calculate_wavg_midprice(order_depth)
                elif idx != 0 and prev_price is None:
                    self.attributes = jsonpickle.decode(state.traderData)
                    prev_price = self.attributes.get("starfruit_price", None)

                ext_buy_price, ext_buy_volume, ext_sell_price, ext_sell_volume \
                    = self.calculate_barrier_price(order_depth, prev_price, 15)

                low = None if ext_buy_volume < 15 else ext_buy_price
                top = None if ext_sell_volume < 15 else ext_sell_price

                if top is None and low is None:
                    cur_price = prev_price
                    if cur_price != int(cur_price):
                        top = int(cur_price + 3.5)
                        low = int(cur_price - 3.5)
                    else:
                        top = int(cur_price + 4)
                        low = int(cur_price - 4)
                elif top is None:
                    cur_price = low + 3.5
                    top = low + 7
                elif low is None:
                    cur_price = top - 3.5
                    low = top - 7
                else:
                    cur_price = (low + top) / 2

                self.attributes['starfruit_price'] = cur_price

                if sell_capacity <= 5:
                    sell_margin, buy_margin = 1, 0.5
                elif buy_capacity <= 5:
                    sell_margin, buy_margin = 0.5, 1
                else:
                    sell_margin, buy_margin = 1, 1
                _orders, buy_capacity, sell_capacity = self.hit_the_book(product, order_depth,
                                                                         buy_capacity, cur_price - buy_margin,
                                                                         sell_capacity, cur_price + sell_margin)
                orders.extend(_orders)

                buy_price = low + 1
                if sell_capacity <= 5 and order_depth.buy_orders.get(buy_price, 0) >= 3:
                    buy_price += 1
                sell_price = top - 1
                if buy_capacity <= 5 and order_depth.sell_orders.get(sell_price, 0) >= 3:
                    sell_price -= 1

                if sell_capacity > 0:
                    orders.append(Order(product, sell_price, -sell_capacity))
                if buy_capacity > 0:
                    orders.append(Order(product, buy_price, buy_capacity))

            elif product == "ORCHIDS":

                bidPrice = state.observations.conversionObservations[product].bidPrice
                askPrice = state.observations.conversionObservations[product].askPrice
                transportFees = state.observations.conversionObservations[product].transportFees
                exportTariff = state.observations.conversionObservations[product].exportTariff
                importTariff = state.observations.conversionObservations[product].importTariff
                sunlight = state.observations.conversionObservations[product].sunlight
                humidity = state.observations.conversionObservations[product].humidity

                if idx == 0:
                    self.attributes['orchids_sell_action'] = False

                sorted_buy_orders = sorted(order_depth.buy_orders.items(), reverse=True)
                sorted_sell_orders = sorted(order_depth.sell_orders.items(), reverse=False)

                if current_position != 0:
                    conversions = -current_position

                sell_capacity = sell_capacity + conversions
                buy_capacity = buy_capacity - conversions

                if DEBUG_MODE:
                    print(f'{{"bidPrice": {bidPrice}, "askPrice": {askPrice}, "transportFees": {transportFees}, "exportTariff": {exportTariff}, "importTariff": {importTariff}, "sunlight": {sunlight}, "humidity": {humidity}, "position": {current_position}}}')

                ext_sell_price = bidPrice - transportFees - exportTariff
                ext_buy_price = askPrice + transportFees + importTariff

                _orders, buy_capacity, sell_capacity = self.hit_the_book(product, order_depth,
                                                                         buy_capacity, ext_sell_price - 0.1,
                                                                         sell_capacity, ext_buy_price + 0.1)
                orders.extend(_orders)

                # print("**", ext_buy_price, ext_sell_price)
                active_buy_price = int(round(ext_sell_price, 0)) - 2
                for i, (p, q) in enumerate(sorted_buy_orders):
                    if p > ext_buy_price:
                        continue
                    else:
                        active_buy_price = min(p + 1, active_buy_price)
                        break
                active_sell_price = int(round(ext_buy_price, 0)) + 2
                for i, (p, q) in enumerate(sorted_sell_orders):
                    if p < ext_sell_price:
                        continue
                    else:
                        active_sell_price = max(p - 1, active_sell_price)
                        break

                buy_capacity = min(buy_capacity, 10)
                sell_capacity = min(sell_capacity, 10)

                if sell_capacity > 0:
                    orders.append(Order(product, active_sell_price, -sell_capacity))
                if buy_capacity > 0:
                    orders.append(Order(product, active_buy_price, buy_capacity))

                cur_price = self.calculate_wavg_midprice(order_depth)
                #
                # if idx > 0:
                #     prev_humidity = self.attributes.get("humidity", 70)
                #     flag1 = (humidity - prev_humidity < 0) & (humidity >= 85)
                #     flag2 = (humidity - prev_humidity > 0) & (humidity <= 55)
                #     flag = flag1 | flag2
                #     if idx <= 5:
                #         self.attributes['humidity_direction'] += [flag]
                #     else:
                #         self.attributes['humidity_direction'] = self.attributes['humidity_direction'][1:] + [flag]
                #
                # if idx > 5:
                #     if sum(self.attributes['humidity_direction']) == 5:
                #         self.attributes['orchids_active_mm'] = False
                #         sell_capacity_ = min(sell_capacity, 80)

                self.attributes['orchids_price'] = cur_price

            result[product] = orders

        trader_data = jsonpickle.encode(self.attributes)

        return result, conversions, trader_data