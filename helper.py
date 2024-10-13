from urlextract import URLExtract
extractor = URLExtract()
from wordcloud import WordCloud
import pandas as pd
from collections import Counter


def fetch_stats(selected_user, df):
    if selected_user != "overall":
        df = df[df['Sender'] == selected_user]

    num_messages= df.shape[0]
    # number of worde
    words = []
    for message in df['Message']:
        words.extend(message.split())


    # fetch the number of media messages
    num_media_messages = df[df['Message'] == '<Media omitted>'].shape[0]

    links = []
    for message in df['Message']:
        links.extend(extractor.find_urls(message))
 
    
    return num_messages, len(words), num_media_messages, len(links)
 
def fetch_most_busy_users(df):
    x = df['Sender'].value_counts().head()
    df = round((df['Sender'].value_counts() / df.shape[0])*100,2).reset_index().rename(columns = {'index': 'name', 'user':'percent'})
    return x, df

def create_wordcloud(selcted_user , df):
    if selcted_user != "overall":
        df = df[df['Sender'] == selcted_user]

    f= open('stop_words.txt', 'r')
    stop_words = f.read()

    temp = df[df['Sender'] != 'group_notification']
    temp = temp[temp['Message'] != '<Media omitted>']
    temp = temp[temp['Message'] != 'null']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    
    WC = WordCloud(width =500 , height = 500 , min_font_size = 10 , background_color = 'white' )
    temp['Message'] = temp['Message'].apply(remove_stop_words)
    df_WC = WC.generate(temp['Message'].str.cat(sep=" "))
    return df_WC

def most_common_words( selected_user,df):
    f= open('stop_words.txt', 'r')
    stop_words = f.read()
    if selected_user != 'overall':
        df = df[df['Sender'] == selected_user]

    temp = df[df['Sender'] != 'group_notification']
    temp = temp[temp['Message'] != '<Media omitted>']
    temp = temp[temp['Message'] != 'null']

    words= []

    for message in temp['Message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    return_df = pd.DataFrame(Counter(words).most_common(20))
    return return_df

def monthly_timeline(selected_user , df):
    if selected_user != "overall":
        df = df[df['Sender'] == selected_user]

    timeline = df.groupby(['year', 'month_number' , 'month']).count()['Message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i]+ '-' + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline

def daily_timeline(selected_user , df):
    if selected_user != "overall":
        df = df[df['Sender'] == selected_user]
    daily_timeline = df.groupby('only_date').count()['Message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != "overall":
        df = df[df['Sender'] == selected_user]
    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != "overall":
        df = df[df['Sender'] == selected_user]
    return df['month'].value_counts()

def user_heatmap(selected_user, df):
    if selected_user != "overall":
        df = df[df['Sender'] == selected_user]
    activity_heatmap= df.pivot_table(index = 'day_name', columns= 'period', values= 'Message', aggfunc = 'count').fillna(0)
    return activity_heatmap


