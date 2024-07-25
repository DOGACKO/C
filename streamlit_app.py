import time  # for simulating real-time data, time loop
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import altair as alt
import streamlit as st
# Streamlit page configuration (must be the first Streamlit command)
st.set_page_config(layout="wide")

# Load the data
erimis_path = "C:/Users/dkoral/Desktop/Haziran_Erimişler_2024_py.xlsx"
erimeyecekler_path = "C:/Users/dkoral/Desktop/Haziran_Eriyecekler_2024_py.xlsx"

Erimis = pd.read_excel("C:/Users/dkoral/Desktop/Haziran_Erimişler_2024_py.xlsx")
Erimeyecekler = pd.read_excel("C:/Users/dkoral/Desktop/Haziran_Eriyecekler_2024_py.xlsx")

# Define regions and their corresponding branches
regions_dict = {
    'İstanbul 1. Bölge': ['Bahçeşehir Şubesi', 'Taksim Şubesi', 'Beylikdüzü Şubesi', 'Yeşilyurt Şubesi', 'Maslak Şubesi', 'Güneşli Şubesi'],
    'İstanbul 2. Bölge': ['Kalamış Şubesi', 'Ataşehir Şubesi', 'Maltepe Şubesi', 'Bağdat Caddesi Şubesi', 'Tuzla Şubesi'],
    'İstanbul 3. Bölge': ['Levent Şubesi', 'Nişantaşı Şubesi'],
    'Batı Anadolu Bölge': ['Bodrum Şubesi', 'Bursa Şubesi', 'Denizli Şubesi', 'Ege Şubesi', 'Eskişehir Şubesi', 'İzmir Şubesi', 'Dokuz Eylül Şubesi', '9 Eylül Şubesi'],
    'Anadolu Bölge': ['Adana Şubesi', 'Anadolu Şubesi', 'Antalya Şubesi', 'Başkent Şubesi', 'Diyarbakır Şubesi', 'Gaziantep Şubesi', 'Kayseri Şubesi', 'Mersin Şubesi', 'Samsun Şubesi', 'Trabzon Şubesi'],
    'Ankara Şubesi': ['Ankara Şubesi'],
    'Yatırım Danışmanlığı Merkezi': ['Yatırım Danışmanlığı Merkezi'],
    'Hepsi': ['Bahçeşehir Şubesi', 'Taksim Şubesi', 'Beylikdüzü Şubesi', 'Yeşilyurt Şubesi', 'Maslak Şubesi', 'Güneşli Şubesi', 'Kalamış Şubesi', 'Ataşehir Şubesi', 'Maltepe Şubesi', 'Bağdat Caddesi Şubesi', 'Tuzla Şubesi', 'Levent Şubesi', 'Nişantaşı Şubesi', 'Bodrum Şubesi', 'Bursa Şubesi', 'Denizli Şubesi', 'Ege Şubesi', 'Eskişehir Şubesi', 'İzmir Şubesi', 'Dokuz Eylül Şubesi', '9 Eylül Şubesi', 'Adana Şubesi', 'Anadolu Şubesi', 'Antalya Şubesi', 'Başkent Şubesi', 'Diyarbakır Şubesi', 'Gaziantep Şubesi', 'Kayseri Şubesi', 'Mersin Şubesi', 'Samsun Şubesi', 'Trabzon Şubesi', 'Ankara Şubesi', 'Yatırım Danışmanlığı Merkezi']
}

# Sidebar for user input
st.sidebar.title("Gösterge Paneli Ayarları")
st.sidebar.markdown("### *Ayarlar*")

# Select dataset
selected_dataset = st.sidebar.selectbox('Veri Seti Seçimi', ['Erimiş', 'Eriyecekler'])

# Load selected dataset
if selected_dataset == 'Erimiş':
    data = Erimis
else:
    data = Erimeyecekler

# Select region
selected_region = st.sidebar.selectbox('Bölge Seçimi', list(regions_dict.keys()))

# Filter branches based on selected region
filtered_branches = regions_dict[selected_region]

# Select branches within the selected region
selected_branches = st.sidebar.multiselect('Şube Seçimi', filtered_branches, default=filtered_branches)

# List of Months
month_columns = ['Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz']
selected_months = st.sidebar.multiselect('Ayları Seçin', month_columns, default=month_columns)

# Filter data based on selections
filtered_data = data[data['Şube'].isin(selected_branches)]

# Filter the data based on selected months
monthly_data = filtered_data[['Müşteri Adı', 'Şube', 'Gelir'] + selected_months].copy()
monthly_data['Toplam_Gelir'] = monthly_data[selected_months].sum(axis=1)

# Pivot table creation
try:
    pivot_table = monthly_data.pivot_table(
        values='Toplam_Gelir',  # Total Gelir for selected months
        index='Müşteri Adı',  # Customer names
        columns='Şube',  # Branches
        aggfunc='sum',  # Aggregation function
        fill_value=0  # Fill missing values with 0
    )
