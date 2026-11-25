# Iris Classification — Distributed Relational Database, SSO & Machine Learning

## 1. Deskripsi Proyek

Proyek ini merupakan implementasi sistem klasifikasi bunga Iris menggunakan Machine Learning yang terintegrasi dengan Distributed Relational Database, Single Sign-On (SSO), Docker, dan Kubernetes.

Sistem menggunakan algoritma Random Forest untuk melakukan prediksi spesies bunga Iris berdasarkan empat parameter:
- Sepal Length
- Sepal Width
- Petal Length
- Petal Width

Hasil prediksi disimpan ke PostgreSQL Primary Database dan direplikasi secara asynchronous ke PostgreSQL Read Replica.

Autentikasi API menggunakan Keycloak dengan protokol OAuth 2.0 dan OpenID Connect (OIDC), serta validasi access token berbasis JWT.

## 2. Teknologi yang Digunakan

| Komponen | Teknologi |
|---|---|
| Backend API | Python, FastAPI |
| Machine Learning | Scikit-learn, Random Forest |
| Database | PostgreSQL 16 |
| Database Replication | PostgreSQL Streaming Replication |
| Authentication | Keycloak 26.8.2 |
| Token | JWT, OAuth 2.0, OIDC |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes, Minikube |
| Storage | PersistentVolumeClaim (PVC) |
| Routing | NGINX Ingress Controller |

## 3. Arsitektur Sistem

Sistem terdiri dari beberapa komponen utama:

1. Keycloak sebagai penyedia autentikasi dan penerbit JWT.
2. FastAPI sebagai backend untuk menerima permintaan dan melakukan validasi token.
3. Random Forest sebagai model klasifikasi bunga Iris.
4. PostgreSQL Primary sebagai database utama untuk operasi penulisan.
5. PostgreSQL Read Replica sebagai database untuk operasi pembacaan.
6. Kubernetes untuk mengelola deployment, service, dan penyimpanan persisten.
7. NGINX Ingress Controller untuk mengatur akses API dan autentikasi.

### Alur Sistem

- Pengguna melakukan autentikasi melalui Keycloak.
- Keycloak menerbitkan access token JWT.
- Pengguna mengirimkan permintaan ke FastAPI dengan Bearer Token.
- Backend memvalidasi tanda tangan JWT menggunakan JWKS dan memeriksa issuer serta authorized party.
- Model Random Forest melakukan klasifikasi bunga Iris.
- Hasil prediksi disimpan ke PostgreSQL Primary.
- Data direplikasi ke PostgreSQL Read Replica.
- Riwayat prediksi dibaca melalui Read Replica.

## 4. Struktur Repository

```text
iris-classification/
├── backend/
│   ├── app/
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── iris_model.joblib
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── train_model.py
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   ├── primary/
│   │   └── init/
│   │       ├── 01-create-replication-user.sh
│   │       └── 02-create-predictions-table.sql
│   └── replica/
│       └── replica-entrypoint.sh
├── kubernetes/
│   ├── backend.yaml
│   ├── backend-configmap.yaml
│   ├── ingress.yaml
│   ├── namespace.yaml
│   ├── postgres-primary.yaml
│   └── postgres-replica.yaml
├── docker-compose.yml
├── README.md
└── .gitignore
```

File Secret dan environment yang berisi kredensial tidak disertakan dalam repository.

## 5. Konfigurasi Environment

Buat file `.env` berdasarkan konfigurasi lokal proyek.

Variabel yang dibutuhkan mencakup:

- KEYCLOAK_ADMIN
- KEYCLOAK_ADMIN_PASSWORD
- KEYCLOAK_URL
- KEYCLOAK_REALM
- KEYCLOAK_CLIENT_ID
- KEYCLOAK_CLIENT_SECRET
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

Jangan mengunggah file `.env` ke repository publik.

## 6. Menjalankan Docker Compose

Jalankan seluruh layanan:

```bash
docker compose up -d --build
```

Periksa container:

```bash
docker ps
```

Untuk menghentikan layanan:

```bash
docker compose down
```

