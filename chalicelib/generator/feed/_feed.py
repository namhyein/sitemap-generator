from xml.dom import minidom

from chalicelib.constant.xml import XML_ROOT, XMLNS, SCHEMA
from chalicelib.utils.string import cleanse_loc, utc_now, cleanse_image_url


class FeedGenerator:
    def __init__(self, title=None, description=None, link=None, feed=None, language="en-US"):
        self._doc = minidom.Document()
        if title and description and link and feed:
            self._root = self._initialize(title, description, link, feed, language)
        else:
            self._root = None
            
    def from_existing_feed(self, feed):
        self.doc = minidom.parseString(feed)
        channels = feed.getElementsByTagName("channel")
        if not channels:
            raise ValueError("Invalid RSS feed: 'channel' element not found.")
        channel = channels[0]

        for node in list(channel.childNodes):
            if node.nodeType == node.TEXT_NODE and node.nodeValue.strip() == "":
                channel.removeChild(node)
        
        self.root = channel

    def _initialize(self, title, description, link, feed, language):
        channel = self._doc.createElement("channel")
        channel.setAttribute(XMLNS.CONTENT.value, SCHEMA.CONTENT.value)

        channel.appendChild(self.cdata("title", title))
        channel.appendChild(self.cdata("description", description))
        channel.appendChild(self.textnode("link", cleanse_loc(link)))

        image = self._doc.createElement("image")
        image.appendChild(self.cdata("title", title))
        image.appendChild(self.textnode("link", cleanse_loc(link)))
        image.appendChild(self.textnode("url", cleanse_image_url("/favicon/favicon.png")))
        channel.appendChild(image)

        atom = self._doc.createElement("atom:link")
        atom.setAttribute("rel", "self")
        atom.setAttribute("type", "application/rss+xml")
        atom.setAttribute("href", cleanse_loc(feed))
        channel.appendChild(atom)

        channel.appendChild(self.cdata("language", language))
        channel.appendChild(self.textnode("lastBuildDate", utc_now("%a, %d %b %Y %H:%M:%S GMT")))

        return channel

    def cdata(self, tag, text):
        node = self._doc.createElement(tag)
        node.appendChild(self._doc.createCDATASection(text))

        return node

    def textnode(self, tag, text):
        node = self._doc.createElement(tag)
        node.appendChild(self._doc.createTextNode(text))

        return node

    def __generate_description(self, description, image):
        div = self._doc.createElement("div")

        img = self._doc.createElement("img")
        img.setAttribute("src", image)
        img.setAttribute("style", "width: 100%;")
        div.appendChild(img)
        div.appendChild(self.textnode("p", description))
        return div

    def append_feed(self, title, description, loc, lastmod, image):
        item = self._doc.createElement("item")
        item.appendChild(self.cdata("title", title))
        item.appendChild(self.textnode("link", loc))

        div = self.__generate_description(description, image)
        item.appendChild(self.cdata("description", div.toxml()))

        item.appendChild(self.cdata("dc:creator", "VEENOVERSE"))
        item.appendChild(self.textnode("pubDate", lastmod))

        guid = self.textnode("guid", loc)
        guid.setAttribute("isPermaLink", "false")
        item.appendChild(guid)

        media = self._doc.createElement("media:content")
        media.setAttribute("url", image)
        media.setAttribute("medium", "image")
        item.appendChild(media)

        self._root.appendChild(item)

    def complete(self):
        rss = self._doc.createElement(XML_ROOT.RSS.value)
        rss.setAttribute("version", "2.0")
        rss.setAttribute(XMLNS.DC.value, SCHEMA.DC.value)
        rss.setAttribute(XMLNS.ATOM.value, SCHEMA.ATOM.value)
        rss.setAttribute(XMLNS.MEDIA.value, SCHEMA.MEDIA.value)
        rss.appendChild(self._root)
        self._doc.appendChild(rss)

    def to_xml(self):
        xml_str = self._doc.toprettyxml(indent="  ", encoding="UTF-8").decode("UTF-8")
        # 빈 줄 제거
        xml_str = "\n".join([line for line in xml_str.split("\n") if line.strip()])
        return xml_str

    def save_xml(self, name):
        with open(name, mode="w", encoding="utf-8") as f:
            f.write(self.to_xml())
