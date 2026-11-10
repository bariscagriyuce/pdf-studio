# YUCE PDF Düzenleyici

**Türkçe** · [English](README.en.md) · [Português (Brasil)](README.pt-BR.md)

*YUCE PDF EDITOR*

Windows, macOS ve Linux üzerinde çalışan, **Adobe Acrobat Pro benzeri** masaüstü PDF
düzenleyici. Sayfa içeriğindeki gerçek metni düzenler, açıklama ekler, sayfaları
yönetir, form doldurur, karartma (redaksiyon) uygular ve belgeyi şifreler.

| | |
|---|---|
| **Motor** | PyMuPDF (MuPDF) — hızlı, yerel, ağ bağlantısı gerektirmez |
| **Arayüz** | PySide6 (Qt 6) — koyu/açık tema; Türkçe, İngilizce, Brezilya Portekizcesi |
| **Platform** | Windows, macOS, Linux |

---

## Kurulum

### Hazır kurulum dosyaları

Güncel dosyalar **[Releases → en son sürüm](https://github.com/bariscagriyuce/pdf-studio/releases/latest)** sayfasındadır.
Aşağıda `<sürüm>` yerine indirdiğiniz sürümü (ör. `1.2.0`) yazın.

| Platform | Dosya | Kurulum |
|---|---|---|
| **Windows** 10/11 | `YUCE-PDF-Editor-<sürüm>-Setup.exe` | Çift tıklayın, sihirbazı izleyin |
| **Windows** (kurulumsuz) | `YUCE-PDF-Editor-<sürüm>-portable.exe` | Çift tıklayın, doğrudan çalışır |
| **Linux** (glibc 2.35+) | `YUCE-PDF-Editor-<sürüm>-x86_64.run` | `bash YUCE-PDF-Editor-<sürüm>-x86_64.run` |
| **macOS** 12+ (Apple Silicon: M1–M4) | `YUCE-PDF-Editor-<sürüm>-macOS-arm64.dmg` | Açın, uygulamayı *Applications*'a sürükleyin |
| **macOS** 12+ (Intel) | `YUCE-PDF-Editor-<sürüm>-macOS-x86_64.dmg` | Açın, uygulamayı *Applications*'a sürükleyin |

Python kurulu olması gerekmez; her şey pakete gömülüdür. Her dosya,
yayımlanmadan önce gömülü sınamadan geçirilir; bütünlüğü sürüm sayfasındaki
`SHA256SUMS.txt` ile doğrulayabilirsiniz.

> **Ad değişikliği (1.1.0):** Uygulamanın adı *PDF Studio* iken *YUCE PDF
> Düzenleyici* oldu. Teknik kimlikler bilerek aynı bırakıldı — komut hâlâ
> `pdf-studio`, paket adı `pdf-studio`, çalıştırılabilir `PDFStudio.exe`.
> Böylece eski sürümlerin üzerine doğrudan güncellenir ve ayarlarınız korunur.

#### Windows

`Setup.exe` Türkçe, İngilizce ve Brezilya Portekizcesi kurulum sihirbazı açar;
yönetici hakkı istemeden yalnızca sizin için ya da tüm kullanıcılar için kurabilir.
Başlat menüsü kısayolu, isteğe bağlı masaüstü kısayolu ve PDF dosyaları için
"Birlikte aç" kaydı ekler; Denetim Masası'ndan temiz kaldırılır.

#### macOS — `.dmg`

Mac'inizin işlemcisine uygun dosyayı indirin ( → *Bu Mac Hakkında*: "Apple M…"
ise `arm64`, "Intel" ise `x86_64`). `.dmg`'yi açın ve **YUCE PDF EDITOR**'ü
*Applications* klasörüne sürükleyin. Uygulama Finder'daki *Birlikte Aç* listesine
eklenir; PDF'leri Dock simgesinin üzerine sürükleyerek de açabilirsiniz.

> **İlk açılışta "doğrulanamadı" uyarısı:** Uygulama Apple geliştirici
> sertifikasıyla imzalanmadığı (notarize edilmediği) için macOS ilk açılışta
> uyarır. Bir kez şöyle açın: *Applications*'ta simgeye **sağ tıklayın → Aç → Aç**.
> macOS 15 ve sonrasında: önce açmayı deneyin, sonra *Sistem Ayarları → Gizlilik
> ve Güvenlik* altındaki **"Yine de Aç"** düğmesine basın. Terminal'den:
>
> ```bash
> xattr -dr com.apple.quarantine "/Applications/YUCE PDF EDITOR.app"
> ```

