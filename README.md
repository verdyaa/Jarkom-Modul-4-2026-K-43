# Laporan Resmi Praktikum Komunikasi Data & Jaringan Komputer 2026 - Modul 4
> **Serial Experiments Lain — Layer:04: The Wired Expansion**  
> **Kelompok:** K-43  
> **Prefix IP:** `10.85.x.x`  
> **Metode Subnetting:** VLSM (Cisco Packet Tracer) & CIDR (GNS3)

---

## Anggota Kelompok

| NAMA | NRP |
| :--- | :--- |
| **I Ketut Weda Adikusuma** | 5027251061 |
| **D'qhaizhar Ari Dhiaulhaq** | 5027251083 |

---

## Struktur Repository

| Path | Deskripsi |
| :--- | :--- |
| `Subnetting Modul 4 Komdat Jarkom 2026.xlsx` | Perhitungan lengkap 4 sheet (`Rute`, `Pembagian IP - VLSM`, `Penggabungan - CIDR`, `Pembagian IP - CIDR`) |
| `VLSM.pkt` | Topologi & konfigurasi **VLSM** pada **Cisco Packet Tracer** (13 Router, 13 Switch, 25 Host, 1 Cloud) |
| `K-43-MODUL-4.gns3project` | Project **CIDR** pada **GNS3** (`ardhptr21/alpinet:latest`) lengkap dengan konfigurasi persisten |
| `Images/pohon-cidr.png` | Visualisasi pohon biner penggabungan & pembagian IP CIDR (`H1: 10.85.0.0/17` → `A1`–`A25`) |
| `scripts/*.sh`, `scripts/*.py` | Skrip setup & persistensi node GNS3 (`alpinet`) beserta otomasi verifikasi konektivitas |
| `scripts/cpt/*.txt` | Skrip konfigurasi CLI Cisco IOS per-router dan gabungan (`script-gabungan.txt`) untuk Cisco Packet Tracer |

---

## 1. Identifikasi Rute & Kebutuhan Subnet (`A1`–`A25`)

Setiap segmen jaringan dihitung berdasarkan rumus:

$$\text{Jumlah IP Dibutuhkan} = \text{Jumlah Host} + \text{Jumlah Interface Router pada Segmen}$$

Pemilihan panjang prefix $p$ memenuhi $2^{32 - p} - 2 \ge \text{Jumlah IP Dibutuhkan}$ agar alamat Network ID dan Broadcast tidak terpakai oleh host maupun router:

| Subnet | Rute Topologi | Host | Router Port | Jumlah IP | Prefix | Kapasitas Usable |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **A1** | `Cyberia > Switch1 > JJ, MyuMyu` | 125 (95 + 30) | 1 | 126 | `/25` | 126 |
| **A2** | `Cyberia > Wired` | 0 | 2 | 2 | `/30` | 2 |
| **A3** | `Wired > Switch2 > Psyche, Copland, Schumann` | 0 | 4 | 4 | `/29` | 6 |
| **A4** | `Psyche > Switch3 > Karl, Lin` | 880 (700 + 180) | 1 | 881 | `/22` | 1022 |
| **A5** | `Copland > Juri` | 31 | 1 | 32 | `/26` | 62 |
| **A6** | `Copland > Switch4 > Masayuki` | 300 | 1 | 301 | `/23` | 510 |
| **A7** | `Schumann > Akashic` | 3 | 1 | 4 | `/29` | 6 |
| **A8** | `Schumann > Accela` | 0 | 2 | 2 | `/30` | 2 |
| **A9** | `Accela > Switch5 > Omnipresence, Denpa` | 513 (510 + 3) | 1 | 514 | `/22` | 1022 |
| **A10** | `Wired > Navi` | 0 | 2 | 2 | `/30` | 2 |
| **A11** | `Navi > Switch6 > Alice, Reika` | 253 (208 + 45) | 1 | 254 | `/24` | 254 |
| **A12** | `Navi > Switch7 > Taro` | 57 | 1 | 58 | `/26` | 62 |
| **A13** | `Navi > Switch8 > Yasuo, Miho, Kuma` | 142 (120 + 18 + 4) | 1 | 143 | `/24` | 254 |
| **A14** | `Wired > Tachibana` | 0 | 2 | 2 | `/30` | 2 |
| **A15** | `Tachibana > Switch9 > Collective, Ghost` | 266 (260 + 6) | 1 | 267 | `/23` | 510 |
| **A16** | `Tachibana > Deus` | 0 | 2 | 2 | `/30` | 2 |
| **A17** | `Deus > Switch10 > Lilith, Specter` | 98 (77 + 21) | 1 | 99 | `/25` | 126 |
| **A18** | `Deus > Protocol7` | 0 | 2 | 2 | `/30` | 2 |
| **A19** | `Protocol7 > Switch11 > Chisa, Hodgeson` | 32 (23 + 9) | 1 | 33 | `/26` | 62 |
| **A20** | `Protocol7 > Knights` | 0 | 2 | 2 | `/30` | 2 |
| **A21** | `Knights > Eiri` | 2 | 1 | 3 | `/29` | 6 |
| **A22** | `Knights > Phantoma` | 0 | 2 | 2 | `/30` | 2 |
| **A23** | `Phantoma > Switch12 > Semi` | 14 | 1 | 15 | `/27` | 30 |
| **A24** | `Phantoma > Shibuya` | 0 | 2 | 2 | `/30` | 2 |
| **A25** | `Shibuya > Switch13 > Lain, Mika` | 61 (57 + 4) | 1 | 62 | `/26` | 62 |
| **Total** | **25 Segmen Jaringan** | **2775** | **39** | **2814** | **`/19`** | — |

