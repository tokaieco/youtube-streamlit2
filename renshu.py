import pandas as pd
import numpy as np
import datetime
import locale                               # ローカライズ用パッケージ

locale.setlocale(locale.LC_TIME, "ja_JP")   # 日本にローカライズ（これがないと、英語の曜日が出えてくる）

excel_path = "f_iden_3.xlsx"

df  = pd.read_excel(excel_path, sheet_name="yukyu")
clnd=df.columns[3:]

df2 = pd.DataFrame({'age': [24, 42], 'state': ['NY', 'CA'], 'point': [64, 92]},
                  index=['Alice', 'Bob'])
tstr = '2023-06-23 00:00:00'
#tstr = '2023-06-23'
tdatetime = datetime.datetime.strptime(tstr, '%Y-%m-%d %H:%M:%S')
print('df',df)
#DataFrame.iterrows()
for index, row in df.iterrows():
    print('index',index)
    print('------')
    print('type(row)',type(row))
    print('------')
    print('type(clnd)',type(clnd))
    print('------')
    print('row',row)
    print('------')
    
    print('row[0],row[tdatetime]',row[0], row[tdatetime])
    print('======')

print('df2',df2)
#DataFrame.iterrows()
for index, row in df2.iterrows():
    print('index',index)
    print('------')
    print('type(row)',type(row))
    print('------')
    print('row',row)
    print('------')
    print('row[0], row[age], row.age',row[0], row['age'], row.age)
    print('======')

df3=df.copy()
    # 空データ(NaN)の置換(0)
df3.fillna(0, inplace=True)
    # データの置換
df3.replace("◎", 2, inplace=True) 
    # 列ごとのデータ型(dtype)を、intに変更しておく
df3[df3.columns[2:]] = df3[df3.columns[2:]] .astype("int64")
#内包表記
# 水土日のリスト
#X list = [list for list in df3.columns[3:] if list.strftime("%a") in "水土日"]
#off_days = [date for date in df3.columns[3:] if date.strftime("%a") in "水土日"]
list = [date for date in df3.columns[3:] if date.strftime("%a") in "水土日"]
#off_days2 = [off_days2 for off_days2 in df3.columns[3:] if off_days2.strftime("%a") in "水土日"]
   # 土日の日付を削除する
df3.drop(columns=list, inplace=True)
#df3.drop(columns=off_days2, inplace=True)
#df3.drop(columns=list, inplace=True)


print('------')
print('df3',df3.iloc[:,:6])
print('off_days',list)
print('------')

