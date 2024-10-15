import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
import firebase_admin
from firebase_admin import credentials, auth

def main_app():
    # Check for user authentication
    if 'user' not in st.session_state or st.session_state['user'] is None:
        st.error("You need to log in first!")
        st.stop()  # Stop the script if the user is not authenticated

    # If user is authenticated, proceed with the main app logic
    st.title("WhatsApp Chat Analyzer")

    # File uploader and processing logic
    uploaded_file = st.sidebar.file_uploader("Choose a file")
    if uploaded_file is not None:
        # Read file as bytes
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.process_data(data)
        st.dataframe(df)

        # Fetch unique senders
        user_list = df['Sender'].unique().tolist()
        user_list.sort()
        user_list.insert(0, "overall")
        selected_user = st.sidebar.selectbox("Show analysis for", user_list)

        if st.sidebar.button("Show analysis"):
            # All your analysis code here
            num_messages, words, num_media_messages, total_links = helper.fetch_stats(selected_user, df)
            st.title("Top Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.header("Total Messages")
                st.title(num_messages)

            with col2:
                st.header("Number of Words")
                st.title(words)

            with col3:
                st.header("Total Media")
                st.title(num_media_messages)

            with col4:
                st.header("Total Links")
                st.title(total_links)

            # Monthly timeline
            st.title('Monthly Timeline')
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(timeline['time'], timeline['Message'])
            ax.plot(timeline['time'], timeline['Message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # Daily timeline
            st.title('Daily Timeline')
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(daily_timeline['only_date'], daily_timeline['Message'])
            ax.plot(daily_timeline['only_date'], daily_timeline['Message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # Activity Map
            st.title('Activity Map')
            col1, col2 = st.columns(2)

            with col1:
                st.header('Most Busy Day')
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.header('Most Busy Month')
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            # Most Busy Users
            if selected_user == 'overall':
                st.title("Most Busy Users")
                x, new_df = helper.fetch_most_busy_users(df)
                fig, ax = plt.subplots()

                col1, col2 = st.columns(2)

                with col1:
                    ax.bar(x.index, x.values, color='red')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                with col2:
                    st.dataframe(new_df)

            st.title("Word Cloud")
            df_WC = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_WC)
            st.pyplot(fig)

            # Most Common Words
            st.title('Most Common Words')
            most_common_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(most_common_df[0], most_common_df[1])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # Weekly Activity Map
            st.title('Weekly Activity Map')
            user_heatmap = helper.user_heatmap(selected_user, df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)

# Call the main app function if this script is run directly
if __name__ == "__main__":
    main_app()
