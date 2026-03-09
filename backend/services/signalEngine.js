export function generateSignal(prices) {

    const shortMA = average(prices.slice(-5));
    const longMA = average(prices.slice(-20));

    if (shortMA > longMA) {
        return "BUY";
    }

    if (shortMA < longMA) {
        return "SELL";
    }

    return "HOLD";
}

function average(arr) {
    return arr.reduce((a, b) => a + b, 0) / arr.length;
}