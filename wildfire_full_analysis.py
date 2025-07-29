import pandas as pd
import time
import os
from geopy.geocoders import Nominatim
import folium
from IPython.display import IFrame

def show_map():
    # ✅ 1. GitHub에 있는 CSV 불러오기
    csv_url = "https://raw.githubusercontent.com/taegwon04/wildfire_Analysis/main/wildfire_data.csv"
    df = pd.read_csv(csv_url, encoding='cp949')

    # ✅ 2. 데이터 정제
    df['예보일시'] = pd.to_datetime(df['예보일시'])
    df_sorted = df.sort_values(by='예보일시', ascending=False)
    df_recent = df_sorted.head(500).copy()

    # ✅ 3. 주소 → 위경도 변환
    geolocator = Nominatim(user_agent="wildfire_alerts", timeout=5)
    coord_cache = {}

    def get_location(address):
        if address in coord_cache:
            return coord_cache[address]
        try:
            location = geolocator.geocode(address)
            time.sleep(1)
            if location:
                coords = pd.Series([location.latitude, location.longitude])
            else:
                coords = pd.Series([None, None])
        except:
            coords = pd.Series([None, None])
        coord_cache[address] = coords
        return coords

    df_recent['주소'] = df_recent.apply(lambda row: f"대한민국 {row['시도명']} {row['시군구명']} {row['읍면동명']}", axis=1)
    unique_addresses = df_recent[['주소']].drop_duplicates().reset_index(drop=True)
    unique_addresses[['lat', 'lon']] = unique_addresses['주소'].apply(get_location)
    df_recent = pd.merge(df_recent, unique_addresses, on='주소', how='left')

    # ✅ 4. 지도 시각화
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    for idx, row in df_recent.iterrows():
        if pd.notnull(row['lat']) and pd.notnull(row['lon']):
            color = "red" if "주의보" in str(row.get("등급", "")) else "orange"
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f"{row['예보일시']}"
            ).add_to(m)

    # ✅ 5. 저장 + 출력
    map_path = os.path.abspath("wildfire_alerts_map.html")
    m.save(map_path)
    return IFrame(src=map_path, width=1000, height=600)