---

## 2. Perhitungan & Implementasi VLSM (Cisco Packet Tracer)

### 2.1 Metodologi VLSM
Pada metode **Variable Length Subnet Masking (VLSM)**, seluruh 25 subnet diurutkan dari ukuran blok terbesar (`/22` = 1024 alamat) hingga terkecil (`/30` = 4 alamat) dan dialokasikan secara berurutan mulai dari `10.85.0.0`. Karena ukuran blok terurut menurun ($1024 \ge 512 \ge 256 \ge \dots \ge 4$), setiap Network ID otomatis selaras pada batas kelipatan binernya **tanpa menyisakan satu pun celah alamat kosong (zero fragmentation)** dari `10.85.0.0` sampai `10.85.16.91`.

### 2.2 Tabel Pembagian IP — VLSM

| Subnet | Prefix | Network ID | Netmask | Broadcast | Range Usable IP |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **A1** | `/25` | `10.85.14.0` | `255.255.255.128` | `10.85.14.127` | `10.85.14.1 - 10.85.14.126` |
| **A2** | `/30` | `10.85.16.56` | `255.255.255.252` | `10.85.16.59` | `10.85.16.57 - 10.85.16.58` |
| **A3** | `/29` | `10.85.16.32` | `255.255.255.248` | `10.85.16.39` | `10.85.16.33 - 10.85.16.38` |
| **A4** | `/22` | `10.85.0.0` | `255.255.252.0` | `10.85.3.255` | `10.85.0.1 - 10.85.3.254` |
| **A5** | `/26` | `10.85.15.192` | `255.255.255.192` | `10.85.15.255` | `10.85.15.193 - 10.85.15.254` |
| **A6** | `/23` | `10.85.8.0` | `255.255.254.0` | `10.85.9.255` | `10.85.8.1 - 10.85.9.254` |
| **A7** | `/29` | `10.85.16.40` | `255.255.255.248` | `10.85.16.47` | `10.85.16.41 - 10.85.16.46` |
| **A8** | `/30` | `10.85.16.60` | `255.255.255.252` | `10.85.16.63` | `10.85.16.61 - 10.85.16.62` |
| **A9** | `/22` | `10.85.4.0` | `255.255.252.0` | `10.85.7.255` | `10.85.4.1 - 10.85.7.254` |
| **A10** | `/30` | `10.85.16.64` | `255.255.255.252` | `10.85.16.67` | `10.85.16.65 - 10.85.16.66` |
| **A11** | `/24` | `10.85.12.0` | `255.255.255.0` | `10.85.12.255` | `10.85.12.1 - 10.85.12.254` |
| **A12** | `/26` | `10.85.15.64` | `255.255.255.192` | `10.85.15.127` | `10.85.15.65 - 10.85.15.126` |
| **A13** | `/24` | `10.85.13.0` | `255.255.255.0` | `10.85.13.255` | `10.85.13.1 - 10.85.13.254` |
| **A14** | `/30` | `10.85.16.68` | `255.255.255.252` | `10.85.16.71` | `10.85.16.69 - 10.85.16.70` |
| **A15** | `/23` | `10.85.10.0` | `255.255.254.0` | `10.85.11.255` | `10.85.10.1 - 10.85.11.254` |
| **A16** | `/30` | `10.85.16.72` | `255.255.255.252` | `10.85.16.75` | `10.85.16.73 - 10.85.16.74` |
| **A17** | `/25` | `10.85.14.128` | `255.255.255.128` | `10.85.14.255` | `10.85.14.129 - 10.85.14.254` |
| **A18** | `/30` | `10.85.16.76` | `255.255.255.252` | `10.85.16.79` | `10.85.16.77 - 10.85.16.78` |
| **A19** | `/26` | `10.85.15.128` | `255.255.255.192` | `10.85.15.191` | `10.85.15.129 - 10.85.15.190` |
| **A20** | `/30` | `10.85.16.80` | `255.255.255.252` | `10.85.16.83` | `10.85.16.81 - 10.85.16.82` |
| **A21** | `/29` | `10.85.16.48` | `255.255.255.248` | `10.85.16.55` | `10.85.16.49 - 10.85.16.54` |
| **A22** | `/30` | `10.85.16.84` | `255.255.255.252` | `10.85.16.87` | `10.85.16.85 - 10.85.16.86` |
| **A23** | `/27` | `10.85.16.0` | `255.255.255.224` | `10.85.16.31` | `10.85.16.1 - 10.85.16.30` |
| **A24** | `/30` | `10.85.16.88` | `255.255.255.252` | `10.85.16.91` | `10.85.16.89 - 10.85.16.90` |
| **A25** | `/26` | `10.85.15.0` | `255.255.255.192` | `10.85.15.63` | `10.85.15.1 - 10.85.15.62` |