Kaldırmak için uygulamayı Çöp Sepeti'ne taşıyın (ayarlar:
`~/Library/Preferences/com.pdfstudio.PDFStudio.plist`, önbellek:
`~/Library/Caches/PDFStudio`).

#### Linux — `.run` kurulumu

```bash
bash YUCE-PDF-Editor-<sürüm>-x86_64.run
```

Root değilseniz `~/.local/opt/pdf-studio` altına, `sudo` ile çalıştırırsanız
`/opt/pdf-studio` altına kurar; uygulama menüsüne kısayol ve `pdf-studio`
komutunu ekler. Seçenekler:

```bash
bash YUCE-PDF-Editor-<sürüm>-x86_64.run --help       # tüm seçenekler
bash YUCE-PDF-Editor-<sürüm>-x86_64.run --verify     # kurup gömülü sınamayı çalıştır
bash YUCE-PDF-Editor-<sürüm>-x86_64.run --system     # sudo ile sistem geneline
bash YUCE-PDF-Editor-<sürüm>-x86_64.run --extract .  # kurmadan sadece çıkar
bash YUCE-PDF-Editor-<sürüm>-x86_64.run --uninstall  # kaldır
```

> **Çift tıklamak neden çalışmıyor?** İki yaygın sebep var:
>
> 1. **Dosya NTFS/FAT bir diskte.** Bu dosya sistemleri çalıştırma iznini
>    tutamaz; `chmod +x` sessizce etkisiz kalır. Dosyayı ev dizininize
>    kopyalayın: `cp YUCE-PDF-Editor-*.run ~/ && chmod +x ~/YUCE-PDF-Editor-*.run`
> 2. **Masaüstünüz kabuk betiklerini çalıştırmıyor.** KDE/Dolphin ve GNOME/Nautilus
>    varsayılan olarak `.run` gibi dosyaları metin düzenleyicide açar.
>    KDE'de: *Dolphin → Ayarlar → Dolphin'i Yapılandır → Genel → Onaylamalar →
>    "Çalıştırılabilir betikleri açarken"* ayarını **"Çalıştır"** yapın.
>
> Her hâlükârda terminalden `bash YUCE-PDF-Editor-*.run` demek her zaman çalışır —
> `.run` kurulumları (NVIDIA sürücüsü, Anaconda vb.) geleneksel olarak böyle
> kullanılır.

#### Arch / CachyOS / Manjaro — yerel paket

