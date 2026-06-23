import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# ==========================================================
# TAMPILAN WEBSITE (STREAMLIT)
# ==========================================================
st.set_page_config(page_title="Sisprod Scheduling App", layout="wide")

st.title("📊 Aplikasi Penjadwalan FCFS")
st.write("Dibuat oleh: Halisa Dwi Humaira")
st.markdown("---")

st.subheader("📋 Input Data & Kebutuhan Waktu (Silakan Edit Angka di Bawah Ini)")
st.info("💡 **Tips:** Kamu bisa mengklik langsung sel angka di bawah ini untuk mengubah nilai *Arrival Time*, *Processing Time*, atau *Due Date*. Hasil di bawah akan langsung berubah otomatis!")

# 1. MENYIAPKAN DATA AWAL DALAM BENTUK DATAFRAME PANDAS
if 'df_sumber' not in st.session_state:
    # Kita buat cetakan data awal terlebih dahulu
    data_awal = {
        "Job": ["J1", "J2", "J3", "J4", "J5"],
        "Produk": ["Rak Buku", "Meja Belajar", "Kursi Lipat", "Lemari Mini", "Meja TV"],
        "Arrival Time": [0, 1, 3, 5, 7],
        "PT Mesin 1": [4, 6, 3, 5, 4],
        "PT Mesin 2": [3, 5, 4, 6, 3],
        "Due Date": [10, 18, 14, 22, 25]
    }
    st.session_state.df_sumber = pd.DataFrame(data_awal)

# MENGGUNAKAN st.data_editor AGAR TABEL BISA DI-EDIT OLEH USER
df_di_edit = st.data_editor(
    st.session_state.df_sumber, 
    use_container_width=True,
    num_rows="fixed", # Mengunci jumlah baris agar tetap 5 job
    disabled=["Job", "Produk"] # Mengunci nama produk agar yang bisa diedit hanya angka parameternya saja
)

# MENGUBAH KEMBALI DATAFRAME YANG SUDAH DI-EDIT MENJADI FORMAT LIST 'daftar_job' SEPERTI KODINGANMU
daftar_job = df_di_edit.values.tolist()

# ==========================================================
# LOGIKA PERHITUNGAN (Sama persis dengan logika asli milikmu)
# ==========================================================
daftar_job.sort(key=lambda x: x[2]) # Urutkan berdasarkan AT

waktu_m1, waktu_m2 = 0, 0
timeline_m1, timeline_m2 = [], []
total_tardiness, jumlah_terlambat = 0, 0

# Penampung data untuk tabel hasil di web
hasil_tabel = []

for job in daftar_job:
    kode, produk, at, pt1, pt2, due_date = job
    
    start_m1 = max(at, waktu_m1)
    end_m1 = start_m1 + pt1
    timeline_m1.append([kode, produk, start_m1, pt1])
    waktu_m1 = end_m1 
    
    start_m2 = max(end_m1, waktu_m2)
    end_m2 = start_m2 + pt2
    timeline_m2.append([kode, produk, start_m2, pt2])
    waktu_m2 = end_m2 
    
    tardiness = max(0, end_m2 - due_date)
    total_tardiness += tardiness
    if tardiness > 0:
        jumlah_terlambat += 1
        
    hasil_tabel.append({
        "Job": kode, "Produk": produk, "AT": at, 
        "PT M1": pt1, "End M1": end_m1, 
        "Start M2": start_m2, "End M2 (CT)": end_m2, 
        "Due Date": due_date, "Tardiness": tardiness
    })

makespan = waktu_m2

# ==========================================================
# MENAMPILKAN HASIL DI WEBSITE
# ==========================================================
st.subheader("🚀 Hasil Perhitungan Penjadwalan")

# Membuat kolom metrik agar terlihat profesional
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="Makespan (Total Waktu)", value=f"{makespan} Jam/Menit")
kpi2.metric(label="Total Keterlambatan", value=f"{total_tardiness} Jam/Menit")
kpi3.metric(label="Produk Terlambat", value=f"{jumlah_terlambat} / {len(daftar_job)}")

# Tampilkan tabel hasil
st.dataframe(hasil_tabel, use_container_width=True)

# ==========================================================
# MEMBUAT GRAPH / GANTT CHART
# ==========================================================
# ==========================================================
# MEMBUAT GRAPH / GANTT CHART (DENGAN TOMBOL)
# ==========================================================
st.subheader("🖼️ Visualisasi Gantt Chart")

# Buat tombol pemicu di sini
if st.button("📊 Tampilkan Gantt Chart", type="primary"):
    
    fig, ax = plt.subplots(figsize=(12, 4.5))
    warna_job = {"J1": "#4E79A7", "J2": "#F28E2B", "J3": "#E15759", "J4": "#76B7B2", "J5": "#59A14F"}

    for baris in timeline_m1:
        kode, produk, start, durasi = baris
        ax.broken_barh([(start, durasi)], (15, 3), facecolors=warna_job[kode], edgecolor='black')
        ax.text(start + durasi/2, 16.5, f"{kode}\n({produk})", ha='center', va='center', color='white', fontweight='bold', fontsize=9)

    for baris in timeline_m2:
        kode, produk, start, durasi = baris
        ax.broken_barh([(start, durasi)], (7, 3), facecolors=warna_job[kode], edgecolor='black')
        ax.text(start + durasi/2, 8.5, f"{kode}\n({produk})", ha='center', va='center', color='white', fontweight='bold', fontsize=9)

    ax.set_ylim(4, 21)
    ax.set_xlim(0, makespan + 2)
    ax.set_xlabel('Garis Waktu / Timeline Produksi', fontsize=10, fontweight='bold')
    ax.set_yticks([16.5, 8.5])
    ax.set_yticklabels(['Mesin 1\n(Potong CNC)', 'Mesin 2\n(Finishing/Cat)'], fontsize=10, fontweight='bold')
    ax.set_xticks(range(0, makespan + 3, 2))
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()

    # Tampilkan grafik matplotlib di web Streamlit
    st.pyplot(fig)
else:
    st.info("Klik tombol merah/biru di atas untuk melihat visualisasi jadwal lini produksi.")

# Tampilkan grafik matplotlib di web Streamlit
st.pyplot(fig)