### 2.3 Pemetaan Antarmuka & Static Routing Router CPT (`VLSM.pkt`)
Seluruh router Cisco `2811` menggunakan antarmuka Layer-3 (`FastEthernet0/0`, `FastEthernet0/1`, `FastEthernet1/0` via modul `NM-1FE-TX`), ditambah `FastEthernet0/3/0` (`interface Vlan1`) khusus pada router berderajat 4 (`Wired` dan `Navi`). Routing statis diringkas menggunakan default route ke arah upstream (`Cyberia`) serta route summarization pada blok yang bersebelahan biner (seperti `A11 + A13` menjadi `10.85.12.0/23`, `A16 + A18` menjadi `10.85.16.72/29`, dan `A20 + A22` menjadi `10.85.16.80/29`, serta summary tunggal `10.85.0.0/19` pada `Cyberia`):

| Router | Antarmuka & IP | Static Routes (`ip route`) |
| :--- | :--- | :--- |
| **Cyberia** | `Fa0/0`: `10.85.16.57/30` (Wired)<br>`Fa0/1`: `10.85.14.1/25` (Switch1)<br>`Fa1/0`: Cloud0 | `10.85.0.0/19 via 10.85.16.58` |
| **Wired** | `Fa0/0`: `10.85.16.58/30` (Cyberia)<br>`Fa0/1`: `10.85.16.69/30` (Tachibana)<br>`Fa1/0`: `10.85.16.33/29` (Switch2)<br>`Vlan1 (Fa0/3/0)`: `10.85.16.65/30` (Navi) | `0.0.0.0/0 via 10.85.16.57`<br>`10.85.0.0/22 via 10.85.16.34` (Psyche)<br>`10.85.8.0/23, 10.85.15.192/26 via 10.85.16.35` (Copland)<br>`10.85.4.0/22, 10.85.16.40/29, 10.85.16.60/30 via 10.85.16.36` (Schumann)<br>`10.85.12.0/23, 10.85.15.64/26 via 10.85.16.66` (Navi)<br>`10.85.10.0/23, 10.85.14.128/25, 10.85.15.0/26, 10.85.15.128/26, 10.85.16.0/27, 10.85.16.48/29, 10.85.16.72/29, 10.85.16.80/29, 10.85.16.88/30 via 10.85.16.70` (Tachibana) |
| **Psyche** | `Fa0/0`: `10.85.16.34/29` (Switch2)<br>`Fa0/1`: `10.85.0.1/22` (Switch3) | `0.0.0.0/0 via 10.85.16.33` |
| **Copland** | `Fa0/0`: `10.85.16.35/29` (Switch2)<br>`Fa0/1`: `10.85.8.1/23` (Switch4)<br>`Fa1/0`: `10.85.15.193/26` (Juri) | `0.0.0.0/0 via 10.85.16.33` |
| **Schumann** | `Fa0/0`: `10.85.16.36/29` (Switch2)<br>`Fa0/1`: `10.85.16.61/30` (Accela)<br>`Fa1/0`: `10.85.16.41/29` (Akashic) | `0.0.0.0/0 via 10.85.16.33`<br>`10.85.4.0/22 via 10.85.16.62` |
| **Accela** | `Fa0/0`: `10.85.16.62/30` (Schumann)<br>`Fa0/1`: `10.85.4.1/22` (Switch5) | `0.0.0.0/0 via 10.85.16.61` |
| **Navi** | `Fa0/0`: `10.85.16.66/30` (Wired)<br>`Fa0/1`: `10.85.15.65/26` (Switch7)<br>`Fa1/0`: `10.85.12.1/24` (Switch6)<br>`Vlan1 (Fa0/3/0)`: `10.85.13.1/24` (Switch8) | `0.0.0.0/0 via 10.85.16.65` |
| **Tachibana** | `Fa0/0`: `10.85.16.70/30` (Wired)<br>`Fa0/1`: `10.85.16.73/30` (Deus)<br>`Fa1/0`: `10.85.10.1/23` (Switch9) | `0.0.0.0/0 via 10.85.16.69`<br>`10.85.14.128/25, 10.85.15.0/26, 10.85.15.128/26, 10.85.16.0/27, 10.85.16.48/29, 10.85.16.76/30, 10.85.16.80/29, 10.85.16.88/30 via 10.85.16.74` |
| **Deus** | `Fa0/0`: `10.85.16.74/30` (Tachibana)<br>`Fa0/1`: `10.85.16.77/30` (Protocol7)<br>`Fa1/0`: `10.85.14.129/25` (Switch10) | `0.0.0.0/0 via 10.85.16.73`<br>`10.85.15.0/26, 10.85.15.128/26, 10.85.16.0/27, 10.85.16.48/29, 10.85.16.80/29, 10.85.16.88/30 via 10.85.16.78` |
| **Protocol7** | `Fa0/0`: `10.85.16.78/30` (Deus)<br>`Fa0/1`: `10.85.16.81/30` (Knights)<br>`Fa1/0`: `10.85.15.129/26` (Switch11) | `0.0.0.0/0 via 10.85.16.77`<br>`10.85.15.0/26, 10.85.16.0/27, 10.85.16.48/29, 10.85.16.84/30, 10.85.16.88/30 via 10.85.16.82` |
| **Knights** | `Fa0/0`: `10.85.16.82/30` (Protocol7)<br>`Fa0/1`: `10.85.16.85/30` (Phantoma)<br>`Fa1/0`: `10.85.16.49/29` (Eiri) | `0.0.0.0/0 via 10.85.16.81`<br>`10.85.15.0/26, 10.85.16.0/27, 10.85.16.88/30 via 10.85.16.86` |
| **Phantoma** | `Fa0/0`: `10.85.16.86/30` (Knights)<br>`Fa0/1`: `10.85.16.89/30` (Shibuya)<br>`Fa1/0`: `10.85.16.1/27` (Switch12) | `0.0.0.0/0 via 10.85.16.85`<br>`10.85.15.0/26 via 10.85.16.90` |
| **Shibuya** | `Fa0/0`: `10.85.16.90/30` (Phantoma)<br>`Fa0/1`: `10.85.15.1/26` (Switch13) | `0.0.0.0/0 via 10.85.16.89` |

