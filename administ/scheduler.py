def minute_scheduler(interval):
    interval += 60
    return interval

def second_scheduler(interval):
    interval += 1
    return interval

def time_check(interval):
    if interval > 0:
        return True
    return False

def over_minute(interval):
    if interval // 60 > 1:
        return True
    return False

def elapse_minute(interval):
    interval -= 60
    return interval

def elapse_second(interval):
    interval -= 1
    return interval