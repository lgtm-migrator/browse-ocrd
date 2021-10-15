from typing import List, Optional, Any, Tuple, Dict, cast

from PIL.Image import Image
from ocrd import Workspace
from ocrd_modelfactory import page_from_file
from ocrd_models import OcrdFile, OcrdExif
from ocrd_models.ocrd_page import PcGtsType, PageType, MetadataType
from ocrd_utils import MIMETYPE_PAGE


class Page:
    def __init__(self, id_: str, file: OcrdFile, pc_gts: Optional[PcGtsType], image_files: List[OcrdFile],
                 images: List[Image]):
        self._id: str = id_
        self._file: OcrdFile = file
        self._pc_gts: PcGtsType = pc_gts
        # due to AlternativeImage on all hierarchy levels,
        # a physical page can have multiple images or none;
        # if it has none itself, a single image representing the page
        # is extracted from the original image and the annotation
        # of the top level
        self._image_files: List[OcrdFile] = image_files
        self._images: List[Image] = images

    @property
    def id(self) -> str:
        return self._id

    @property
    def file(self) -> OcrdFile:
        return self._file

    @property
    def pc_gts(self) -> PcGtsType:
        return self._pc_gts

    @property
    def images(self) -> List[Image]:
        return self._images

    @property
    def image_files(self) -> List[OcrdFile]:
        return self._image_files

    @property
    def page(self) -> PageType:
        return self.pc_gts.get_Page()

    @property
    def meta(self) -> MetadataType:
        return self.pc_gts.get_Metadata()


class LazyPage(Page):
    def __init__(self, id_: str, file_group: str, document: Any):
        self._id = id_
        self.file_group = file_group
        self.document = document

    @property
    def images(self) -> List[Image]:
        return [self.document.resolve_image(f) for f in self.image_files]

    @property
    def image_files(self) -> List[OcrdFile]:
        return cast(List[OcrdFile], self.document.files_for_page_id(self.id, self.file_group, mimetype="//image/.*"))

    @property
    def page_file(self) -> OcrdFile:
        page_files = self.document.files_for_page_id(self.id, self.file_group, mimetype=MIMETYPE_PAGE)
        if len(page_files) > 0:
            return page_files[0]

    @property
    def file(self) -> OcrdFile:
        if self.page_file:
            return self.page_file
        else:
            if len(self.image_files) > 0:
                return next(iter(self.image_files))

    @property
    def pc_gts(self) -> PcGtsType:
        return page_from_file(self.file)

    def get_image(self, feature_selector: str = '', feature_filter: str = '') -> Tuple[Image, Dict[str, Any], OcrdExif]:
        ws: Workspace = self.document.workspace
        try:
            page_image, page_coords, page_image_info = ws.image_from_page(self.page, self.id, transparency=True, feature_selector=feature_selector, feature_filter=feature_filter)
        except Exception:
            page_image, page_coords, page_image_info = ws.image_from_page(self.page, self.id, transparency=True)

        # print((page_coords, page_image_info))
        return page_image, page_coords, page_image_info

    """
    ViewImages.redraw
        images
        image_files[0]
        image_files[i]
        pc_gts.gds_elementtree_node_....
        id


             for i, img in enumerate(page.images if page else [None]):
                ...
                        if page.image_files[0] == page.file:
                            # PAGE-XML was created from the (first) image file directly
                            image.set_tooltip_text(page.id)
                        else:
                            img_file = page.image_files[i]
                            # get segment ID for AlternativeImage as tooltip
                            img_id = page.pc_gts.gds_elementtree_node_.xpath('//page:AlternativeImage[@filename="{}"]/../@id'.format(img_file.local_filename),namespaces=NS)
                            if img_id:
                                image.set_tooltip_text(page.id + ':' + img_id[0])
                                ...
    ViewHtml.reload
        files = self.document.files_for_page_id(self.page_id, self.use_file_group, mimetype='text/html')
        self.current = Page(self.page_id, files[0], None, [], [])

    ViewHtml.redraw
        file

        self.web_view.load_uri('file://' + str(self.document.path(self.current.file.local_filename)))

    ViewDiff.redraw
        pc_gts
                text = self.get_page_text(self.current.pc_gts)

    ViewPage.rescale
        images[0]
                img = self.current.images[0]

    ViewText.redraw
        pc_gts
                regions = self.current.pc_gts.get_Page().get_AllRegions(classes=['Text'], order='reading-order')

    ViewXml.open_jpageviewer
        file
                if self.current.file and self.current.file.mimetype == MIMETYPE_PAGE:

    ViewXml.redraw
        file
        pc_gts
            if self.current.file and self.current.file.mimetype == MIMETYPE_PAGE:
                with self.document.path(self.current.file).open('r') as f:
                    text = f.read()
            else:
                text = to_xml(self.current.pc_gts)

    DocumentTestCase.test_page_for_id_with_multiple_images_for_page_and_fileGrp
            with self.assertLogs('ocrd_browser.model.document', level='WARNING') as log_watch:
                page = doc.page_for_id('PHYS_0017', 'OCR-D-IMG-CLIP')
            self.assertIsInstance(page, Page)

    self.id: str = id_
    self.file: OcrdFile = file
    self.pc_gts: PcGtsType = pc_gts
    self.image_files: List[OcrdFile] = image_files
    self.images: List[Image] = images
    """
