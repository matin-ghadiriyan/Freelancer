import time
dict_rate_limit = {}
def rate_limit(limit:int=10 , ip:str=None , limit_time:int=60)->bool:
    now = time.time()
    if ip not in dict_rate_limit:
        dict_rate_limit[ip] = {'count': 0, 'late_time': now}
    count , late_time = dict_rate_limit[ip]['count'] , dict_rate_limit[ip]['late_time']
    if now - late_time >= limit_time:
        dict_rate_limit[ip] = {'count': 1, 'late_time': now}
        return True
    elif count < limit:
        dict_rate_limit[ip] = {'count': count + 1, 'late_time': now}
        return True
    return False