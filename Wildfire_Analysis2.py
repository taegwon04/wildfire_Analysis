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