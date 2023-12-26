# %% [markdown]
# # スケジュール算出プログラム

# %% [markdown]
# ## 1.ライブラリのインポート
# pandasは表の処理

# %%
import streamlit
import random
import datetime
import numpy as np
import pandas as pd
from array import array
import locale                               # ローカライズ用パッケージ

# %% [markdown]
# ## 2.時間のローカライズ

# %%
locale.setlocale(locale.LC_TIME, "ja_JP")   # 日本にローカライズ（これがないと、英語の曜日が出えてくる）

# %%
def read_excels():

    excel_path = "f_iden_3.xlsx"

    off_day_df  = pd.read_excel(excel_path, sheet_name="yukyu")                         # 休みの希望表
    skill_df    = pd.read_excel(excel_path, sheet_name="skill", header=[0, 1])          # スキル表
    due_date_df = pd.read_excel(excel_path, sheet_name="calendar")                      # 納期表
    start_day:pd.Series = pd.read_excel(excel_path, sheet_name="start")    

    # 空データ(NaN)の置換(0)
    off_day_df.fillna(0, inplace=True)
    # skill_df.fillna(0, inplace=True)
    due_date_df.fillna(0, inplace=True)

    # データの置換
    off_day_df.replace("◎", 2, inplace=True)                                            # 希望休（◎）を 2 に置換
    due_date_df.replace("☆", 3, inplace=True)                                          # 納期（☆）を 3 に置換

    # 列ごとのデータ型(dtype)を、intに変更しておく
    off_day_df[off_day_df.columns[2:]] = off_day_df[off_day_df.columns[2:]].astype("int64")
    due_date_df[due_date_df.columns[4:]] = due_date_df[due_date_df.columns[4:]].astype("int64")

    # 品番の抽出
    product_num = due_date_df.loc[:, "品番"]

    # 土日の削除
    # データの中から土日の日付を取り出す
    off_days = [date for date in due_date_df.columns[4:] if date.strftime("%a") in "土日"]
    # 土日の日付を削除する
    off_day_df.drop(columns=off_days, inplace=True)
    due_date_df.drop(columns=off_days, inplace=True)

    return off_day_df, skill_df, due_date_df, product_num , start_day

# %%
off_day_df, skill_df, due_date_df, product_num , start_day = read_excels()

# %%
off_day_df.iloc[:, :15]

# %%
skill_df

# %%
due_date_df.iloc[-1:, :15]

# %%
start_day

# %% [markdown]
# ## 3.第1世代関数

# %%
def first_gen(off_day_df: pd.DataFrame, skill_df: pd.DataFrame, due_date_df: pd.DataFrame, product_num: pd.Series):
    
    # 調整後の納期表（納期表のコピー）　→　以降、『調整納期表』　と呼ぶ
    adjusted_due_date_df = due_date_df.copy()


    # 作業者の割り振り　と　作業者の希望休を調整納期表にコピー
    worker_list = []
    # indexごとにrowを取り出して、作業者をランダムに割り振る
    for index, row in adjusted_due_date_df.iterrows():
       
#作業者を選ぶ →ajauted_date_dfのスキルグループ番号と同じskill_dfのスキルグループ番号のリストを選択、worker選択。()はマルチヘッダー。
        workers: pd.DataFrame = skill_df.loc[:, (["スキルグループ"], [row["スキルグループ"]])]
        worker = workers.dropna().sample().values[0, 0]
#練習
        #print('選ばれたスキルグループworkers',workers) 
        #print('スキルグループの任意のworker',worker)       
        worker_list.append(worker)
        worker_off_days: pd.DataFrame = off_day_df.loc[off_day_df["設備"].isin([worker]), off_day_df.columns[2:]]                   # 作業者の希望休を抽出
