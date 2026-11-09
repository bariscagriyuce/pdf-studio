"""İngilizce çevirisi — YUCE PDF Düzenleyici.

Anahtar: Türkçe kaynak metin (koddaki _() argümanı). Yer tutucular ({0},
{name}, {0:.0f}) kaynakla birebir aynı kalmalıdır; packaging/check_translations.py
bunu denetler. Sayıya bağlı mesajlar {"one": ..., "other": ...} biçimindedir.
"""

MESSAGES = {
    '{tr} ({en}) — ayrıntılı PDF düzenleyici\n\nKullanım:\n  PDFStudio [dosya.pdf]      Belgeyi açar (dosya verilmezse boş başlar)\n  PDFStudio --self-test      Kurulumu doğrular ve çıkar (CI / kurulum sonrası)\n      [--log YOL]            Sınama çıktısını dosyaya da yazar\n      [--screenshot YOL]     Ekran görüntüsü kaydeder\n  PDFStudio --version        Sürümü yazar\n  PDFStudio --help           Bu yardımı gösterir\n\nDil, uygulamada Görünüm → Dil menüsünden ya da PDFSTUDIO_LANG ortam\ndeğişkeniyle (tr, en, pt_BR) seçilir.\n':
        '{en} ({tr}) — detailed PDF editor\n\nUsage:\n  PDFStudio [file.pdf]       Opens the document (starts empty if none is given)\n  PDFStudio --self-test      Verifies the installation and exits (CI / post-install)\n      [--log PATH]           Also writes the test output to a file\n      [--screenshot PATH]    Saves a screenshot\n  PDFStudio --version        Prints the version\n  PDFStudio --help           Shows this help\n\nThe language is chosen in the app under View → Language, or with the\nPDFSTUDIO_LANG environment variable (tr, en, pt_BR).\n',
    '%{0}':
        '{0}%',
    'Yapışkan not':
        'Sticky note',
    'Serbest metin':
        'Free text',
    'Çizgi':
        'Line',
    'Dikdörtgen':
        'Rectangle',
    'Elips':
        'Ellipse',
    'Çokgen':
        'Polygon',
    'Çoklu çizgi':
        'Polyline',
    'Vurgu':
        'Highlight',
    'Altı çizili':
        'Underline',
    'Dalgalı':
        'Squiggly',
    'Üstü çizili':
        'Strikeout',
    'Damga':
        'Stamp',
    'Şapka':
        'Caret',
    'Serbest çizim':
        'Freehand drawing',
    'Dosya eki':
        'File attachment',
    'Karartma':
        'Redaction',
    'Form alanı':
        'Form field',
    'Altını çiz':
        'Underline',
    'Dalgalı çizgi':
        'Squiggly line',
    'Üstünü çiz':
        'Strike out',
    'Serbest metin kutusu':
        'Free text box',
    'Ok':
        'Arrow',
    'Çift ok':
        'Double arrow',
    'Şapka işareti':
        'Caret mark',
    'Bağlantı ekle':
        'Add link',
    'Bağlantıyı sil':
        'Delete link',
    'Açıklamayı sil':
        'Delete annotation',
    'Açıklamaları sil':
        'Delete annotations',
    'Tüm açıklamaları kaldır':
        'Remove all annotations',
    'Açıklamayı düzenle':
        'Edit annotation',
    'Açıklamayı taşı':
        'Move annotation',
    'Düzleştir':
        'Flatten',
    'Görüntü ekle':
        'Insert image',
    'İmza ekle':
        'Add signature',
    'Seçili alan sayfanın dışında kalıyor':
        'The selected area is outside the page',
    'Yazdırılacak geçerli bir alan yok':
        'There is no valid area to print',
    'Adsız.pdf':
        'Untitled.pdf',
    'Açık belge yok':
        'No document is open',
    'Belge parola korumalı':
        'The document is password-protected',
    'Hedef dosya belirtilmedi':
        'No target file was specified',
    'Meta veri':
        'Metadata',
    'Yer imleri':
        'Bookmarks',
    'Düz metin (.txt)':
        'Plain text (.txt)',
    'HTML (.html)':
        'HTML (.html)',
    'XHTML (.xhtml)':
        'XHTML (.xhtml)',
    'XML (.xml)':
        'XML (.xml)',
    'JSON (.json)':
        'JSON (.json)',
    'Markdown benzeri (.md)':
        'Markdown-like (.md)',
    '\n----- Sayfa {0} -----\n{txt}':
        '\n----- Page {0} -----\n{txt}',
    "tesseract bulunamadı (Linux: 'tesseract' + 'tesseract-data-tur', Windows: Tesseract-OCR kurulumu)":
        "tesseract was not found (Linux: 'tesseract' + 'tesseract-data-eng', Windows: install Tesseract-OCR)",
    'TESSDATA_PREFIX ayarlanmamış':
        'TESSDATA_PREFIX is not set',
    '(hiçbiri)':
        '(none)',
    'Dil verisi eksik: {0}.\nKurulu diller: {have}\n\nLinux: sudo pacman -S tesseract-data-tur tesseract-data-eng\n  (Debian/Ubuntu: sudo apt install tesseract-ocr-tur tesseract-ocr-eng)\nWindows: Tesseract kurulumunda ilgili dil paketlerini seçin.':
        'Missing language data: {0}.\nInstalled languages: {have}\n\nLinux: sudo pacman -S tesseract-data-eng\n  (Debian/Ubuntu: sudo apt install tesseract-ocr-eng)\nWindows: select the language packs in the Tesseract installer.',
    'OCR uygula':
        'Apply OCR',
    'Dil verisi eksik: {0}':
        'Missing language data: {0}',
    'Düğme':
        'Button',
    'Onay kutusu':
        'Check box',
    'Açılır liste':
        'Drop-down list',
    'Liste':
        'List box',
    'Seçenek düğmesi':
        'Radio button',
    'İmza':
        'Signature',
    'Metin kutusu':
        'Text box',
    'Alan':
        'Field',
    'Form alanını doldur':
        'Fill form field',
    'Formu doldur':
        'Fill form',
    'Form alanı ekle':
        'Add form field',
    'Form alanını sil':
        'Delete form field',
    'Formu düzleştir':
        'Flatten form',
    'Görüntüyü sil':
        'Delete image',
    'Görüntüyü değiştir':
        'Replace image',
    'Görüntüyü taşı/boyutlandır':
        'Move/resize image',
    'Boş sayfa ekle':
        'Insert blank page',
    'Sayfayı çoğalt':
        'Duplicate page',
    'Belgede en az bir sayfa kalmalı':
        'The document must keep at least one page',
    'Sayfa sil':
        'Delete page',
    'Sayfaları yeniden sırala':
        'Reorder pages',
    'Sayfayı döndür':
        'Rotate page',
    'Dönüşü ayarla':
        'Set rotation',
    'Sayfayı kırp':
        'Crop page',
    'Kırpmayı sıfırla':
        'Reset crop',
    'Sayfa boyutunu değiştir':
        'Change page size',
    'PDF birleştir':
        'Merge PDF',
    'Görüntüyü sayfa olarak ekle':
        'Insert image as page',
    'Filigran ekle':
        'Add watermark',
    'Görüntü filigranı':
        'Image watermark',
    'Sayfa numarası ekle':
        'Add page numbers',
    'Üst/alt bilgi':
        'Header/footer',
    'Yazdırma':
        'Printing',
    'İçeriği değiştirme':
        'Changing the content',
    'Metin/görüntü kopyalama':
        'Copying text/images',
    'Açıklama ekleme':
        'Adding annotations',
    'Form doldurma':
        'Filling in forms',
    'Erişilebilirlik için çıkarma':
        'Extraction for accessibility',
    'Sayfa düzenleme (birleştir/böl)':
        'Page assembly (merge/split)',
    'Yüksek çözünürlüklü yazdırma':
        'High-resolution printing',
    'AES-256 (en güçlü)':
        'AES-256 (strongest)',
    'AES-128':
        'AES-128',
    'RC4-128 (eski)':
        'RC4-128 (legacy)',
    'Şifreleme yok':
        'No encryption',
    'Belgeyi temizle':
        'Sanitize document',
    '(kaydedilmedi)':
        '(not saved)',
    'Dosya':
        'File',
    'Sayfa sayısı':
        'Page count',
    'PDF sürümü':
        'PDF version',
    'Başlık':
        'Title',
    'Yazar':
        'Author',
    'Konu':
        'Subject',
    'Anahtar kelimeler':
        'Keywords',
    'Üretici':
        'Producer',
    'Oluşturan':
        'Creator',
    'Oluşturma':
        'Created',
    'Değiştirme':
        'Modified',
    'Evet':
        'Yes',
    'Hayır':
        'No',
    'Şifreli':
        'Encrypted',
    'Form içeriyor':
        'Contains a form',
    'Açıklama sayısı':
        'Annotation count',
    'Görüntü sayısı':
        'Image count',
    'Kelime sayısı':
        'Word count',
    'Yer imi sayısı':
        'Bookmark count',
    'Metni düzenle':
        'Edit text',
    'Metin ekle':
        'Add text',
    'Alanı sil':
        'Erase area',
    'Karart (redaksiyon)':
        'Redact',
    "'{needle}' değiştir":
        "Replace '{needle}'",
    'Seç / Düzenle':
        'Select / Edit',
    'Görünüm':
        'Appearance',
    'Çizgi rengi':
        'Stroke color',
    'Dolgu':
        'Fill',
    'Kalınlık':
        'Width',
    'Yazı':
        'Text',
    'Metin rengi':
        'Text color',
    'Araç ayarları':
        'Tool settings',
    'Adınız':
        'Your name',
    'Görüntü seç…':
        'Choose image…',
    'İmza oluştur / seç…':
        'Create / choose signature…',
    'Not simgesi':
        'Note icon',
    'Seçili nesne':
        'Selected object',
    'Açıklama içeriği / not metni':
        'Annotation content / note text',
    'Değişiklikleri uygula':
        'Apply changes',
    'Nesneyi sil':
        'Delete object',
    'Tür':
        'Type',
    'İçerik':
        'Content',
    'Konum X/Y':
        'Position X/Y',
    'Boyut G/Y':
        'Size W/H',
    'Sayfa':
        'Page',
    'Araç':
        'Tool',
    'Açıklama':
        'Annotation',
    'Açıklama · {0}':
        'Annotation · {0}',
    'Form · {0}':
        'Form · {0}',
    'Sayfa {0} / {1}\nBoyut: {2:.0f} × {3:.0f} pt ({4:.0f} × {5:.0f} mm)\nDönüş: {6}°\nAçıklama: {7} · Görüntü: {8}':
        'Page {0} of {1}\nSize: {2:.0f} × {3:.0f} pt ({4:.0f} × {5:.0f} mm)\nRotation: {6}°\nAnnotations: {7} · Images: {8}',
    'Bu noktada düzenlenebilir metin bulunamadı.':
        'No editable text was found at this point.',
    'Uzunluk: {dist:.1f} pt  •  {0:.1f} mm  •  {1:.2f} inç':
        'Length: {dist:.1f} pt  •  {0:.1f} mm  •  {1:.2f} in',
    'Büyük':
        'Large',
    'Küçük':
        'Small',
    'Orta':
        'Medium',
    'Sola döndür':
        'Rotate left',
    'Sağa döndür':
        'Rotate right',
    'Boş sayfa ekle (önüne)':
        'Insert blank page (before)',
    'Boş sayfa ekle (arkasına)':
        'Insert blank page (after)',
    'Çoğalt':
        'Duplicate',
    'PDF olarak dışa aktar':
        'Export as PDF',
    'Görüntü olarak kaydet':
        'Save as image',
    'Sil':
        'Delete',
    '{title}  →  sayfa {page}':
        '{title}  →  page {page}',
    'Yer imi ekle':
        'Add bookmark',
    'Sayfa {0} için başlık:':
        'Title for page {0}:',
    'Başlık:':
        'Title:',
    'Yeniden adlandır':
        'Rename',
    '0 açıklama':
        '0 annotations',
    'Seçili açıklamaları sil':
        'Delete selected annotations',
    'Tür / İçerik':
        'Type / Content',
    'Sayfa {0}':
        'Page {0}',
    '{0} açıklama':
        {'one': '{0} annotation', 'other': '{0} annotations'},
    'Aranacak metin…':
        'Text to find…',
    'Büyük/küçük':
        'Match case',
    'Tam kelime':
        'Whole word',
    'Değiştir':
        'Replace',
    'Yeni metin…':
        'New text…',
    'Özgün yazı tipi/rengi koru':
        'Keep original font/color',
    's.{0}  …{text}…':
        'p.{0}  …{text}…',
    'Sonuç yok':
        'No results',
    '{0} sonuç':
        {'one': '{0} result', 'other': '{0} results'},
    'Form alanı yok':
        'No form fields',
    'Değer':
        'Value',
    '{0} form alanı':
        {'one': '{0} form field', 'other': '{0} form fields'},
    'Görüntü yok':
        'No images',
    'Tümünü dışa aktar':
        'Export all',
    '{total} görüntü':
        {'one': '{total} image', 'other': '{total} images'},
    'Değiştir…':
        'Replace…',
    'Kaydır (el)':
        'Pan (hand)',
    'Vurgula':
        'Highlight',
    'Dalgalı çiz':
        'Squiggly underline',
    'Metin kutusu (açıklama)':
        'Text box (annotation)',
    'Açıklama sil':
        'Delete annotation',
    'İmza yerleştir':
        'Place signature',
    'Bağlantı':
        'Link',
    'Kırp':
        'Crop',
    'Form: metin kutusu':
        'Form: text box',
    'Form: onay kutusu':
        'Form: check box',
    'Ölç':
        'Measure',
    'Alanı yazdır':
        'Print area',
    'Metin seçmek için sürükleyin; açıklamaya tıklayıp taşıyın/boyutlandırın.':
        'Drag to select text; click an annotation to move/resize it.',
    'Bir metin bloğuna tıklayın; içeriği, punto ve rengi düzenleyin.':
        'Click a text block to edit its content, size and color.',
    'Sayfada bir kutu çizin ve yeni metni yazın (sayfa içeriğine işlenir).':
        'Draw a box on the page and type the new text (written into the page content).',
    'Vurgulamak istediğiniz metnin üzerinde sürükleyin.':
        'Drag over the text you want to highlight.',
    'Fare ile serbestçe çizin; bırakınca açıklama olarak eklenir.':
        'Draw freely with the mouse; it is added as an annotation when you release.',
    "Alanları işaretleyin, sonra 'Karartmaları uygula' deyin — içerik kalıcı silinir.":
        "Mark the areas, then choose 'Apply redactions' — the content is removed permanently.",
    'Yeni sayfa sınırını çizin.':
        'Draw the new page boundary.',
    'Silinecek alanı çizin; o alandaki metin/grafik kalıcı kaldırılır.':
        'Draw the area to erase; text/graphics in it are removed permanently.',
    'Yazdırmak istediğiniz alanı çizin; yalnızca o bölge basılır.':
        'Draw the area you want to print; only that region is printed.',
    'Renk seç':
        'Choose color',
    'Tüm sayfalar (1–{total})':
        'All pages (1–{total})',
    'Geçerli sayfa ({0})':
        'Current page ({0})',
    'Aralık:':
        'Range:',
    'örn. 1-3, 5, 9-':
        'e.g. 1-3, 5, 9-',
    'Tamam':
        'OK',
    'Vazgeç':
        'Cancel',
    'Blok: {0:.0f} × {1:.0f} pt — değişiklik doğrudan sayfa içeriğine işlenir.':
        'Block: {0:.0f} × {1:.0f} pt — changes are written directly into the page content.',
    'Ortala':
        'Center',
    'Sağa':
        'Right',
    'Sola':
        'Left',
    'İki yana':
        'Justify',
    'Kalın':
        'Bold',
    'İtalik':
        'Italic',
    'Sığmazsa kutuyu büyüt':
        'Grow the box if the text does not fit',
    'Yazı tipi':
        'Font',
    'Punto':
        'Size',
    'Renk':
        'Color',
    'Hizalama':
        'Alignment',
    'Satır aralığı':
        'Line spacing',
    'Stil':
        'Style',
    'Arka plan':
        'Background',
    'Önizleme':
        'Preview',
    'Metni sil':
        'Delete text',
    'Uygula':
        'Apply',
    'Önizleme yok\n{exc}':
        'No preview\n{exc}',
    'Parola gerekli':
        'Password required',
    '<b>{0}</b> korumalı.':
        '<b>{0}</b> is protected.',
    'Parola':
        'Password',
    'Aç':
        'Open',
    'Belge özellikleri':
        'Document properties',
    'Kaydet':
        'Save',
    'Şifreleme ve izinler':
        'Encryption and permissions',
    'Belgeyi açmak için (boş = parolasız açılır)':
        'To open the document (empty = no password)',
    'İzinleri değiştirmek için':
        'To change the permissions',
    'Kullanıcı parolası':
        'User password',
    'Sahip parolası':
        'Owner password',
    'Yöntem':
        'Method',
    'İzin verilen işlemler':
        'Allowed actions',
    'Şifreli kaydet':
        'Save encrypted',
    'Filigran':
        'Watermark',
    'Metin':
        'Text',
    'Açı':
        'Angle',
    'Saydamlık':
        'Opacity',
    'Seç…':
        'Choose…',
    'Ölçek':
        'Scale',
    'Görüntü':
        'Image',
    'İçeriğin arkasına yerleştir':
        'Place behind the content',
    'Uygulanacak sayfalar':
        'Pages to apply to',
    'Filigran görüntüsü':
        'Watermark image',
    'Görüntüler (*.png *.jpg *.jpeg *.webp)':
        'Images (*.png *.jpg *.jpeg *.webp)',
    'TASLAK':
        'DRAFT',
    'Sayfa numarası / üst-alt bilgi':
        'Page numbers / header-footer',
    'Sayfa {n}':
        'Page {n}',
    'Sayfa {n} / {total}':
        'Page {n} of {total}',
    'Alt orta':
        'Bottom center',
    'Alt sağ':
        'Bottom right',
    'Alt sol':
        'Bottom left',
    'Üst orta':
        'Top center',
    'Üst sağ':
        'Top right',
    'Üst sol':
        'Top left',
    'Üst bilgi (isteğe bağlı)':
        'Header (optional)',
    'Alt bilgi (isteğe bağlı)':
        'Footer (optional)',
    'Numara biçimi':
        'Number format',
    'Konum':
        'Position',
    'Başlangıç no':
        'Start number',
    'Kenar boşluğu':
        'Margin',
    'Üst bilgi':
        'Header',
    'Alt bilgi':
        'Footer',
    'Özel':
        'Custom',
    'Geçerli sayfadan sonra ({0})':
        'After the current page ({0})',
    'Geçerli sayfadan önce ({0})':
        'Before the current page ({0})',
    'Belgenin başına':
        'At the beginning of the document',
    'Belgenin sonuna':
        'At the end of the document',
    'Yatay':
        'Landscape',
    'Boyut':
        'Size',
    'Genişlik':
        'Width',
    'Yükseklik':
        'Height',
    'Adet':
        'Count',
    'Ekle':
        'Insert',
    "PDF'i böl":
        'Split PDF',
    'Her N sayfada bir böl':
        'Split every N pages',
    'Aralıklara göre böl (örn. 1-3, 4-8, 9-)':
        'Split by ranges (e.g. 1-3, 4-8, 9-)',
    'Böl':
        'Split',
    'Hedef klasör':
        'Target folder',
    'Sayfaları görüntü olarak dışa aktar':
        'Export pages as images',
    'Gri tonlama':
        'Grayscale',
    'Saydam arka plan (PNG)':
        'Transparent background (PNG)',
    'Biçim':
        'Format',
    'Çözünürlük':
        'Resolution',
    'Klasör…':
        'Folder…',
    'Dışa aktar':
        'Export',
    'Boyut küçült':
        'Reduce file size',
    'Yazı tiplerini alt kümele':
        'Subset fonts',
    'Görüntü çözünürlüğü':
        'Image resolution',
    'JPEG kalitesi':
        'JPEG quality',
    'Küçült ve kaydet':
        'Reduce and save',
    'OCR — aranabilir metin katmanı':
        'OCR — searchable text layer',
    '✔ Tesseract hazır — kurulu diller: {0}':
        '✔ Tesseract ready — installed languages: {0}',
    '⚠ Tesseract bulundu ama hiç dil verisi kurulu değil.\nLinux: sudo pacman -S tesseract-data-tur tesseract-data-eng\n(Debian/Ubuntu: sudo apt install tesseract-ocr-tur tesseract-ocr-eng)':
        '⚠ Tesseract was found but no language data is installed.\nLinux: sudo pacman -S tesseract-data-eng\n(Debian/Ubuntu: sudo apt install tesseract-ocr-eng)',
    'Dil':
        'Language',
    'Web adresi':
        'Web address',
    'Belge içi sayfa':
        'Page in this document',
    'Buraya imzanızı çizin':
        'Draw your signature here',
    'İmza oluştur':
        'Create signature',
    'Temizle':
        'Clear',
    'Çiz':
        'Draw',
    'Ad Soyad':
        'Full name',
    'Yaz':
        'Type',
    'Saydam arka planlı PNG önerilir.':
        'A PNG with a transparent background is recommended.',
    'İmzayı hazırla':
        'Prepare signature',
    'İmza görüntüsü':
        'Signature image',
    'Belge bilgisi':
        'Document information',
    'Kapat':
        'Close',
    'Eklenecek metin…':
        'Text to add…',
    'Seçili alanı yazdır':
        'Print selected area',
    '<b>Sayfa {0}</b> · seçili alan {1:.0f} × {2:.0f} mm':
        '<b>Page {0}</b> · selected area {1:.0f} × {2:.0f} mm',
    'Kâğıda sığdır':
        'Fit to paper',
    'Küçük alanları büyütme (en fazla %100)':
        'Do not enlarge small areas (max. 100%)',
    'Gerçek boyut (%100)':
        'Actual size (100%)',
    'Özel:':
        'Custom:',
    'Yerleşim':
        'Placement',
    'Kâğıdın ortasına yerleştir':
        'Center on the paper',
    'Kesim işaretleri ekle (köşelere ince çizgi)':
        'Add crop marks (thin lines at the corners)',
    'Sayfalar':
        'Pages',
    'Yalnızca bu sayfa ({0})':
        'This page only ({0})',
    'Aynı alanı şu sayfalarda:':
        'Same area on these pages:',
    'örn. 1-{total} veya 2, 5, 8':
        'e.g. 1-{total} or 2, 5, 8',
    'Her sayfadaki aynı bölge ayrı bir kâğıda basılır (etiket, fiş, form kesiti gibi).':
        'The same region of each page is printed on its own sheet (labels, receipts, form sections, etc.).',
    'PDF olarak kaydet…':
        'Save as PDF…',
    "Alanı gerçek boyutta, vektör kalitesinde ayrı bir PDF'e kaydeder;\nmetin seçilebilir kalır. Ölçek seçenekleri uygulanmaz.":
        'Saves the area at actual size, in vector quality, to a separate PDF;\ntext stays selectable. Scale options are not applied.',
    'Önizle ve yazdır…':
        'Preview and print…',
    'Geçerli bir sayfa aralığı girin.':
        'Enter a valid page range.',
    'Sayfa aralığı':
        'Page range',
    'PDF dosyaları (*.pdf);;Tüm dosyalar (*)':
        'PDF files (*.pdf);;All files (*)',
    'Görüntüler (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff);;Tüm dosyalar (*)':
        'Images (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff);;All files (*)',
    'Açıklamalar':
        'Annotations',
    'Ara':
        'Search',
    'Formlar':
        'Forms',
    'Görüntüler':
        'Images',
    'Gezinme':
        'Navigation',
    'Özellikler':
        'Properties',
    'Yeni boş belge':
        'New blank document',
    'Görüntülerden yeni PDF':
        'New PDF from images',
    'Aç…':
        'Open…',
    'Farklı kaydet…':
        'Save as…',
    'Belgeyi kapat':
        'Close document',
    'Yazdır…':
        'Print…',
    'Baskı önizleme…':
        'Print preview…',
    'Seçili alanı yazdır…':
        'Print selected area…',
    'Çıkış':
        'Quit',
    'Geri al':
        'Undo',
    'Yinele':
        'Redo',
    'Seçili metni kopyala':
        'Copy selected text',
    'Bul / Değiştir':
        'Find / Replace',
    'Sonraki sonuç':
        'Next result',
    'Önceki sonuç':
        'Previous result',
    'Belge özellikleri…':
        'Document properties…',
    'Yakınlaştır':
        'Zoom in',
    'Uzaklaştır':
        'Zoom out',
    'Genişliğe sığdır':
        'Fit width',
    'Sayfaya sığdır':
        'Fit page',
    'Sayfayı sola döndür':
        'Rotate page left',
    'Sayfayı sağa döndür':
        'Rotate page right',
    'Kenar çubuğu':
        'Sidebar',
    'Özellikler paneli':
        'Properties panel',
    'Tam ekran':
        'Full screen',
    'Temayı değiştir':
        'Toggle theme',
    'Metin bloklarını göster':
        'Show text blocks',
    'İlk sayfa':
        'First page',
    'Önceki sayfa':
        'Previous page',
    'Sonraki sayfa':
        'Next page',
    'Son sayfa':
        'Last page',
    'Boş sayfa ekle…':
        'Insert blank page…',
    'Sayfaları sil':
        'Delete pages',
    'Sayfaları çoğalt':
        'Duplicate pages',
    'Sayfaları çıkar…':
        'Extract pages…',
    'Kırpma aracı':
        'Crop tool',
    'Sayfa boyutunu değiştir…':
        'Change page size…',
    'PDF birleştir…':
        'Merge PDFs…',
    'Görüntüleri sayfa olarak ekle…':
        'Insert images as pages…',
    "PDF'i böl…":
        'Split PDF…',
    'Sayfa sırasını ters çevir':
        'Reverse page order',
    'Filigran…':
        'Watermark…',
    'Sayfa numarası / üst-alt bilgi…':
        'Page numbers / header-footer…',
    'Dosya eki ekle…':
        'Add file attachment…',
    'Form değerlerini dışa aktar…':
        'Export form values…',
    'Form değerlerini içe aktar…':
        'Import form values…',
    'Karartmaları uygula':
        'Apply redactions',
    'Açıklamaları düzleştir':
        'Flatten annotations',
    'OCR uygula…':
        'Apply OCR…',
    'Boyut küçült…':
        'Reduce file size…',
    'Gizlilik temizliği…':
        'Privacy cleanup…',
    'Şifrele / izinler…':
        'Encrypt / permissions…',
    'Şifrelemeyi kaldır…':
        'Remove encryption…',
    'Belge bilgisi…':
        'Document information…',
    'Yazı tiplerini yeniden tara':
        'Rescan fonts',
    'Sayfaları görüntü olarak…':
        'Pages as images…',
    'Metin / HTML olarak…':
        'As text / HTML…',
    'Seçili sayfaları PDF olarak…':
        'Selected pages as PDF…',
    'Gömülü görüntüleri çıkar…':
        'Extract embedded images…',
    'Hakkında':
        'About',
    'Klavye kısayolları':
        'Keyboard shortcuts',
    'Ana':
        'Main',
    'Sürekli':
        'Continuous',
    'Tek sayfa':
        'Single page',
    'Çift sayfa':
        'Two pages',
    'Çift sayfa (kapaklı)':
        'Two pages (cover)',
    'Araçlar':
        'Tools',
    'Son kullanılanlar':
        'Recent files',
    '&Dosya':
        '&File',
    'Dü&zen':
        '&Edit',
    '&Görünüm':
        '&View',
    '&Sayfa':
        '&Page',
    '&Metin':
        '&Text',
    '&Ekle':
        '&Insert',
    '&Form':
        'F&orm',
    '&Araçlar':
        '&Tools',
    '&Yardım':
        '&Help',
    'Belge açık değil':
        'No document open',
    'Kaydedilmemiş belge':
        'Unsaved document',
    'Geri al: {0}':
        'Undo: {0}',
    'Kaydedilmemiş değişiklikler':
        'Unsaved changes',
    '“{0}” kaydedilmedi. Ne yapmak istersiniz?':
        '“{0}” has not been saved. What would you like to do?',
    'Görüntü seç':
        'Choose image',
    'PDF aç':
        'Open PDF',
    'Açılamadı':
        'Could not open',
    'Açıldı: {path}':
        'Opened: {path}',
    'Kaydedilemedi':
        'Could not save',
    'Kaydedildi: {0}':
        'Saved: {0}',
    'Farklı kaydet':
        'Save as',
    'Kaydedildi: {path}':
        'Saved: {path}',
    '(boş)':
        '(empty)',
    'Listeyi temizle':
        'Clear list',
    'Yazdır':
        'Print',
    'Seçili alan çok küçük ya da sayfanın dışında':
        'The selected area is too small or outside the page',
    'Alanı PDF olarak kaydet':
        'Save area as PDF',
    'Alan kaydedildi: {path}':
        'Area saved: {path}',
    '{0} — seçili alan':
        '{0} — selected area',
    'Seçili alan — baskı önizleme':
        'Selected area — print preview',
    'Geri alındı: {label}':
        'Undone: {label}',
    'Yinelendi: {label}':
        'Redone: {label}',
    '{0} karakter kopyalandı':
        {'one': '{0} character copied', 'other': '{0} characters copied'},
    'Önce metin seçin (Seç aracı ile sürükleyin)':
        'Select some text first (drag with the Select tool)',
    'Belge özellikleri güncellendi':
        'Document properties updated',
    '{0} sonuç bulundu':
        {'one': '{0} result found', 'other': '{0} results found'},
    'Tümünü değiştir':
        'Replace all',
    "'{needle}' → '{repl}' değişimi belgedeki tüm eşleşmelere uygulanacak.\nBu işlem sayfa içeriğini kalıcı olarak değiştirir (geri alınabilir).":
        "Replacing '{needle}' → '{repl}' will be applied to every match in the document.\nThis changes the page content permanently (it can be undone).",
    '{n} eşleşme değiştirildi':
        {'one': '{n} match replaced', 'other': '{n} matches replaced'},
    'Görüntü hazır: {0} — sayfada bir kutu çizin':
        'Image ready: {0} — draw a box on the page',
    'İmza hazır — yerleştirmek için sayfada bir kutu çizin':
        'Signature ready — draw a box on the page to place it',
    'İmza oluşturulamadı.':
        'The signature could not be created.',
    'Düzenlenemedi':
        'Could not edit',
    'Metin kutuya tam sığmadı; punto otomatik küçültüldü.':
        'The text did not fit the box; the font size was reduced automatically.',
    'Metin güncellendi':
        'Text updated',
    'Metin:':
        'Text:',
    '{0} karartma bekliyor — uygulamak için Ctrl+Shift+R':
        {'one': '{0} redaction pending — press Ctrl+Shift+R to apply', 'other': '{0} redactions pending — press Ctrl+Shift+R to apply'},
    'Alan adı:':
        'Field name:',
    'Metin alanı':
        'Text field',
    'İşlem başarısız':
        'Operation failed',
    'Not:':
        'Note:',
    'Bu noktada açıklama yok':
        'There is no annotation at this point',
    '{0} karakter seçildi (Ctrl+C ile kopyalayın)':
        {'one': '{0} character selected (copy with Ctrl+C)', 'other': '{0} characters selected (copy with Ctrl+C)'},
    'Kopyala':
        'Copy',
    'Bu nesneyi sil':
        'Delete this object',
    'Görüntüyü değiştir…':
        'Replace image…',
    'Görüntüyü kaydet…':
        'Save image…',
    'Bu metni düzenle…':
        'Edit this text…',
    'Bu sayfayı sil':
        'Delete this page',
    'Bu sayfayı çoğalt':
        'Duplicate this page',
    'Form alanını taşı':
        'Move form field',
    'Taşınamadı':
        'Could not move',
    'Güncellenemedi':
        'Could not update',
    'Önce bir nesne seçin':
        'Select an object first',
    'Silinemedi':
        'Could not delete',
    'Belgede en az bir sayfa kalmalı.':
        'The document must keep at least one page.',
    'Silinemez':
        'Cannot delete',
    '{0} sayfa silinecek. Devam edilsin mi?':
        {'one': '{0} page will be deleted. Continue?', 'other': '{0} pages will be deleted. Continue?'},
    'Sayfaları PDF olarak kaydet':
        'Save pages as PDF',
    '{0} sayfa kaydedildi: {path}':
        {'one': '{0} page saved: {path}', 'other': '{0} pages saved: {path}'},
    "Birleştirilecek PDF'ler":
        'PDFs to merge',
    'Birleştir':
        'Merge',
    'Seçilen dosyalar nereye eklensin?\nEvet: sona · Hayır: geçerli sayfaya':
        'Where should the selected files be inserted?\nYes: at the end · No: at the current page',
    'Birleştirilemedi':
        'Could not merge',
    '{n} sayfa eklendi':
        {'one': '{n} page added', 'other': '{n} pages added'},
    'Bölünemedi':
        'Could not split',
    'Tamamlandı':
        'Done',
    '{0} dosya oluşturuldu:\n{out_dir}':
        {'one': '{0} file created:\n{out_dir}', 'other': '{0} files created:\n{out_dir}'},
    'PDF olarak kaydet':
        'Save as PDF',
    '{0} görüntü kaydedildi':
        {'one': '{0} image saved', 'other': '{0} images saved'},
    'Filigran eklenemedi':
        'Could not add the watermark',
    'Eklenemedi':
        'Could not add',
    'Eklenecek dosya':
        'File to attach',
    'Form değerlerini kaydet':
        'Save form values',
    'Form değerlerini yükle':
        'Load form values',
    '{n} alan dolduruldu':
        {'one': '{n} field filled', 'other': '{n} fields filled'},
    'Form alanları sayfa içeriğine gömülecek ve artık düzenlenemeyecek. Devam?':
        'The form fields will be merged into the page content and can no longer be edited. Continue?',
    'Bekleyen karartma yok — önce Karart aracıyla alan çizin':
        'No pending redactions — draw areas with the Redact tool first',
    '{0} alandaki metin ve görüntüler KALICI olarak silinecek.\nBelgeyi kaydettikten sonra bu içerik geri getirilemez.':
        {'one': 'Text and images in {0} area will be PERMANENTLY removed.\nOnce the document is saved, this content cannot be recovered.', 'other': 'Text and images in {0} areas will be PERMANENTLY removed.\nOnce the document is saved, this content cannot be recovered.'},
    'Uygulanamadı':
        'Could not apply',
    'Karartmalar uygulandı':
        'Redactions applied',
    'Tüm açıklamalar sayfa içeriğine gömülecek. Devam?':
        'All annotations will be merged into the page content. Continue?',
    'Açıklamaları kaldır':
        'Remove annotations',
    'Belgedeki tüm açıklamalar silinecek. Devam?':
        'All annotations in the document will be deleted. Continue?',
    '{n} açıklama silindi':
        {'one': '{n} annotation deleted', 'other': '{n} annotations deleted'},
    'OCR uygulanıyor…':
        'Applying OCR…',
    'İptal':
        'Cancel',
    'OCR başarısız':
        'OCR failed',
    'OCR tamamlandı':
        'OCR completed',
    'Küçültülmüş PDF':
        'Reduced PDF',
    'Küçültülemedi':
        'Could not reduce',
    'Önce: {0:.2f} MB\nSonra: {1:.2f} MB\nKazanç: %{pct:.1f}\n\n{path}':
        'Before: {0:.2f} MB\nAfter: {1:.2f} MB\nSaved: {pct:.1f}%\n\n{path}',
    'Gizlilik temizliği':
        'Privacy cleanup',
    'Meta veri, JavaScript ve otomatik eylemler kaldırılsın mı?':
        'Remove metadata, JavaScript and automatic actions?',
    'Belge temizlendi':
        'Document sanitized',
    'Şifreli kopya kaydedildi:\n{path}':
        'Encrypted copy saved:\n{path}',
    'Şifresiz kaydet':
        'Save without encryption',
    'Kaydedildi:\n{path}':
        'Saved:\n{path}',
    'Yazı tipleri':
        'Fonts',
    '{n} yazı tipi ailesi bulundu.':
        {'one': '{n} font family found.', 'other': '{n} font families found.'},
    'Dışa aktarılıyor…':
        'Exporting…',
    'Dışa aktarılamadı':
        'Could not export',
    '{0} dosya kaydedildi:\n{out}':
        {'one': '{0} file saved:\n{out}', 'other': '{0} files saved:\n{out}'},
    'Biçim:':
        'Format:',
    'Metin dışa aktar':
        'Export text',
    'Görüntülerin kaydedileceği klasör':
        'Folder to save the images in',
    '{0} görüntü kaydedildi:\n{out}':
        {'one': '{0} image saved:\n{out}', 'other': '{0} images saved:\n{out}'},
    'Görüntüyü kaydet':
        'Save image',
    'Görüntüler (*.png *.jpg)':
        'Images (*.png *.jpg)',
    'Kaydedildi: {real}':
        'Saved: {real}',
    'Yeni görüntü':
        'New image',
    'Sistem dili ({0})':
        'System language ({0})',
    'Dil tercihi kaydedildi':
        'Language preference saved',
    'Dil değişikliği uygulama yeniden başlatıldığında geçerli olur.':
        'The language change takes effect when the application restarts.',
    'Şimdi yeniden başlatılsın mı?':
        'Restart now?',
    'Şimdi yeniden başlat':
        'Restart now',
    'Daha sonra':
        'Later',
    'Uygulama yeniden başlatılamadı. Lütfen kapatıp yeniden açın.':
        'The application could not be restarted. Please close it and open it again.',
    '{APP_NAME} hakkında':
        'About {APP_NAME}',
    '<h3>{APP_NAME_TR} {APP_VERSION}</h3><p><i>{APP_NAME_EN}</i></p><p>Windows ve Linux üzerinde çalışan, ayrıntılı PDF düzenleme uygulaması.</p><p>Motor: <b>PyMuPDF (MuPDF)</b> · Arayüz: <b>PySide6 (Qt 6)</b></p><p>PyMuPDF {0}</p>':
        '<h3>{APP_NAME_EN} {APP_VERSION}</h3><p><i>{APP_NAME_TR}</i></p><p>A detailed PDF editing application for Windows and Linux.</p><p>Engine: <b>PyMuPDF (MuPDF)</b> · Interface: <b>PySide6 (Qt 6)</b></p><p>PyMuPDF {0}</p>',
    'Aç / Kaydet':
        'Open / Save',
    'Geri al / Yinele':
        'Undo / Redo',
    'Bul / sonraki sonuç':
        'Find / next result',
    'Yakınlaştır / uzaklaştır':
        'Zoom in / out',
    '%100 / genişliğe / sayfaya sığdır':
        '100% / fit width / fit page',
    'Ctrl+Fare tekerleği':
        'Ctrl+Mouse wheel',
    'Sürekli yakınlaştırma':
        'Smooth zoom',
    'Sayfa değiştir':
        'Change page',
    'Seç · El · Metni düzenle · Metin ekle':
        'Select · Hand · Edit text · Add text',
    'Çizim · Dikdörtgen · Çizgi · Ok':
        'Draw · Rectangle · Line · Arrow',
    'Not · İmza · Görüntü · Bağlantı':
        'Note · Signature · Image · Link',
    'Kırp · Ölç':
        'Crop · Measure',
    'Kenar çubuğu / özellikler / tam ekran':
        'Sidebar / properties / full screen',
    'Sayfayı kaydır':
        'Pan the page',
    'Shift+Sürükle':
        'Shift+Drag',
    'Ok tuşları':
        'Arrow keys',
    'Seçili nesneyi taşı':
        'Move the selected object',
    'Seçimi/çizimi iptal et':
        'Cancel selection/drawing',
}
