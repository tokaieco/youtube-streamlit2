import pandas as pd
import numpy as np
import datetime
import locale                               # ローカライズ用パッケージ

locale.setlocale(locale.LC_TIME, "ja_JP")   # 日本にローカライズ（これがないと、英語の曜日が出えてくる）

excel_path = "f_iden_3.xlsx"

df  = pd.read_excel(excel_path, sheet_name="yukyu")
clnd=df.columns[3:]

df5  = pd.read_excel(excel_path, sheet_name="calendar")

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
df6=df5.copy()
    # 空データ(NaN)の置換(0)
df3.fillna(0, inplace=True)
df6.fillna(0, inplace=True)
    # データの置換
df3.replace("◎", 2, inplace=True) 
df6.replace("☆", 3, inplace=True) 

    # 列ごとのデータ型(dtype)を、intに変更しておく
df3[df3.columns[2:]] = df3[df3.columns[2:]] .astype("int64")
df6[df6.columns[4:]] = df6[df6.columns[4:]] .astype("int64")
#内包表記
# 水土日のリスト
#X list = [list for list in df3.columns[3:] if list.strftime("%a") in "水土日"]
#off_days = [date for date in df3.columns[3:] if date.strftime("%a") in "水土日"]
#〇内包表記：df3を条件付きでdateに入れる、条件は曜日変換し、水土日の文字が入っている。
list = [date for date in df3.columns[3:] if date.strftime("%a") in "水土日"]
#off_days2 = [off_days2 for off_days2 in df3.columns[3:] if off_days2.strftime("%a") in "水土日"]
   # 土日の日付を削除する
df3.drop(columns=list, inplace=True)
#df3.drop(columns=off_days2, inplace=True)
#df3.drop(columns=list, inplace=True)


print('------')
print('df3',df3.iloc[:,:6])
print('list',list)
print('------')

#列追加
df2['スキルグループ']=[1,2]

#行追加df2.loc[]=[,,]でも可
df21 = pd.DataFrame({'age': [29, 25,31], 'state': ['SFR', 'ID','TK'], 'point': [99, 78,77],'スキルグループ':[3,4,5]},index=['大谷', 'ヌートバー','岡本'])
print('df2',df2)
df2=pd.concat([df2,df21])
#index新設
df2.reset_index(inplace=True)
df2=df2.rename({'index':'設備'},axis='columns')
print('新df2',df2)

#☆index付きリスト(pandas)をつくる方法1
for index, row in df2.iterrows():
    workers1:pd.DataFrame= df3["設備"]
    #唯のdf3"設備"抽出
print('workers1',workers1)
for index, row in df2.iterrows():
    workers2:pd.DataFrame= df3.loc[:,"設備"]
    #唯のdf3"設備"抽出
print('workers2',workers2)

#〇index付き値のseries(columns指定）→df2は5行なのでヌートバー～岡本まで可→大谷、ヌートバー、岡本で平日有休取っているのは岡本だけ→6/9
# 岡本の有給だけを取り出す
worker = "岡本"

worker_data: pd.Series =  df3[df3["設備"] == worker].iloc[0, :]
worker_off_days = worker_data[worker_data.isin([2])]

print("worker_off_days :\n", worker_off_days)
print("Type :", type(worker_off_days))

print("-" * 50)

# ndarray(numpy配列)にしたいとき　→　.values
worker_off_day_ndarray = worker_off_days.values
print("ndarray:", worker_off_day_ndarray)
print("index ndarray:", worker_off_days.index.values)
print("Type :", type(worker_off_day_ndarray))

print("-" * 50)

# list(ただの配列)にしたいとき　→　.to_list()
worker_off_day_list = worker_off_days.to_list()
print("list :", worker_off_day_list)
print("index list :", worker_off_days.index.to_list())
print("Type :", type(worker_off_day_list))


for index, row in df2.iterrows():
    process:pd.Series= df3.loc[index,df3.columns[2:]]
    sr= process[process.isin([2])]
    print('sr',sr)
for index, row in df2.iterrows():
    process:pd.DataFrame= df3.loc[index,df3.columns[2:]]
    sr= process[process.isin([2])]
    print('sr2',sr)



#〇index付きリスト(pandas)をつくる方法2？なぜリストなのに怒られる？→isinは[]列指定！
for index, row in df2.iterrows():
    workers3:pd.DataFrame= df3.loc[df3["設備"].isin(["岡本"]),df3.columns[2:]]
    #唯のdf2"設備"休み入り
print('workers3',workers3)

workers4:pd.DataFrame= df3.loc[df3["設備"]=="源田"].iloc[0,:]#源田有休抽出△
print('workers4',workers4)
workers41:pd.DataFrame= df3[df3["設備"]=="源田"].iloc[0,:]#源田有休抽出〇→シンプル
print('workers41',workers41)

print('------')
#X 納期を設定できるか確認していく→new_due_dateには6/12が入る？
#print('df6',df6)
#for index, row in df6[::-1].iterrows():
#    for new_due_date in df3.columns[::-1]:
            # 納期を１日早める(-1日)
#        print("納期候補:", new_due_date)

        # その日が希望休でない場合(0 のとき)　→　納期決定　→　ループ終了
#        if df6.loc[index, new_due_date] == 0:

            # 納期が確定するのはココだけ。valuesで[3]が入るindexと配列指定。values[0]で3指定。
#            print("納期決定:", new_due_date)
#            df3.loc[index, new_due_date] = df6.values[0]
#            break
#            after_index = index
#            print("-" * 100) 