#練習x
        #worker_off_days: pd.DataFrame = off_day_df.loc[off_day_df["設備"].isin([worker]),:]   

        # 希望休を調整納期表にコピー（希望休ですべて上書きして納期を一度消す）
        #index毎にadjusted_due_date_df.columns[4:]取得、但しカラムはadjusted_due_date_df
        #値はworker_off_days.valuesに入替え
        adjusted_due_date_df.loc[[index], adjusted_due_date_df.columns[4:]] = worker_off_days.values
#練習
        #print('workers',workers) 
        #print('任意のworkerの累積list',worker_list) 
        #print('任意のworkerのoff_days',worker_off_days)
        #print('☆任意のworkerのoff_daysのseries化_worker_off_days.values',worker_off_days.values)
        #print('adjusted_due_date_df(due_date_dfコピー)',adjusted_due_date_df) 
    # 割り当てたワーカーを adjusted_due_date_df へ「作業者」列として追加（※ここから adjusted_due_date_df が一列増えるので注意）
    adjusted_due_date_df.insert(3, "作業者", worker_list)

    #print('for後作業者追加adjusted_due_date_df',adjusted_due_date_df) 
    # 作業者の希望休に合わせて、納期を調整
    after_index = None                                                                                                              # 後工程の index を保持する
    
    for index, row in adjusted_due_date_df[::-1].iterrows():                                                                        # due_date_df を逆順で行ごとに処理

        # 現工程の納期を抽出
        process: pd.Series = due_date_df.loc[index, due_date_df.columns[4:]]                                                        # 現工程の納期表データ
        process_due_date = process[process.isin([3])]                                                                               # 現工程の納期
        print("入力納期:", process_due_date.index[0])
        #練習
        #print("入力納期process_due_date.index:", process_due_date.index)
        print("入力納期process_due_date:", process_due_date)
        #print("入力納期process:", process)

        # 後工程の納期と本工程の納期を確認して調整
        # 後工程候補があるか（一つ目のデータは None なので無視）
        if after_index != None:

            after_process_df: pd.DataFrame = adjusted_due_date_df[adjusted_due_date_df["製造番号"] == row["製造番号"]]                               # 同じ製造番号のタスクを取り出す。

            print("[INFO]: 工程:", row["スキルグループ"])

            # 後工程があるか確認（後工程候補　に　現工程の次のスキルグループ（工程）があるか確認する）
            
            if row["スキルグループ"] + 1 in after_process_df["スキルグループ"].values:

                print("後工程あり")

                after_index = after_process_df[after_process_df["スキルグループ"].isin([row["スキルグループ"] + 1])].index[0]
                print("after_index :", after_index)

                # 後工程の納期を抽出
                after_process: pd.Series = adjusted_due_date_df.loc[after_index, adjusted_due_date_df.columns[5:]]                  # 後工程のデータ
                after_process_due_date = after_process[after_process.isin([3])]                                                     # 後工程の納期
                print("後工程の納期:", after_process_due_date.index[0])

                # 本工程の納期が後工程の納期より前に設定されていない場合　→　本工程の納期を後工程より前の日付にする
                if not process_due_date.index[0] < after_process_due_date.index[0]:

                    # 納期を１営業日早めて調整する（この時点では、有休をチェックしてないので決定しない）
                    before_days:pd.DataFrame = due_date_df.loc[[index], due_date_df.columns[4]:after_process_due_date.index[0]]     # 現在の納期より前のデータを抽出
                    new_due_date = before_days.columns[-2]                                                                          # 納期を１営業日早める
                    print("後工程を考慮した納期調整:", new_due_date)
                    
                    due_date_df.loc[index, process_due_date.index[0]] = 0                                                           # 現在の納期を納期表から削除
                    due_date_df.loc[index, new_due_date] = process_due_date.values[0]                                               # 新しい納期を納期表に追加

                    process: pd.Series = due_date_df.loc[index, due_date_df.columns[4:]]                                            # 現工程の納期表データ
                    process_due_date = process[process.isin([3])]                                                                   # 現工程の納期
                    print("現工程の納期:", process_due_date.index[0])

            else:

                print("後工程なし:")
        
        else:

            print("後工程なし（1つ目のデータ）:")
        
        
        # 希望休に合わせた調整
        # 現在の納期より前のデータを抽出
        before_days: pd.DataFrame = adjusted_due_date_df.loc[[index], adjusted_due_date_df.columns[5]:process_due_date.index[0]]

