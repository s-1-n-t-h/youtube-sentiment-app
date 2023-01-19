from flask import Flask, render_template, request, url_for
from get_comments import get_comments
from pytube import extract

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/prediction',methods=['POST','GET'])
def predict():
    if request.method   == 'POST':
        url = request.form['video-url']
        df_comm = get_comments(url)
        if df_comm is None:
            return render_template('prediction-2.html',url=url)
        else:
            vid = extract.video_id(url)
            var = df_comm['sentiment type'].value_counts()
            # sending tables to render data at each table
            table_1 = [[1,2,3],list(var.index),[round((var[i]/sum(var))*100,2) for i in range(len(var)) ]]
            table_2 = [list(range(1,df_comm.shape[0]+1)),  list(df_comm['comments'].values), df_comm['language'].to_list()]
            table_3 = [list(range(1,df_comm.shape[0]+1)),  df_comm['translated comments'].to_list(), df_comm['sentiment type'].to_list()]
            var = df_comm['language'].value_counts()
            table_4 = [[i for i in range(1, len(var)+1)],list(var.index),[var[i] for i in range(len(var)) ]]

            return render_template('prediction-1.html',vid=vid,table1=table_1,table2=table_2,table3=table_3,table4=table_4,length1=len(table_1[0]),length2=len(table_2[0]),length3=len(table_4[0]))
            
if __name__ == '__main__':
    app.run()