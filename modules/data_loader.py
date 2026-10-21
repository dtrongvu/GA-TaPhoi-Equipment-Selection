"""
data_loader.py - Data Ingestion and Preprocessing Module
=========================================================
Project: GA-TaPhoi-Equipment-Selection
Mining Site: Sector B, Tả Phời Copper Mine, Lào Cai, Vietnam
Target Journal: Acta Montanistica Slovaca (AMS)

This module handles the loading, type casting, and preprocessing of the four
primary engineering, geomechanical, operational, and financial database tables
from Google Sheets (via gspread & google.auth) or local CSV fallbacks.
"""

import os
import pandas as pd
import numpy as np

def authenticate_google_colab():
    """
    Authenticates Google Colab user session and returns a gspread client instance.
    Returns None if running outside Google Colab or if authentication fails.
    """
    try:
        from google.colab import auth
        from google.auth import default
        import gspread
        
        print("Authenticating Google Colab user session...")
        auth.authenticate_user()
        creds, _ = default()
        gc = gspread.authorize(creds)
        print("✅ Google Colab authentication successful!")
        return gc
    except Exception as e:
        print(f"⚠️ Google Colab auth skipped or unavailable ({e}). Using local fallback if needed.")
        return None


def read_sheet_to_df(gc, sheet_name):
    """
    Reads a Google Sheet tab into a Pandas DataFrame using a gspread client instance.
    """
    if gc is None:
        return None
    try:
        worksheet = gc.open(sheet_name).sheet1
        rows = worksheet.get_all_values()
        if not rows:
            return None
        df = pd.DataFrame.from_records(rows[1:], columns=rows[0])
        print(f"✅ Successfully loaded Google Sheet: '{sheet_name}'")
        return df
    except Exception as e:
        print(f"❌ Error loading Google Sheet '{sheet_name}': {e}")
        return None


