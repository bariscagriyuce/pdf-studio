# YUCE PDF EDITOR

[Türkçe](README.md) · [English](README.en.md) · **Português (Brasil)**

*YUCE PDF Düzenleyici*

Editor de PDF para desktop **no estilo do Adobe Acrobat Pro**, para Windows, macOS e
Linux. Edita o texto real do conteúdo da página, adiciona anotações, gerencia
páginas, preenche formulários, aplica tarja (redação) de verdade e criptografa
documentos.

| | |
|---|---|
| **Motor** | PyMuPDF (MuPDF) — rápido, local, não precisa de conexão com a internet |
| **Interface** | PySide6 (Qt 6) — tema escuro/claro; turco, inglês, português do Brasil |
| **Plataformas** | Windows, macOS, Linux |

---

## Instalação

### Instaladores prontos

Os arquivos atuais estão na página **[Releases → versão mais recente](https://github.com/bariscagriyuce/pdf-studio/releases/latest)**.
Abaixo, substitua `<versão>` pela versão baixada (ex.: `1.2.0`).

| Plataforma | Arquivo | Como instalar |
|---|---|---|
| **Windows** 10/11 | `YUCE-PDF-Editor-<versão>-Setup.exe` | Clique duas vezes e siga o assistente |
| **Windows** (sem instalação) | `YUCE-PDF-Editor-<versão>-portable.exe` | Clique duas vezes; executa diretamente |
| **Linux** (glibc 2.35+) | `YUCE-PDF-Editor-<versão>-x86_64.run` | `bash YUCE-PDF-Editor-<versão>-x86_64.run` |
| **macOS** 12+ (Apple Silicon: M1–M4) | `YUCE-PDF-Editor-<versão>-macOS-arm64.dmg` | Abra e arraste o app para *Aplicativos* |

Não é preciso ter o Python instalado; tudo vem embutido. Cada arquivo passa
pelo autoteste embutido antes de ser publicado, e você pode verificar sua
integridade com o `SHA256SUMS.txt` da página da versão.

> **Mudança de nome (1.1.0):** O aplicativo se chamava *PDF Studio*. Os
> identificadores técnicos foram mantidos de propósito — o comando continua
> sendo `pdf-studio`, o nome do pacote `pdf-studio` e o executável
> `PDFStudio.exe`. Assim, as versões novas atualizam as instalações antigas no
> lugar e suas configurações são preservadas.

#### Windows

O `Setup.exe` abre um assistente de instalação em turco, inglês ou português do
Brasil e pode instalar só para você (sem direitos de administrador) ou para
todos os usuários. Ele adiciona um atalho no menu Iniciar, um atalho opcional
na área de trabalho e uma entrada "Abrir com" para arquivos PDF, e é removido
de forma limpa pelo Painel de Controle.

#### macOS — `.dmg`

Somente Macs com Apple Silicon (M1 ou posterior) são suportados; não há versão
para Macs Intel. Abra o `.dmg` e arraste o
**YUCE PDF EDITOR** para *Aplicativos*. O app aparece na lista *Abrir com* do
Finder, e você também pode soltar PDFs sobre o ícone no Dock.

O app é assinado com um Developer ID e notarizado pela Apple, então abre
sem aviso de segurança.

Para desinstalar, mova o app para o Lixo (ajustes:
`~/Library/Preferences/com.pdfstudio.PDFStudio.plist`, cache:
`~/Library/Caches/PDFStudio`).

#### Linux — instalador `.run`

```bash
bash YUCE-PDF-Editor-<versão>-x86_64.run
```

Sem root, instala em `~/.local/opt/pdf-studio`; com `sudo`, em
`/opt/pdf-studio`. Adiciona uma entrada no menu de aplicativos e o comando
`pdf-studio`. Opções:

```bash
bash YUCE-PDF-Editor-<versão>-x86_64.run --help       # todas as opções
bash YUCE-PDF-Editor-<versão>-x86_64.run --verify     # instala e executa o autoteste
bash YUCE-PDF-Editor-<versão>-x86_64.run --system     # para todo o sistema, com sudo
bash YUCE-PDF-Editor-<versão>-x86_64.run --extract .  # só extrai, sem instalar
bash YUCE-PDF-Editor-<versão>-x86_64.run --uninstall  # desinstala
```

> As mensagens do instalador no terminal estão em turco; o aplicativo em si
> segue o idioma que você escolher.

> **Por que clicar duas vezes não funciona?** Dois motivos comuns:
>
> 1. **O arquivo está em um disco NTFS/FAT.** Esses sistemas de arquivos não
>    guardam a permissão de execução; o `chmod +x` não tem efeito. Copie o
>    arquivo para sua pasta pessoal:
>    `cp YUCE-PDF-Editor-*.run ~/ && chmod +x ~/YUCE-PDF-Editor-*.run`
> 2. **Seu ambiente não executa scripts de shell.** O KDE/Dolphin e o
>    GNOME/Nautilus abrem arquivos como `.run` em um editor de texto por padrão.
>    No KDE: *Dolphin → Configurações → Configurar o Dolphin → Geral →
>    Confirmações → "Ao abrir um arquivo executável"* → **"Executar script"**.
>
> Executar `bash YUCE-PDF-Editor-*.run` em um terminal sempre funciona — os
> instaladores `.run` (driver da NVIDIA, Anaconda etc.) são usados
> tradicionalmente assim.

#### Arch / CachyOS / Manjaro — pacote local

**Não há** um pacote Arch pronto na página de versões; o instalador `.run`
também funciona em distribuições baseadas no Arch. Se preferir uma instalação
gerenciada pelo pacman, você pode gerar o pacote a partir do código-fonte (veja
[Gerando seu próprio instalador](#gerando-seu-próprio-instalador) abaixo):

```bash
bash packaging/arch/build-arch-package.sh dist/PDFStudio <versão>
sudo pacman -U pdf-studio-<versão>-1-x86_64.pkg.tar.zst
```

Instala em `/opt/pdf-studio`; para desinstalar, `sudo pacman -R pdf-studio`.

#### Verificando a instalação

```bash
pdf-studio --self-test
```

O aplicativo cria um documento real, executa todos os caminhos — edição de
texto, anotações, tarja, formulários, criptografia e exportação — e informa o
resultado.

### Executando a partir do código-fonte

Para desenvolver ou testar suas próprias alterações:

```bash
bash run.sh
```

`bash run.sh` também funciona no macOS (requer Python 3.9+: `brew install python@3.12`).
No Windows, `run.bat`. A primeira execução cria um ambiente virtual e baixa as
dependências; as seguintes abrem na hora.

### Gerando seu próprio instalador

Veja [`packaging/README.md`](packaging/README.md) (em turco) para detalhes. Em resumo:

```bash
python3 -m PyInstaller --noconfirm --clean packaging/pdfstudio.spec

# Instalador .run universal
bash packaging/make_linux_installer.sh dist/PDFStudio YUCE-PDF-Editor-<versão>-x86_64.run <versão>

# Pacote Arch/CachyOS (requer makepkg)
bash packaging/arch/build-arch-package.sh dist/PDFStudio <versão>
```

No macOS, um único comando gera o `.app` e o `.dmg`:

```bash
python3 build.py     # → dist/YUCE PDF EDITOR.app e dist/YUCE-PDF-Editor-<versão>-macOS-<arq>.dmg
```

Os arquivos de cada plataforma só podem ser gerados nela.
Os arquivos do Windows não podem ser gerados no Linux. O fluxo
`.github/workflows/build.yml` compila as três plataformas (Windows, Linux, macOS) nas máquinas do GitHub:

- **Compilação manual:** repositório → *Actions* → *Kurulum dosyalarını derle* → *Run workflow*.
  Os resultados ficam guardados como artefatos por 90 dias.
- **Publicando uma versão:** `git tag v1.2.3 && git push --tags`. Os arquivos
  são enviados para a página *Releases* com somas SHA256 e **ficam lá
  permanentemente** (ao contrário dos artefatos, não expiram).

Cada compilação passa pelo autoteste embutido e pela verificação de traduções antes de ser enviada.

#### Como o número da versão é definido

Há uma única fonte: `__version__` em `pdfstudio/__init__.py`. Numa compilação
com tag, a versão é **lida da tag** e aplicada em todos os lugares por
`packaging/set_version.py`: nomes de arquivo, propriedades do executável do
Windows, o assistente de instalação e a janela Sobre do aplicativo. Assim, a
tag `v1.2.3` gera `YUCE-PDF-Editor-1.2.3-Setup.exe`; não é preciso atualizar a
versão à mão.

Para mudar a versão localmente:

```bash
python packaging/set_version.py 1.2.3
```

### Atalho na área de trabalho do Linux (ao executar a partir do código-fonte)

```bash
sudo cp -r . /opt/pdf-studio && sudo cp pdf-studio.desktop /usr/share/applications/ && sudo cp pdfstudio/resources/icon.png /usr/share/icons/hicolor/512x512/apps/pdf-studio.png
```

---

## Recursos

### Edição de texto (o principal diferencial)
- **Ferramenta Editar texto (E)** — clique em um bloco de texto da página e
  edite o conteúdo, a fonte, o tamanho, a cor, o alinhamento e o espaçamento
  entre linhas numa janela com pré-visualização ao vivo. O texto antigo é
  realmente removido (redação) e o novo é gravado no conteúdo da página.
- **Suporte completo a Unicode** — as 14 fontes embutidas do PDF não codificam
  caracteres como os do turco (`ığşİĞŞ`). O aplicativo examina os arquivos
  TTF/OTF do sistema, associa-os aos nomes reais das famílias e incorpora a
  fonte quando necessário.
- **Adicionar texto (T)** — desenhe uma caixa na página e digite o novo texto;
  ele é adicionado como conteúdo real da página, não como anotação.
- **Localizar e substituir** — no documento inteiro, mantendo a fonte e a cor originais.
- **Apagar área** — remove permanentemente texto, gráficos e imagens da região selecionada.

### Anotações
Destaque, sublinhado, tachado, ondulado, nota adesiva, caixa de texto livre,
desenho à mão livre (caneta), retângulo, elipse, linha, seta, polígono,
carimbo, link, anexo de arquivo. Cada anotação tem cor, preenchimento,
espessura, opacidade e autor; selecione para mover, redimensione pelas alças,
ajuste fino com as teclas de seta.

### Gerenciamento de páginas
Inserir páginas em branco, excluir, duplicar, girar, reordenar arrastando as
miniaturas, recortar, alterar o tamanho da página, mesclar PDFs, dividir (a
cada N páginas ou por intervalos), extrair páginas, inserir imagens como
páginas, inverter a ordem das páginas.

### Formulários
Listar e preencher campos, adicionar caixas de texto / caixas de seleção,
exportar e importar valores em JSON, nivelar o formulário.

### Imagens
Inserir imagens na página, listar as imagens incorporadas, mover/redimensionar,
substituir, excluir, exportar uma a uma ou todas de uma vez.

### Assinatura
Desenhe com o mouse, digite (com a fonte que quiser) ou importe um PNG
transparente; insira desenhando uma caixa na página.

### Segurança e privacidade
Criptografia AES-256 / AES-128 / RC4, senhas de usuário e de proprietário,
controle detalhado de permissões (impressão, cópia, edição, preenchimento de
formulários…), remoção de senha, **tarja de verdade** (o conteúdo é removido
permanentemente, não apenas coberto), limpeza de metadados e de JavaScript.

### Imprimir uma área selecionada
Com a ferramenta **Imprimir área** (`Ctrl+Shift+P`, a barra de ferramentas ou o
menu de contexto), desenhe uma caixa na página; somente essa região é
impressa. Opções: ajustar ao papel, tamanho real ou escala personalizada;
centralização; marcas de corte; imprimir a mesma área em várias páginas (para
etiquetas, recibos, trechos de formulário). Uma pré-visualização abre antes da
impressão. **Salvar como PDF** exporta a área em tamanho real, com qualidade
vetorial, para um PDF separado — o texto continua selecionável e as anotações
são incluídas.

### Exportação
Imagens PNG/JPG/WEBP (36–1200 DPI, tons de cinza, fundo transparente), texto
simples, HTML, XHTML, XML, JSON, páginas selecionadas como PDF separado,
imagens incorporadas, redução de tamanho (reamostragem de imagens +
subconjunto de fontes).

### OCR
Se o Tesseract estiver instalado, adiciona uma camada de texto pesquisável às
páginas digitalizadas.

- Linux: `sudo pacman -S tesseract tesseract-data-por tesseract-data-eng`
  (Debian/Ubuntu: `sudo apt install tesseract-ocr tesseract-ocr-por`)
- Windows: instale o [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki).

### Visualização
Layouts contínuo / página única / duas páginas / duas páginas (com capa), zoom
de 8% a 1200%, ajustar à largura e à página, painel de miniaturas, marcadores
(adicionar, renomear, excluir), lista de anotações, painel de resultados de
pesquisa, temas escuro e claro, visualização de impressão e impressão, arrastar
e soltar PDFs.

---

## Idiomas

A interface oferece **turco**, **inglês** e **português do Brasil**. Escolha em
*Exibir → Idioma*; a mudança entra em vigor ao reiniciar (o aplicativo oferece
reiniciar sozinho com o documento aberto). O padrão é **Idioma do sistema**:
num sistema em turco abre em turco, num sistema em português abre em
português, nos demais em inglês. As janelas do próprio Qt (botões Sim/Não,
seletores de arquivo e de cor, visualização de impressão) e a formatação de
números também seguem o idioma escolhido.

O aplicativo se chama *YUCE PDF Düzenleyici* na interface em turco e
*YUCE PDF EDITOR* nos demais idiomas. Para forçar um idioma pela linha de
comando:

```bash
PDFSTUDIO_LANG=pt_BR pdf-studio
```

### Adicionando ou corrigindo uma tradução

O idioma de origem é o turco: os textos `_("…")` do código também são as
chaves de tradução. As traduções ficam no dicionário `MESSAGES` em
`pdfstudio/locales/<idioma>.py`. Depois de uma alteração, execute:

```bash
python packaging/check_translations.py
```

Ele aponta traduções ausentes e espaços reservados divergentes (`{0}`,
`{name}`, `{0:.0f}`) — um espaço reservado divergente faz o aplicativo travar
quando a mensagem é exibida. A CI executa essa verificação em toda compilação.
Para adicionar um idioma novo, inclua-o no dicionário `LANGUAGES` em
`pdfstudio/i18n.py` e crie um arquivo de catálogo com a mesma estrutura.

## Atalhos de teclado

| Atalho | Ação |
|---|---|
| `Ctrl+O` / `Ctrl+S` / `Ctrl+Shift+S` | Abrir / Salvar / Salvar como |
| `Ctrl+Z` / `Ctrl+Y` | Desfazer / Refazer |
| `Ctrl+F` / `F3` / `Shift+F3` | Localizar / próximo / resultado anterior |
| `Ctrl+P` | Imprimir |
| `Ctrl+Shift+P` | Imprimir área selecionada |
| `Ctrl+=` / `Ctrl+-` / `Ctrl+0` | Ampliar / reduzir / 100% |
| `Ctrl+1` / `Ctrl+2` | Ajustar à largura / à página |
| `Ctrl` + roda do mouse | Zoom contínuo |
| `V` `H` `E` `T` | Selecionar · Mão · Editar texto · Adicionar texto |
| `D` `R` `L` `A` | Desenho · Retângulo · Linha · Seta |
| `N` `S` `I` `K` `C` `M` | Nota · Assinatura · Imagem · Link · Recortar · Medir |
| `Ctrl+Shift+R` | Aplicar tarjas |
| `Ctrl+Shift+←/→` | Girar página |
| `F9` / `F10` / `F11` | Barra lateral / propriedades / tela cheia |
| `Shift`+arrastar | Mover a página |
| Teclas de seta | Mover o objeto selecionado (`Shift` para ajuste fino) |
| `Esc` | Cancelar seleção / desenho |

---

## Estrutura do projeto

```
pdfstudio/
├── app.py                 Inicialização do aplicativo
├── i18n.py                Camada de tradução (_ / _n / N_, escolha de idioma, traduções do Qt)
├── locales/               Catálogos de tradução (en.py, pt_BR.py)
├── selftest.py            Autoteste embutido (--self-test)
├── branding.py            Nome do aplicativo e identificadores técnicos
├── core/                  Motor de PDF (independente da interface)
│   ├── document.py        Modelo do documento, desfazer/refazer por instantâneos
│   ├── textedit.py        Detecção de blocos de texto, substituição no lugar, localizar/substituir
│   ├── fonts.py           Leitor de fontes do sistema (tabela de nomes TTF)
│   ├── annots.py          Anotações
│   ├── pageops.py         Operações de página, marca d'água, números de página
│   ├── images.py          Imagens incorporadas
│   ├── forms.py           Campos de formulário
│   ├── security.py        Criptografia, permissões, higienização
│   ├── exporting.py       Exportação, compressão, OCR
│   └── renderer.py        Cache de renderização das páginas
└── ui/                    Interface Qt
    ├── mainwindow.py      Menus, barras de ferramentas, todos os comandos
    ├── pageview.py        Tela das páginas, interação das ferramentas, transformação de coordenadas
    ├── inspector.py       Painel direito (configurações da ferramenta / propriedades do objeto)
    ├── panels.py          Miniaturas, marcadores, anotações, pesquisa, formulários, imagens
    ├── dialogs.py         Todas as caixas de diálogo
    ├── tools.py           Definições das ferramentas
    ├── widgets.py         Componentes compartilhados
    ├── icons.py           Conjunto de ícones vetoriais
    └── theme.py           Paleta escura/clara e folha de estilos

packaging/                 Geração dos instaladores
├── pdfstudio.spec         Configuração do PyInstaller (Linux + Windows)
├── pdfstudio.iss          Assistente de instalação Inno Setup
├── installer_header.sh    Script inicial do arquivo .run do Linux
├── make_linux_installer.sh
├── arch/                  Pacote Arch/CachyOS (PKGBUILD + script de geração)
├── check_translations.py  Verificador de traduções (executado na CI)
├── set_version.py         Aplica o número da versão em todos os lugares
└── version_info.txt       Informações de versão do executável Windows (gerado)

.github/workflows/build.yml  Compilações automáticas (Windows + Linux)
```

---

## É bom saber

- **A edição de texto é limitada pela natureza do PDF.** O PDF é um formato de
  descrição de páginas; não há refluxo de parágrafos como num processador de
  texto. Se você aumentar um bloco, o texto quebra dentro da caixa e o tamanho
  da fonte diminui se necessário, mas os blocos de baixo não descem sozinhos.
  O Acrobat funciona com a mesma limitação.
- **O desfazer é baseado em instantâneos** (30 passos por padrão). O uso de
  memória pode crescer com documentos muito grandes; ajuste pelo `limit` em
  `pdfstudio/core/history.py`.
- **A tarja não tem volta**: depois de aplicada e o documento salvo, o conteúdo
  realmente deixa de existir.
- O aplicativo funciona totalmente offline; nenhum dado é enviado para lugar algum.

## Licença

O código é de uso livre. Valem as licenças das dependências:
PyMuPDF **AGPL-3.0** (uso comercial exige licença comercial da Artifex),
PySide6 **LGPL-3.0**.
