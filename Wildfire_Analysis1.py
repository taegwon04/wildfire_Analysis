from geopy.geocoders import Nominatim
import time
import pandas as pd

geolocator = Nominatim(user_agent="wildfire_alerts")
coord_cache = {}

def get_location(address):
    # 캐시 확인
    if address in coord_cache:
        return coord_cache[address]
    try:
        location = geolocator.geocode(address)
        time.sleep(1)  # Rate limit
        if location:
            coords = pd.Series([location.latitude, location.longitude])
        else:
            coords = pd.Series([None, None])
    except:
        coords = pd.Series([None, None])

    # 캐시에 저장
    coord_cache[address] = coords
    return coords
# 최근 100건만 예시로 사용
df_recent = df_sorted.head(500)

# 유니크 주소만 추출
df_recent['주소'] = df_recent.apply(lambda row: f"대한민국 {row['시도명']} {row['시군구명']} {row['읍면동명']}", axis=1)
unique_addresses = df_recent[['주소']].drop_duplicates().reset_index(drop=True)

# 유니크 주소에만 geocode 수행
unique_addresses[['lat', 'lon']] = unique_addresses['주소'].apply(get_location)

# 원본 데이터와 merge하여 lat/lon 붙이기
df_recent = pd.merge(df_recent, unique_addresses, on='주소', how='left')


import folium

# 지도 중심 좌표 (대한민국 중앙)
m = folium.Map(location=[36.5, 127.8], zoom_start=7)

# 마커 추가
for idx, row in df_recent.iterrows():
    if pd.notnull(row['lat']) and pd.notnull(row['lon']):
        # 위험도에 따른 색깔 설정
        color = "red" if "주의보" in row["등급"] else "orange"

        # CircleMarker: 작고 예쁜 동그라미
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,               # 동그라미 크기
            color=color,            # 테두리 색
            fill=True,
            fill_color=color,       # 내부 색
            fill_opacity=0.7,
            popup=f"{row['예보일시']}"
        ).add_to(m)

# 지도 저장
m.save("wildfire_alerts_map.html")
m
