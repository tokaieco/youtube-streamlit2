import datetime

# 2つの datetime オブジェクトがあるとき
start_day = datetime.datetime(2023, 6, 2)       # 2023.06.02
due_date = datetime.datetime(2023, 6, 12)       # 2023.06.12

# ２つの datetime を減算すると、時間差(timedelta)が求まる
time_delta = due_date - start_day
print(f"{due_date} - {start_day} = {time_delta}")
print()
print("時間差：", time_delta)
print("　型　：",type(time_delta))