#X 納期を設定できるか確認していく→new_due_dateには6/12が入る？
        for new_due_date in before_days.columns[::-1]:
                        
            # 納期を１日早める(-1日)
            print("納期候補:", new_due_date)

            # その日が希望休でない場合(0 のとき)　→　納期決定　→　ループ終了
            if adjusted_due_date_df.loc[index, new_due_date] == 0:

                # 納期が確定するのはココだけ。valuesで[3]が入るindexと配列指定。values[0]で3指定。
                print("納期決定:", new_due_date)
                adjusted_due_date_df.loc[index, new_due_date] = process_due_date.values[0]
                break
        
        after_index = index
        print("-" * 100)              # デバッグ用（ループごとに横線を表示）

    return adjusted_due_date_df


# %%
#受取
adjusted_due_date_df = first_gen(off_day_df, skill_df, due_date_df, product_num)

# %%
off_day_df.iloc[:,:12]

# %%
adjusted_due_date_df.iloc[-5:,:12]

# %%
adjusted_due_date_df

# %%
#第1世代


# %% [markdown]
# ## ※　データのルール
# 製造番号は必ず連番

# %%
adjusted_due_date_df[adjusted_due_date_df["製造番号"] == 1].iloc[:, :15]

# %% [markdown]
# ## 5.納期をランダムで振り直し（再帰処理）
# ※　この処理中は希望休を考慮しない
# 

# %% [markdown]
# ### 開始日

# %%
start_date = datetime.datetime(2023, 6, 2)

# %% [markdown]
# ### 納期のランダム振り分け関数

# %%
def generate_random_dates(
        start_date: datetime.datetime, 
        end_date: datetime.datetime):
    
    start_date = due_date_df.loc[:, start_date:].columns[1]

    working_days = due_date_df.loc[:, start_date:end_date].columns
    print(working_days)

    random_num = random.randint(0, working_days.shape[0]-1)
    random_date = working_days[random_num]
    print(random_date)
    print("-" * 50, "納期ランダム割り振り完了","-" * 50)

    return random_date

# %% [markdown]
# ### 同じ製造番号のタスクをランダムにリスケする関数（これが再帰関数：関数内の処理に自分自身の呼び出しがある）

# %%
def random_due_date(
        start_date: datetime.datetime,
        process_df: pd.DataFrame,
        process_num: int):
    
    print("process_num :", process_num, "-" * 100)
    print(process_df.loc[[process_df.index[process_num]], process_df.columns[:5]])

    process: pd.Series = process_df.loc[process_df.index[process_num], process_df.columns[5:]]              # 現工程の納期表データ
    deadline = process[process.isin([3])]                                                                   # 現工程の納期
    deadline_date: datetime.datetime = deadline.index[0]                                                    # その工程のデッドライン
    print("process_deadline :", deadline_date)

    # 最初の工程以外の時
    if process_num != 0:

        start_date = random_due_date(start_date, process_df.loc[process_df.index[:-1], :], process_num-1)   # 開始日を前工程の納期に置き換える（※　ここが再帰処理）

    new_due_date = generate_random_dates(start_date, deadline_date)                                         # 開始日～デッドライン　の期間からランダムに日付を選択

    due_date_df.loc[process_df.index[process_num], deadline.index[0]] = 0                                   # 現在の納期を納期表から削除
    due_date_df.loc[process_df.index[process_num], new_due_date] = deadline.values[0]                       # 新しい納期を納期表に追加

    return new_due_date                        


# %% [markdown]
# ### タスクを製造番号ごとに処理する関数

