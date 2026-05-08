# Product Requirements Document (PRD)
## LinkCraft — Short Link & QR Code Generator Platform

**Versi:** 1.0  
**Tanggal:** 7 Mei 2026  
**Status:** Draft  
**Penulis:** Product Team

---

## 1. Ringkasan Produk

**LinkCraft** adalah platform SaaS berbasis web untuk pembuatan *short link*, *QR code*, dan *custom landing page*. Produk ini ditujukan untuk individu, marketer, dan bisnis yang ingin mengelola, melacak, dan mengoptimalkan distribusi tautan secara efisien.

### 1.1 Visi Produk
Menjadi platform manajemen tautan yang intuitif, fleksibel, dan terjangkau — dari pengguna personal hingga tim bisnis.

### 1.2 Tujuan Utama
- Memberikan pengalaman generate short link dan QR code yang cepat dan mudah
- Mendorong konversi dari pengguna gratis ke premium melalui value yang terasa nyata
- Menyediakan data analitik yang actionable bagi pengguna berbayar

---

## 2. Target Pengguna

| Segmen | Deskripsi |
|--------|-----------|
| **Individual / Creator** | Konten kreator, influencer, blogger yang butuh link pendek untuk bio atau postingan |
| **Marketer / Growth Hacker** | Tim pemasaran yang menjalankan kampanye dan butuh tracking klik |
| **Bisnis Kecil-Menengah** | UMKM yang butuh QR code untuk menu, brosur, atau promosi |
| **Developer / Power User** | Pengguna teknis yang butuh bulk generation dan integrasi |

---

## 3. Fitur & Scope

### 3.1 Halaman Utama (`/`)

Halaman landing publik yang berfungsi sebagai *hook* utama sebelum pengguna login.

**Elemen yang ditampilkan:**
- Hero section dengan input URL untuk generate short link dan QR code
- Tombol **"Generate"** — saat diklik, pengguna **diarahkan ke halaman login/register**
- Preview demo animasi atau contoh hasil generate (non-interaktif)
- Section fitur unggulan
- Section pricing (lihat §4)
- Header dengan tombol Login dan Sign Up
- Footer standar

**Catatan UX:** Input URL boleh diisi sebelum login — konversi isinya ke session/localStorage agar setelah login langsung masuk dashboard dengan URL tersebut sudah terisi.

---

### 3.2 Autentikasi

| Fitur | Keterangan |
|-------|------------|
| Register | Email + password, atau OAuth (Google) |
| Login | Email + password, atau OAuth (Google) |
| Lupa password | Reset via email |
| Verifikasi email | Wajib sebelum bisa generate |
| Session | JWT dengan refresh token, expire 30 hari |

---

### 3.3 Dashboard Pengguna (Post-Login)

Setelah login, pengguna diarahkan ke `/dashboard`. Navigasi utama:

```
Home | Links | QR Codes | Pages | Analytics
```

#### 3.3.1 Home (`/dashboard`)
- Ringkasan statistik bulan ini: link dibuat, QR dibuat, total klik, total scan
- Progress bar penggunaan kuota (link, QR, pages) vs limit paket
- Shortcut: tombol "Buat Short Link", "Buat QR Code", "Buat Landing Page"
- Feed aktivitas terbaru (5 item terakhir)

#### 3.3.2 Links (`/dashboard/links`)
- Tabel daftar semua short link milik pengguna
- Kolom: Original URL, Short URL, Klik, Tanggal Dibuat, Status (Aktif/Nonaktif)
- Fitur per baris: Salin, Edit, Hapus, Lihat Analitik
- Form buat short link baru:
  - Input URL asli
  - Custom alias (opsional, validasi ketersediaan real-time)
  - Tanggal kedaluwarsa (opsional)
  - UTM parameters (opsional)
- Filter & search berdasarkan nama, tanggal, status
- Paginasi atau infinite scroll

#### 3.3.3 QR Codes (`/dashboard/qr`)
- Grid/tabel daftar QR code yang telah dibuat
- Kolom: Thumbnail QR, Nama, Target URL, Scan, Tanggal
- Fitur per item: Download (PNG/SVG), Edit, Hapus, Lihat Analitik
- Form buat QR code baru:
  - Input URL target
  - **Kustomisasi gaya** (lihat §3.4)
