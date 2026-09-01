# PDF Studio

Windows ve Linux üzerinde çalışan, **Adobe Acrobat Pro benzeri** masaüstü PDF
düzenleyici. Sayfa içeriğindeki gerçek metni düzenler, açıklama ekler, sayfaları
yönetir, form doldurur, karartma (redaksiyon) uygular ve belgeyi şifreler.

| | |
|---|---|
| **Motor** | PyMuPDF (MuPDF) — hızlı, yerel, ağ bağlantısı gerektirmez |
| **Arayüz** | PySide6 (Qt 6) — koyu/açık tema, tamamen Türkçe |
| **Platform** | Linux, Windows (macOS'ta da çalışır) |

---

## Kurulum

### Hazır kurulum dosyaları

| Platform | Dosya | Kurulum komutu |
|---|---|---|
| **Arch / CachyOS / Manjaro** | `pdf-studio-1.0.0-1-x86_64.pkg.tar.zst` | `sudo pacman -U pdf-studio-1.0.0-1-x86_64.pkg.tar.zst` |
| **Diğer Linux** (glibc 2.35+) | `PDFStudio-1.0.0-x86_64.run` | `bash PDFStudio-1.0.0-x86_64.run` |
| **Windows** 10/11 | `PDFStudio-1.0.0-Setup.exe` | Çift tıklayın, sihirbazı izleyin |
| **Windows** (kurulumsuz) | `PDFStudio-1.0.0-portable.exe` | Çift tıklayın, doğrudan çalışır |

Python kurulu olması gerekmez; her şey pakete gömülüdür.

#### Arch tabanlı dağıtımlar (önerilen yol)

```bash
sudo pacman -U pdf-studio-1.0.0-1-x86_64.pkg.tar.zst
```

`/opt/pdf-studio` altına kurulur; uygulama menüsüne, `pdf-studio` komutuna ve
PDF "Birlikte aç" listesine eklenir. Kaldırmak için:

```bash
sudo pacman -R pdf-studio
```

#### Diğer dağıtımlar — `.run` kurulumu

```bash
bash PDFStudio-1.0.0-x86_64.run
```

Root değilseniz `~/.local/opt/pdf-studio` altına, `sudo` ile çalıştırırsanız
`/opt/pdf-studio` altına kurar. Seçenekler:

```bash
bash PDFStudio-1.0.0-x86_64.run --help       # tüm seçenekler
bash PDFStudio-1.0.0-x86_64.run --verify     # kurup gömülü sınamayı çalıştır
bash PDFStudio-1.0.0-x86_64.run --system     # sudo ile sistem geneline
bash PDFStudio-1.0.0-x86_64.run --extract .  # kurmadan sadece çıkar
bash PDFStudio-1.0.0-x86_64.run --uninstall  # kaldır
```

> **Çift tıklamak neden çalışmıyor?** İki yaygın sebep var:
>
> 1. **Dosya NTFS/FAT bir diskte.** Bu dosya sistemleri çalıştırma iznini
>    tutamaz; `chmod +x` sessizce etkisiz kalır. Dosyayı ev dizininize
>    kopyalayın: `cp PDFStudio-*.run ~/ && chmod +x ~/PDFStudio-*.run`
> 2. **Masaüstünüz kabuk betiklerini çalıştırmıyor.** KDE/Dolphin ve GNOME/Nautilus
>    varsayılan olarak `.run` gibi dosyaları metin düzenleyicide açar.
>    KDE'de: *Dolphin → Ayarlar → Dolphin'i Yapılandır → Genel → Onaylamalar →
>    "Çalıştırılabilir betikleri açarken"* ayarını **"Çalıştır"** yapın.
>
> Her hâlükârda terminalden `bash PDFStudio-*.run` demek her zaman çalışır —
> `.run` kurulumları (NVIDIA sürücüsü, Anaconda vb.) geleneksel olarak böyle
> kullanılır.

#### Kurulumu doğrulamak

```bash
pdf-studio --self-test
```

Uygulama gerçek bir belge oluşturup metin düzenleme, açıklama, karartma, form,
şifreleme ve dışa aktarma yollarının hepsini çalıştırır ve sonucu raporlar.

### Kaynaktan çalıştırma

Geliştirme veya kendi değişikliklerinizi denemek için:

```bash
bash run.sh
```

Windows'ta `run.bat`. İlk çalıştırmada sanal ortam kurulur ve bağımlılıklar
indirilir; sonraki açılışlar anında olur.

### Kendi kurulum dosyanızı üretmek

Ayrıntılar için [`packaging/README.md`](packaging/README.md). Kısaca:

```bash
python3 -m PyInstaller --noconfirm --clean packaging/pdfstudio.spec

# Evrensel .run kurulumu
bash packaging/make_linux_installer.sh dist/PDFStudio PDFStudio-1.0.0-x86_64.run 1.0.0

# Arch/CachyOS paketi (makepkg gerekir)
bash packaging/arch/build-arch-package.sh dist/PDFStudio 1.0.0
```

Windows dosyalarını Linux'tan üretmek mümkün değildir. `.github/workflows/build.yml`
iş akışı her iki platformu da GitHub'ın makinelerinde derler:

- **Elle:** depo → *Actions* → *Kurulum dosyalarını derle* → *Run workflow*
- **Sürüm:** `git tag v1.0.0 && git push --tags` → dosyalar *Releases* sayfasına
  SHA256 toplamlarıyla yüklenir

Her yapı, yüklenmeden önce gömülü sınamadan geçirilir.

### Linux masaüstü kısayolu (kaynaktan çalıştıranlar için)

```bash
sudo cp -r . /opt/pdf-studio && sudo cp pdf-studio.desktop /usr/share/applications/ && sudo cp pdfstudio/resources/icon.png /usr/share/icons/hicolor/512x512/apps/pdf-studio.png
```

---

## Yetenekler

### Metin düzenleme (asıl fark)
- **Metni düzenle aracı (E)** — sayfadaki bir metin bloğuna tıklayın; içerik,
  yazı tipi, punto, renk, hizalama ve satır aralığı canlı önizlemeli bir
  pencerede düzenlenir. Eski metin gerçekten kaldırılır (redaksiyon), yenisi
  sayfa içeriğine yazılır.
- **Türkçe karakter desteği** — PDF'in yerleşik 14 fontu `ığşİĞŞ` karakterlerini
  bozar. Uygulama sistemdeki TTF/OTF dosyalarını tarayıp gerçek aile adlarıyla
  eşler ve gerektiğinde fontu belgeye gömer.
- **Metin ekle (T)** — sayfada kutu çizip yeni metin yazın; açıklama değil,
  gerçek sayfa içeriği olarak eklenir.
- **Bul ve değiştir** — belge genelinde, özgün yazı tipi ve rengi koruyarak.
- **Alanı sil** — seçilen bölgedeki metin, grafik ve görüntüleri kalıcı kaldırır.

### Açıklamalar
Vurgu, altı çizili, üstü çizili, dalgalı, yapışkan not, serbest metin kutusu,
serbest çizim (kalem), dikdörtgen, elips, çizgi, ok, çokgen, damga, bağlantı,
dosya eki. Her açıklamada renk, dolgu, kalınlık, saydamlık ve yazar ayarı;
seçip taşıma, tutamaklarla boyutlandırma, ok tuşlarıyla ince ayar.

### Sayfa yönetimi
Boş sayfa ekleme, silme, çoğaltma, döndürme, küçük resimlerden sürükleyip
yeniden sıralama, kırpma, sayfa boyutu değiştirme, PDF birleştirme, bölme
(N sayfada bir veya aralıklara göre), sayfa çıkarma, görüntüleri sayfa olarak
ekleme, sıralamayı ters çevirme.

### Formlar
Form alanlarını listeleme ve doldurma, metin kutusu / onay kutusu ekleme,
değerleri JSON olarak dışa ve içe aktarma, formu düzleştirme.

### Görüntüler
Sayfaya görüntü ekleme, gömülü görüntüleri listeleme, taşıma/boyutlandırma,
değiştirme, silme, tek tek veya toplu dışa aktarma.

### İmza
Fare ile çizin, yazın (istediğiniz yazı tipiyle) veya saydam PNG içe aktarın;
sayfada kutu çizerek yerleştirin.

### Güvenlik ve gizlilik
AES-256 / AES-128 / RC4 şifreleme, kullanıcı ve sahip parolası, ayrıntılı izin
kontrolü (yazdırma, kopyalama, düzenleme, form doldurma…), şifre kaldırma,
**gerçek karartma** (içerik kalıcı silinir, sadece üstü boyanmaz), meta veri ve
JavaScript temizliği.

### Dışa aktarma
PNG/JPG/WEBP görüntü (36–1200 DPI, gri tonlama, saydam arka plan), düz metin,
HTML, XHTML, XML, JSON, seçili sayfaları ayrı PDF, gömülü görüntüler,
boyut küçültme (görüntü yeniden örnekleme + font alt kümeleme).

### OCR
Tesseract kuruluysa taranmış sayfalara aranabilir metin katmanı ekler.

- Linux: `sudo pacman -S tesseract tesseract-data-tur tesseract-data-eng`
  (Debian/Ubuntu: `sudo apt install tesseract-ocr tesseract-ocr-tur`)
- Windows: [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki) kurun.

### Görüntüleme
Sürekli / tek sayfa / çift sayfa / çift sayfa (kapaklı) düzenleri, %8–%1200
yakınlaştırma, genişliğe ve sayfaya sığdırma, küçük resim paneli, yer imleri
(ekleme, yeniden adlandırma, silme), açıklama listesi, arama sonuçları paneli,
koyu ve açık tema, baskı önizleme ve yazdırma, PDF sürükleyip bırakma.

---

## Klavye kısayolları

| Kısayol | İşlev |
|---|---|
| `Ctrl+O` / `Ctrl+S` / `Ctrl+Shift+S` | Aç / Kaydet / Farklı kaydet |
| `Ctrl+Z` / `Ctrl+Y` | Geri al / Yinele |
| `Ctrl+F` / `F3` / `Shift+F3` | Bul / sonraki / önceki sonuç |
| `Ctrl+P` | Yazdır |
| `Ctrl+=` / `Ctrl+-` / `Ctrl+0` | Yakınlaştır / uzaklaştır / %100 |
| `Ctrl+1` / `Ctrl+2` | Genişliğe / sayfaya sığdır |
| `Ctrl` + fare tekerleği | Sürekli yakınlaştırma |
| `V` `H` `E` `T` | Seç · El · Metni düzenle · Metin ekle |
| `D` `R` `L` `A` | Çizim · Dikdörtgen · Çizgi · Ok |
| `N` `S` `I` `K` `C` `M` | Not · İmza · Görüntü · Bağlantı · Kırp · Ölç |
| `Ctrl+Shift+R` | Karartmaları uygula |
| `Ctrl+Shift+←/→` | Sayfayı döndür |
| `F9` / `F10` / `F11` | Kenar çubuğu / özellikler / tam ekran |
| `Shift`+sürükle | Sayfayı kaydır |
| Ok tuşları | Seçili nesneyi taşı (`Shift` ile ince ayar) |
| `Esc` | Seçimi / çizimi iptal et |

---

## Proje yapısı

```
pdfstudio/
├── app.py                 Uygulama başlangıcı
├── core/                  PDF motoru (arayüzden bağımsız)
│   ├── document.py        Belge modeli, anlık görüntü tabanlı undo/redo
│   ├── textedit.py        Metin bloğu tespiti, yerinde değiştirme, ara-değiştir
│   ├── fonts.py           Sistem yazı tipi tarayıcı (TTF ad tablosu okuyucu)
│   ├── annots.py          Açıklamalar
│   ├── pageops.py         Sayfa işlemleri, filigran, sayfa numarası
│   ├── images.py          Gömülü görüntüler
│   ├── forms.py           Form alanları
│   ├── security.py        Şifreleme, izinler, temizlik
│   ├── exporting.py       Dışa aktarma, sıkıştırma, OCR
│   └── renderer.py        Sayfa görüntüleme önbelleği
└── ui/                    Qt arayüzü
    ├── mainwindow.py      Menüler, araç çubukları, tüm komutlar
    ├── pageview.py        Sayfa tuvali, araç etkileşimleri, koordinat dönüşümü
    ├── inspector.py       Sağ panel (araç ayarları / nesne özellikleri)
    ├── panels.py          Küçük resim, yer imi, açıklama, arama, form, görüntü
    ├── dialogs.py         Tüm iletişim kutuları
    ├── tools.py           Araç tanımları
    ├── widgets.py         Ortak bileşenler
    ├── icons.py           Vektör ikon seti
    └── theme.py           Koyu/açık palet ve stil sayfası

packaging/                 Kurulum dosyası üretimi
├── pdfstudio.spec         PyInstaller yapılandırması (Linux + Windows)
├── pdfstudio.iss          Inno Setup kurulum sihirbazı
├── installer_header.sh    Linux .run dosyasının açılış betiği
├── make_linux_installer.sh
├── arch/                  Arch/CachyOS paketi (PKGBUILD + üretim betiği)
└── version_info.txt       Windows exe sürüm bilgisi

.github/workflows/build.yml  Otomatik derleme (Windows + Linux)
```

---

## Bilinmesi gerekenler

- **Metin düzenleme akışı PDF'in doğasıyla sınırlıdır.** PDF bir sayfa tanımlama
  biçimidir; kelime işlemci gibi paragraf akışı yoktur. Bir bloğu uzatırsanız
  metin kutu içinde kaydırılır ve gerekirse punto küçültülür, ancak alttaki
  bloklar kendiliğinden aşağı kaymaz. Acrobat da aynı kısıtla çalışır.
- **Geri alma tam kopya tabanlıdır** (varsayılan 30 adım). Çok büyük belgelerde
  bellek kullanımı artabilir; `pdfstudio/core/history.py` içindeki `limit`
  değeriyle ayarlanır.
- **Karartma geri alınamaz bir kayıttır**: uygulandıktan sonra belge
  kaydedilirse içerik gerçekten silinmiştir.
- Uygulama tamamen çevrimdışıdır; hiçbir veri dışarı gönderilmez.

## Lisans

Kod serbestçe kullanılabilir. Bağımlılıkların lisansları geçerlidir:
PyMuPDF **AGPL-3.0** (ticari kullanım için Artifex'ten ticari lisans gerekir),
PySide6 **LGPL-3.0**.