def load_database():
    """
    Primary data ingestion pipeline. Loads all 4 database tables, casts numeric
    data types, and prepares lookup dictionaries for economic/geomechanical inputs.
    
    Returns:
        tuple: (df_bang1, df_bang2, df_bang3, df_bang4, kinh_te, dia_chat)
    """
    gc = authenticate_google_colab()

    # 1. Read the 4 database tables from Google Sheets
    df_bang1 = read_sheet_to_df(gc, 'Bảng 1: Ràng buộc mục tiêu và Thông số địa chất')
    df_bang2 = read_sheet_to_df(gc, 'Bảng 2: Cơ sở dữ liệu Máy xúc')
    df_bang3 = read_sheet_to_df(gc, 'Bảng 3: Cơ sở dữ liệu Ô tô vận tải')
    df_bang4 = read_sheet_to_df(gc, 'Bảng 4: Thông số vận hành và Kinh tế')

    # 2. Local CSV / Default Fallback if Google Sheets are not accessible
    if df_bang1 is None:
        print("ℹ️ Loading local fallback data for Table 1 (Geomechanical & Targets)...")
        df_bang1 = pd.DataFrame({
            'Thông số': [
                'Sản lượng đất đá mục tiêu (A_đ)', 'Sản lượng quặng mục tiêu (A_q)',
                'Cung độ vận tải đất đá (L_đ)', 'Cung độ vận tải quặng (L_q)',
                'Tỷ trọng đất đá (gamma_đ)', 'Tỷ trọng quặng (gamma_q)',
                'Hệ số tơi đất đá (K_t_đ)', 'Hệ số tơi quặng (K_t_q)',
                'Chiều cao tầng (h)', 'Góc dốc đường ramp (i)'
            ],
            'Giá trị': [4500000, 1000000, 5.25, 2.16, 2.65, 2.95, 1.45, 1.55, 12, 0.08]
        })

    if df_bang2 is None:
        print("ℹ️ Loading local fallback data for Table 2 (Excavators)...")
        df_bang2 = pd.DataFrame({
            'Mã số': [0, 1, 2, 3],
            'Loại máy': ['Komatsu PC1250', 'Komatsu PC650', 'Komatsu PC450', 'EKG-8U'],
            'Chủng loại': ['Thủy lực Diesel', 'Thủy lực Diesel', 'Thủy lực Diesel', 'Điện cáp'],
            'E (m3)': [6.7, 2.7, 2.3, 8.0],
            'T_ck (s)': [36, 31, 31, 40],
            'Giá mua (triệu VND)': [8500, 3500, 2800, 12000]
        })

    if df_bang3 is None:
        print("ℹ️ Loading local fallback data for Table 3 (Dump Trucks)...")
        df_bang3 = pd.DataFrame({
            'Mã số': [0, 1, 2, 3],
            'Loại xe': ['Tonly MT95', 'HOWO Sinotruk', 'MT95 Heavy', 'Komatsu HD325-7'],
            'Tải trọng q (tấn)': [55, 24, 70, 36],
            'Dung tích V (m3)': [25, 13, 34, 18],
            'V_ct (km/h)': [20, 20, 20, 20],
            'V_kt (km/h)': [30, 30, 30, 30],
            'Giá mua (triệu VND)': [4200, 1500, 5500, 3800]
        })

    if df_bang4 is None:
        print("ℹ️ Loading local fallback data for Table 4 (Economic & Operational Parameters)...")
        df_bang4 = pd.DataFrame({
            'Hạng mục': [
                'Đơn giá dầu Diezel', 'Giá bán quặng tinh', 'Hệ số thu hồi quặng tinh',
                'Lương lái ô tô', 'Lương lái máy xúc', 'Thuế tài nguyên',
                'Thuế thu nhập DN', 'Lãi suất vay vốn', 'Đơn giá điện công nghiệp'
            ],
            'Giá trị (triệu VND)': [0.021, 22.0, 0.032, 12.0, 15.0, 2.0, 25.0, 15.0, 0.00195]
        })

    # 3. Numeric Type Casting & Formatting
    df_bang1['Giá trị'] = pd.to_numeric(df_bang1['Giá trị'], errors='coerce')
    
    df_bang2['E (m3)'] = pd.to_numeric(df_bang2['E (m3)'], errors='coerce')
    df_bang2['T_ck (s)'] = pd.to_numeric(df_bang2['T_ck (s)'], errors='coerce')
    df_bang2['Giá mua (triệu VND)'] = pd.to_numeric(df_bang2['Giá mua (triệu VND)'], errors='coerce')

    df_bang3['Tải trọng q (tấn)'] = pd.to_numeric(df_bang3['Tải trọng q (tấn)'], errors='coerce')
    df_bang3['V_ct (km/h)'] = pd.to_numeric(df_bang3['V_ct (km/h)'], errors='coerce')
    df_bang3['V_kt (km/h)'] = pd.to_numeric(df_bang3['V_kt (km/h)'], errors='coerce')
    df_bang3['Giá mua (triệu VND)'] = pd.to_numeric(df_bang3['Giá mua (triệu VND)'], errors='coerce')

    col_econ = 'Giá trị (triệu VND)'
    df_bang4[col_econ] = pd.to_numeric(df_bang4[col_econ], errors='coerce')

    # 4. Construct Lookup Dictionaries
    kinh_te = dict(zip(df_bang4['Hạng mục'], df_bang4[col_econ]))
    dia_chat = dict(zip(df_bang1['Thông số'], df_bang1['Giá trị']))

    print("✅ All database tables loaded, sanitized, and ready for GA evaluation!")
    return df_bang1, df_bang2, df_bang3, df_bang4, kinh_te, dia_chat


if __name__ == '__main__':
    # Test script standalone
    df1, df2, df3, df4, econ_dict, geo_dict = load_database()
    print("\n--- Sample Excavator Catalog (Table 2) ---")
    print(df2[['Loại máy', 'E (m3)', 'T_ck (s)', 'Giá mua (triệu VND)']])
    print("\n--- Sample Dump Truck Catalog (Table 3) ---")
    print(df3[['Loại xe', 'Tải trọng q (tấn)', 'Giá mua (triệu VND)']])
