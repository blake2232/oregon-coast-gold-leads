# 🪙 Oregon Gold Leads — Public Beta

Live: https://blake2232.github.io/oregon-coast-gold-leads/

An interactive, mobile-friendly field map of Oregon gold prospecting leads:
- **Central coast:** lidar-detected candidates (Cape Perpetua, Heceta Head, Upper Yachats, Whiskey Run), USGS MRDS mines and historic newspaper leads (1853–1931).
- **SW Oregon gold country** (Josephine, Jackson, Curry, Douglas, Coos): 4,771 metallic mine records (USGS MRDS + DOGAMI MILO-4, merged and clustered), 17 mining-district center markers with sourced history, and 8 lidar candidates from USGS 3DEP 1 m DEMs (Josephine Creek, Sucker Creek, Upper Applegate, Mule Creek).
- **Land status** for every site comes from BLM Surface Management Agency data, and an optional BLM SMA overlay is included.

- Static site (Leaflet), no backend. The data and images are bundled, so it works offline as a folder. Basemaps need a network connection.
- Run locally: `python3 -m http.server 8080` and open http://localhost:8080
- Feedback / early access: [open an issue](https://github.com/blake2232/oregon-coast-gold-leads/issues/new?template=early-access.md)

## Disclaimer
This map is for information only and is **not legal advice**. Many sites are on **private land**, and listing them here gives no permission to enter. Respect ARPA, ORS 358, Oregon Parks rules and salmon-stream mining restrictions. Data is provided AS IS, and accuracy is not guaranteed. See the in-app Legal & Terms panel.

Sources: USGS 3DEP & MRDS (public domain); Historic Oregon Newspapers (University of Oregon Libraries).
