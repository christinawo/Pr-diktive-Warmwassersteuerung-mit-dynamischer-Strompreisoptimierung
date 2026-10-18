def adjust_prices(prices, factor, mean_price):
    new_prices = prices.copy()
    new_prices["price"] = mean_price + factor * (prices["price"] - mean_price)
    new_prices["price_ct_per_kWh"] = new_prices["price"] / 10

    return new_prices