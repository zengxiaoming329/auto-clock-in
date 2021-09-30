import datetime
with open('time_log.txt', 'w', encoding='utf-8') as f:
  f.write('test')
local_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(local_time_str)