# %%
#def change_due_date(off_day_df, skill_df, due_date_df, product_num):
def change_due_date():
    
    serial_number = due_date_df.loc[:, "製造番号"].max()
    print(serial_number)

    # 製造番号ごとに繰り返す
    for i in range(1, serial_number + 1):

        # 同じ製造番号のタスクを取り出す。
        process_df = adjusted_due_date_df[adjusted_due_date_df["製造番号"] == i]
        print(process_df.loc[:, process_df.columns[:5]])

        random_due_date(start_date, process_df, process_df.shape[0]-1)                                          # 製造番号ごとに納期のランダム割り当て（再帰関数）

        print("*" * 200)

### ※　この時点では、希望休を考慮した納期になっていない為、first_gen()関数を使ってもう一度希望休に沿った調整をする。

    #adjusted_due_date_df = first_gen(off_day_df, skill_df, due_date_df, product_num)
    #return adjusted_due_date_df
    #return NG?

# %%
#追加
#受け取り
#adjusted_due_date_df= change_due_date(off_day_df, skill_df, due_date_df, product_num)

# %%
# 呼び出し
change_due_date()

# %%
due_date_df

# %% [markdown]
# ### ※　この時点では、希望休を考慮した納期になっていない為、first_gen()関数を使ってもう一度希望休に沿った調整をする。

# %%
adjusted_due_date_df = first_gen(off_day_df, skill_df, due_date_df, product_num)

# %% [markdown]
# #### これでランダムな納期かつ希望休の調整ができる

# %% [markdown]
# ##### 希望休表

# %%
off_day_df.iloc[:,:11]

# %% [markdown]
# ##### 希望休調整前(ランダム)

# %%
due_date_df.iloc[-5:,:13]

# %% [markdown]
# ##### 希望休調整後

# %%
adjusted_due_date_df.iloc[-5:,:14]

# %%
adjusted_due_date_df.columns

# %%
adjusted_due_date_df.iloc[:, :15]

# %% [markdown]
# 

# %%
adjusted_due_date_df_copy= adjusted_due_date_df.copy()
adjusted_due_date_df_copy=adjusted_due_date_df_copy.iloc[:,5:]
adjusted_due_date_df_copy.reset_index(inplace=True,drop=True)
#行と列の数を取り出す
sh3=adjusted_due_date_df_copy.shape
adjusted_due_date_df_copy.columns=range(sh3[1])
print(adjusted_due_date_df_copy)

# %%
#55変換
def pre_evalution(adjusted_due_date_df):
    adjusted_due_date_df2=adjusted_due_date_df.iloc[:,5:]
    return adjusted_due_date_df2

# %%
#受取
adjusted_due_date_df2= pre_evalution(adjusted_due_date_df)

# %% [markdown]
# ## 6.評価方法　