- Filter & search

#### 3.3.4 Pages (`/dashboard/pages`)
- Daftar custom landing page yang dibuat
- Setiap page punya URL unik: `linkcraft.io/p/nama-page`
- Form buat/edit page:
  - Judul page
  - Bio/deskripsi singkat
  - Avatar/foto
  - Daftar link (drag-and-drop untuk reorder)
  - Pilihan tema/warna (terbatas di free, lebih banyak di premium)
- Preview real-time
- Tombol publish/unpublish

#### 3.3.5 Analytics (`/dashboard/analytics`)
- Overview grafik klik & scan dalam rentang waktu tertentu
- Filter per link / QR code / page
- Data yang ditampilkan (sesuai paket — lihat §4):
  - Total klik / scan
  - Klik unik
  - Grafik tren harian
  - Sumber referral (top 5)
  - Negara asal (top 5)
  - Perangkat & browser
- Ekspor data ke CSV (khusus premium)

---

### 3.4 Kustomisasi QR Code

| Opsi Kustomisasi | Free | Premium ($5) | Premium ($15) |
|------------------|------|--------------|---------------|
| Warna foreground | ✅ | ✅ | ✅ |
| Warna background | ✅ | ✅ | ✅ |
| Gaya dot (square) | ✅ | ✅ | ✅ |
| Gaya dot (rounded, dots) | 🔒 | ✅ | ✅ |
| Gaya dot (classy, extra-rounded) | 🔒 | ✅ | ✅ |
| Tambah logo/gambar di tengah | 🔒 | ✅ | ✅ |
| Custom corner style | 🔒 | 🔒 | ✅ |
| Gradient warna | 🔒 | 🔒 | ✅ |
| Download SVG resolusi tinggi | 🔒 | ✅ | ✅ |

> Opsi yang terkunci ditampilkan di UI dengan ikon gembok dan tooltip "Upgrade ke Premium".

---

## 4. Pricing & Paket

### Free — Gratis
| Fitur | Limit |
|-------|-------|
| Short link | 80 / bulan |
| QR code | 5 / bulan |
| Custom landing pages | 5 |
| Klik & scan | Unlimited |
| Data analitik | Tidak tersedia |
| Kustomisasi QR | Dasar saja |
| Bulk creation | ❌ |

---

### Starter — Rp 50.000 / bulan
| Fitur | Limit |
|-------|-------|
| Short link | 140 / bulan |
| QR code | 15 / bulan |
| Custom landing pages | 10 |
| Klik & scan | Unlimited |
| Data analitik | 30 hari ke belakang |
| Kustomisasi QR | Lanjutan (kecuali corner & gradient) |
| Bulk creation | ❌ |

---

### Pro — Rp 150.000 / bulan
| Fitur | Limit |
|-------|-------|
| Short link | 300 / bulan |
| QR code | 30 / bulan |
| Custom landing pages | 20 |
| Klik & scan | Unlimited |
| Data analitik | 1 tahun ke belakang |
| Kustomisasi QR | Penuh (semua opsi) |
| Bulk creation | ✅ (link & QR) |

---

### 4.1 Pengelolaan Billing
- Payment gateway: **Midtrans (Snap API)**
- Billing cycle: bulanan / satu kali bayar
- Upgrade/downgrade bisa kapan saja (prorated)
- Notifikasi email saat kuota mendekati batas (80% dan 100%)
- Invoice otomatis dikirim via email tiap bulan

---

## 5. Admin Panel (`/admin`)

Admin panel hanya dapat diakses oleh akun dengan role `ADMIN` atau `SUPERADMIN`.

### 5.1 Akses & Role

| Role | Kemampuan |
|------|-----------|
| **Superadmin** | Akses penuh, bisa kelola admin lain |
| **Admin** | Kelola pengguna, konten, melihat semua data |
| **Support** | Read-only akses ke data pengguna untuk keperluan support |

### 5.2 Fitur Admin Panel