---

## 3. Perhitungan & Implementasi CIDR / Supernetting (GNS3)

### 3.1 Metodologi CIDR
Berbeda dengan VLSM yang mengurutkan subnet semata berdasarkan ukuran, metode **Classless Inter-Domain Routing (CIDR)** mengelompokkan subnet secara **hierarkis mengikuti percabangan topologi fisik** dari lapisan terdalam (`Shibuya`) menuju router pusat (`Cyberia`). Setiap penggabungan dua blok anak dengan prefix $p_1$ dan $p_2$ membentuk blok induk dengan aturan:

$$p_{\text{induk}} = \min(p_1, p_2) - 1$$

Setelah mencapai akar `H1` (`10.85.0.0/17`), alamat Network ID diturunkan secara top-down dengan membelah blok induk menjadi paruh bawah (bit `0`) dan paruh atas (bit `1`). Hasilnya, **seluruh cabang di bawah satu router berada dalam satu blok IP kontigu**, sehingga tabel routing menjadi sangat ringkas (1–2 baris static route per cabang!).

### 3.2 Pohon Pembagian IP CIDR

![Pohon Pembagian IP CIDR](./Images/pohon-cidr.png)

### 3.3 Tabel Penggabungan CIDR (Tahap I – VII)

| Tahap | Blok Baru | Gabungan 1 | Gabungan 2 | Prefix Akhir | Network ID Induk |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **I** | `B1` | `A24 (/30)` | `A25 (/26)` | `/25` | `10.85.0.0/25` |
| **I** | `B2` | `A22 (/30)` | `A23 (/27)` | `/26` | `10.85.0.128/26` |
| **I** | `B3` | `A20 (/30)` | `A21 (/29)` | `/28` | `10.85.1.0/28` |
| **I** | `B4` | `A18 (/30)` | `A19 (/26)` | `/25` | `10.85.1.128/25` |
| **I** | `B5` | `A16 (/30)` | `A17 (/25)` | `/24` | `10.85.8.0/24` |
| **I** | `B6` | `A14 (/30)` | `A15 (/23)` | `/22` | `10.85.12.0/22` |
| **I** | `B7` | `A11 (/24)` | `A12 (/26)` | `/23` | `10.85.16.0/23` |
| **I** | `B8` | `A10 (/30)` | `A13 (/24)` | `/23` | `10.85.18.0/23` |
| **I** | `B9` | `A8 (/30)` | `A9 (/22)` | `/21` | `10.85.32.0/21` |
| **I** | `B10` | `A5 (/26)` | `A6 (/23)` | `/22` | `10.85.48.0/22` |
| **I** | `B11` | `A3 (/29)` | `A4 (/22)` | `/21` | `10.85.56.0/21` |
| **I** | `B12` | `A1 (/25)` | `A2 (/30)` | `/24` | `10.85.64.0/24` |
| **II** | `C1` | `B1 (/25)` | `B2 (/26)` | `/24` | `10.85.0.0/24` |
| **II** | `C2` | `B3 (/28)` | `B4 (/25)` | `/24` | `10.85.1.0/24` |
| **II** | `C3` | `B7 (/23)` | `B8 (/23)` | `/22` | `10.85.16.0/22` |
| **II** | `C4` | `B9 (/21)` | `A7 (/29)` | `/20` | `10.85.32.0/20` |
| **II** | `C5` | `B10 (/22)` | `B11 (/21)` | `/20` | `10.85.48.0/20` |
| **III** | `D1` | `C1 (/24)` | `C2 (/24)` | `/23` | `10.85.0.0/23` |
| **III** | `D2` | `B5 (/24)` | `B6 (/22)` | `/21` | `10.85.8.0/21` |
| **III** | `D3` | `C4 (/20)` | `C5 (/20)` | `/19` | `10.85.32.0/19` |
| **IV** | `E1` | `D1 (/23)` | `D2 (/21)` | `/20` | `10.85.0.0/20` |
| **V** | `F1` | `E1 (/20)` | `C3 (/22)` | `/19` | `10.85.0.0/19` |
| **VI** | `G1` | `F1 (/19)` | `D3 (/19)` | `/18` | `10.85.0.0/18` |
| **VII** | `H1` | `G1 (/18)` | `B12 (/24)` | `/17` | `10.85.0.0/17` |

