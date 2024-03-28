def secant_method(f, low, high, target=0, tol=1e-9, max_n=1e5):

    f_ = (lambda x: f(x) - target) if target != 0 else f

    if f_(low) * f_(high) > 0:
        return None
    elif abs(f_(low)) <= tol:
        return low
    elif abs(f_(high)) <= tol:
        return high
    
    error = float('inf')

    cur, prev = low, high
    for i in range(int(max_n) + 1):
        if abs(f_(cur)) <= tol:
            return cur
        
        nxt = cur - f_(cur) * (cur - prev) / (f_(cur) - f_(prev))
        cur, prev = nxt, cur

    return None


def bisection_method(f, low, high, target=0, tol=1e-9):

    f_ = (lambda x: f(x) - target) if target != 0 else f

    if f_(low) * f_(high) > 0:
        return None
    elif abs(f_(low)) <= tol:
        return low
    elif abs(f_(high)) <= tol:
        return high
    
    mid = (low + high) / 2
    while abs(f_(mid)) > tol:
        
        if f_(mid) * f_(low) > 0:
            low = mid
        else:
            high = mid
        
        mid = (low + high) / 2
    
    return mid

