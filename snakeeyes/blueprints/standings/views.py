from flask import Blueprint, render_template


standings = Blueprint('standings', __name__, template_folder='templates')



import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import datetime #for the today date
#import matplotlib.pyplot as plt
#import seaborn as sns
#sns.set_style('whitegrid')
#from subprocess import check_output
#print(check_output(["ls", "../input"]).decode("utf8"))

#import file
path="./data/"

df=pd.read_csv(path+"GamesMTG_2.csv", sep=";")


df['pA_team_won']=df.apply(lambda row: 1 if row['legsA']>row['legsB'] else 0,axis=1)
df['pB_team_won']=df.apply(lambda row: 1 if row['legsA']<row['legsB'] else 0,axis=1)
df['draw']=df.apply(lambda row: 1 if row['legsA']==row['legsB'] else 0,axis=1)
df['bye']=df.apply(lambda row: 1 if (row['playerA']=='bye' or row['playerB']=='bye') else 0,axis=1)


df['playerA'] = df['playerA'].str.strip()
df['playerB'] = df['playerB'].str.strip()

df1=df

a=df1.groupby(['season','round','playerA'])['pA_team_won'].sum().reset_index().rename(columns={'playerA': 'player','pA_team_won': 'won'})
b=df1.groupby(['season','round','playerB'])['pB_team_won'].sum().reset_index().rename(columns={'playerB': 'player','pB_team_won': 'won'})
c=df1.groupby(['season','round','playerA'])['draw'].sum().reset_index().rename(columns={'playerA': 'player','draw': 'draw'})
d=df1.groupby(['season','round','playerB'])['draw'].sum().reset_index().rename(columns={'playerB': 'player','draw': 'draw'})
e=df1.groupby(['season','round','playerA'])['pB_team_won'].sum().reset_index().rename(columns={'playerA': 'player','pB_team_won': 'lost'})
f=df1.groupby(['season','round','playerB'])['pA_team_won'].sum().reset_index().rename(columns={'playerB': 'player','pA_team_won': 'lost'})
#preliminari
g=df1.groupby(['season','round','playerA'])['bye'].max().reset_index().rename(columns={'playerA': 'player','bye': 'bye'})
h=df1.groupby(['season','round','playerB'])['bye'].max().reset_index().rename(columns={'playerB': 'player','bye': 'bye'})

point_table=a.merge(b, how='outer',on=['season','round','player']).merge(c, how='outer',on=['season','round','player']).merge(d, how='outer',on=['season','round','player']).merge(e, how='outer',on=['season','round','player']).merge(f, how='outer',on=['season','round','player']).merge(g, how='outer',on=['season','round','player']).merge(h, how='outer',on=['season','round','player']).fillna(0)

point_table= point_table.rename(columns={'won_x':'home_win','won_y':'away_win','lost_x':'home_loss','lost_y':'away_loss'})

point_table['bye']=point_table[['bye_x','bye_y']].max(axis=1)

point_table['matches_won']=point_table.home_win+point_table.away_win-point_table.bye
point_table['matches_lost']=point_table.home_loss+point_table.away_loss
point_table['matches_drawn']=point_table.draw_x+point_table.draw_y

point_table=point_table.drop(['draw_x','draw_y','bye_x','bye_y'],axis=1)

point_table['total_matches']=point_table.matches_won+point_table.matches_lost+point_table.matches_drawn

point_table.iloc[:, -9:] = point_table.iloc[:, -9:].apply(pd.to_numeric, downcast='integer')

point_table['points']=0
conditions = [
    (point_table['total_matches'] == 2) & (point_table['matches_won'] == 1) & (point_table['bye'] == 1),
    (point_table['total_matches'] == 3) & (point_table['matches_won'] == 2) & (point_table['bye'] == 1),
    (point_table['total_matches'] == 4) & (point_table['matches_won'] == 3) & (point_table['bye'] == 1),
    (point_table['total_matches'] == 4) & (point_table['matches_won'] == 4) & (point_table['bye'] == 1),

    (point_table['total_matches'] == 2) & (point_table['matches_won'] == 1) & (point_table['bye'] == 0),
    (point_table['total_matches'] == 3) & (point_table['matches_won'] == 2) & (point_table['bye'] == 0),
    (point_table['total_matches'] == 4) & (point_table['matches_won'] == 3) & (point_table['bye'] == 0),
    (point_table['total_matches'] == 5) & (point_table['matches_won'] == 4) & (point_table['bye'] == 0),
    (point_table['total_matches'] == 5) & (point_table['matches_won'] == 5) & (point_table['bye'] == 0),

    (point_table['total_matches'] == 1) & (point_table['matches_won'] == 0)
]

choices = [4,7,11,16,3,7,10,14,19,1]
point_table['points'] = np.select(conditions, choices, default=-1)


point_table2=point_table.drop(['home_win','away_win','home_loss','away_loss','matches_drawn','bye'],axis=1)

# ### calcolo bonus
df_bonus=pd.read_csv(path+"bonus_mn_mtg.csv", sep=";").fillna(0)
df_bonus['bonus']=df_bonus.bigscore+df_bonus.bigchk+df_bonus.darts18+df_bonus.darts15*2+df_bonus.darts12*3+df_bonus.other

monday_night=point_table2.merge(df_bonus, how='left',on=['season','round','player']).fillna(0).drop(['data'],axis=1)

monday_night.iloc[:, -11:] = monday_night.iloc[:, -11:].apply(pd.to_numeric, downcast='integer')

monday_night_f=monday_night.groupby(['season','player']).agg({'points':'sum','bonus':'sum','round':'count'}).reset_index().rename(columns={'round': 'played'})
monday_night_f['total']=monday_night_f.points+monday_night_f.bonus


monday_night_f1=monday_night_f.drop(['season'], axis=1).sort_values(by="total", ascending=False).reset_index(drop=True)

mn_top10=monday_night_f1.head(10)


##calendario
now = datetime.datetime.now()

calendar=pd.read_csv(path+"calendar.csv", sep=";")

calendar['datetime']=pd.to_datetime(calendar['date'],format="%d/%m/%Y")
calendar_2=calendar.loc[calendar['datetime']>now.strftime("%Y-%m-%d")].drop(['season_year','season','competition','datetime'],axis=1).head(5)


@standings.route('/')
def home():


    return render_template('standings/index1.html', tables=[mn_top10.to_html(index=False, justify='right', table_id = "hello", classes=["table", "table table-hover", "table table-bordered"])], tablesb=[calendar_2.to_html(table_id = "calendar", index=False, classes=["table", "table table-hover", "table table-bordered"])])


   # return render_template('standings/index.html', tablesb=[calendar.head().to_html(table_id = "calendar", classes=["table", "table table-hover", "table table-bordered"])])

@standings.route('/championship')
def home_mn():
    return render_template('standings/championship.html', tables=[monday_night_f1.to_html(index=False, justify='right', table_id = "hello", classes=["table", "table table-hover", "table table-bordered"])])
