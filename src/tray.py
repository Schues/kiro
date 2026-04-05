import pystray
from PIL import Image, ImageDraw


def _make_icon_image(color: str) -> Image.Image:
    """指定色の円アイコンを生成する（64x64 RGBA）。"""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 8
    draw.ellipse([margin, margin, size - margin, size - margin], fill=color)
    return img


# 監視中: 緑 / 停止中: グレー
_COLOR_WATCHING = "#22C55E"
_COLOR_STOPPED = "#9CA3AF"


class TrayApp:
    """
    Mac / Windows 共通のシステムトレイアイコン。
    pystray を daemon スレッドで動かし、tkinter の mainloop() はメインスレッドに残す。

    コールバックはすべてトレイのワーカースレッドから呼ばれる。
    tkinter 操作は on_settings / on_quit 側で root.after() を使ってスケジュールすること。
    """

    def __init__(self, on_start, on_stop, on_settings, on_quit):
        self._on_start_cb = on_start
        self._on_stop_cb = on_stop
        self._on_settings_cb = on_settings
        self._on_quit_cb = on_quit
        self._is_watching = False
        self._icon: pystray.Icon | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_detached(self) -> None:
        """トレイアイコンをバックグラウンドスレッドで起動する。"""
        self._icon = pystray.Icon(
            name="kiro",
            icon=_make_icon_image(_COLOR_STOPPED),
            title="kiro",
            menu=self._build_menu(),
        )
        self._icon.run_detached()

    def update_status(self, is_watching: bool) -> None:
        """監視状態に応じてアイコン色とメニューを更新する。スレッドセーフ。"""
        self._is_watching = is_watching
        if self._icon is None:
            return
        color = _COLOR_WATCHING if is_watching else _COLOR_STOPPED
        self._icon.icon = _make_icon_image(color)
        self._icon.title = "kiro - 監視中" if is_watching else "kiro - 停止中"
        self._icon.menu = self._build_menu()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_menu(self) -> pystray.Menu:
        status_label = "● 監視中" if self._is_watching else "○ 停止中"
        toggle_label = "停止する" if self._is_watching else "開始する"
        return pystray.Menu(
            pystray.MenuItem(status_label, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(toggle_label, self._toggle),
            pystray.MenuItem("設定を開く", self._open_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("終了", self._quit),
        )

    def _toggle(self, icon, item):
        if self._is_watching:
            self._on_stop_cb()
        else:
            self._on_start_cb()

    def _open_settings(self, icon, item):
        self._on_settings_cb()

    def _quit(self, icon, item):
        self._on_quit_cb()
        icon.stop()
