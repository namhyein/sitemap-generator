from xml.dom import minidom

from chalicelib.constant.xml import XML_ROOT, XMLNS, SCHEMA
from chalicelib.settings import SERVICE_URL


class SitemapGenerator:
    def __init__(self, root=XML_ROOT.URLSET.value):
        self.doc = minidom.Document()
        self.root = self.doc.createElement(root)
        self.root.setAttribute(XMLNS.DEFAULT.value, SCHEMA.ROOT.value)

    def is_image_sitemap(self):
        return self.root.getAttribute(XMLNS.IMAGE.value) != ""

    def is_news_sitemap(self):
        return self.root.getAttribute(XMLNS.NEWS.value) != ""

    def is_video_sitemap(self):
        return self.root.getAttribute(XMLNS.VIDEO.value) != ""

    def is_html_sitemap(self):
        return self.root.getAttribute(XMLNS.XHTML.value) != ""

    def add_news_schema(self):
        self.root.setAttribute(XMLNS.NEWS.value, SCHEMA.NEWS.value)

    def add_image_schema(self):
        self.root.setAttribute(XMLNS.IMAGE.value, SCHEMA.IMAGE.value)

    def add_video_schema(self):
        self.root.setAttribute(XMLNS.VIDEO.value, SCHEMA.VIDEO.value)

    def add_html_schema(self):
        self.root.setAttribute(XMLNS.XHTML.value, SCHEMA.XHTML.value)

    def __generate_text_node(self, tag, text, attributes=None):
        if attributes is None:
            attributes = {}

        node = self.doc.createElement(tag)
        for key, value in attributes.items():
            node.setAttribute(key, value)

        node.appendChild(self.doc.createTextNode(text))

        return node

    def __generate_news_node(self, name, lastmod):
        news = self.doc.createElement("news:news")
        news.appendChild(self.__generate_text_node("news:title", name))
        news.appendChild(self.__generate_text_node("news:publication_date", lastmod))

        pub = self.doc.createElement("news:publication")
        pub.appendChild(self.__generate_text_node("news:name", name))
        pub.appendChild(self.__generate_text_node("news:language", "en"))
        news.appendChild(pub)

        return news

    def __generate_image_node(self, src):
        image = self.doc.createElement("image:image")
        image.appendChild(self.__generate_text_node("image:loc", src))

        return image

    def append_sitemap_node(self, loc, lastmod):
        url = self.doc.createElement("sitemap")
        url.appendChild(self.__generate_text_node("loc", loc))
        url.appendChild(self.__generate_text_node("lastmod", lastmod))

        self.root.appendChild(url)

    def append_url_node(self, loc, lastmod, images=None, language=None):
        if images is None:
            images = []

        if language is None:
            language = []

        if images and not self.is_image_sitemap():
            self.add_image_schema()

        if language and not self.is_html_sitemap():
            self.add_html_schema()

        url = self.doc.createElement("url")
        url.appendChild(self.__generate_text_node("loc", loc))
        url.appendChild(self.__generate_text_node("lastmod", lastmod))

        for lang in language:
            url.appendChild(self.__generate_text_node("xhtml:link", loc.replace(SERVICE_URL, f"{SERVICE_URL}/{lang}") if lang != "en" else loc, {"rel": "alternate", "hreflang": lang}))

        for image in images:
            url.appendChild(self.__generate_image_node(image))

        self.root.appendChild(url)

    def append_news_node(self, loc, lastmod, name, images=None):
        if images is None:
            images = []

        if not self.is_news_sitemap():
            self.add_news_schema()
        if images and not self.is_image_sitemap():
            self.add_image_schema()

        url = self.doc.createElement("url")
        url.appendChild(self.__generate_text_node("loc", loc))
        url.appendChild(self.__generate_news_node(name, lastmod))

        for image in images:
            url.appendChild(self.__generate_image_node(image))

        url.appendChild(self.__generate_text_node("lastmod", lastmod))
        self.root.appendChild(url)

    def complete(self):
        self.doc.appendChild(self.root)

    def to_xml(self):
        return self.doc.toprettyxml(encoding="UTF-8").decode()

    def save_xml(self, name):
        with open(name, mode="w", encoding="utf-8") as f:
            f.write(self.to_xml())
            f.close()