### 3.4 Tabel Pembagian IP — CIDR

| Subnet | Prefix | Network ID | Netmask | Broadcast | Range Usable IP |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **A1** | `/25` | `10.85.64.0` | `255.255.255.128` | `10.85.64.127` | `10.85.64.1 - 10.85.64.126` |
| **A2** | `/30` | `10.85.64.128` | `255.255.255.252` | `10.85.64.131` | `10.85.64.129 - 10.85.64.130` |
| **A3** | `/29` | `10.85.56.0` | `255.255.255.248` | `10.85.56.7` | `10.85.56.1 - 10.85.56.6` |
| **A4** | `/22` | `10.85.60.0` | `255.255.252.0` | `10.85.63.255` | `10.85.60.1 - 10.85.63.254` |
| **A5** | `/26` | `10.85.48.0` | `255.255.255.192` | `10.85.48.63` | `10.85.48.1 - 10.85.48.62` |
| **A6** | `/23` | `10.85.50.0` | `255.255.254.0` | `10.85.51.255` | `10.85.50.1 - 10.85.51.254` |
| **A7** | `/29` | `10.85.40.0` | `255.255.255.248` | `10.85.40.7` | `10.85.40.1 - 10.85.40.6` |
| **A8** | `/30` | `10.85.32.0` | `255.255.255.252` | `10.85.32.3` | `10.85.32.1 - 10.85.32.2` |
| **A9** | `/22` | `10.85.36.0` | `255.255.252.0` | `10.85.39.255` | `10.85.36.1 - 10.85.39.254` |
| **A10** | `/30` | `10.85.18.0` | `255.255.255.252` | `10.85.18.3` | `10.85.18.1 - 10.85.18.2` |
| **A11** | `/24` | `10.85.16.0` | `255.255.255.0` | `10.85.16.255` | `10.85.16.1 - 10.85.16.254` |
| **A12** | `/26` | `10.85.17.0` | `255.255.255.192` | `10.85.17.63` | `10.85.17.1 - 10.85.17.62` |
| **A13** | `/24` | `10.85.19.0` | `255.255.255.0` | `10.85.19.255` | `10.85.19.1 - 10.85.19.254` |
| **A14** | `/30` | `10.85.12.0` | `255.255.255.252` | `10.85.12.3` | `10.85.12.1 - 10.85.12.2` |
| **A15** | `/23` | `10.85.14.0` | `255.255.254.0` | `10.85.15.255` | `10.85.14.1 - 10.85.15.254` |
| **A16** | `/30` | `10.85.8.0` | `255.255.255.252` | `10.85.8.3` | `10.85.8.1 - 10.85.8.2` |
| **A17** | `/25` | `10.85.8.128` | `255.255.255.128` | `10.85.8.255` | `10.85.8.129 - 10.85.8.254` |
| **A18** | `/30` | `10.85.1.128` | `255.255.255.252` | `10.85.1.131` | `10.85.1.129 - 10.85.1.130` |
| **A19** | `/26` | `10.85.1.192` | `255.255.255.192` | `10.85.1.255` | `10.85.1.193 - 10.85.1.254` |
| **A20** | `/30` | `10.85.1.0` | `255.255.255.252` | `10.85.1.3` | `10.85.1.1 - 10.85.1.2` |
| **A21** | `/29` | `10.85.1.8` | `255.255.255.248` | `10.85.1.15` | `10.85.1.9 - 10.85.1.14` |
| **A22** | `/30` | `10.85.0.128` | `255.255.255.252` | `10.85.0.131` | `10.85.0.129 - 10.85.0.130` |
| **A23** | `/27` | `10.85.0.160` | `255.255.255.224` | `10.85.0.191` | `10.85.0.161 - 10.85.0.190` |
| **A24** | `/30` | `10.85.0.0` | `255.255.255.252` | `10.85.0.3` | `10.85.0.1 - 10.85.0.2` |
| **A25** | `/26` | `10.85.0.64` | `255.255.255.192` | `10.85.0.127` | `10.85.0.65 - 10.85.0.126` |