#### Dashboard Admin (`/admin/dashboard`)
- Total pengguna (aktif, baru bulan ini, churn)
- Total link, QR code, halaman yang dibuat platform-wide
- Pendapatan MRR (monthly recurring revenue)
- Grafik pertumbuhan pengguna dan pendapatan

#### Manajemen Pengguna (`/admin/users`)
- Tabel semua pengguna dengan filter: paket, status, tanggal daftar
- Detail per pengguna: profil, paket, histori billing, penggunaan kuota
- Aksi: suspend akun, reset password, ubah paket manual, hapus akun
- Search by email, nama, ID

#### Manajemen Konten (`/admin/content`)
- Daftar semua link pendek platform-wide (dengan filter per user)
- Daftar semua QR code
- Daftar semua landing page
- Kemampuan untuk nonaktifkan/hapus konten yang melanggar TOS
- Blacklist URL (domain atau URL spesifik yang diblokir dari sistem)

#### Manajemen Billing (`/admin/billing`)
- Riwayat transaksi semua pengguna
- Daftar subscription aktif
- Refund manual (terintegrasi Stripe)
- Laporan pendapatan bulanan (ekspor CSV)

#### Sistem & Konfigurasi (`/admin/settings`)
- Atur batas kuota per paket (tanpa deploy ulang)
- Toggle maintenance mode
- Manajemen domain kustom (jika fitur ini dibuka di masa depan)
- Email template untuk notifikasi sistem
- Audit log: rekam semua aksi admin (siapa, apa, kapan)

---

## 6. Arsitektur Teknis (Rekomendasi)

### 6.1 Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Frontend | HTML5, TailwindCSS, JavaScript (Vanilla/Alpine.js) |
| Backend / API | Python (Flask) |
| Database | MySQL (via SQLAlchemy ORM) |
| Auth | Flask-Login / Flask-JWT-Extended |
| QR Generator | `python-qrcode` (server-side) / `qr-code-styling` (client-side) |
| Payment | Midtrans Snap API |
| Analytics Storage | MySQL (Timeseries optimization) |
| File Storage | AWS S3 / Cloudflare R2 |
| Caching | Redis |
| Hosting | DigitalOcean / Railway / VPS |
| CDN / Redirect | Cloudflare Workers (Edge redirection) |

### 6.2 Alur Redirect Short Link
```
User mengakses linkcraft.io/abc123
        ↓
Cloudflare Worker mencari slug "abc123" di cache/KV
        ↓
Jika ada → redirect 301/302 ke URL tujuan + kirim event klik ke queue
        ↓
Queue worker memproses event: simpan data klik (timestamp, IP, user-agent, referrer)
        ↓
Data diagregasi ke database analitik
```

### 6.3 Rate Limiting
- Generate link/QR: maks 10 request/menit per user
- Public endpoint (halaman landing page): maks 100 request/menit per IP
- API (jika tersedia): sesuai paket

---

## 7. User Flow Utama

### 7.1 New User — Generate Short Link
```
Landing page (/) 
  → Isi URL → Klik "Generate" 
  → Redirect ke /register 
  → Daftar akun 
  → Verifikasi email 
  → Redirect ke /dashboard (URL sebelumnya sudah terisi) 
  → Generate link berhasil 
  → Tampilkan hasil + opsi salin
```

### 7.2 Existing User — Buat QR Code
```
Login → /dashboard/qr 
  → Klik "Buat QR Code" 
  → Isi URL target 
  → Kustomisasi gaya (opsi berbeda berdasarkan paket) 
  → Preview real-time 
  → Simpan 
  → Download PNG/SVG
```

### 7.3 Upgrade Paket
```
Pengguna mencoba fitur terkunci 
  → Muncul modal "Upgrade untuk fitur ini" 
  → Klik "Lihat Paket" 
  → Halaman /pricing 
  → Pilih paket 
  → Checkout via Midtrans Snap 
  → Redirect ke /dashboard dengan paket baru aktif atau status pending
```

---

## 8. Keamanan

