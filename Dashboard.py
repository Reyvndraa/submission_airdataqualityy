import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
files = [
    "PRSA_Data_Aotizhongxin_20130301-20170228.csv",
    "PRSA_Data_Changping_20130301-20170228.csv",
    "PRSA_Data_Dingling_20130301-20170228.csv",
    "PRSA_Data_Dongsi_20130301-20170228.csv",
    "PRSA_Data_Guanyuan_20130301-20170228.csv"
]

locations = ["Aotizhongxin", "Changping", "Dingling", "Dongsi", "Guanyuan"]

# Load and preprocess datasets
dfs = {}

for loc, file in zip(locations, files):
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
        df['date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
        df.set_index('date', inplace=True)

        # Ensure numeric data types
        for col in ['PM2.5', 'TEMP', 'HUMI', 'WSPM']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop missing values in existing key columns
        existing_cols = [col for col in ['PM2.5', 'TEMP', 'HUMI', 'WSPM'] if col in df.columns]
        df.dropna(subset=existing_cols, inplace=True)

        dfs[loc] = df
    except Exception as e:
        st.error(f"Error loading {loc}: {e}")

# Set title for the dashboard
st.title("Dashboard Analisis Kualitas Udara")
st.subheader("Analisis Data Kualitas Udara Berdasarkan Faktor Cuaca dan Waktu")

# Sidebar
with st.sidebar:
    st.header("📊 Menu Sidebar")

    # Pilih lokasi
    st.subheader("📍 Pilih Lokasi")
    selected_location = st.selectbox("Lokasi", locations)

    # Tampilkan informasi dataset
    st.subheader("📂 Informasi Dataset")
    st.write(f"Dataset yang dipilih: **{selected_location}**")
    st.write(f"Jumlah baris data: **{len(dfs[selected_location])}**")

    # Filter berdasarkan tanggal
    st.subheader("📅 Filter Tanggal")
    min_date = dfs[selected_location].index.min()
    max_date = dfs[selected_location].index.max()
    start_date = st.date_input("Tanggal Mulai", min_date)
    end_date = st.date_input("Tanggal Selesai", max_date)

    # Filter data berdasarkan tanggal yang dipilih
    filtered_df = dfs[selected_location].loc[start_date:end_date]

    # Informasi Kontak
    st.subheader("📞 Informasi Kontak")
    st.write("Nama: **Yuda Reyvandra Herman**")
    st.write("Email: **reyvandrayuda@gmail.com**")
    st.write("ID Dicoding: **MC189D5Y0450**")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["📈 Analisis Polusi Udara", "📊 Pola Polusi Udara", "📝 Kesimpulan"])

# Tab 1: Analisis Polusi Udara
with tab1:
    st.header("📈 Analisis Polusi Udara")

    st.subheader(f"Data untuk {selected_location}")
    st.write(filtered_df.head())

    available_columns = filtered_df.columns.tolist()

    # Scatter plots
    scatter_plots = [
        ('TEMP', 'PM2.5', 'Hubungan Suhu terhadap PM2.5'),
        ('HUMI', 'PM2.5', 'Hubungan Kelembaban terhadap PM2.5'),
        ('WSPM', 'PM2.5', 'Hubungan Kecepatan Angin terhadap PM2.5')
    ]

    for x_col, y_col, title in scatter_plots:
        if {x_col, y_col}.issubset(available_columns):
            fig, ax = plt.subplots()
            sns.scatterplot(data=filtered_df, x=x_col, y=y_col, ax=ax)
            ax.set_title(f'{title} - {selected_location}')
            st.pyplot(fig)

    # Heatmap korelasi
    required_columns = {'TEMP', 'HUMI', 'WSPM', 'PM2.5'}
    if required_columns.issubset(set(available_columns)):
        fig, ax = plt.subplots()
        sns.heatmap(filtered_df[list(required_columns)].corr(), annot=True, cmap='coolwarm', ax=ax)
        ax.set_title(f'Korelasi Faktor Cuaca terhadap PM2.5 - {selected_location}')
        st.pyplot(fig)