# %%
##(1)工程ができるだけ長くならないこと
##(2)前倒し生産方式の場合、できるだけ開始日に近いこと、ジャストインタイム方式の場合、できるだけ納期に近いこと。
#評価方法
def evalution_function(adjusted_due_date_df2):

    #tstr = '2023-06-23 00:00:00'
    #tdatetime = datetime.datetime.strptime(tstr, '%Y-%m-%d %H:%M:%S')
    # データの中から土日の日付を取り出す ?何故空？
    #locale.setlocale(locale.LC_TIME, "ja_JP")
    #off_days2 = [date for date in due_date_df.columns[4:] if date.strftime("%a") in "土日"]
    #print('off_days2',off_days2)



    fix_day= []
    tds_list=[]
    tdos_list=[]
    #fix_day_sum= []
    score=[]
    adjusted_due_date_df_copy= adjusted_due_date_df2.copy()
    #adjusted_due_date_df_copy=adjusted_due_date_df_copy.iloc[:,5:]
    adjusted_due_date_df_copy.reset_index(inplace=True,drop=True)
    #行と列の数を取り出す
    sh3=adjusted_due_date_df_copy.shape
    adjusted_due_date_df_copy.columns=range(sh3[1])
    print('sh3',sh3)
    print('sh3[1]',sh3[1])
    #for index, row in adjusted_due_date_df.iterrows():
        #if adjusted_due_date_df.loc[:,]
        #print('row[4]',row[4])
        #fix_day= adjusted_due_date_df.columns

        #for fix_day in adjusted_due_date_df.columns[::-1]:
                    
        # 納期を１日早める(-1日)
        #print("納期候補:", new_due_date)
    for k in range(len(adjusted_due_date_df_copy)):
        for v in range(len(adjusted_due_date_df_copy.columns)):
            if adjusted_due_date_df_copy.iloc[k,v]==3:
                fix_day.append(adjusted_due_date_df.columns[v+5])
                #fix_day.append(adjusted_due_date_df_copy.columns[v])
        # その日が希望休でない場合(0 のとfixき)　→　納期決定　→　ループ終了
            #if adjusted_due_date_df.loc[index, row] == 3:
            #   fix_day.append(index)
    print('fix_day',fix_day)
    print(type(fix_day))
    print('start_date',start_date)
    print(type(start_date))
    #td= '2023-06-23 00:00:00'
    tdos= '0000-00-00 00:00:00'
    td= '0000-00-00 00:00:00'
    tm : datetime.datetime
    #tm= tm.date()
    #for tm in range(len(fix_day)):
    for tm in fix_day:
        print('tm',tm)
        print(type(tm))
        ttdelta= tm- start_date 
        print('ttdelta',ttdelta)
        tdos= ttdelta.total_seconds()
        print('tdos',tdos)
        tdos=int(tdos)
        tdos_list.append(tdos)
    print('tdos_list',tdos_list)
    score=sum(tdos_list)*(-1)
    print('score',score)

                   

    #td= fix_day[0]- start_date
    print('td',td)
    #print(td.total_seconds())
    #日付け→時間（S）換算
    #tds= td.total_seconds()
    #tds=int(tds)
    #for m in range(len(fix_day)):
    #    tds_list.append(tds)
    #print('tds_list',tds_list)
    #score=sum(tds_list)*(-1)
    #print('score',score)
    #for n in range(len(tds_list)):
    #    fix_day_sum= tds[n] + fix_day_sum
    #print('fix_day_sum',fix_day_sum)
    #for index, row in adjusted_due_date_df[::-1].iterrows():                                                                        # due_date_df を逆順で行ごとに処理
    #for index, row in adjusted_due_date_df.iterrows():	
        #worker_off_days: pd.DataFrame = off_day_df.loc[off_day_df["設備"].isin([worker]), off_day_df.columns[2:]] 
        #process2: pd.Series = due_date_df.loc[off_day_df["設備"].isin(['2']), off_day_df.columns[2:]]
        # 現工程の納期を抽出
        #process: pd.Series = due_date_df.loc[index, due_date_df.columns[4:]]
        #process2: pd.Series = due_date_df.loc[:, due_date_df[4:].isin(['2'])]
        #process2: pd.Series = due_date_df.loc[:, ['スキルグループ']]
        #process2: pd.Series = due_date_df.loc[:,'納期']
        #process2: pd.DataFrame = due_date_df.loc[:,'納期']
    #process2: pd.Series = due_date_df.iloc[:,1]
        # データの中から土日の日付を取り出す
    #add: pd.Series= adjusted_due_date_df.loc[index, adjusted_due_date_df.columns[5:]]
        #add= adjusted_due_date_df.loc[index, adjusted_due_date_df.columns[5:]]
        #add_date= add[add.isin([3])]
    #print('add',add)
    #print('修正納期',add_date)

    #off_days = [date for date in due_date_df.columns[4:] if date.strftime("%a") in "土日"]

    #print('process2',process2)
    return score


# %%
#受取
score= evalution_function(adjusted_due_date_df2)

# %% [markdown]
# ## 6.遺伝的アルゴリズム