- Semua data dikirim via HTTPS
- Password di-hash dengan bcrypt (cost factor 12)
- Rate limiting di endpoint auth untuk mencegah brute force
- Validasi dan sanitasi semua URL input (cegah open redirect ke malware)
- Scan URL terhadap Google Safe Browsing API sebelum disimpan
- CSRF protection di semua form
- Audit log untuk semua aksi sensitif (admin & billing)
- Data pengguna tidak pernah dijual ke pihak ketiga

---

## 9. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Redirect latency | < 100ms (via CDN/edge) |
| Uptime | 99.9% SLA |
| Page load (dashboard) | < 2 detik (LCP) |
| Mobile responsive | Ya, semua halaman |
| Aksesibilitas | WCAG 2.1 Level AA |
| Dukungan browser | Chrome, Firefox, Safari, Edge (2 versi terakhir) |

---

## 10. Metrik Keberhasilan (KPI)

| Metrik | Target (6 bulan) |
|--------|------------------|
| Registered users | 5.000 |
| Paying users (konversi free → paid) | ≥ 5% |
| MRR | $1.500 |
| Churn rate bulanan | < 5% |
| NPS Score | ≥ 40 |
| Link redirects berhasil | 99.99% |

---

## 11. Roadmap

### Phase 1 — MVP (Bulan 1–2)
- [x] Landing page dengan demo form
- [x] Auth (register, login, reset password)
- [x] Generate short link
- [x] Generate QR code (kustomisasi dasar)
- [x] Dashboard: Home, Links, QR Codes
- [x] Pricing page
- [x] Stripe billing (Free + Starter)
- [x] Admin panel dasar (user & content management)

### Phase 2 — Growth (Bulan 3–4)
- [ ] Custom landing pages (Pages)
- [ ] Analytics dashboard
- [ ] Paket Pro + bulk creation
- [ ] QR kustomisasi lanjutan (logo, gradient)
- [ ] Email notification (kuota, invoice)

### Phase 3 — Scale (Bulan 5–6)
- [ ] API publik untuk developer
- [ ] Custom domain untuk short link (premium)
- [ ] Integrasi webhook
- [ ] Tim/workspace (multi-user per akun)
- [ ] A/B testing untuk link (redirect ke URL berbeda secara bergantian)

---

## 12. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| Penyalahgunaan untuk phishing/spam | Tinggi | Validasi URL via Safe Browsing API, blacklist domain, laporan user |
| Latensi redirect tinggi | Sedang | Gunakan Cloudflare Workers / edge caching |
| Churn tinggi dari free tier | Sedang | Onboarding yang baik, email nurturing, highlight value premium |
| Stripe payment failure | Sedang | Retry logic, notifikasi email, grace period 3 hari |
| Data analitik tidak akurat | Rendah | Bot filtering, validasi IP, deduplikasi klik |

---

## 13. Glosarium

| Istilah | Definisi |
|---------|----------|
| **Short link** | URL pendek yang merupakan alias dari URL panjang aslinya |
| **Slug** | Bagian unik dari short link (mis. `abc123` pada `linkcraft.io/abc123`) |
| **QR Code** | Kode matriks yang bisa dipindai kamera untuk membuka URL |
| **Landing page** | Halaman profil berisi kumpulan link milik satu pengguna |
| **MRR** | Monthly Recurring Revenue — pendapatan berulang bulanan |
| **Churn** | Persentase pengguna berbayar yang berhenti berlangganan |
| **UTM** | Parameter tracking URL untuk kampanye pemasaran |

---

## 14. Models

# ─── ENUMS ────────────────────────────────────────────────────────────────────

class UserRole(enum.Enum):
    user = "user"
    admin = "admin"
    superadmin = "superadmin"
    support = "support"

class PlanType(enum.Enum):
    free = "free"
    starter = "starter"
    pro = "pro"

class SubscriptionStatus(enum.Enum):
    active = "active"
    cancelled = "cancelled"
    past_due = "past_due"
    trialing = "trialing"

class DeviceType(enum.Enum):
    desktop = "desktop"
    mobile = "mobile"
    tablet = "tablet"
    unknown = "unknown"

class ClickSourceType(enum.Enum):
    short_link = "short_link"
    qr_code = "qr_code"
    landing_page = "landing_page"


# ─── MODELS ───────────────────────────────────────────────────────────────────

