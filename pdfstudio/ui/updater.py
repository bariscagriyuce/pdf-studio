"""Güncelleme denetimi ve kurulumu — arayüz ve ağ kısmı.

Akış: GitHub'a en son sürüm sorulur → daha yeniyse kullanıcıya gösterilir →
onaylanırsa kurulum türüne uygun dosya indirilir, SHA256SUMS.txt ile
doğrulanır → platforma göre kurulur:

* Windows (kurulum sihirbazı): sessiz kurulum başlatılır, uygulama kapanır,
  kurulum bitince yeni sürüm kendiliğinden açılır.
* macOS: uygulama kapanınca küçük bir betik .app paketini .dmg içindekiyle
  değiştirip yeniden açar.
* Linux: pacman paketi ya da .run kurulumu çalıştırılır (sistem geneli
  kurulumda parola penceresi pkexec ile açılır), sonra yeniden başlatılır.

Kendiliğinden kurulamayan durumlarda (taşınabilir exe, kaynak koddan çalışma)
indirme sayfası tarayıcıda açılır.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time

from PySide6.QtCore import QObject, QProcess, QStandardPaths, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QMessageBox, QProgressDialog,
                               QPushButton, QTextBrowser, QVBoxLayout)

from .. import __version__ as APP_VERSION
from ..core import updater as up
from ..i18n import _

ENV_DISABLE = "PDFSTUDIO_NO_UPDATE_CHECK"


class UpdateDialog(QDialog):
    """'Yeni sürüm var' penceresi."""

    UPDATE, SKIP, LATER = 1, 2, 0

    def __init__(self, release: up.Release, can_install: bool, parent=None):
        super().__init__(parent)
        self.choice = self.LATER
        self.setWindowTitle(_("Güncelleme var"))
        self.setMinimumSize(520, 380)
        lay = QVBoxLayout(self)
        head = QLabel(_("<h3>Yeni sürüm hazır: {new}</h3>"
                        "<p>Kullandığınız sürüm: {current}</p>").format(
            new=release.version, current=APP_VERSION))
        lay.addWidget(head)
        notes = QTextBrowser()
        notes.setOpenExternalLinks(True)
        notes.setMarkdown(release.notes or _("Sürüm notu yok."))
        lay.addWidget(notes, 1)
        if not can_install:
            hint = QLabel(_("Bu kurulum kendiliğinden güncellenemiyor; "
                            "indirme sayfası tarayıcıda açılacak."))
            hint.setProperty("hint", True)
            hint.setWordWrap(True)
            lay.addWidget(hint)

        row = QHBoxLayout()
        skip = QPushButton(_("Bu sürümü atla"))
        later = QPushButton(_("Daha sonra"))
        go = QPushButton(_("Şimdi güncelle") if can_install else _("İndirme sayfasını aç"))
        go.setProperty("accent", True)
        go.setDefault(True)
        skip.clicked.connect(lambda: self._done(self.SKIP))
        later.clicked.connect(lambda: self._done(self.LATER))
        go.clicked.connect(lambda: self._done(self.UPDATE))
        row.addWidget(skip)
        row.addStretch(1)
        row.addWidget(later)
        row.addWidget(go)
        lay.addLayout(row)

    def _done(self, choice: int) -> None:
        self.choice = choice
        self.accept()


class UpdateManager(QObject):
    def __init__(self, window):
        super().__init__(window)
        self.win = window
        self.settings = window.settings_store
        self.nam = QNetworkAccessManager(self)
        self.kind = up.install_kind()
        self._busy = False
        self._progress: QProgressDialog | None = None
        self._reply: QNetworkReply | None = None
        self._proc: QProcess | None = None

    # ------------------------------------------------------------ ayarlar
    def auto_enabled(self) -> bool:
        v = self.settings.value("update/auto", True)
        return v not in (False, "false", "0", 0)

    def set_auto_enabled(self, on: bool) -> None:
        self.settings.setValue("update/auto", bool(on))

    def check_on_startup(self) -> None:
        """Açılışta, günde en çok bir kez, sessizce denetler."""
        if os.environ.get(ENV_DISABLE) or not self.auto_enabled():
            return
        try:
            last = float(self.settings.value("update/last_check", 0) or 0)
        except (TypeError, ValueError):
            last = 0.0
        if time.time() - last < up.CHECK_INTERVAL_S:
            return
        self.check(manual=False)

    # ------------------------------------------------------------ denetim
    def _request(self, url: str) -> QNetworkRequest:
        req = QNetworkRequest(QUrl(url))
        req.setHeader(QNetworkRequest.UserAgentHeader, f"YUCE-PDF-Editor/{APP_VERSION}")
        req.setRawHeader(b"Accept", b"application/vnd.github+json")
        req.setAttribute(QNetworkRequest.RedirectPolicyAttribute,
                         QNetworkRequest.NoLessSafeRedirectPolicy)
        req.setTransferTimeout(30_000)
        return req

    def check(self, manual: bool = True) -> None:
        if self._busy:
            return
        self._busy = True
        if manual:
            self.win.statusBar().showMessage(_("Güncellemeler denetleniyor…"))
        reply = self.nam.get(self._request(up.LATEST_URL))
        reply.finished.connect(lambda: self._on_latest(reply, manual))

    def _on_latest(self, reply: QNetworkReply, manual: bool) -> None:
        self._busy = False
        reply.deleteLater()
        if manual:
            self.win.statusBar().clearMessage()
        if reply.error() != QNetworkReply.NoError:
            status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            if manual:
                if status == 404:
                    QMessageBox.information(self.win, _("Güncelleme"),
                                            _("Henüz yayımlanmış bir sürüm yok."))
                else:
                    QMessageBox.warning(self.win, _("Güncelleme"),
                                        _("Güncelleme denetlenemedi:\n{0}").format(
                                            reply.errorString()))
            return
        self.settings.setValue("update/last_check", time.time())
        try:
            release = up.parse_release(json.loads(bytes(reply.readAll()).decode("utf-8")))
        except (ValueError, UnicodeDecodeError):
            release = None
        if release is None or not up.is_newer(release.version, APP_VERSION):
            if manual:
                QMessageBox.information(
                    self.win, _("Güncelleme"),
                    _("En son sürümü kullanıyorsunuz ({0}).").format(APP_VERSION))
            return
        if not manual and self.settings.value("update/skip", "") == release.version:
            return
        self._offer(release)

    def _offer(self, release: up.Release) -> None:
        asset = up.pick_asset(release, self.kind) if self.kind in up.AUTO_INSTALL else None
        d = UpdateDialog(release, asset is not None, self.win)
        d.exec()
        if d.choice == UpdateDialog.SKIP:
            self.settings.setValue("update/skip", release.version)
        elif d.choice == UpdateDialog.UPDATE:
            if asset is None:
                QDesktopServices.openUrl(QUrl(release.page_url))
            else:
                self._start(release, asset)

    # ------------------------------------------------------------ indirme
    def _download_dir(self) -> str:
        base = QStandardPaths.writableLocation(QStandardPaths.CacheLocation) or \
            os.path.join(os.path.expanduser("~"), ".cache", "pdfstudio")
        path = os.path.join(base, "updates")
        shutil.rmtree(path, ignore_errors=True)     # eski indirmeleri temizle
        os.makedirs(path, exist_ok=True)
        return path

    def _start(self, release: up.Release, asset: up.Asset) -> None:
        if not self.win._confirm_discard():
            return
        self._busy = True
        folder = self._download_dir()
        sums_asset = release.asset(up.CHECKSUMS_NAME)

        def got_sums(text: str | None):
            sums = up.parse_checksums(text or "")
            expected = sums.get(asset.name)
            if sums_asset is not None and not expected:
                self._fail(_("İndirilen dosya doğrulanamadı (özet listesinde yok)."))
                return
            dest = os.path.join(folder, asset.name)
            self._download(asset.url, dest, asset.size,
                           lambda ok: self._downloaded(ok, dest, expected))

        if sums_asset is None:
            got_sums(None)
        else:
            reply = self.nam.get(self._request(sums_asset.url))

            def done():
                reply.deleteLater()
                if reply.error() != QNetworkReply.NoError:
                    self._fail(_("İndirme başarısız:\n{0}").format(reply.errorString()))
                    return
                got_sums(bytes(reply.readAll()).decode("utf-8", "replace"))
            reply.finished.connect(done)

    def _download(self, url: str, dest: str, size: int, on_done) -> None:
        prog = QProgressDialog(_("Güncelleme indiriliyor…"), _("Vazgeç"), 0,
                               max(1, size // 1024), self.win)
        prog.setWindowTitle(_("Güncelleme"))
        prog.setWindowModality(Qt.WindowModal)
        prog.setMinimumDuration(0)
        prog.setAutoClose(False)
        prog.setAutoReset(False)
        prog.setValue(0)
        self._progress = prog
        fh = open(dest, "wb")
        reply = self.nam.get(self._request(url))
        reply.setReadBufferSize(0)
        self._reply = reply
        state = {"cancelled": False}

        def ready():
            fh.write(bytes(reply.readAll()))

        def progress(received: int, total: int):
            if total > 0:
                prog.setMaximum(max(1, total // 1024))
            prog.setValue(min(prog.maximum(), received // 1024))
            mb = 1024 * 1024
            prog.setLabelText(_("Güncelleme indiriliyor… {0:.1f} / {1:.1f} MB").format(
                received / mb, max(total, size, received) / mb))

        def cancel():
            state["cancelled"] = True
            reply.abort()

        def finished():
            # QProgressDialog kapanırken de canceled yayar; artık dinleme
            prog.canceled.disconnect(cancel)
            ready()
            fh.close()
            reply.deleteLater()
            self._reply = None
            ok = reply.error() == QNetworkReply.NoError and not state["cancelled"]
            if not ok and not state["cancelled"]:
                self._fail(_("İndirme başarısız:\n{0}").format(reply.errorString()))
                return
            if state["cancelled"]:
                self._close_progress()
                self._busy = False
                return
            on_done(True)

        reply.readyRead.connect(ready)
        reply.downloadProgress.connect(progress)
        reply.finished.connect(finished)
        prog.canceled.connect(cancel)

    def _downloaded(self, ok: bool, path: str, expected: str | None) -> None:
        if expected:
            self._progress.setLabelText(_("Dosya doğrulanıyor…"))
            if up.sha256_file(path) != expected:
                os.remove(path)
                self._fail(_("İndirilen dosya bozuk (SHA-256 uyuşmuyor). "
                             "Lütfen daha sonra yeniden deneyin."))
                return
        self._install(path)

    # ------------------------------------------------------------ kurulum
    def _install(self, path: str) -> None:
        kind = self.kind
        if kind == up.WIN_SETUP:
            self._close_progress()
            started = QProcess.startDetached(
                path, ["/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART",
                       "/CLOSEAPPLICATIONS", "/RELAUNCH=1"])
            if not (started[0] if isinstance(started, tuple) else started):
                self._fail(_("Kurulum başlatılamadı."))
                return
            self._quit_for_update()
        elif kind == up.MAC_APP:
            self._install_mac(path)
        elif kind == up.LINUX_PACMAN:
            self._run_installer(["pkexec", "pacman", "-U", "--noconfirm", path],
                                needs_pkexec=True)
        elif kind == up.LINUX_RUN_SYSTEM:
            self._run_installer(["pkexec", "bash", path, "--system"], needs_pkexec=True)
        elif kind == up.LINUX_RUN_USER:
            self._run_installer(["bash", path, "--user"], needs_pkexec=False)
        else:
            self._close_progress()
            self._busy = False

    def _install_mac(self, dmg: str) -> None:
        self._close_progress()
        bundle = up.mac_bundle_path(os.path.realpath(sys.executable))
        parent = os.path.dirname(bundle) if bundle else ""
        if not bundle or not os.access(parent, os.W_OK):
            # Yazma izni yoksa (ör. yönetici olmayan hesap) .dmg açılır,
            # kullanıcı uygulamayı kendisi sürükler.
            self._busy = False
            QDesktopServices.openUrl(QUrl.fromLocalFile(dmg))
            QMessageBox.information(
                self.win, _("Güncelleme"),
                _("Yeni sürüm indirildi. Açılan pencerede uygulamayı Applications "
                  "klasörüne sürükleyip eskisinin yerine koyun."))
            return
        script = os.path.join(os.path.dirname(dmg), "replace-app.sh")
        with open(script, "w", encoding="utf-8") as fh:
            fh.write(up.MAC_REPLACE_SCRIPT)
        started = QProcess.startDetached("/bin/bash", [script, str(os.getpid()), dmg, bundle])
        if not (started[0] if isinstance(started, tuple) else started):
            self._fail(_("Kurulum başlatılamadı."))
            return
        self._quit_for_update()

    def _run_installer(self, cmd: list[str], needs_pkexec: bool) -> None:
        if needs_pkexec and not shutil.which("pkexec"):
            self._close_progress()
            self._busy = False
            QMessageBox.information(
                self.win, _("Güncelleme"),
                _("Yeni sürüm indirildi ama kurulum için yönetici izni gerekiyor. "
                  "Terminalde şu komutu çalıştırın:\n\nsudo {0}").format(" ".join(cmd[1:])))
            return
        prog = self._progress
        if prog is not None:
            prog.setLabelText(_("Kuruluyor… (parola sorulabilir)"))
            prog.setRange(0, 0)
            prog.setCancelButton(None)
        proc = QProcess(self)
        proc.setProcessChannelMode(QProcess.MergedChannels)
        self._proc = proc

        def finished(code: int, _status):
            out = bytes(proc.readAll()).decode("utf-8", "replace").strip()
            self._proc = None
            self._close_progress()
            self._busy = False
            if code == 0:
                box = QMessageBox(self.win)
                box.setWindowTitle(_("Güncelleme"))
                box.setText(_("Yeni sürüm kuruldu."))
                box.setInformativeText(_("Kullanmaya başlamak için uygulama yeniden "
                                         "başlatılmalı. Şimdi yeniden başlatılsın mı?"))
                now = box.addButton(_("Şimdi yeniden başlat"), QMessageBox.AcceptRole)
                box.addButton(_("Daha sonra"), QMessageBox.RejectRole)
                box.setDefaultButton(now)
                box.exec()
                if box.clickedButton() is now:
                    self.win.restart_app()
            elif needs_pkexec and code in (126, 127):
                QMessageBox.information(self.win, _("Güncelleme"),
                                        _("Kurulum iptal edildi (yönetici izni verilmedi)."))
            else:
                box = QMessageBox(QMessageBox.Warning, _("Güncelleme"),
                                  _("Kurulum başarısız oldu (çıkış kodu {0}).").format(code),
                                  QMessageBox.Ok, self.win)
                if out:
                    box.setDetailedText(out[-4000:])
                box.exec()

        proc.finished.connect(finished)
        proc.start(cmd[0], cmd[1:])
        proc.closeWriteChannel()      # .run kurulumu soru sormasın

    # ------------------------------------------------------------ yardımcı
    def _quit_for_update(self) -> None:
        self._busy = False
        self.win._restarting = True     # kaydetme sorusu indirmeden önce soruldu
        QTimer.singleShot(0, self.win.close)

    def _close_progress(self) -> None:
        if self._progress is not None:
            self._progress.close()
            self._progress.deleteLater()
            self._progress = None

    def _fail(self, message: str) -> None:
        self._close_progress()
        self._busy = False
        QMessageBox.warning(self.win, _("Güncelleme"), message)