Sürüm sayfasında hazır bir Arch paketi **yoktur**; `.run` kurulumu Arch
tabanlı dağıtımlarda da çalışır. pacman ile yönetilen bir kurulum isterseniz
paketi kaynaktan kendiniz üretebilirsiniz (aşağıdaki
[Kendi kurulum dosyanızı üretmek](#kendi-kurulum-dosyanızı-üretmek) bölümü):

```bash
bash packaging/arch/build-arch-package.sh dist/PDFStudio <sürüm>
sudo pacman -U pdf-studio-<sürüm>-1-x86_64.pkg.tar.zst
```

`/opt/pdf-studio` altına kurulur; kaldırmak için `sudo pacman -R pdf-studio`.

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

macOS'ta da `bash run.sh` çalışır (Python 3.9+ gerekir: `brew install python@3.12`).
Windows'ta `run.bat`. İlk çalıştırmada sanal ortam kurulur ve bağımlılıklar
indirilir; sonraki açılışlar anında olur.

### Kendi kurulum dosyanızı üretmek

Ayrıntılar için [`packaging/README.md`](packaging/README.md). Kısaca:

```bash
python3 -m PyInstaller --noconfirm --clean packaging/pdfstudio.spec

# Evrensel .run kurulumu
bash packaging/make_linux_installer.sh dist/PDFStudio YUCE-PDF-Editor-<sürüm>-x86_64.run <sürüm>

# Arch/CachyOS paketi (makepkg gerekir)
bash packaging/arch/build-arch-package.sh dist/PDFStudio <sürüm>
```

macOS'ta tek komut `.app` ve `.dmg` üretir:

```bash
python3 build.py     # → dist/YUCE PDF EDITOR.app ve dist/YUCE-PDF-Editor-<sürüm>-macOS-<mimari>.dmg
```

Her platformun dosyası yalnızca o platformda üretilebilir.
Windows dosyalarını Linux'tan üretmek mümkün değildir. `.github/workflows/build.yml`
iş akışı üç platformu da (Windows, Linux, macOS) GitHub'ın makinelerinde derler:

- **Elle derleme:** depo → *Actions* → *Kurulum dosyalarını derle* → *Run workflow*.
  Çıktılar artefakt olarak 90 gün saklanır.
- **Sürüm yayımlama:** `git tag v1.2.3 && git push --tags`. Dosyalar *Releases*
  sayfasına SHA256 toplamlarıyla yüklenir ve **kalıcı olarak orada kalır**
  (artefaktlardan farklı olarak süresi dolmaz).

Her yapı, yüklenmeden önce gömülü sınamadan geçirilir.

#### Sürüm numarası nasıl belirlenir

Tek kaynak `pdfstudio/__init__.py` içindeki `__version__`. Etiketli bir derlemede
sürüm **etiketten** okunur ve `packaging/set_version.py` ile her yere işlenir:
dosya adları, Windows exe özellikleri, kurulum sihirbazı ve uygulamanın "Hakkında"
penceresi. Yani `v1.2.3` etiketi `YUCE-PDF-Editor-1.2.3-Setup.exe` üretir; elle sürüm
güncellemek gerekmez.

Yerelde sürüm değiştirmek için:

```bash
python packaging/set_version.py 1.2.3
```

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

### Seçili alanı yazdırma
**Alanı yazdır** aracıyla (`Ctrl+Shift+P`, araç çubuğu veya sağ tık menüsü)
sayfada bir kutu çizin; yalnızca o bölge basılır. Seçenekler: kâğıda sığdır,
gerçek boyut veya özel ölçek; ortalama; kesim işaretleri; aynı alanı birden
çok sayfada basma (etiket, fiş, form kesiti için). Baskıdan önce önizleme
açılır. **PDF olarak kaydet** ise alanı gerçek boyutta, vektör kalitesinde ayrı
bir PDF'e çıkarır — metin seçilebilir kalır, açıklamalar dahil edilir.

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

## Diller

Arayüz **Türkçe**, **İngilizce** ve **Brezilya Portekizcesi** destekler.
*Görünüm → Dil* menüsünden seçilir; değişiklik yeniden başlatınca uygulanır
(uygulama açık belgeyle birlikte kendini yeniden başlatmayı önerir).
Varsayılan **Sistem dili**dir: Türkçe sistemde Türkçe, Portekizce sistemde
Portekizce, diğerlerinde İngilizce açılır. Qt'nin kendi pencereleri (Evet/Hayır,
dosya ve renk seçici, baskı önizleme) ile sayı biçimi de seçilen dili izler.

Uygulama adı Türkçe arayüzde *YUCE PDF Düzenleyici*, diğer dillerde
*YUCE PDF EDITOR* olarak görünür. Komut satırından dil zorlamak için:

```bash
PDFSTUDIO_LANG=en pdf-studio
```

### Çeviri eklemek / düzeltmek

Kaynak dil Türkçedir: koddaki `_("…")` metinleri aynı zamanda çeviri
anahtarıdır. Çeviriler `pdfstudio/locales/<dil>.py` içindeki `MESSAGES`
sözlüğündedir. Bir değişiklikten sonra:

```bash
python packaging/check_translations.py
```

eksik çevirileri ve yer tutucu uyumsuzluklarını (`{0}`, `{name}`, `{0:.0f}`)
raporlar — uyumsuz bir yer tutucu, o mesaj gösterildiğinde uygulamayı
çökertir. CI her derlemede bu denetimi çalıştırır. Yeni bir dil için
`pdfstudio/i18n.py` içindeki `LANGUAGES` sözlüğüne ekleyip aynı yapıda bir
katalog dosyası oluşturmak yeterlidir.

## Klavye kısayolları

| Kısayol | İşlev |
|---|---|
| `Ctrl+O` / `Ctrl+S` / `Ctrl+Shift+S` | Aç / Kaydet / Farklı kaydet |
| `Ctrl+Z` / `Ctrl+Y` | Geri al / Yinele |
| `Ctrl+F` / `F3` / `Shift+F3` | Bul / sonraki / önceki sonuç |
| `Ctrl+P` | Yazdır |
| `Ctrl+Shift+P` | Seçili alanı yazdır |
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
├── i18n.py                Çeviri altyapısı (_ / _n / N_, dil seçimi, Qt çevirileri)
├── locales/               Çeviri katalogları (en.py, pt_BR.py)
├── selftest.py            Gömülü sınama (--self-test)
├── branding.py            Uygulama adı ve teknik kimlikler
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
├── check_translations.py Çeviri denetleyicisi (CI'da çalışır)
├── set_version.py         Sürüm numarasını her yere işler
└── version_info.txt       Windows exe sürüm bilgisi (üretilir)

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