class User(db.Model):
    __tablename__ = "users"

    id                  = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    email               = db.Column(db.String(255), nullable=False, unique=True)
    password_hash       = db.Column(db.String(255), nullable=True)          # NULL jika OAuth
    name                = db.Column(db.String(100), nullable=False)
    avatar_url          = db.Column(db.String(500), nullable=True)
    role                = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.user)
    is_email_verified   = db.Column(db.Boolean, nullable=False, default=False)
    email_verified_at   = db.Column(db.DateTime, nullable=True)
    last_login_at       = db.Column(db.DateTime, nullable=True)
    created_at          = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription        = db.relationship("Subscription", back_populates="user", uselist=False)
    quota_usage         = db.relationship("QuotaUsage", back_populates="user", uselist=False)
    short_links         = db.relationship("ShortLink", back_populates="user", lazy="dynamic")
    qr_codes            = db.relationship("QRCode", back_populates="user", lazy="dynamic")
    landing_pages       = db.relationship("LandingPage", back_populates="user", lazy="dynamic")
    audit_logs          = db.relationship("AuditLog", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.email}>"


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id                      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id                 = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    plan                    = db.Column(db.Enum(PlanType), nullable=False, default=PlanType.free)
    status                  = db.Column(db.Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.active)
    midtrans_customer_id    = db.Column(db.String(100), nullable=True)
    midtrans_order_id       = db.Column(db.String(100), nullable=True)
    current_period_start    = db.Column(db.DateTime, nullable=True)
    current_period_end      = db.Column(db.DateTime, nullable=True)
    cancelled_at            = db.Column(db.DateTime, nullable=True)
    created_at              = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at              = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription user={self.user_id} plan={self.plan.value}>"


class QuotaUsage(db.Model):
    __tablename__ = "quota_usages"
    __table_args__ = (
        db.UniqueConstraint("user_id", "year", "month", name="uq_quota_user_month"),
    )

    id          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id     = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    year        = db.Column(db.Integer, nullable=False)
    month       = db.Column(db.Integer, nullable=False)
    links_used  = db.Column(db.Integer, nullable=False, default=0)
    qrcodes_used= db.Column(db.Integer, nullable=False, default=0)
    pages_used  = db.Column(db.Integer, nullable=False, default=0)
    updated_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="quota_usage")

    def __repr__(self):
        return f"<QuotaUsage user={self.user_id} {self.year}/{self.month}>"


class ShortLink(db.Model):
    __tablename__ = "short_links"

    id           = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id      = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    slug         = db.Column(db.String(50), nullable=False, unique=True)
    original_url = db.Column(db.Text, nullable=False)
    title        = db.Column(db.String(255), nullable=True)
    expires_at   = db.Column(db.DateTime, nullable=True)
    is_active    = db.Column(db.Boolean, nullable=False, default=True)
    utm_source   = db.Column(db.String(100), nullable=True)
    utm_medium   = db.Column(db.String(100), nullable=True)
    utm_campaign = db.Column(db.String(100), nullable=True)
    created_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user         = db.relationship("User", back_populates="short_links")
    qr_code      = db.relationship("QRCode", back_populates="short_link", uselist=False)
    click_events = db.relationship("ClickEvent", back_populates="short_link", lazy="dynamic")

    def __repr__(self):
        return f"<ShortLink /{self.slug}>"


class QRCode(db.Model):
    __tablename__ = "qr_codes"

    id             = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id        = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    short_link_id  = db.Column(db.BigInteger, db.ForeignKey("short_links.id", ondelete="SET NULL"), nullable=True)
    name           = db.Column(db.String(255), nullable=False)
    target_url     = db.Column(db.Text, nullable=False)
    style_config   = db.Column(db.JSON, nullable=True)        # dot_style, colors, logo_url, dll
    file_path_png  = db.Column(db.String(500), nullable=True)
    file_path_svg  = db.Column(db.String(500), nullable=True)
    created_at     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user         = db.relationship("User", back_populates="qr_codes")
    short_link   = db.relationship("ShortLink", back_populates="qr_code")
    click_events = db.relationship("ClickEvent", back_populates="qr_code", lazy="dynamic")

    def __repr__(self):
        return f"<QRCode {self.name}>"


