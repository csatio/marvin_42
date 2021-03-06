import pandas as pd
import numpy as np
import streamlit as st 
from PIL import Image
from datetime import datetime
import time
import requests
import os
import pickle

urlbase = 'https://mighty-bastion-45199.herokuapp.com/'


def get_result(x):
    try:
        result = pd.DataFrame.from_dict(x.json())
    except:
        result = x.text
    return result

def api_post(route, payload):
    url = urlbase + route
    x = requests.post(url, data = payload)
    df = get_result(x)
    return df

def api_get(route):
    url = urlbase + route
    x = requests.get(url)
    df = get_result(x)
    return df


image = Image.open('Don__t_Panic_Wallpaper_by_rogueXunited.jpg')

st.image(image, caption='')

st.markdown("# BITCOIN BOT MARVIN 42")


def robot():
  
  model = pickle.load(open('best_model_xgb.pkl', 'rb'))



  token = os.environ.get('MARVIN_TOKEN')
  ticker = 'BTCUSDT'
  status=''
  iter=0
  while iter<720:

    df = api_post('cripto_quotation', {'token': token, 'ticker': ticker})

    for i in range(1, 16):
      df["lag_min{}".format(i)] = df.low.shift(i)

    for i in range(1, 16):
      df["lag_max{}".format(i)] = df.high.shift(i)

    df['min_15']=(df[['lag_min15','lag_min14','lag_min13','lag_min12','lag_min11']]).min(axis=1)
    df['min_10']=(df[['lag_min10','lag_min9','lag_min8','lag_min7','lag_min6']]).min(axis=1)
    df['min_5']=(df[['lag_min5','lag_min4','lag_min3','lag_min2','lag_min1']]).min(axis=1)

    df['max_15']=(df[['lag_max15','lag_max14','lag_max13','lag_max12','lag_max11']]).max(axis=1)
    df['max_10']=(df[['lag_max10','lag_max9','lag_max8','lag_max7','lag_max6']]).max(axis=1)
    df['max_5']=(df[['lag_max5','lag_max4','lag_max3','lag_max2','lag_max1']]).max(axis=1)

    df['pivo'] = np.where(
      ((df['max_10'] > df['min_15']) & (df['min_5'] > df['min_15']) & (df['close'] > df['max_10'])), 'PA', np.where(
      ((df['min_10'] < df['max_15']) & (df['max_5'] < df['max_15']) & (df['close'] < df['min_10'])), 'PB', '')) 

    df['close_5'] = df.close.shift(5)

    df_last = df.iloc[[np.argmax(df['datetime'])]]

    df_modelo=df_last[[ 'volume', 'number_of_trades', 'pivo']]

    tendencia = model.predict(df_modelo)[0]

    st.markdown("--------------------")

    st.markdown("Atual (fechamento):")
    st.write(df_last['close'])

    st.markdown("-5 min:")
    st.write(df_last['close_5'])


    st.markdown("Predi????o    1= compra       -1=venda. Setado para |0.3|")
    st.markdown(tendencia)

    

    if tendencia > 0.3 and status=='':
        api_post('buy', payload = {'token': token, 'ticker': ticker, 'quantity': 0.02})
        status='comprado'
        iter_compra=iter
        st.write(api_post('status', payload = {'token': token}))
    if tendencia < -0.3 and status=='':
        api_post('sell', payload = {'token': token, 'ticker': ticker, 'quantity': 0.02})
        status='vendido'
        iter_venda=iter
        st.write(api_post('status', payload = {'token': token}))

    if status=='comprado':
        if  iter>iter_compra+5 or iter==60:
            api_post('sell', payload = {'token': token, 'ticker': ticker, 'quantity': 0.02})
            status=''
            st.write(api_post('status', payload = {'token': token}))

    if status=='vendido':
        if  iter>iter_venda+5 or iter==60:
            api_post('buy', payload = {'token': token, 'ticker': ticker, 'quantity': 0.02})
            status=''
            st.write(api_post('status', payload = {'token': token}))


    st.markdown(status)
    st.markdown(datetime.now())

    time.sleep(60)
    iter=iter+1

if __name__ == '__main__':
    robot()
    