Volume database dan Keycloak dipertahankan selama tidak menggunakan opsi penghapusan volume.

## 7. Deployment Kubernetes

Pastikan Minikube aktif:

```bash
minikube start --driver=docker
```

Aktifkan NGINX Ingress:

```bash
minikube addons enable ingress
```

Buat namespace:

```bash
kubectl apply -f kubernetes/namespace.yaml
```

Terapkan konfigurasi database dan Secret yang telah disiapkan secara lokal:

```bash
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/keycloak-secret.yaml
kubectl apply -f kubernetes/postgres-primary.yaml
kubectl apply -f kubernetes/postgres-replica.yaml
```

Terapkan ConfigMap dan Backend:

```bash
kubectl apply -f kubernetes/backend-configmap.yaml
kubectl apply -f kubernetes/backend.yaml
```

Terapkan Ingress:

```bash
kubectl apply -f kubernetes/ingress.yaml
```

Periksa resource:

```bash
kubectl get pods,pvc,svc,ingress -n iris-system
```

## 8. Konfigurasi Ingress

Sistem menggunakan dua hostname:

| Hostname | Layanan |
|---|---|
| api.lokal | FastAPI Backend |
| auth.lokal | Keycloak |

Untuk pengujian melalui port-forward:

```bash
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8081:80
```

Contoh pengujian API:

```bash
curl -H "Host: api.lokal" http://127.0.0.1:8081/docs
```

Contoh pengujian Keycloak:

```bash
curl -H "Host: auth.lokal" http://127.0.0.1:8081/realms/iris-realms/.well-known/openid-configuration
```

## 9. Endpoint API

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | /health | Pemeriksaan kesehatan API |
| GET | /health/db | Pemeriksaan koneksi database |
| GET | /model-info | Informasi model Machine Learning |
| POST | /predict | Melakukan prediksi Iris |
| GET | /predictions | Membaca riwayat prediksi |

Endpoint prediksi dan riwayat prediksi memerlukan Bearer Token JWT.

## 10. Pengujian Sistem

Pengujian yang telah dilakukan:

1. Pemeriksaan container Docker.
2. Pemeriksaan Pod Kubernetes.
3. Pemeriksaan PersistentVolumeClaim.
4. Pengujian koneksi PostgreSQL Primary dan Replica.
5. Pengujian PostgreSQL Streaming Replication.
6. Pengujian autentikasi Keycloak dan penerbitan JWT.
7. Pengujian validasi JWT pada FastAPI.
8. Pengujian prediksi menggunakan Random Forest.
9. Pengujian penulisan data ke Primary Database.
10. Pengujian replikasi data ke Read Replica.
11. Pengujian pembacaan riwayat dari Replica.
12. Pengujian penolakan akses API tanpa JWT.
13. Pengujian persistensi data setelah Pod database dibuat ulang.

### Hasil Pengujian

- API berhasil diakses melalui Ingress dengan HTTP 200.
- Keycloak berhasil menerbitkan access token.
- Validasi JWT berhasil.
- Prediksi data Iris berhasil menghasilkan kelas Virginica.
- Data prediksi berhasil disimpan di PostgreSQL Primary.
- Data yang sama berhasil ditemukan di PostgreSQL Replica.
- Permintaan tanpa token ditolak dengan HTTP 401.
- Primary dan Replica tetap terhubung setelah konfigurasi Backend diperbarui.

## 11. Penyimpanan Data

PostgreSQL menggunakan StatefulSet dan PersistentVolumeClaim berkapasitas 2 GiB untuk masing-masing database.

Pengujian penghapusan dan pembuatan ulang Pod telah dilakukan dan data tetap tersedia pada PVC yang sama.

## 12. Keamanan

- Autentikasi menggunakan Keycloak.
- Access token menggunakan JWT dengan algoritma RS256.
- Validasi tanda tangan token menggunakan JWKS.
- Validasi issuer dan authorized party.
- Password dan client secret disimpan menggunakan Kubernetes Secret.
- Konfigurasi non-rahasia dikelola melalui ConfigMap.
- File `.env` dan Secret lokal dikecualikan dari Git.
