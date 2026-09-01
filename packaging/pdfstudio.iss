; ===========================================================================
;  PDF Studio - Windows kurulum sihirbazi (Inno Setup 6)
;  Derleme:  iscc packaging\pdfstudio.iss
;  Girdi  :  dist\PDFStudio\   (PyInstaller onedir ciktisi)
;  Cikti  :  dist\installer\PDFStudio-<surum>-Setup.exe
; ===========================================================================

#define AppName        "PDF Studio"
; Version can also be passed on the command line:
#ifndef AppVersion
  #define AppVersion   "1.0.0"
#endif
; VersionInfoVersion yalnizca sayisal olabilir (1.2.3 gibi); on-surum
; etiketli surumlerde (1.2.3-beta) ayri bir deger gerekir.
#ifndef AppVersionNumeric
  #define AppVersionNumeric AppVersion
#endif
#define AppPublisher   "PDF Studio"
#define AppExeName     "PDFStudio.exe"
#define AppId          "{{9F3A6C41-7B2E-4D58-9A16-3C7E5D8B1042}"
#define SourceDir      "..\dist\PDFStudio"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
VersionInfoVersion={#AppVersionNumeric}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
DisableDirPage=no
AllowNoIcons=yes
OutputDir=..\dist\installer
OutputBaseFilename=PDFStudio-{#AppVersion}-Setup
SetupIconFile=..\pdfstudio\resources\icon.ico
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName} {#AppVersion}
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

[CustomMessages]
turkish.CreateDesktopIcon=Masaustu kisayolu olustur
turkish.AssociatePdf=PDF dosyalarini "Birlikte ac" listesine ekle
turkish.SetDefaultPdf=PDF dosyalari icin varsayilan uygulama yap
turkish.LaunchApp={#AppName} uygulamasini baslat
turkish.AdditionalIcons=Ek kisayollar:
turkish.FileAssoc=Dosya iliskilendirmesi:
english.CreateDesktopIcon=Create a desktop shortcut
english.AssociatePdf=Add to the "Open with" list for PDF files
english.SetDefaultPdf=Make the default application for PDF files
english.LaunchApp=Launch {#AppName}
english.AdditionalIcons=Additional shortcuts:
english.FileAssoc=File association:

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "assocpdf";    Description: "{cm:AssociatePdf}";      GroupDescription: "{cm:FileAssoc}"
Name: "defaultpdf";  Description: "{cm:SetDefaultPdf}";     GroupDescription: "{cm:FileAssoc}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\README.md";  DestDir: "{app}"; DestName: "BENIOKU.md"; Flags: ignoreversion
Source: "LICENSE-notice.txt"; DestDir: "{app}"; DestName: "LISANS.txt"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}";                 Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";           Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
; Uygulama kaydi - "Birlikte ac" listesinde gorunmesi icin
Root: HKA; Subkey: "Software\Classes\Applications\{#AppExeName}\shell\open\command"; \
    ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; \
    Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\Applications\{#AppExeName}\DefaultIcon"; \
    ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName},0"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\Applications\{#AppExeName}\SupportedTypes"; \
    ValueType: string; ValueName: ".pdf"; ValueData: ""; Flags: uninsdeletekey

; Kendi ProgID'si
Root: HKA; Subkey: "Software\Classes\PDFStudio.Document"; \
    ValueType: string; ValueName: ""; ValueData: "PDF Belgesi"; \
    Flags: uninsdeletekey; Tasks: assocpdf
Root: HKA; Subkey: "Software\Classes\PDFStudio.Document\DefaultIcon"; \
    ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName},0"; Tasks: assocpdf
Root: HKA; Subkey: "Software\Classes\PDFStudio.Document\shell\open\command"; \
    ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Tasks: assocpdf

; .pdf icin "Birlikte ac" secenegi (varsayilani degistirmeden)
Root: HKA; Subkey: "Software\Classes\.pdf\OpenWithProgids"; \
    ValueType: string; ValueName: "PDFStudio.Document"; ValueData: ""; \
    Flags: uninsdeletevalue; Tasks: assocpdf

; Istege bagli: varsayilan uygulama yap
Root: HKA; Subkey: "Software\Classes\.pdf"; ValueType: string; ValueName: ""; \
    ValueData: "PDFStudio.Document"; Flags: uninsdeletevalue; Tasks: defaultpdf

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchApp}"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\PDFStudio"