# %%
#42
def eva2():
  koteikan=0
  hoshiki=0
  if kiso2.iloc[0,6]=='〇':
    h=1
  else:
    h=0
  #for k3 in range(len(hinban)):
  #        for d3 in range(len(kiso_copy2.columns)):
  def evalution_function2(startup_day, minlist, maxlist):
  ##(1)工程ができるだけ長くならないこと
  #  for d3 in range(len(kiso_copy2)):
  #    for e3 in range(len(hinban)):
  #      kouteikan=((d3(max)-d3(min))^2)^0.5
    #for k4 in range(len(hinban)):
  #  for d4 in 2:
  #    if hinban(k4,0)== hinban(k4 +1,0):
  #      kouteikan=((d4(max)-d4(min))^2)^0.5
    for k4 in maxlist:
      koteikan=-1*sum(abs(maxlist[k4]- minlist[k4]))
      
  ##(2)前倒し生産方式の場合、できるだけ開始日に近いこと、ジャストインタイム方式の場合、できるだけ納期に近いこと。
    #①前倒し時スタート-第１工程近い
    #startup_day
  # houshiki=0
    if h== 0:
    #for d4 in range(len(kiso_copy2)):
    # for e4 in range(len(hinban)):
    #   if hinban.iloc[e4,1]==1:
    #     kiso_copy2.iloc[e4,d4]
    #       houshiki=-1*((d4(start)-d4(min))^2)^0.5
      for k41 in maxlist:
        hoshiki=-1*sum(abs(minlist[k41])-startup_day)
        
    #②ジャストインタイム時納期-最終工程近い
    hoshiki=0
    if h== 1:
    #for d4 in range(len(kiso_copy2)):
    # for e4 in range(len(hinban)):
    #   kouteikan=-1*((d4(noki)-d4(max))^2)^0.5
      for k42 in maxlist:
        hoshiki=-1*sum(abs(nokilist[k42])-maxlist[k42])



    #評価
    score2+=koteikan+hoshiki
    return score2
    #print(score)

# %%
##52関数化
#1エクセル読み込み
#kiso2,holiday=read_excel()
#due_date_df,product_num=read_excels()
#2第1世代
#kiso_copy=first_gene(kiso,holiday)
#kiso_copy2=first_gen(kiso_copy2, days2)
#3休日数の修正
#kiso_copy=holiday_fix(kiso_copy,holiday)
#kiso_copy2=noki_fix(kiso_copy2, product_num, minlist, maxlist, nokilist)
#4評価
#score=evalution_function(kiso_copy)
#score2=evalution_function2(koteikan, hoshiki)
#score2

# %%
##62遺伝的アルゴリズム


def crossover(ep,sd,p1,p2):
    #1か月の日数
    #days=len(p1.columns)
    days= len(off_day_df.columns) - 2
    #1次元化
    p1=np.array(p1).flatten()
    p2=np.array(p2).flatten()

    print(p1)
    print(p2)
    #子の変数
    ch1=[]
    ch2=[]
    for p1_,p2_ in zip(p1,p2):
        if ep > random.random():
            ch1.append(p1_)
            ch2.append(p2_)
        else:
            ch1.append(p2_)
            ch2.append(p1_)

    #突然変異
    ch1=mutation(sd, np.array(ch1).flatten())
    ch2=mutation(sd, np.array(ch2).flatten())
    
    #pandasに変換
    ch1=pd.DataFrame(ch1.reshape([int(len(ch1)/days), days]))
    ch2=pd.DataFrame(ch2.reshape([int(len(ch2)/days), days]))
    #列名の変更
    ch1.columns=[i+1 for i in range(len(ch1.columns))]
    ch2.columns=[i+1 for i in range(len(ch2.columns))]
    return ch1,ch2


