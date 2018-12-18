from flask import Blueprint, render_template


premier = Blueprint('premier', __name__, template_folder='templates')



import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
#import matplotlib.pyplot as plt
#import seaborn as sns
#sns.set_style('whitegrid')
#from subprocess import check_output
#print(check_output(["ls", "../input"]).decode("utf8"))

#import file
path="./data/"

df=pd.read_csv(path+"new_premier_league.csv", sep=";")

#calendario incontri
schedule=df.drop(["competition", "season_year", "season", "date"], axis=1)

#costruzione classifica
df['pA_team_won']=df.apply(lambda row: 1 if row['legsA']>row['legsB'] else 0,axis=1)
df['pB_team_won']=df.apply(lambda row: 1 if row['legsA']<row['legsB'] else 0,axis=1)
df['draw']=df.apply(lambda row: 1 if row['legsA']==row['legsB'] else 0,axis=1)


df['playerA'] = df['playerA'].str.strip()
df['playerB'] = df['playerB'].str.strip()

df1=df

#partite
a=df1.groupby(['season','playerA'])['pA_team_won'].sum().reset_index().rename(columns={'playerA': 'player','pA_team_won': 'won'})
b=df1.groupby(['season','playerB'])['pB_team_won'].sum().reset_index().rename(columns={'playerB': 'player','pB_team_won': 'won'})
c=df1.groupby(['season','playerA'])['draw'].sum().reset_index().rename(columns={'playerA': 'player','draw': 'draw'})
d=df1.groupby(['season','playerB'])['draw'].sum().reset_index().rename(columns={'playerB': 'player','draw': 'draw'})
e=df1.groupby(['season','playerA'])['pB_team_won'].sum().reset_index().rename(columns={'playerA': 'player','pB_team_won': 'lost'})
f=df1.groupby(['season','playerB'])['pA_team_won'].sum().reset_index().rename(columns={'playerB': 'player','pA_team_won': 'lost'})
#legs
a1=df1.groupby(['season','playerA'])['legsA'].sum().reset_index().rename(columns={'playerA': 'player','legsA': 'legwon'})
b1=df1.groupby(['season','playerB'])['legsB'].sum().reset_index().rename(columns={'playerB': 'player','legsB': 'legwon'})
c1=df1.groupby(['season','playerA'])['legsB'].sum().reset_index().rename(columns={'playerA': 'player','legsB': 'leglost'})
d1=df1.groupby(['season','playerB'])['legsA'].sum().reset_index().rename(columns={'playerB': 'player','legsA': 'leglost'})

point_table=a.merge(b, how='outer',on=['season','player']).merge(c, how='outer',on=['season','player']).merge(d, how='outer',on=['season','player']).merge(e, how='outer',on=['season','player']).merge(f, how='outer',on=['season','player']).merge(a1, how='outer',on=['season','player']).merge(b1, how='outer',on=['season','player']).merge(c1, how='outer',on=['season','player']).merge(d1, how='outer',on=['season','player']).fillna(0)


point_table= point_table.rename(columns={'won_x':'home_win','won_y':'away_win','lost_x':'home_loss','lost_y':'away_loss'})


point_table['W']=point_table.home_win+point_table.away_win
point_table['L']=point_table.home_loss+point_table.away_loss
point_table['D']=point_table.draw_x+point_table.draw_y
point_table['+/-']=(point_table.legwon_x+point_table.legwon_y)-(point_table.leglost_x+point_table.leglost_y)

point_table=point_table.drop(['draw_x','draw_y','legwon_x','legwon_y','leglost_x','leglost_y'],axis=1)

point_table['P']=point_table.W+point_table.L+point_table.D


point_table.iloc[:, -9:] = point_table.iloc[:, -8:].apply(pd.to_numeric, downcast='integer')

point_table['PTS'] = point_table.W*2+point_table.D*1+point_table.L*0

point_table2=point_table.drop(['home_win','away_win','home_loss','away_loss'],axis=1)

point_table2.sort_values(by="PTS", ascending=False).reset_index()

cols=['player','P', 'W', 'D', 'L', '+/-', 'PTS']

point_table2=point_table2[cols]





@premier.route('/premierleague')
def home():
    return render_template('premier/premierleague.html', tables=[schedule.to_html(index=False, justify='center', table_id = "pl", na_rep = '' ,classes=["table", "table table-hover", "table table-bordered", "width:100%"])], tables2=[point_table2.to_html(index=False, justify='center', table_id = "pl-class", classes=["table", "table table-hover", "table table-bordered"])])
