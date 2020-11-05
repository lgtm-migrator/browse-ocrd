from gi.repository import GObject, Gtk, WebKit2

from typing import Optional, Tuple, Any

from ocrd_browser.view import View
from ocrd_browser.view.base import FileGroupSelector, FileGroupFilter
from ocrd_browser.model import Page

GObject.type_register(WebKit2.WebView)


class ViewHtml(View):
    """
    A view of the HTML+CSS annotation (as produced by ocrd-dinglehopper reports).
    """

    label = 'HTML'

    def __init__(self, name: str, window: Gtk.Window):
        super().__init__(name, window)
        self.file_group: Tuple[Optional[str], Optional[str]] = (None, 'text/html')
        # noinspection PyTypeChecker
        self.web_view: WebKit2.WebView = None

    def build(self) -> None:
        super().build()
        self.add_configurator('file_group', FileGroupSelector(FileGroupFilter.HTML))

        self.web_view = WebKit2.WebView()

        self.scroller.add(self.web_view)

    @property
    def use_file_group(self) -> str:
        return self.file_group[0]

    def config_changed(self, name: str, value: Any) -> None:
        super().config_changed(name, value)
        self.reload()

    def reload(self) -> None:
        files = self.document.files_for_page_id(self.page_id, self.use_file_group, mimetype='text/html')
        if files:
            self.current = Page(self.page_id, files[0], None, [], [])
        self.redraw()

    def redraw(self) -> None:
        if self.current:
            self.web_view.set_tooltip_text(self.page_id)
            self.web_view.load_uri('file://' + str(self.document.path(self.current.file.local_filename)))
            self.web_view.show()
