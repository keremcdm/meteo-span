import time
from api_client import fetch_weather_data

print("=" * 50)
print("Test 1: İlk çağrı (API'den çekmeli)")
print("=" * 50)

start = time.time()
df1 = fetch_weather_data()
elapsed1 = time.time() - start

print(f"✓ Süre: {elapsed1:.2f} saniye")
print(f"✓ Satır sayısı: {len(df1)}")
print(f"✓ İlk birkaç satır:")
print(df1.head())

print()
print("=" * 50)
print("Test 2: İkinci çağrı (cache'den gelmeli)")
print("=" * 50)

start = time.time()
df2 = fetch_weather_data()
elapsed2 = time.time() - start

print(f"✓ Süre: {elapsed2:.6f} saniye")
print(f"✓ Satır sayısı: {len(df2)}")

print()
print("=" * 50)
print("Sonuç")
print("=" * 50)
print(f"İlk çağrı:    {elapsed1:.6f} saniye")
print(f"İkinci çağrı: {elapsed2:.6f} saniye")

if elapsed2 > 0:
    speedup = elapsed1 / elapsed2
    print(f"Hızlanma: {speedup:.0f}x daha hızlı")
else:
    print("Hızlanma: ikinci çağrı ölçülemeyecek kadar hızlı (mükemmel cache!)")