def secant_method(f, low, high, tol=1e-9, max_n=1e5):
    if f(low) * f(high) > 0:
        return None
    elif abs(f(low)) <= tol:
        return low
    elif abs(f(high)) <= tol:
        return high

    cur, prev = low, high
    for i in range(int(max_n) + 1):
        if abs(f(cur)) <= tol:
            return cur

        nxt = cur - f(cur) * (cur - prev) / (f(cur) - f(prev))
        cur, prev = nxt, cur

    return None


def bisection_method(f, low, high, tol=1e-9):
    if f(low) * f(high) > 0:
        return None
    elif abs(f(low)) <= tol:
        return low
    elif abs(f(high)) <= tol:
        return high

    mid = (low + high) / 2
    while abs(f(mid)) > tol:

        if f(mid) * f(low) > 0:
            low = mid
        else:
            high = mid

        mid = (low + high) / 2

    return mid

