import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid




def build_sidebar():
    st.image("images\logolateral.jpeg")
    ticker_list = pd.read_csv("tickers_ibra.csv", index_col=0)
    tickers = st.multiselect(label="Selecione as Empresas", options=ticker_list, placeholder="Códigos")
    tickers = [t+".SA" for t in tickers]
    start_date = st.date_input("De", format="DD/MM/YYYY", value=datetime(2023,1,1))
    end_date = st.date_input("Até", format="DD/MM/YYYY", value="today")
    
    if tickers:
        valid_tickers = []
        for ticker in tickers:
            try:
                yf.Ticker(ticker).info  # Checa se o ticker existe
                valid_tickers.append(ticker)
            except:
                st.warning(f"O ticker {ticker} não é válido ou foi deslistado.")
        
        if valid_tickers:
            prices = yf.download(valid_tickers, group_by='Ticker', start=start_date, end=end_date)
            prices = prices.xs('Close', axis=1, level=1)
            prices.columns = prices.columns.str.rstrip(".SA")
            return valid_tickers, prices
        else:
            st.error("Nenhum ticker válido foi selecionado.")
            return [], pd.DataFrame()
    else:
        return [], pd.DataFrame()

def build_main(valid_tickers, prices):
    weights = np.ones(len(valid_tickers))/len(valid_tickers)
    prices["Portifolio"] = prices @ weights
    norm_prices = 100 * prices / prices.iloc[0]
    returns = prices.pct_change()[1:]
    vols = returns.std()*np.sqrt(252)
    rets = (norm_prices.iloc[-1] - 100)/100

    mygrid = grid(5, 5, 5, 5, 5, 5, vertical_align="top")
    for t in prices.columns:
        c = mygrid.container(border=True)
        c.subheader(t, divider="red")
        colA, colB, colC = c.columns(3)
        if t == "Portifolio":
            colA.image("images\portfolio.png")
        else:
            colA.image(f"https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/{t}.png", width=85)
        colB.metric(label="Retorno", value=f"{rets[t]:.0%}")
        colC.metric(label="Volatilidade", value=f"{vols[t]:.0%}")
        style_metric_cards(background_color='rga(255,255,255,0)')

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("Desempenho Relativo")
        st.line_chart(norm_prices, height=600)

    with col2:
        st.subheader("Risco-Retorno")
        fig = px.scatter(
            x=vols,
            y=rets,
            text=vols.index,
            color=rets/vols,
            color_continuous_scale=px.colors.sequential.Bluered_r
        )
        fig.update_traces(
            textfont_color="white",
            marker=dict(size=45),
            textfont_size=10,
        )
        fig.layout.yaxis.title = "Retorno Total"
        fig.layout.xaxis.title = "Volatilidade Anualizada"
        fig.layout.height = 600
        fig.layout.xaxis.tickformat = ".0%"
        fig.layout.yaxis.tickformat = ".0%"
        fig.layout.coloraxis.colorbar.title = "Sharpe"
        st.plotly_chart(fig, use_container_width=True)




st.set_page_config(layout="wide")

with st.sidebar:
    valid_tickers, prices = build_sidebar()

st.title('Stock DashBoard Python')

if valid_tickers:
    build_main(valid_tickers, prices)