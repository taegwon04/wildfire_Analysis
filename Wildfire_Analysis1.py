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
