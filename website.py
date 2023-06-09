import streamlit as st
import requests
import pandas as pd 
# from results import *

# def convertMillis(start_ms):
#     seconds = int((start_ms/1000)%60)
#     minutes = int((start_ms/(1000*60))%60)
#     hours = int((start_ms/(1000*60*60))%24)
#     btn_text = ''
#     if hours > 0:
#         btn_txt += f'{hours:02d}:{minutes:02d}:{seconds:02d}'
#     else:
#         btn_text += f'{minutes:02d}:{seconds:02d}'
#     return btn_txt

# import requests
# from configure import *
auth_token = st.text_input('type in your ASSEMBLYAI auth token:')

headers = {"authorization":auth_token, "content-type":"application/json"}

def upload_to_AssemblyAI(audio_file):
    transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
    upload_endpoint = "https://api.assemblyai.com/v2/upload"
    print('uploading')
    upload_response = requests.post(upload_endpoint, headers = headers, data = audio_file)
    audio_url = upload_response.json()['upload_url']
    print('done')
    json = { "audio_url": audio_url, "iab_categories":True, "auto_chapters":True}
    response = requests.post(transcript_endpoint,json = json, headers = headers)
    print(response.json())
    polling_endpoint = transcript_endpoint + "/" + response.json()['id']
    return polling_endpoint

uploaded_file = st.file_uploader('Please upload a file')

if uploaded_file is not None:
    st.audio(uploaded_file, start_time = 0)
    polling_endpoint = upload_to_AssemblyAI(uploaded_file)
    
    status = 'submitted'
    while status != 'completed':
        polling_response = requests.get(polling_endpoint, headers = headers)
        status = polling_response.json()['status']
        
        if status == 'completed':
            st.subheader('Main themes')
            with st.expander('Themes'):
                categories = polling_response.json()['iab_categories_result']['summary']
                for cat in categories:
                    st.markdown("* " + cat)
            
            
            st.subheader('Summary Notes')
            chapters = polling_response.json()['chapters']
            chapters_df = pd.DataFrame(chapters)
            # chapters_df['start_str'] = chapters_df['start'].apply(convertMillis)
            # chapters_df['end_str'] = chapters_df['end'].apply(convertMillis)
            
            
            with st.container():
                st.dataframe(chapters_df)
                for index, row in chapters_df.iterrows():
                    with st.expander(row['gist']):
                        st.write(row['summary'])
                        # st.button(row['start_str'])