except KeyError as e:
    st.error(f"KeyError: {e}. Lütfen sütun isimlerini kontrol edin.")
    pivot_table = pd.DataFrame()  # Set to empty DataFrame to avoid further errors

pivot_table.reset_index(inplace=True)

if not pivot_table.empty:
    pivot_chart = alt.Chart(pivot_table.melt(id_vars=['Müşteri Adı'], var_name='Şube', value_name='Toplam_Gelir')).mark_bar().encode(
        x=alt.X('Müşteri Adı:N', title='Müşteri'),
        y=alt.Y('Toplam_Gelir:Q', title='Toplam Gelir'),
        color=alt.Color('Şube:N', title='Şube', scale=alt.Scale(scheme='category20b')),
        tooltip=['Müşteri Adı:N', 'Şube:N', 'Toplam_Gelir:Q']
    ).properties(
        height=400,
        width=600,
        title='Müşteri ve Şubeye Göre Gelir'
    )

# Şube Bazında Gelir dağılımı
branch_revenue = monthly_data.groupby('Şube')['Toplam_Gelir'].sum().reset_index()
branch_revenue['Percentage'] = (branch_revenue['Toplam_Gelir'] / branch_revenue['Toplam_Gelir'].sum()) * 100

# Bar chart instead of pie chart
branch_bar_chart = alt.Chart(branch_revenue).mark_bar().encode(
    x=alt.X('Şube:N', title='Şube'),
    y=alt.Y('Toplam_Gelir:Q', title='Toplam Gelir'),
    color=alt.Color('Şube:N', title='Şube', scale=alt.Scale(scheme='category20b')),
    tooltip=[alt.Tooltip('Şube:N', title='Şube'), alt.Tooltip('Toplam_Gelir:Q', title='Gelir')]
).properties(
    height=300,
    width=600,
    title='Şubelere Göre Gelir Dağılımı'
)

# Müşteri & Gelir
top_customers = monthly_data.groupby('Müşteri Adı')['Toplam_Gelir'].sum().reset_index().sort_values(by='Toplam_Gelir', ascending=False).head(10)
top_customers_chart = alt.Chart(top_customers).mark_bar().encode(
    x=alt.X('Müşteri Adı:N', title='Müşteri'),
    y=alt.Y('Toplam_Gelir:Q', title='Toplam Gelir'),
    color=alt.Color('Müşteri Adı:N', legend=None, scale=alt.Scale(scheme='category20b')),
    tooltip=['Müşteri Adı:N', 'Toplam_Gelir:Q']
).properties(
    height=300,
    title='Gelirine Göre İlk 10 Müşteri'
)

# Şube Bazında Ortalama Gelir
avg_revenue_branch = monthly_data.groupby('Şube')['Toplam_Gelir'].mean().reset_index()
avg_revenue_branch_chart = alt.Chart(avg_revenue_branch).mark_bar().encode(
    x=alt.X('Şube:N', title='Şube'),
    y=alt.Y('Toplam_Gelir:Q', title='Ortalama Gelir'),
    color=alt.Color('Şube:N', legend=None, scale=alt.Scale(scheme='category20b')),
    tooltip=[alt.Tooltip('Şube:N', title='Şube'), alt.Tooltip('Toplam_Gelir:Q', title='Ortalama Gelir')]
).properties(
    height=300,
    title='Şubelere Göre Ortalama Gelir'
)
# Sidebar Metrics
Gerçekleşmiş_Erime_Oranı = 1.21
avg_account_amount = Gerçekleşmiş_Erime_Oranı
st.sidebar.metric(label="Erime Oranı", value=f"{avg_account_amount:.2f}%")

avg_gelir = 13684265.00
formatted_avg_gelir = "{:,.2f}".format(avg_gelir)
st.sidebar.metric(label="Erimişlerin Komisyon Geliri", value=formatted_avg_gelir)

eriyecekler_yüzde = 20.19
eriyecekler_yüzde = eriyecekler_yüzde
st.sidebar.metric(label="Eriyecekler Yüzdesi", value=f"{eriyecekler_yüzde:.2f}%")

eriyecekler_sayısı = 2927
eriyecekler_sayısı = eriyecekler_sayısı
st.sidebar.metric(label="Eriyecekler Sayısı", value=f"{eriyecekler_sayısı:.2f}")

# Display the charts
st.title("Erimişler ve Eriyecekler Gösterge Paneli")
st.markdown("### Şube ve Müşteriye Göre Gelir Analizi")

st.altair_chart(pivot_chart, use_container_width=True)
st.altair_chart(branch_bar_chart, use_container_width=True)
st.altair_chart(top_customers_chart, use_container_width=True)
st.altair_chart(avg_revenue_branch_chart, use_container_width=True)