class LandingPage(db.Model):
    __tablename__ = "landing_pages"

    id           = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id      = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    slug         = db.Column(db.String(100), nullable=False, unique=True)
    title        = db.Column(db.String(255), nullable=False)
    bio          = db.Column(db.Text, nullable=True)
    avatar_url   = db.Column(db.String(500), nullable=True)
    theme_config = db.Column(db.JSON, nullable=True)          # bg_color, font, button_style, dll
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    created_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user         = db.relationship("User", back_populates="landing_pages")
    page_links   = db.relationship("PageLink", back_populates="landing_page", order_by="PageLink.sort_order", cascade="all, delete-orphan")
    click_events = db.relationship("ClickEvent", back_populates="landing_page", lazy="dynamic")

    def __repr__(self):
        return f"<LandingPage /{self.slug}>"


class PageLink(db.Model):
    __tablename__ = "page_links"

    id              = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    landing_page_id = db.Column(db.BigInteger, db.ForeignKey("landing_pages.id", ondelete="CASCADE"), nullable=False)
    label           = db.Column(db.String(255), nullable=False)
    url             = db.Column(db.Text, nullable=False)
    icon            = db.Column(db.String(100), nullable=True)
    sort_order      = db.Column(db.Integer, nullable=False, default=0)
    is_active       = db.Column(db.Boolean, nullable=False, default=True)
    created_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    landing_page = db.relationship("LandingPage", back_populates="page_links")

    def __repr__(self):
        return f"<PageLink {self.label}>"


class ClickEvent(db.Model):
    __tablename__ = "click_events"

    id              = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    short_link_id   = db.Column(db.BigInteger, db.ForeignKey("short_links.id", ondelete="CASCADE"), nullable=True)
    qr_code_id      = db.Column(db.BigInteger, db.ForeignKey("qr_codes.id", ondelete="CASCADE"), nullable=True)
    landing_page_id = db.Column(db.BigInteger, db.ForeignKey("landing_pages.id", ondelete="CASCADE"), nullable=True)
    source_type     = db.Column(db.Enum(ClickSourceType), nullable=False)
    ip_address      = db.Column(db.String(45), nullable=True)    # IPv4 & IPv6
    country_code    = db.Column(db.String(2), nullable=True)     # ISO 3166-1 alpha-2
    city            = db.Column(db.String(100), nullable=True)
    device_type     = db.Column(db.Enum(DeviceType), nullable=False, default=DeviceType.unknown)
    browser         = db.Column(db.String(100), nullable=True)
    os              = db.Column(db.String(100), nullable=True)
    referrer        = db.Column(db.Text, nullable=True)
    clicked_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    short_link   = db.relationship("ShortLink", back_populates="click_events")
    qr_code      = db.relationship("QRCode", back_populates="click_events")
    landing_page = db.relationship("LandingPage", back_populates="click_events")

    def __repr__(self):
        return f"<ClickEvent type={self.source_type.value} at={self.clicked_at}>"


class UrlBlacklist(db.Model):
    __tablename__ = "url_blacklist"

    id          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    domain      = db.Column(db.String(255), nullable=True)
    url_pattern = db.Column(db.Text, nullable=True)
    reason      = db.Column(db.String(255), nullable=True)
    added_by    = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    admin = db.relationship("User", foreign_keys=[added_by])

    def __repr__(self):
        return f"<UrlBlacklist {self.domain or self.url_pattern}>"


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id     = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action      = db.Column(db.String(100), nullable=False)   # misal: "user.suspend", "link.delete"
    entity_type = db.Column(db.String(50), nullable=True)     # misal: "ShortLink", "User"
    entity_id   = db.Column(db.BigInteger, nullable=True)
    old_values  = db.Column(db.JSON, nullable=True)
    new_values  = db.Column(db.JSON, nullable=True)
    ip_address  = db.Column(db.String(45), nullable=True)
    created_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} by user={self.user_id}>"

*Dokumen ini bersifat living document dan akan diperbarui seiring dengan perkembangan produk.*