# Tab 2: Pola Polusi Udara
with tab2:
    st.header("📊 Pola Polusi Udara")

    # Penjelasan Umum
    st.write(
        "Bagian ini menganalisis pola polusi udara berdasarkan data PM2.5. "
        "Kita dapat melihat tren bulanan PM2.5 dan membandingkan tingkat polusi antara hari kerja dan akhir pekan."
    )

    # Line plot tren PM2.5
    st.subheader("Tren Polusi PM2.5")
    st.write(
        "Grafik di bawah ini menunjukkan tren bulanan konsentrasi PM2.5 di lokasi yang dipilih. "
        "Tren ini dapat membantu mengidentifikasi pola mus iman atau perubahan tingkat polusi dari waktu ke waktu."
    )
    plt.figure(figsize=(12, 6))
    if 'PM2.5' in filtered_df.columns:
        filtered_df['PM2.5'].resample('M').mean().plot(label=selected_location)

    plt.title('Tren Bulanan PM2.5')
    plt.xlabel('Tanggal')
    plt.ylabel('Rata-rata PM2.5')
    plt.legend()
    st.pyplot(plt)

    # Box plot perbandingan polusi antara hari kerja dan akhir pekan
    st.subheader("Perbandingan PM2.5 antara Hari Kerja dan Akhir Pekan")
    st.write(
        "Grafik di bawah ini membandingkan tingkat polusi PM2.5 antara hari kerja (Senin-Jumat) dan akhir pekan (Sabtu-Minggu). "
        "Perbandingan ini dapat memberikan wawasan tentang apakah aktivitas manusia selama hari kerja memengaruhi tingkat polusi."
    )
    if 'PM2.5' in filtered_df.columns:
        filtered_df['weekday'] = filtered_df.index.weekday
        filtered_df['is_weekend'] = filtered_df['weekday'].apply(lambda x: 1 if x >= 5 else 0)
        fig, ax = plt.subplots()
        sns.boxplot(x='is_weekend', y='PM2.5', data=filtered_df, ax=ax)
        ax.set_title(f"Perbandingan PM2.5 di Hari Kerja vs Akhir Pekan - {selected_location}")
        ax.set_xticklabels(["Hari Kerja", "Akhir Pekan"])
        st.pyplot(fig)

# Tab 3: Kesimpulan
with tab3:
    st.header("📝 Kesimpulan")
    # Ringkasan Analisis Polusi Udara
    st.subheader("Analisis Polusi Udara")
    st.write(
        "Analisis ini menunjukkan hubungan antara faktor cuaca (suhu, kelembaban, dan kecepatan angin) "
        "dan kualitas udara berdasarkan data PM2.5. Berikut adalah ringkasan statistik untuk lokasi yang dipilih:"
    )
    # Tabel Ringkasan Statistik PM2.5
    if 'PM2.5' in filtered_df.columns:
        pm25_stats = filtered_df['PM2.5'].describe().reset_index()
        pm25_stats.columns = ['Statistik', 'Nilai']
        st.write("**Statistik PM2.5:**")
        st.table(pm25_stats)
    # Ringkasan Pola Polusi Udara
    st.subheader("Pola Polusi Udara")
    st.write(
        "Pola polusi udara menunjukkan tren bulanan PM2.5 dan perbandingan tingkat polusi antara hari kerja dan akhir pekan. "
        "Berikut adalah perbandingan rata-rata PM2.5 antara hari kerja dan akhir pekan:"
    )
    # Tabel Perbandingan Hari Kerja vs Akhir Pekan
    if 'PM2.5' in filtered_df.columns:
        filtered_df['weekday'] = filtered_df.index.weekday
        filtered_df['is_weekend'] = filtered_df['weekday'].apply(lambda x: 1 if x >= 5 else 0)
        weekend_comparison = filtered_df.groupby('is_weekend')['PM2.5'].mean().reset_index()
        weekend_comparison['is_weekend'] = weekend_comparison['is_weekend'].map({0: 'Hari Kerja', 1: 'Akhir Pekan'})
        weekend_comparison.columns = ['Jenis Hari', 'Rata-rata PM2.5']
        st.write("**Perbandingan PM2.5 antara Hari Kerja dan Akhir Pekan:**")
        st.table(weekend_comparison)
    # Kesimpulan Umum
    st.subheader("Kesimpulan Umum")
    st.write(
        "1. **Analisis Polusi Udara**: Terdapat hubungan yang signifikan antara faktor cuaca (suhu, kelembaban, dan kecepatan angin) "
        "dan tingkat polusi PM2.5. Data menunjukkan variasi konsentrasi PM2.5 yang dipengaruhi oleh kondisi cuaca."
    )
    st.write(
        "2. **Pola Polusi Udara**: Tren bulanan PM2.5 menunjukkan pola musiman yang jelas, dengan peningkatan polusi pada bulan-bulan tertentu. "
        "Perbandingan antara hari kerja dan akhir pekan menunjukkan bahwa aktivitas manusia selama hari kerja dapat memengaruhi tingkat polusi."
    )
    st.write(
        "3. **Rekomendasi**: Penting untuk terus memantau data kualitas udara dan menerapkan kebijakan yang tepat untuk mengurangi dampak polusi udara "
        "terhadap lingkungan dan kesehatan masyarakat."
    )

# Footer
st.markdown("---")
st.write("© 2025 Yuda Reyvandra Herman. All rights reserved.")