#突然変異
def mutation(sd2, ch):
    if sd2 > random.random():

        rand = np.random.permutation(list(range(len(ch))))

        #遺伝子の10％を変異させる
        #並び換えた先頭10％
        rand=rand[:int(len(ch)//10)]
        for i in rand:
            #1なら0,0なら1
            if ch[i]==3:
                ch[i]==0

            if ch[i]==0:
                ch[i]==3
                #ch2も同じことをする。

    return ch


# %%
#追加
#受け取りできない→ep,sdは都度指定,p1,p2は代入の為
#ch= crossover(ep,sd,p1,p2)

# %%
##72全体
#遺伝的アルゴリズム
#エクセル読み込み
off_day_df, skill_df, due_date_df, product_num , start_day =read_excels()
#親の保存
parent=[]
#for i in range(100):
#5世代へ変更
for i in range(2):
    #第1世代
    adjusted_due_date_df = first_gen(off_day_df, skill_df, due_date_df, product_num)
    #休日数の修正
    #kiso_copy2=noki_fix(kiso_copy2, product_num, startup_day)
    #納期をランダムで振り直し（再帰処理）
    #納期のランダム振り分け関数：def generate_random_date;受取りなし,def random_due_date;受取りなし,
    # 呼び出し?
    change_due_date()
    adjusted_due_date_df = first_gen(off_day_df, skill_df, due_date_df, product_num)


    #評価
    #追加
    adjusted_due_date_df2= pre_evalution(adjusted_due_date_df)
    score= evalution_function(adjusted_due_date_df2)
    #第1世代を格納
    #parent.append([score, adjusted_due_date_df.iloc[:, 5:].values])
    parent.append([score, adjusted_due_date_df2.values])

print('parent',parent)



#上位個体数
elite_length=20
#世代数
gene_length=50

#一様交叉確立
ep=0.5
#突然変異確立
sd=0.05

#一様交叉
#ch1 = pd.DataFrame(ch1)
#ch2 = pd.DataFrame(ch2)
#ch1,ch2=crossover(ep,sd,parent[0],parent[1])
#休日数変更
#ch1=holiday_fix(ch1,holiday)
#ch2=holiday_fix(ch2,holiday)

for i in range(gene_length):
    #点数で並び換え
    parent = sorted(parent, key=lambda x: -x[0])
    #parent=sorted(np.array(parent), key=lambda x:-x[0])
    #parent=sorted(np.array(parent[0]).flatten(), key=lambda x:-x[0])
    #p1=np.array(parent[0]).flatten()
    #上位個体を選別
    parent=parent[:elite_length]
    #各世代
    print('第'+str(i+1)+'世代')

    #最高得点の更新
    #if i ==0 or top[0]<parent[0][0]:
    if i ==0:
        top=parent[0]
            #各世代の最高得点の表示
        print(top[0])
        print(np.array(top[1]))
    else:
        if top[0]>parent[0][0]:
            parent.append(top)
            #各世代の最高得点の表示
            print(top[0])
            print(np.array(top[1]))
        else:
            top=parent[0]
            #各世代の最高得点の表示
            print(parent[0][0])
            print(np.array(parent[0][1]))

    #各世代
    #print('第'+str(i+1)+'世代')
    #各世代の最高得点の表示
    #print(top[0])
    #print(np.array(top[1]))

    #子世代
    children=[]
    #遺伝子操作
    for k1,v1 in enumerate(parent):
        for k2,v2 in enumerate(parent):
            if k1<k2:
                #一様交叉
                print(ep)
                print(sd)
                print(v1[1])
                print(v2[1])
                ch,ch2=crossover(ep,sd,v1[1],v2[1])
                #休日数変更
                #ch21=noki_fix(ch21,product_num)
                #ch22=noki_fix(ch22,product_num)
                #納期をランダムで振り直し（再帰処理）
                #納期のランダム振り分け関数：def generate_random_date;受取りなし,def random_due_date;受取りなし,
                # 呼び出し?
                change_due_date()
                adjusted_due_date_df = first_gen(off_day_df, skill_df, due_date_df, product_num)
                #評価
                score1=evalution_function(ch)
                score2=evalution_function(ch2)
                #子孫を格納
                children.append([score1,ch])
                children.append([score2,ch2])

    #子を親にコピー
    parent=children.copy()

#最強個体の保存
x=top[1].replace(3,'〇').replace(2,'◎').replace(0,'')
x.to_excel('f_shiftf_32.xlsx')


# %%
ch


