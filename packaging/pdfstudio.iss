; ===========================================================================
;  YUCE PDF Düzenleyici / YUCE PDF EDITOR - Windows kurulum sihirbazı (Inno Setup 6)
;  Derleme:  iscc packaging\pdfstudio.iss
;  Girdi  :  dist\PDFStudio\   (PyInstaller onedir çıktısı)
;  Çıktı  :  dist\installer\YUCE-PDF-Editor-<sürüm>-Setup.exe
;  Not    :  Dosya UTF-8 (BOM'lu) kaydedilmelidir; Türkçe karakterler içerir.
; ===========================================================================

#define AppNameEn      "YUCE PDF EDITOR"
#define AppNameTr      "YUCE PDF Düzenleyici"
; Sürüm komut satırından verilebilir:  iscc /DAppVersion=1.2.3 pdfstudio.iss
#ifndef AppVersion
  #define AppVersion   "1.0.0"
#endif
; VersionInfoVersion yalnızca sayısal olabilir (1.2.3 gibi)
#ifndef AppVersionNumeric
  #define AppVersionNumeric AppVersion
#endif
#define AppPublisher   "YUCE"
; Teknik kimlikler önceki sürümle aynı: AppId ve exe adı değişirse güncelleme
; yerine ikinci bir kopya kurulur.
#define AppExeName     "PDFStudio.exe"
#define AppId          "{{9F3A6C41-7B2E-4D58-9A16-3C7E5D8B1042}"
#define AppDirName     "YUCE PDF Editor"
#define SourceDir      "..\dist\PDFStudio"

[Setup]
AppId={#AppId}
AppName={cm:AppTitle}
AppVersion={#AppVersion}
AppVerName={cm:AppTitle} {#AppVersion}
AppPublisher={#AppPublisher}
VersionInfoVersion={#AppVersionNumeric}
VersionInfoProductName={#AppNameEn}
VersionInfoDescription={#AppNameEn} Setup
VersionInfoCompany={#AppPublisher}
DefaultDirName={autopf}\{#AppDirName}
DefaultGroupName={#AppNameEn}
UsePreviousGroup=no
DisableProgramGroupPage=yes
DisableDirPage=no
AllowNoIcons=yes
OutputDir=..\dist\installer
OutputBaseFilename=YUCE-PDF-Editor-{#AppVersion}-Setup
SetupIconFile=..\pdfstudio\resources\icon.ico
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={cm:AppTitle} {#AppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0
LicenseFile=LICENSE-notice.txt
ChangesAssociations=yes
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "turkish";  MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[CustomMessages]
turkish.AppTitle={#AppNameTr}
turkish.CreateDesktopIcon=Masaüstü kısayolu oluştur
turkish.AssociatePdf=PDF dosyalarını "Birlikte aç" listesine ekle
turkish.SetDefaultPdf=PDF dosyaları için varsayılan uygulama yap
turkish.LaunchApp={#AppNameTr} uygulamasını başlat
turkish.AdditionalIcons=Ek kısayollar:
turkish.FileAssoc=Dosya ilişkilendirmesi:
turkish.PdfDocument=PDF Belgesi
english.AppTitle={#AppNameEn}
english.CreateDesktopIcon=Create a desktop shortcut
english.AssociatePdf=Add to the "Open with" list for PDF files
english.SetDefaultPdf=Make the default application for PDF files
english.LaunchApp=Launch {#AppNameEn}
english.AdditionalIcons=Additional shortcuts:
english.FileAssoc=File association:
english.PdfDocument=PDF Document
brazilianportuguese.AppTitle={#AppNameEn}
brazilianportuguese.CreateDesktopIcon=Criar um atalho na área de trabalho
brazilianportuguese.AssociatePdf=Adicionar à lista "Abrir com" dos arquivos PDF
brazilianportuguese.SetDefaultPdf=Tornar o aplicativo padrão para arquivos PDF
brazilianportuguese.LaunchApp=Iniciar o {#AppNameEn}
brazilianportuguese.AdditionalIcons=Atalhos adicionais:
brazilianportuguese.FileAssoc=Associação de arquivos:
brazilianportuguese.PdfDocument=Documento PDF

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "assocpdf";    Description: "{cm:AssociatePdf}";      GroupDescription: "{cm:FileAssoc}"
Name: "defaultpdf";  Description: "{cm:SetDefaultPdf}";     GroupDescription: "{cm:FileAssoc}"; Flags: unchecked

[InstallDelete]
; 1.0.0 sürümünün "PDF Studio" adlı kısayollarını temizle
Type: filesandordirs; Name: "{autoprograms}\PDF Studio"
Type: files;          Name: "{autodesktop}\PDF Studio.lnk"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\README.md";  DestDir: "{app}"; DestName: "BENIOKU.md"; Flags: ignoreversion
Source: "LICENSE-notice.txt"; DestDir: "{app}"; DestName: "LISANS.txt"; Flags: ignoreversion

[Icons]
Name: "{group}\{cm:AppTitle}";                     Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{cm:AppTitle}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{cm:AppTitle}";               Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
; Uygulama kaydı - "Birlikte aç" listesinde görünmesi için
Root: HKA; Subkey: "Software\Classes\Applications\{#AppExeName}"; \
    ValueType: string; ValueName: "FriendlyAppName"; ValueData: "{cm:AppTitle}"; \
    Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\Applications\{#AppExeName}\shell\open\command"; \
    ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; \
    Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\Applications\{#AppExeName}\DefaultIcon"; \
    ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName},0"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\Applications\{#AppExeName}\SupportedTypes"; \
    ValueType: string; ValueName: ".pdf"; ValueData: ""; Flags: uninsdeletekey

; Kendi ProgID'si
Root: HKA; Subkey: "Software\Classes\PDFStudio.Document"; \
    ValueType: string; ValueName: ""; ValueData: "{cm:PdfDocument}"; \
    Flags: uninsdeletekey; Tasks: assocpdf
Root: HKA; Subkey: "Software\Classes\PDFStudio.Document\DefaultIcon"; \
    ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName},0"; Tasks: assocpdf
Root: HKA; Subkey: "Software\Classes\PDFStudio.Document\shell\open\command"; \
    ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Tasks: assocpdf

; .pdf için "Birlikte aç" seçeneği (varsayılanı değiştirmeden)
Root: HKA; Subkey: "Software\Classes\.pdf\OpenWithProgids"; \
    ValueType: string; ValueName: "PDFStudio.Document"; ValueData: ""; \
    Flags: uninsdeletevalue; Tasks: assocpdf

; İsteğe bağlı: varsayılan uygulama yap
Root: HKA; Subkey: "Software\Classes\.pdf"; ValueType: string; ValueName: ""; \
    ValueData: "PDFStudio.Document"; Flags: uninsdeletevalue; Tasks: defaultpdf

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchApp}"; \
    Flags: nowait postinstall skipifsilent
; Uygulama içinden güncelleme: sessiz kurulum bitince yeni sürümü yeniden aç
Filename: "{app}\{#AppExeName}"; Flags: nowait runasoriginaluser; Check: ShouldRelaunch

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\PDFStudio"

[Code]
// Uygulama, güncellemeyi "/SILENT /RELAUNCH=1" ile başlatır
function ShouldRelaunch: Boolean;
begin
  Result := WizardSilent and (ExpandConstant('{param:RELAUNCH|0}') = '1');
end;
