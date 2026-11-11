"""Brezilya Portekizcesi çevirisi — YUCE PDF Düzenleyici.

Anahtar: Türkçe kaynak metin (koddaki _() argümanı). Yer tutucular ({0},
{name}, {0:.0f}) kaynakla birebir aynı kalmalıdır; packaging/check_translations.py
bunu denetler. Sayıya bağlı mesajlar {"one": ..., "other": ...} biçimindedir.
"""

MESSAGES = {
    '{tr} ({en}) — ayrıntılı PDF düzenleyici\n\nKullanım:\n  PDFStudio [dosya.pdf]      Belgeyi açar (dosya verilmezse boş başlar)\n  PDFStudio --self-test      Kurulumu doğrular ve çıkar (CI / kurulum sonrası)\n      [--log YOL]            Sınama çıktısını dosyaya da yazar\n      [--screenshot YOL]     Ekran görüntüsü kaydeder\n  PDFStudio --version        Sürümü yazar\n  PDFStudio --help           Bu yardımı gösterir\n\nDil, uygulamada Görünüm → Dil menüsünden ya da PDFSTUDIO_LANG ortam\ndeğişkeniyle (tr, en, pt_BR) seçilir.\n':
        '{en} ({tr}) — editor de PDF completo\n\nUso:\n  PDFStudio [arquivo.pdf]    Abre o documento (inicia vazio se nenhum for informado)\n  PDFStudio --self-test      Verifica a instalação e sai (CI / pós-instalação)\n      [--log CAMINHO]        Também grava a saída do teste em um arquivo\n      [--screenshot CAMINHO] Salva uma captura de tela\n  PDFStudio --version        Mostra a versão\n  PDFStudio --help           Mostra esta ajuda\n\nO idioma é escolhido no aplicativo em Exibir → Idioma, ou pela variável\nde ambiente PDFSTUDIO_LANG (tr, en, pt_BR).\n',
    '%{0}':
        '{0}%',
    'Yapışkan not':
        'Nota adesiva',
    'Serbest metin':
        'Texto livre',
    'Çizgi':
        'Linha',
    'Dikdörtgen':
        'Retângulo',
    'Elips':
        'Elipse',
    'Çokgen':
        'Polígono',
    'Çoklu çizgi':
        'Polilinha',
    'Vurgu':
        'Destaque',
    'Altı çizili':
        'Sublinhado',
    'Dalgalı':
        'Ondulado',
    'Üstü çizili':
        'Tachado',
    'Damga':
        'Carimbo',
    'Şapka':
        'Sinal de inserção',
    'Serbest çizim':
        'Desenho à mão livre',
    'Dosya eki':
        'Anexo de arquivo',
    'Karartma':
        'Tarja',
    'Form alanı':
        'Campo de formulário',
    'Altını çiz':
        'Sublinhar',
    'Dalgalı çizgi':
        'Linha ondulada',
    'Üstünü çiz':
        'Tachar',
    'Serbest metin kutusu':
        'Caixa de texto livre',
    'Ok':
        'Seta',
    'Çift ok':
        'Seta dupla',
    'Şapka işareti':
        'Sinal de inserção',
    'Bağlantı ekle':
        'Adicionar link',
    'Bağlantıyı sil':
        'Excluir link',
    'Açıklamayı sil':
        'Excluir anotação',
    'Açıklamaları sil':
        'Excluir anotações',
    'Tüm açıklamaları kaldır':
        'Remover todas as anotações',
    'Açıklamayı düzenle':
        'Editar anotação',
    'Açıklamayı taşı':
        'Mover anotação',
    'Düzleştir':
        'Nivelar',
    'Görüntü ekle':
        'Inserir imagem',
    'İmza ekle':
        'Adicionar assinatura',
    'Seçili alan sayfanın dışında kalıyor':
        'A área selecionada está fora da página',
    'Yazdırılacak geçerli bir alan yok':
        'Não há uma área válida para imprimir',
    'Adsız.pdf':
        'Sem título.pdf',
    'Açık belge yok':
        'Nenhum documento aberto',
    'Belge parola korumalı':
        'O documento é protegido por senha',
    'Hedef dosya belirtilmedi':
        'Nenhum arquivo de destino foi informado',
    'Meta veri':
        'Metadados',
    'Yer imleri':
        'Marcadores',
    'Düz metin (.txt)':
        'Texto simples (.txt)',
    'HTML (.html)':
        'HTML (.html)',
    'XHTML (.xhtml)':
        'XHTML (.xhtml)',
    'XML (.xml)':
        'XML (.xml)',
    'JSON (.json)':
        'JSON (.json)',
    'Markdown benzeri (.md)':
        'Estilo Markdown (.md)',
    '\n----- Sayfa {0} -----\n{txt}':
        '\n----- Página {0} -----\n{txt}',
    "tesseract bulunamadı (Linux: 'tesseract' + 'tesseract-data-tur', macOS: 'brew install tesseract tesseract-lang', Windows: Tesseract-OCR kurulumu)":
        "o tesseract não foi encontrado (Linux: 'tesseract' + 'tesseract-data-por', macOS: 'brew install tesseract tesseract-lang', Windows: instale o Tesseract-OCR)",
    'TESSDATA_PREFIX ayarlanmamış':
        'TESSDATA_PREFIX não está definido',
    '(hiçbiri)':
        '(nenhum)',
    'Dil verisi eksik: {0}.\nKurulu diller: {have}\n\nLinux: sudo pacman -S tesseract-data-tur tesseract-data-eng\n  (Debian/Ubuntu: sudo apt install tesseract-ocr-tur tesseract-ocr-eng)\nWindows: Tesseract kurulumunda ilgili dil paketlerini seçin.':
        'Dados de idioma ausentes: {0}.\nIdiomas instalados: {have}\n\nLinux: sudo pacman -S tesseract-data-por tesseract-data-eng\n  (Debian/Ubuntu: sudo apt install tesseract-ocr-por tesseract-ocr-eng)\nWindows: selecione os pacotes de idioma no instalador do Tesseract.',
    'OCR uygula':
        'Aplicar OCR',
    'Dil verisi eksik: {0}':
        'Dados de idioma ausentes: {0}',
    'Düğme':
        'Botão',
    'Onay kutusu':
        'Caixa de seleção',
    'Açılır liste':
        'Lista suspensa',
    'Liste':
        'Caixa de listagem',
    'Seçenek düğmesi':
        'Botão de opção',
    'İmza':
        'Assinatura',
    'Metin kutusu':
        'Caixa de texto',
    'Alan':
        'Campo',
    'Form alanını doldur':
        'Preencher campo de formulário',
    'Formu doldur':
        'Preencher formulário',
    'Form alanı ekle':
        'Adicionar campo de formulário',
    'Form alanını sil':
        'Excluir campo de formulário',
    'Formu düzleştir':
        'Nivelar formulário',
    'Görüntüyü sil':
        'Excluir imagem',
    'Görüntüyü değiştir':
        'Substituir imagem',
    'Görüntüyü taşı/boyutlandır':
        'Mover/redimensionar imagem',
    'Boş sayfa ekle':
        'Inserir página em branco',
    'Sayfayı çoğalt':
        'Duplicar página',
    'Belgede en az bir sayfa kalmalı':
        'O documento deve manter ao menos uma página',
    'Sayfa sil':
        'Excluir página',
    'Sayfaları yeniden sırala':
        'Reordenar páginas',
    'Sayfayı döndür':
        'Girar página',
    'Dönüşü ayarla':
        'Definir rotação',
    'Sayfayı kırp':
        'Recortar página',
    'Kırpmayı sıfırla':
        'Redefinir recorte',
    'Sayfa boyutunu değiştir':
        'Alterar tamanho da página',
    'PDF birleştir':
        'Mesclar PDF',
    'Görüntüyü sayfa olarak ekle':
        'Inserir imagem como página',
    'Filigran ekle':
        "Adicionar marca d'água",
    'Görüntü filigranı':
        "Marca d'água de imagem",
    'Sayfa numarası ekle':
        'Adicionar números de página',
    'Üst/alt bilgi':
        'Cabeçalho/rodapé',
    'Yazdırma':
        'Impressão',
    'İçeriği değiştirme':
        'Alteração do conteúdo',
    'Metin/görüntü kopyalama':
        'Cópia de texto/imagens',
    'Açıklama ekleme':
        'Inclusão de anotações',
    'Form doldurma':
        'Preenchimento de formulários',
    'Erişilebilirlik için çıkarma':
        'Extração para acessibilidade',
    'Sayfa düzenleme (birleştir/böl)':
        'Montagem de páginas (mesclar/dividir)',
    'Yüksek çözünürlüklü yazdırma':
        'Impressão em alta resolução',
    'AES-256 (en güçlü)':
        'AES-256 (mais forte)',
    'AES-128':
        'AES-128',
    'RC4-128 (eski)':
        'RC4-128 (legado)',
    'Şifreleme yok':
        'Sem criptografia',
    'Belgeyi temizle':
        'Higienizar documento',
    '(kaydedilmedi)':
        '(não salvo)',
    'Dosya':
        'Arquivo',
    'Sayfa sayısı':
        'Número de páginas',
    'PDF sürümü':
        'Versão do PDF',
    'Başlık':
        'Título',
    'Yazar':
        'Autor',
    'Konu':
        'Assunto',
    'Anahtar kelimeler':
        'Palavras-chave',
    'Üretici':
        'Produtor',
    'Oluşturan':
        'Criador',
    'Oluşturma':
        'Criação',
    'Değiştirme':
        'Modificação',
    'Evet':
        'Sim',
    'Hayır':
        'Não',
    'Şifreli':
        'Criptografado',
    'Form içeriyor':
        'Contém formulário',
    'Açıklama sayısı':
        'Número de anotações',
    'Görüntü sayısı':
        'Número de imagens',
    'Kelime sayısı':
        'Número de palavras',
    'Yer imi sayısı':
        'Número de marcadores',
    'Metni düzenle':
        'Editar texto',
    'Metin ekle':
        'Adicionar texto',
    'Alanı sil':
        'Apagar área',
    'Karart (redaksiyon)':
        'Tarjar (redação)',
    "'{needle}' değiştir":
        "Substituir '{needle}'",
    'Seç / Düzenle':
        'Selecionar / Editar',
    'Görünüm':
        'Aparência',
    'Çizgi rengi':
        'Cor da linha',
    'Dolgu':
        'Preenchimento',
    'Kalınlık':
        'Espessura',
    'Yazı':
        'Texto',
    'Metin rengi':
        'Cor do texto',
    'Araç ayarları':
        'Configurações da ferramenta',
    'Adınız':
        'Seu nome',
    'Görüntü seç…':
        'Escolher imagem…',
    'İmza oluştur / seç…':
        'Criar / escolher assinatura…',
    'Not simgesi':
        'Ícone da nota',
    'Seçili nesne':
        'Objeto selecionado',
    'Açıklama içeriği / not metni':
        'Conteúdo da anotação / texto da nota',
    'Değişiklikleri uygula':
        'Aplicar alterações',
    'Nesneyi sil':
        'Excluir objeto',
    'Tür':
        'Tipo',
    'İçerik':
        'Conteúdo',
    'Konum X/Y':
        'Posição X/Y',
    'Boyut G/Y':
        'Tamanho L/A',
    'Sayfa':
        'Página',
    'Araç':
        'Ferramenta',
    'Açıklama':
        'Anotação',
    'Açıklama · {0}':
        'Anotação · {0}',
    'Form · {0}':
        'Formulário · {0}',
    'Sayfa {0} / {1}\nBoyut: {2:.0f} × {3:.0f} pt ({4:.0f} × {5:.0f} mm)\nDönüş: {6}°\nAçıklama: {7} · Görüntü: {8}':
        'Página {0} de {1}\nTamanho: {2:.0f} × {3:.0f} pt ({4:.0f} × {5:.0f} mm)\nRotação: {6}°\nAnotações: {7} · Imagens: {8}',
    'Bu noktada düzenlenebilir metin bulunamadı.':
        'Nenhum texto editável foi encontrado neste ponto.',
    'Uzunluk: {dist:.1f} pt  •  {0:.1f} mm  •  {1:.2f} inç':
        'Comprimento: {dist:.1f} pt  •  {0:.1f} mm  •  {1:.2f} pol',
    'Büyük':
        'Grande',
    'Küçük':
        'Pequeno',
    'Orta':
        'Médio',
    'Sola döndür':
        'Girar para a esquerda',
    'Sağa döndür':
        'Girar para a direita',
    'Boş sayfa ekle (önüne)':
        'Inserir página em branco (antes)',
    'Boş sayfa ekle (arkasına)':
        'Inserir página em branco (depois)',
    'Çoğalt':
        'Duplicar',
    'PDF olarak dışa aktar':
        'Exportar como PDF',
    'Görüntü olarak kaydet':
        'Salvar como imagem',
    'Sil':
        'Excluir',
    '{title}  →  sayfa {page}':
        '{title}  →  página {page}',
    'Yer imi ekle':
        'Adicionar marcador',
    'Sayfa {0} için başlık:':
        'Título para a página {0}:',
    'Başlık:':
        'Título:',
    'Yeniden adlandır':
        'Renomear',
    '0 açıklama':
        '0 anotação',
    'Seçili açıklamaları sil':
        'Excluir anotações selecionadas',
    'Tür / İçerik':
        'Tipo / Conteúdo',
    'Sayfa {0}':
        'Página {0}',
    '{0} açıklama':
        {'one': '{0} anotação', 'other': '{0} anotações'},
    'Aranacak metin…':
        'Texto a localizar…',
    'Büyük/küçük':
        'Diferenciar maiúsc./minúsc.',
    'Tam kelime':
        'Palavra inteira',
    'Değiştir':
        'Substituir',
    'Yeni metin…':
        'Novo texto…',
    'Özgün yazı tipi/rengi koru':
        'Manter fonte/cor originais',
    's.{0}  …{text}…':
        'p.{0}  …{text}…',
    'Sonuç yok':
        'Nenhum resultado',
    '{0} sonuç':
        {'one': '{0} resultado', 'other': '{0} resultados'},
    'Form alanı yok':
        'Nenhum campo de formulário',
    'Değer':
        'Valor',
    '{0} form alanı':
        {'one': '{0} campo de formulário', 'other': '{0} campos de formulário'},
    'Görüntü yok':
        'Nenhuma imagem',
    'Tümünü dışa aktar':
        'Exportar tudo',
    '{total} görüntü':
        {'one': '{total} imagem', 'other': '{total} imagens'},
    'Değiştir…':
        'Substituir…',
    'Kaydır (el)':
        'Mover (mão)',
    'Vurgula':
        'Destacar',
    'Dalgalı çiz':
        'Sublinhado ondulado',
    'Metin kutusu (açıklama)':
        'Caixa de texto (anotação)',
    'Açıklama sil':
        'Excluir anotação',
    'İmza yerleştir':
        'Inserir assinatura',
    'Bağlantı':
        'Link',
    'Kırp':
        'Recortar',
    'Form: metin kutusu':
        'Formulário: caixa de texto',
    'Form: onay kutusu':
        'Formulário: caixa de seleção',
    'Ölç':
        'Medir',
    'Alanı yazdır':
        'Imprimir área',
    'Metin seçmek için sürükleyin; açıklamaya tıklayıp taşıyın/boyutlandırın.':
        'Arraste para selecionar texto; clique em uma anotação para movê-la/redimensioná-la.',
    'Bir metin bloğuna tıklayın; içeriği, punto ve rengi düzenleyin.':
        'Clique em um bloco de texto para editar o conteúdo, o tamanho e a cor.',
    'Sayfada bir kutu çizin ve yeni metni yazın (sayfa içeriğine işlenir).':
        'Desenhe uma caixa na página e digite o novo texto (gravado no conteúdo da página).',
    'Vurgulamak istediğiniz metnin üzerinde sürükleyin.':
        'Arraste sobre o texto que deseja destacar.',
    'Fare ile serbestçe çizin; bırakınca açıklama olarak eklenir.':
        'Desenhe livremente com o mouse; ao soltar, é adicionado como anotação.',
    "Alanları işaretleyin, sonra 'Karartmaları uygula' deyin — içerik kalıcı silinir.":
        "Marque as áreas e escolha 'Aplicar tarjas' — o conteúdo é removido permanentemente.",
    'Yeni sayfa sınırını çizin.':
        'Desenhe o novo limite da página.',
    'Silinecek alanı çizin; o alandaki metin/grafik kalıcı kaldırılır.':
        'Desenhe a área a apagar; o texto/gráficos nela são removidos permanentemente.',
    'Yazdırmak istediğiniz alanı çizin; yalnızca o bölge basılır.':
        'Desenhe a área que deseja imprimir; somente essa região é impressa.',
    'Renk seç':
        'Escolher cor',
    'Tüm sayfalar (1–{total})':
        'Todas as páginas (1–{total})',
    'Geçerli sayfa ({0})':
        'Página atual ({0})',
    'Aralık:':
        'Intervalo:',
    'örn. 1-3, 5, 9-':
        'ex.: 1-3, 5, 9-',
    'Tamam':
        'OK',
    'Vazgeç':
        'Cancelar',
    'Blok: {0:.0f} × {1:.0f} pt — değişiklik doğrudan sayfa içeriğine işlenir.':
        'Bloco: {0:.0f} × {1:.0f} pt — as alterações são gravadas diretamente no conteúdo da página.',
    'Ortala':
        'Centralizar',
    'Sağa':
        'Direita',
    'Sola':
        'Esquerda',
    'İki yana':
        'Justificar',
    'Kalın':
        'Negrito',
    'İtalik':
        'Itálico',
    'Sığmazsa kutuyu büyüt':
        'Aumentar a caixa se o texto não couber',
    'Yazı tipi':
        'Fonte',
    'Punto':
        'Tamanho',
    'Renk':
        'Cor',
    'Hizalama':
        'Alinhamento',
    'Satır aralığı':
        'Espaçamento entre linhas',
    'Stil':
        'Estilo',
    'Arka plan':
        'Fundo',
    'Önizleme':
        'Pré-visualização',
    'Metni sil':
        'Excluir texto',
    'Uygula':
        'Aplicar',
    'Önizleme yok\n{exc}':
        'Sem pré-visualização\n{exc}',
    'Parola gerekli':
        'Senha necessária',
    '<b>{0}</b> korumalı.':
        '<b>{0}</b> está protegido.',
    'Parola':
        'Senha',
    'Aç':
        'Abrir',
    'Belge özellikleri':
        'Propriedades do documento',
    'Kaydet':
        'Salvar',
    'Şifreleme ve izinler':
        'Criptografia e permissões',
    'Belgeyi açmak için (boş = parolasız açılır)':
        'Para abrir (vazio = sem senha)',
    'İzinleri değiştirmek için':
        'Para alterar as permissões',
    'Kullanıcı parolası':
        'Senha de usuário',
    'Sahip parolası':
        'Senha de proprietário',
    'Yöntem':
        'Método',
    'İzin verilen işlemler':
        'Ações permitidas',
    'Şifreli kaydet':
        'Salvar criptografado',
    'Filigran':
        "Marca d'água",
    'Metin':
        'Texto',
    'Açı':
        'Ângulo',
    'Saydamlık':
        'Opacidade',
    'Seç…':
        'Escolher…',
    'Ölçek':
        'Escala',
    'Görüntü':
        'Imagem',
    'İçeriğin arkasına yerleştir':
        'Colocar atrás do conteúdo',
    'Uygulanacak sayfalar':
        'Páginas a aplicar',
    'Filigran görüntüsü':
        "Imagem da marca d'água",
    'Görüntüler (*.png *.jpg *.jpeg *.webp)':
        'Imagens (*.png *.jpg *.jpeg *.webp)',
    'TASLAK':
        'RASCUNHO',
    'Sayfa numarası / üst-alt bilgi':
        'Números de página / cabeçalho-rodapé',
    'Sayfa {n}':
        'Página {n}',
    'Sayfa {n} / {total}':
        'Página {n} de {total}',
    'Alt orta':
        'Inferior centro',
    'Alt sağ':
        'Inferior direita',
    'Alt sol':
        'Inferior esquerda',
    'Üst orta':
        'Superior centro',
    'Üst sağ':
        'Superior direita',
    'Üst sol':
        'Superior esquerda',
    'Üst bilgi (isteğe bağlı)':
        'Cabeçalho (opcional)',
    'Alt bilgi (isteğe bağlı)':
        'Rodapé (opcional)',
    'Numara biçimi':
        'Formato do número',
    'Konum':
        'Posição',
    'Başlangıç no':
        'Número inicial',
    'Kenar boşluğu':
        'Margem',
    'Üst bilgi':
        'Cabeçalho',
    'Alt bilgi':
        'Rodapé',
    'Özel':
        'Personalizado',
    'Geçerli sayfadan sonra ({0})':
        'Depois da página atual ({0})',
    'Geçerli sayfadan önce ({0})':
        'Antes da página atual ({0})',
    'Belgenin başına':
        'No início do documento',
    'Belgenin sonuna':
        'No final do documento',
    'Yatay':
        'Paisagem',
    'Boyut':
        'Tamanho',
    'Genişlik':
        'Largura',
    'Yükseklik':
        'Altura',
    'Adet':
        'Quantidade',
    'Ekle':
        'Inserir',
    "PDF'i böl":
        'Dividir PDF',
    'Her N sayfada bir böl':
        'Dividir a cada N páginas',
    'Aralıklara göre böl (örn. 1-3, 4-8, 9-)':
        'Dividir por intervalos (ex.: 1-3, 4-8, 9-)',
    'Böl':
        'Dividir',
    'Hedef klasör':
        'Pasta de destino',
    'Sayfaları görüntü olarak dışa aktar':
        'Exportar páginas como imagens',
    'Gri tonlama':
        'Tons de cinza',
    'Saydam arka plan (PNG)':
        'Fundo transparente (PNG)',
    'Biçim':
        'Formato',
    'Çözünürlük':
        'Resolução',
    'Klasör…':
        'Pasta…',
    'Dışa aktar':
        'Exportar',
    'Boyut küçült':
        'Reduzir tamanho',
    'Yazı tiplerini alt kümele':
        'Criar subconjunto de fontes',
    'Görüntü çözünürlüğü':
        'Resolução das imagens',
    'JPEG kalitesi':
        'Qualidade JPEG',
    'Küçült ve kaydet':
        'Reduzir e salvar',
    'OCR — aranabilir metin katmanı':
        'OCR — camada de texto pesquisável',
    '✔ Tesseract hazır — kurulu diller: {0}':
        '✔ Tesseract pronto — idiomas instalados: {0}',
    '⚠ Tesseract bulundu ama hiç dil verisi kurulu değil.\nLinux: sudo pacman -S tesseract-data-tur tesseract-data-eng\n(Debian/Ubuntu: sudo apt install tesseract-ocr-tur tesseract-ocr-eng)':
        '⚠ O Tesseract foi encontrado, mas nenhum dado de idioma está instalado.\nLinux: sudo pacman -S tesseract-data-por tesseract-data-eng\n(Debian/Ubuntu: sudo apt install tesseract-ocr-por tesseract-ocr-eng)',
    'Dil':
        'Idioma',
    'Web adresi':
        'Endereço web',
    'Belge içi sayfa':
        'Página deste documento',
    'Buraya imzanızı çizin':
        'Desenhe sua assinatura aqui',
    'İmza oluştur':
        'Criar assinatura',
    'Temizle':
        'Limpar',
    'Çiz':
        'Desenhar',
    'Ad Soyad':
        'Nome completo',
    'Yaz':
        'Digitar',
    'Saydam arka planlı PNG önerilir.':
        'Recomenda-se um PNG com fundo transparente.',
    'İmzayı hazırla':
        'Preparar assinatura',
    'İmza görüntüsü':
        'Imagem da assinatura',
    'Belge bilgisi':
        'Informações do documento',
    'Kapat':
        'Fechar',
    'Eklenecek metin…':
        'Texto a adicionar…',
    'Seçili alanı yazdır':
        'Imprimir área selecionada',
    '<b>Sayfa {0}</b> · seçili alan {1:.0f} × {2:.0f} mm':
        '<b>Página {0}</b> · área selecionada {1:.0f} × {2:.0f} mm',
    'Kâğıda sığdır':
        'Ajustar ao papel',
    'Küçük alanları büyütme (en fazla %100)':
        'Não ampliar áreas pequenas (máx. 100%)',
    'Gerçek boyut (%100)':
        'Tamanho real (100%)',
    'Özel:':
        'Personalizado:',
    'Yerleşim':
        'Posicionamento',
    'Kâğıdın ortasına yerleştir':
        'Centralizar no papel',
    'Kesim işaretleri ekle (köşelere ince çizgi)':
        'Adicionar marcas de corte (linhas finas nos cantos)',
    'Sayfalar':
        'Páginas',
    'Yalnızca bu sayfa ({0})':
        'Somente esta página ({0})',
    'Aynı alanı şu sayfalarda:':
        'Mesma área nestas páginas:',
    'örn. 1-{total} veya 2, 5, 8':
        'ex.: 1-{total} ou 2, 5, 8',
    'Her sayfadaki aynı bölge ayrı bir kâğıda basılır (etiket, fiş, form kesiti gibi).':
        'A mesma região de cada página é impressa em uma folha separada (etiquetas, recibos, trechos de formulário etc.).',
    'PDF olarak kaydet…':
        'Salvar como PDF…',
    "Alanı gerçek boyutta, vektör kalitesinde ayrı bir PDF'e kaydeder;\nmetin seçilebilir kalır. Ölçek seçenekleri uygulanmaz.":
        'Salva a área em tamanho real, com qualidade vetorial, em um PDF separado;\no texto continua selecionável. As opções de escala não são aplicadas.',
    'Önizle ve yazdır…':
        'Visualizar e imprimir…',
    'Geçerli bir sayfa aralığı girin.':
        'Informe um intervalo de páginas válido.',
    'Sayfa aralığı':
        'Intervalo de páginas',
    'PDF dosyaları (*.pdf);;Tüm dosyalar (*)':
        'Arquivos PDF (*.pdf);;Todos os arquivos (*)',
    'Görüntüler (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff);;Tüm dosyalar (*)':
        'Imagens (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff);;Todos os arquivos (*)',
    'Açıklamalar':
        'Anotações',
    'Ara':
        'Pesquisar',
    'Formlar':
        'Formulários',
    'Görüntüler':
        'Imagens',
    'Gezinme':
        'Navegação',
    'Özellikler':
        'Propriedades',
    'Yeni boş belge':
        'Novo documento em branco',
    'Görüntülerden yeni PDF':
        'Novo PDF a partir de imagens',
    'Aç…':
        'Abrir…',
    'Farklı kaydet…':
        'Salvar como…',
    'Belgeyi kapat':
        'Fechar documento',
    'Yazdır…':
        'Imprimir…',
    'Baskı önizleme…':
        'Visualizar impressão…',
    'Seçili alanı yazdır…':
        'Imprimir área selecionada…',
    'Çıkış':
        'Sair',
    'Geri al':
        'Desfazer',
    'Yinele':
        'Refazer',
    'Seçili metni kopyala':
        'Copiar texto selecionado',
    'Bul / Değiştir':
        'Localizar / Substituir',
    'Sonraki sonuç':
        'Próximo resultado',
    'Önceki sonuç':
        'Resultado anterior',
    'Belge özellikleri…':
        'Propriedades do documento…',
    'Yakınlaştır':
        'Ampliar',
    'Uzaklaştır':
        'Reduzir',
    'Genişliğe sığdır':
        'Ajustar à largura',
    'Sayfaya sığdır':
        'Ajustar à página',
    'Sayfayı sola döndür':
        'Girar página para a esquerda',
    'Sayfayı sağa döndür':
        'Girar página para a direita',
    'Kenar çubuğu':
        'Barra lateral',
    'Özellikler paneli':
        'Painel de propriedades',
    'Tam ekran':
        'Tela cheia',
    'Temayı değiştir':
        'Alternar tema',
    'Metin bloklarını göster':
        'Mostrar blocos de texto',
    'İlk sayfa':
        'Primeira página',
    'Önceki sayfa':
        'Página anterior',
    'Sonraki sayfa':
        'Próxima página',
    'Son sayfa':
        'Última página',
    'Boş sayfa ekle…':
        'Inserir página em branco…',
    'Sayfaları sil':
        'Excluir páginas',
    'Sayfaları çoğalt':
        'Duplicar páginas',
    'Sayfaları çıkar…':
        'Extrair páginas…',
    'Kırpma aracı':
        'Ferramenta de recorte',
    'Sayfa boyutunu değiştir…':
        'Alterar tamanho da página…',
    'PDF birleştir…':
        'Mesclar PDFs…',
    'Görüntüleri sayfa olarak ekle…':
        'Inserir imagens como páginas…',
    "PDF'i böl…":
        'Dividir PDF…',
    'Sayfa sırasını ters çevir':
        'Inverter ordem das páginas',
    'Filigran…':
        "Marca d'água…",
    'Sayfa numarası / üst-alt bilgi…':
        'Números de página / cabeçalho-rodapé…',
    'Dosya eki ekle…':
        'Adicionar anexo de arquivo…',
    'Form değerlerini dışa aktar…':
        'Exportar valores do formulário…',
    'Form değerlerini içe aktar…':
        'Importar valores do formulário…',
    'Karartmaları uygula':
        'Aplicar tarjas',
    'Açıklamaları düzleştir':
        'Nivelar anotações',
    'OCR uygula…':
        'Aplicar OCR…',
    'Boyut küçült…':
        'Reduzir tamanho…',
    'Gizlilik temizliği…':
        'Limpeza de privacidade…',
    'Şifrele / izinler…':
        'Criptografar / permissões…',
    'Şifrelemeyi kaldır…':
        'Remover criptografia…',
    'Belge bilgisi…':
        'Informações do documento…',
    'Yazı tiplerini yeniden tara':
        'Verificar fontes novamente',
    'Sayfaları görüntü olarak…':
        'Páginas como imagens…',
    'Metin / HTML olarak…':
        'Como texto / HTML…',
    'Seçili sayfaları PDF olarak…':
        'Páginas selecionadas como PDF…',
    'Gömülü görüntüleri çıkar…':
        'Extrair imagens incorporadas…',
    'Hakkında':
        'Sobre',
    'Klavye kısayolları':
        'Atalhos de teclado',
    'Ana':
        'Principal',
    'Sürekli':
        'Contínuo',
    'Tek sayfa':
        'Página única',
    'Çift sayfa':
        'Duas páginas',
    'Çift sayfa (kapaklı)':
        'Duas páginas (com capa)',
    'Araçlar':
        'Ferramentas',
    'Son kullanılanlar':
        'Arquivos recentes',
    '&Dosya':
        '&Arquivo',
    'Dü&zen':
        '&Editar',
    '&Görünüm':
        'E&xibir',
    '&Sayfa':
        '&Página',
    '&Metin':
        '&Texto',
    '&Ekle':
        '&Inserir',
    '&Form':
        'F&ormulário',
    '&Araçlar':
        'Ferra&mentas',
    '&Yardım':
        'A&juda',
    'Belge açık değil':
        'Nenhum documento aberto',
    'Kaydedilmemiş belge':
        'Documento não salvo',
    'Geri al: {0}':
        'Desfazer: {0}',
    'Kaydedilmemiş değişiklikler':
        'Alterações não salvas',
    '“{0}” kaydedilmedi. Ne yapmak istersiniz?':
        '“{0}” não foi salvo. O que deseja fazer?',
    'Görüntü seç':
        'Escolher imagem',
    'PDF aç':
        'Abrir PDF',
    'Açılamadı':
        'Não foi possível abrir',
    'Açıldı: {path}':
        'Aberto: {path}',
    'Kaydedilemedi':
        'Não foi possível salvar',
    'Kaydedildi: {0}':
        'Salvo: {0}',
    'Farklı kaydet':
        'Salvar como',
    'Kaydedildi: {path}':
        'Salvo: {path}',
    '(boş)':
        '(vazio)',
    'Listeyi temizle':
        'Limpar lista',
    'Yazdır':
        'Imprimir',
    'Seçili alan çok küçük ya da sayfanın dışında':
        'A área selecionada é pequena demais ou está fora da página',
    'Alanı PDF olarak kaydet':
        'Salvar área como PDF',
    'Alan kaydedildi: {path}':
        'Área salva: {path}',
    '{0} — seçili alan':
        '{0} — área selecionada',
    'Seçili alan — baskı önizleme':
        'Área selecionada — visualizar impressão',
    'Geri alındı: {label}':
        'Desfeito: {label}',
    'Yinelendi: {label}':
        'Refeito: {label}',
    '{0} karakter kopyalandı':
        {'one': '{0} caractere copiado', 'other': '{0} caracteres copiados'},
    'Önce metin seçin (Seç aracı ile sürükleyin)':
        'Selecione um texto primeiro (arraste com a ferramenta Selecionar)',
    'Belge özellikleri güncellendi':
        'Propriedades do documento atualizadas',
    '{0} sonuç bulundu':
        {'one': '{0} resultado encontrado', 'other': '{0} resultados encontrados'},
    'Tümünü değiştir':
        'Substituir tudo',
    "'{needle}' → '{repl}' değişimi belgedeki tüm eşleşmelere uygulanacak.\nBu işlem sayfa içeriğini kalıcı olarak değiştirir (geri alınabilir).":
        "A substituição '{needle}' → '{repl}' será aplicada a todas as ocorrências do documento.\nIsso altera o conteúdo da página permanentemente (pode ser desfeito).",
    '{n} eşleşme değiştirildi':
        {'one': '{n} ocorrência substituída', 'other': '{n} ocorrências substituídas'},
    'Görüntü hazır: {0} — sayfada bir kutu çizin':
        'Imagem pronta: {0} — desenhe uma caixa na página',
    'İmza hazır — yerleştirmek için sayfada bir kutu çizin':
        'Assinatura pronta — desenhe uma caixa na página para inseri-la',
    'İmza oluşturulamadı.':
        'Não foi possível criar a assinatura.',
    'Düzenlenemedi':
        'Não foi possível editar',
    'Metin kutuya tam sığmadı; punto otomatik küçültüldü.':
        'O texto não coube na caixa; o tamanho da fonte foi reduzido automaticamente.',
    'Metin güncellendi':
        'Texto atualizado',
    'Metin:':
        'Texto:',
    '{0} karartma bekliyor — uygulamak için Ctrl+Shift+R':
        {'one': '{0} tarja pendente — pressione Ctrl+Shift+R para aplicar', 'other': '{0} tarjas pendentes — pressione Ctrl+Shift+R para aplicar'},
    'Alan adı:':
        'Nome do campo:',
    'Metin alanı':
        'Campo de texto',
    'İşlem başarısız':
        'Falha na operação',
    'Not:':
        'Nota:',
    'Bu noktada açıklama yok':
        'Não há anotação neste ponto',
    '{0} karakter seçildi (Ctrl+C ile kopyalayın)':
        {'one': '{0} caractere selecionado (copie com Ctrl+C)', 'other': '{0} caracteres selecionados (copie com Ctrl+C)'},
    'Kopyala':
        'Copiar',
    'Bu nesneyi sil':
        'Excluir este objeto',
    'Görüntüyü değiştir…':
        'Substituir imagem…',
    'Görüntüyü kaydet…':
        'Salvar imagem…',
    'Bu metni düzenle…':
        'Editar este texto…',
    'Bu sayfayı sil':
        'Excluir esta página',
    'Bu sayfayı çoğalt':
        'Duplicar esta página',
    'Form alanını taşı':
        'Mover campo de formulário',
    'Taşınamadı':
        'Não foi possível mover',
    'Güncellenemedi':
        'Não foi possível atualizar',
    'Önce bir nesne seçin':
        'Selecione um objeto primeiro',
    'Silinemedi':
        'Não foi possível excluir',
    'Belgede en az bir sayfa kalmalı.':
        'O documento deve manter ao menos uma página.',
    'Silinemez':
        'Não é possível excluir',
    '{0} sayfa silinecek. Devam edilsin mi?':
        {'one': '{0} página será excluída. Continuar?', 'other': '{0} páginas serão excluídas. Continuar?'},
    'Sayfaları PDF olarak kaydet':
        'Salvar páginas como PDF',
    '{0} sayfa kaydedildi: {path}':
        {'one': '{0} página salva: {path}', 'other': '{0} páginas salvas: {path}'},
    "Birleştirilecek PDF'ler":
        'PDFs a mesclar',
    'Birleştir':
        'Mesclar',
    'Seçilen dosyalar nereye eklensin?\nEvet: sona · Hayır: geçerli sayfaya':
        'Onde inserir os arquivos selecionados?\nSim: no final · Não: na página atual',
    'Birleştirilemedi':
        'Não foi possível mesclar',
    '{n} sayfa eklendi':
        {'one': '{n} página adicionada', 'other': '{n} páginas adicionadas'},
    'Bölünemedi':
        'Não foi possível dividir',
    'Tamamlandı':
        'Concluído',
    '{0} dosya oluşturuldu:\n{out_dir}':
        {'one': '{0} arquivo criado:\n{out_dir}', 'other': '{0} arquivos criados:\n{out_dir}'},
    'PDF olarak kaydet':
        'Salvar como PDF',
    '{0} görüntü kaydedildi':
        {'one': '{0} imagem salva', 'other': '{0} imagens salvas'},
    'Filigran eklenemedi':
        "Não foi possível adicionar a marca d'água",
    'Eklenemedi':
        'Não foi possível adicionar',
    'Eklenecek dosya':
        'Arquivo a anexar',
    'Form değerlerini kaydet':
        'Salvar valores do formulário',
    'Form değerlerini yükle':
        'Carregar valores do formulário',
    '{n} alan dolduruldu':
        {'one': '{n} campo preenchido', 'other': '{n} campos preenchidos'},
    'Form alanları sayfa içeriğine gömülecek ve artık düzenlenemeyecek. Devam?':
        'Os campos do formulário serão incorporados ao conteúdo da página e não poderão mais ser editados. Continuar?',
    'Bekleyen karartma yok — önce Karart aracıyla alan çizin':
        'Nenhuma tarja pendente — desenhe áreas com a ferramenta Tarjar primeiro',
    '{0} alandaki metin ve görüntüler KALICI olarak silinecek.\nBelgeyi kaydettikten sonra bu içerik geri getirilemez.':
        {'one': 'O texto e as imagens de {0} área serão removidos PERMANENTEMENTE.\nDepois que o documento for salvo, esse conteúdo não poderá ser recuperado.', 'other': 'O texto e as imagens de {0} áreas serão removidos PERMANENTEMENTE.\nDepois que o documento for salvo, esse conteúdo não poderá ser recuperado.'},
    'Uygulanamadı':
        'Não foi possível aplicar',
    'Karartmalar uygulandı':
        'Tarjas aplicadas',
    'Tüm açıklamalar sayfa içeriğine gömülecek. Devam?':
        'Todas as anotações serão incorporadas ao conteúdo da página. Continuar?',
    'Açıklamaları kaldır':
        'Remover anotações',
    'Belgedeki tüm açıklamalar silinecek. Devam?':
        'Todas as anotações do documento serão excluídas. Continuar?',
    '{n} açıklama silindi':
        {'one': '{n} anotação excluída', 'other': '{n} anotações excluídas'},
    'OCR uygulanıyor…':
        'Aplicando OCR…',
    'İptal':
        'Cancelar',
    'OCR başarısız':
        'Falha no OCR',
    'OCR tamamlandı':
        'OCR concluído',
    'Küçültülmüş PDF':
        'PDF reduzido',
    'Küçültülemedi':
        'Não foi possível reduzir',
    'Önce: {0:.2f} MB\nSonra: {1:.2f} MB\nKazanç: %{pct:.1f}\n\n{path}':
        'Antes: {0:.2f} MB\nDepois: {1:.2f} MB\nEconomia: {pct:.1f}%\n\n{path}',
    'Gizlilik temizliği':
        'Limpeza de privacidade',
    'Meta veri, JavaScript ve otomatik eylemler kaldırılsın mı?':
        'Remover metadados, JavaScript e ações automáticas?',
    'Belge temizlendi':
        'Documento higienizado',
    'Şifreli kopya kaydedildi:\n{path}':
        'Cópia criptografada salva:\n{path}',
    'Şifresiz kaydet':
        'Salvar sem criptografia',
    'Kaydedildi:\n{path}':
        'Salvo:\n{path}',
    'Yazı tipleri':
        'Fontes',
    '{n} yazı tipi ailesi bulundu.':
        {'one': '{n} família de fontes encontrada.', 'other': '{n} famílias de fontes encontradas.'},
    'Dışa aktarılıyor…':
        'Exportando…',
    'Dışa aktarılamadı':
        'Não foi possível exportar',
    '{0} dosya kaydedildi:\n{out}':
        {'one': '{0} arquivo salvo:\n{out}', 'other': '{0} arquivos salvos:\n{out}'},
    'Biçim:':
        'Formato:',
    'Metin dışa aktar':
        'Exportar texto',
    'Görüntülerin kaydedileceği klasör':
        'Pasta onde salvar as imagens',
    '{0} görüntü kaydedildi:\n{out}':
        {'one': '{0} imagem salva:\n{out}', 'other': '{0} imagens salvas:\n{out}'},
    'Görüntüyü kaydet':
        'Salvar imagem',
    'Görüntüler (*.png *.jpg)':
        'Imagens (*.png *.jpg)',
    'Kaydedildi: {real}':
        'Salvo: {real}',
    'Yeni görüntü':
        'Nova imagem',
    'Sistem dili ({0})':
        'Idioma do sistema ({0})',
    'Dil tercihi kaydedildi':
        'Preferência de idioma salva',
    'Dil değişikliği uygulama yeniden başlatıldığında geçerli olur.':
        'A mudança de idioma entra em vigor quando o aplicativo for reiniciado.',
    'Şimdi yeniden başlatılsın mı?':
        'Reiniciar agora?',
    'Şimdi yeniden başlat':
        'Reiniciar agora',
    'Daha sonra':
        'Mais tarde',
    'Uygulama yeniden başlatılamadı. Lütfen kapatıp yeniden açın.':
        'Não foi possível reiniciar o aplicativo. Feche-o e abra-o novamente.',
    '{APP_NAME} hakkında':
        'Sobre o {APP_NAME}',
    '<h3>{APP_NAME_TR} {APP_VERSION}</h3><p><i>{APP_NAME_EN}</i></p><p>Windows, macOS ve Linux üzerinde çalışan, ayrıntılı PDF düzenleme uygulaması.</p><p>Motor: <b>PyMuPDF (MuPDF)</b> · Arayüz: <b>PySide6 (Qt 6)</b></p><p>PyMuPDF {0}</p>':
        '<h3>{APP_NAME_EN} {APP_VERSION}</h3><p><i>{APP_NAME_TR}</i></p><p>Aplicativo completo de edição de PDF para Windows, macOS e Linux.</p><p>Motor: <b>PyMuPDF (MuPDF)</b> · Interface: <b>PySide6 (Qt 6)</b></p><p>PyMuPDF {0}</p>',
    'Aç / Kaydet':
        'Abrir / Salvar',
    'Geri al / Yinele':
        'Desfazer / Refazer',
    'Bul / sonraki sonuç':
        'Localizar / próximo resultado',
    'Yakınlaştır / uzaklaştır':
        'Ampliar / reduzir',
    '%100 / genişliğe / sayfaya sığdır':
        '100% / ajustar à largura / à página',
    'Ctrl+Fare tekerleği':
        'Ctrl+Roda do mouse',
    'Sürekli yakınlaştırma':
        'Zoom contínuo',
    'Sayfa değiştir':
        'Mudar de página',
    'Seç · El · Metni düzenle · Metin ekle':
        'Selecionar · Mão · Editar texto · Adicionar texto',
    'Çizim · Dikdörtgen · Çizgi · Ok':
        'Desenho · Retângulo · Linha · Seta',
    'Not · İmza · Görüntü · Bağlantı':
        'Nota · Assinatura · Imagem · Link',
    'Kırp · Ölç':
        'Recortar · Medir',
    'Kenar çubuğu / özellikler / tam ekran':
        'Barra lateral / propriedades / tela cheia',
    'Sayfayı kaydır':
        'Mover a página',
    'Shift+Sürükle':
        'Shift+Arrastar',
    'Ok tuşları':
        'Teclas de seta',
    'Seçili nesneyi taşı':
        'Mover o objeto selecionado',
    'Seçimi/çizimi iptal et':
        'Cancelar seleção/desenho',
    'Soldan sağa, sonra aşağı':
        'Da esquerda para a direita, depois para baixo',
    'Sağdan sola, sonra aşağı':
        'Da direita para a esquerda, depois para baixo',
    'Yukarıdan aşağı, sonra sağa':
        'De cima para baixo, depois para a direita',
    'Yukarıdan aşağı, sonra sola':
        'De cima para baixo, depois para a esquerda',
    'Sayfa düzeni':
        'Layout da página',
    'Kâğıt başına sayfa':
        'Páginas por folha',
    'Hazır:':
        'Predefinidos:',
    'Satır:':
        'Linhas:',
    'Sütun:':
        'Colunas:',
    'Sayfa sırası:':
        'Ordem das páginas:',
    'Her sayfanın çevresine çerçeve çiz':
        'Desenhar borda em volta de cada página',
    'Kâğıt boyutu ve kenar boşlukları yazıcı ayarlarından gelir. Sayfalar iki kez küçülmesin diye yazıcı özelliklerindeki "Pages per sheet" seçeneğini 1 olarak bırakın.':
        'O tamanho do papel e as margens vêm das configurações da impressora. Deixe "Pages per sheet" nas propriedades da impressora em 1 para que as páginas não sejam reduzidas duas vezes.',
    '= kâğıt başına {n} sayfa':
        {'one': '= {n} página por folha', 'other': '= {n} páginas por folha'},
    '{rows} satır × {cols} sütun':
        '{rows} linhas × {cols} colunas',
    '<h3>Yeni sürüm hazır: {new}</h3><p>Kullandığınız sürüm: {current}</p>':
        '<h3>Nova versão disponível: {new}</h3><p>Sua versão: {current}</p>',
    'Açılışta güncellemeleri denetle':
        'Verificar atualizações ao iniciar',
    'Bu kurulum kendiliğinden güncellenemiyor; indirme sayfası tarayıcıda açılacak.':
        'Esta instalação não pode se atualizar sozinha; a página de download será aberta no navegador.',
    'Bu sürümü atla':
        'Pular esta versão',
    'Dosya doğrulanıyor…':
        'Verificando arquivo…',
    'En son sürümü kullanıyorsunuz ({0}).':
        'Você está usando a versão mais recente ({0}).',
    'Güncelleme':
        'Atualização',
    'Güncelleme denetlenemedi:\n{0}':
        'Não foi possível verificar atualizações:\n{0}',
    'Güncelleme indiriliyor…':
        'Baixando atualização…',
    'Güncelleme indiriliyor… {0:.1f} / {1:.1f} MB':
        'Baixando atualização… {0:.1f} / {1:.1f} MB',
    'Güncelleme var':
        'Atualização disponível',
    'Güncellemeler denetleniyor…':
        'Verificando atualizações…',
    'Güncellemeleri denetle…':
        'Verificar atualizações…',
    'Henüz yayımlanmış bir sürüm yok.':
        'Nenhuma versão foi publicada ainda.',
    'Kullanmaya başlamak için uygulama yeniden başlatılmalı. Şimdi yeniden başlatılsın mı?':
        'O aplicativo precisa ser reiniciado para usá-la. Reiniciar agora?',
    'Kurulum başarısız oldu (çıkış kodu {0}).':
        'A instalação falhou (código de saída {0}).',
    'Kurulum başlatılamadı.':
        'Não foi possível iniciar o instalador.',
    'Kurulum iptal edildi (yönetici izni verilmedi).':
        'Instalação cancelada (permissão de administrador não concedida).',
    'Kuruluyor… (parola sorulabilir)':
        'Instalando… (sua senha pode ser solicitada)',
    'Sürüm notu yok.':
        'Sem notas da versão.',
    'Yeni sürüm indirildi ama kurulum için yönetici izni gerekiyor. Terminalde şu komutu çalıştırın:\n\nsudo {0}':
        'A nova versão foi baixada, mas a instalação requer permissão de administrador. Execute este comando no terminal:\n\nsudo {0}',
    'Yeni sürüm indirildi. Açılan pencerede uygulamayı Applications klasörüne sürükleyip eskisinin yerine koyun.':
        'A nova versão foi baixada. Na janela que se abrir, arraste o aplicativo para a pasta Aplicativos para substituir o antigo.',
    'Yeni sürüm kuruldu.':
        'A nova versão foi instalada.',
    'İndirilen dosya bozuk (SHA-256 uyuşmuyor). Lütfen daha sonra yeniden deneyin.':
        'O arquivo baixado está corrompido (SHA-256 não confere). Tente novamente mais tarde.',
    'İndirilen dosya doğrulanamadı (özet listesinde yok).':
        'Não foi possível verificar o arquivo baixado (não está na lista de somas).',
    'İndirme başarısız:\n{0}':
        'Falha no download:\n{0}',
    'İndirme sayfasını aç':
        'Abrir página de download',
    'Şimdi güncelle':
        'Atualizar agora',
    'Otomatik (en büyük sığan)':
        'Automático (maior encaixe)',
    'Döndürme yok':
        'Sem rotação',
    '90° sağa (saat yönünde)':
        '90° à direita (sentido horário)',
    '90° sola (saat yönü tersine)':
        '90° à esquerda (sentido anti-horário)',
    'Baş aşağı (180°)':
        'De cabeça para baixo (180°)',
    'Yazıcı ayarındaki gibi':
        'Conforme a impressora',
    'Dikey':
        'Retrato',
    'Sayfa yönü:':
        'Orientação da página:',
    'Kâğıt yönü:':
        'Orientação do papel:',
    'Çıktının tamamını sayfa sayfa gösterir; oradan yazdırabilirsiniz.':
        'Mostra toda a impressão folha por folha; você pode imprimir a partir dela.',
    'Yerleşim şeması: numaralar basım sırasını, kalın kenar sayfanın üstünü gösterir.':
        'Esquema do layout: os números mostram a ordem de impressão e a borda grossa indica o topo de cada página.',
    'Baskı önizleme':
        'Visualizar impressão',
    'Sayfa düzeni: kâğıt başına sayfa, sayfa ve kâğıt yönü':
        'Layout da página: páginas por folha, orientação da página e do papel',
}
