i = 0
j = 11
try:
    n = j/i
except ZeroDivisionError as e:
    print("except:", e)
    raise

print("this is the end.")
