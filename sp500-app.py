import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import yfinance as yf

st.title('S&P 500 App')

st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikipedia) and 
its corresponding **stock closing price** (year-to-date).
* **Python libraries:** base64, pandas, streamlit, matplotlib, yfinance
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

# Web scraping of S&P 500 data
@st.cache
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header=0)
    return html[0]


df = load_data()
df = df[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry', 'Headquarters Location', 'Date first added', 'Founded']]

# All data dateframe
st.header('All data')
st.write('Data Dimension: ' + str(df.shape[0]) + ' rows and '
         + str(df.shape[1]) + ' columns.')
st.dataframe(df)


# Download S&P500 data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(load_df):
    csv = load_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href


#Link to download csv file
st.markdown(filedownload(df), unsafe_allow_html=True)


#All data plots
st.header('Sectors')
#data for plotting
sectors = df['GICS Sector'].value_counts(ascending=True)

fig, axs= plt.subplots(1, 2, figsize=(15, 5))

#pie plot
def autopct(pct): # only show the label when it's > 10%
    return ('{:.2f}%'.format(pct))  if pct > 10 else ''


sectors.plot(kind='pie', autopct=autopct, ax=axs[0])
axs[0].axes.get_yaxis().set_visible(False)

#bar plot
sectors.plot(kind='barh', ax=axs[1])
axs[1].set_xlabel('Companies')
plt.subplots_adjust(wspace=0.7)
st.write(fig)


# Sector data
st.header('Data in Selected Sector')
sorted_sector_unique = sorted(df['GICS Sector'].unique())
selected_sector = st.selectbox('', sorted_sector_unique)

# Filtering data
df_selected_sector = df[df['GICS Sector'] == selected_sector].reset_index()

#plot Sub-Industry by number of company
#data for plot
sector_data = df_selected_sector['GICS Sub-Industry'].value_counts(ascending=True)
#plot
fig, ax= plt.subplots()
sector_data.plot(kind='barh', ax=ax)
ax.set_xlabel('Companies count')
ax.set_title(f'{selected_sector}', fontweight='bold')
st.write(fig)

#selected sector data frame
# Download S&P500 data
def filedownload(load_df):
    csv = load_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500_{selected_sector}.csv">Download CSV File (Sector - {selected_sector})</a>'
    return href


#selected sector data frame
if st.button(f'{selected_sector} Data'):
    st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and '
             + str(df_selected_sector.shape[1]) + ' columns.')
    st.dataframe(df_selected_sector)
    # Link to download csv file
    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

#Company finance data
#select company
st.subheader('Finance Company Data \n(https://pypi.org/project/yfinance/)')

#selectboxes
col1, col2 = st.beta_columns(2)

#select company
selected_company = col1.selectbox(f'Company:', df.Security)

#select period
selected_period = col2.selectbox('Period: ', ['1 month', '3 months', '6 months', '1 year', '2 years', '5 years', '10 years', 'all time'])

# get company symbol
selected_symbol = list(df[df['Security'] == selected_company]['Symbol'])[0]


##company data by yfinance https://pypi.org/project/yfinance/
@st.cache
def load_company_data(symbol, period):
    period_dic = {
        '1 month': '1mo',
        '3 months': '3mo',
        '6 months': '6mo',
        '1 year': '1y',
        '2 years': '2y',
        '5 years': '5y',
        '10 years': '10y',
        'all time': 'max'
    }
    company_data = yf.Ticker(symbol)
    company_history = company_data.history(period=period_dic[period], interval='1d', actions=False)
    company_info = company_data.info
    return company_history, company_info

#get company data
company_history, company_info = load_company_data(selected_symbol, selected_period)

#plot company data
fig, ax = plt.subplots(figsize=(15, 5))
ax.fill_between(company_history.index, company_history.Close, color='skyblue', alpha=0.3)
company_history.plot(y='Close', ax=ax)
plt.xticks(rotation=90)
ax.set_title(selected_company, fontweight='bold')
ax.set_xlabel('Date', fontweight='bold')
ax.set_ylabel('Closing Price', fontweight='bold')
st.write(fig)

# Common info about company
st.write(f"**Market Cap :** {company_info['marketCap']}\n")
st.write(f"**Employees :** {company_info['fullTimeEmployees']}\n")
with st.beta_expander(f'{selected_company} - Business Summary'):
    st.write(f"**Business Summary :** \n{company_info['longBusinessSummary']}")