### 3.5 Pemetaan Antarmuka, NAT, & Hierarchical Route Aggregation GNS3 (`K-43-MODUL-4.gns3project`)
Seluruh 38 container (`ardhptr21/alpinet:latest`) dikonfigurasi secara persisten menggunakan `/root/init.sh` (`chmod +x`, dieksekusi otomatis oleh entrypoint container `/etc/alpinet-init.sh` saat boot), `/etc/profile.d/init.sh`, `/root/.bashrc`, dan `/etc/network/interfaces`. Router `Cyberia` mengaktifkan IPv4 forwarding serta `iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE` menuju `NAT1`:

| Router | Antarmuka & IP | Aggregated Static Routes (`ip route`) |
| :--- | :--- | :--- |
| **Cyberia** | `eth0`: DHCP (`NAT1`) + MASQUERADE<br>`eth1`: `10.85.64.1/25` (`A1`)<br>`eth2`: `10.85.64.129/30` (`A2`) | `10.85.0.0/18 via 10.85.64.130` (`G1`) |
| **Wired** | `eth0`: `10.85.64.130/30` (`A2`)<br>`eth1`: `10.85.56.1/29` (`A3`)<br>`eth2`: `10.85.18.1/30` (`A10`)<br>`eth3`: `10.85.12.1/30` (`A14`) | `default via 10.85.64.129`<br>`10.85.60.0/22 via 10.85.56.2` (`A4` Psyche)<br>`10.85.48.0/21 via 10.85.56.3` (`B10` Copland)<br>`10.85.32.0/20 via 10.85.56.4` (`C4` Schumann+Accela)<br>`10.85.16.0/22 via 10.85.18.2` (`C3` Navi)<br>`10.85.0.0/20 via 10.85.12.2` (`E1` Tachibana dkk.) |
| **Psyche** | `eth0`: `10.85.56.2/29`<br>`eth1`: `10.85.60.1/22` | `default via 10.85.56.1` |
| **Copland** | `eth0`: `10.85.56.3/29`<br>`eth1`: `10.85.48.1/26`<br>`eth2`: `10.85.50.1/23` | `default via 10.85.56.1` |
| **Schumann** | `eth0`: `10.85.56.4/29`<br>`eth1`: `10.85.40.1/29`<br>`eth2`: `10.85.32.1/30` | `default via 10.85.56.1`<br>`10.85.36.0/22 via 10.85.32.2` (`A9` Accela) |
| **Accela** | `eth0`: `10.85.32.2/30`<br>`eth1`: `10.85.36.1/22` | `default via 10.85.32.1` |
| **Navi** | `eth0`: `10.85.18.2/30`<br>`eth1`: `10.85.16.1/24`<br>`eth2`: `10.85.17.1/26`<br>`eth3`: `10.85.19.1/24` | `default via 10.85.18.1` |
| **Tachibana** | `eth0`: `10.85.12.2/30`<br>`eth1`: `10.85.14.1/23`<br>`eth2`: `10.85.8.1/30` | `default via 10.85.12.1`<br>`10.85.0.0/21 via 10.85.8.2` (`D1` downstream)<br>`10.85.8.128/25 via 10.85.8.2` (`A17` Deus) |
| **Deus** | `eth0`: `10.85.8.2/30`<br>`eth1`: `10.85.8.129/25`<br>`eth2`: `10.85.1.129/30` | `default via 10.85.8.1`<br>`10.85.0.0/23 via 10.85.1.130` (`D1` Protocol7 dkk.) |
| **Protocol7** | `eth0`: `10.85.1.130/30`<br>`eth1`: `10.85.1.193/26`<br>`eth2`: `10.85.1.1/30` | `default via 10.85.1.129`<br>`10.85.0.0/24 via 10.85.1.2` (`C1` Phantoma+Shibuya)<br>`10.85.1.8/29 via 10.85.1.2` (`A21` Eiri) |
| **Knights** | `eth0`: `10.85.1.2/30`<br>`eth1`: `10.85.1.9/29`<br>`eth2`: `10.85.0.129/30` | `default via 10.85.1.1`<br>`10.85.0.0/24 via 10.85.0.130` (`C1` Phantoma+Shibuya) |
| **Phantoma** | `eth0`: `10.85.0.130/30`<br>`eth1`: `10.85.0.161/27`<br>`eth2`: `10.85.0.1/30` | `default via 10.85.0.129`<br>`10.85.0.64/26 via 10.85.0.2` (`A25` Shibuya) |
| **Shibuya** | `eth0`: `10.85.0.2/30`<br>`eth1`: `10.85.0.65/26` | `default via 10.85.0.1` |
