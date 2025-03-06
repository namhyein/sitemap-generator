from enum import Enum


class XML_ROOT(Enum):
    RSS = "rss"
    URLSET = "urlset"
    SITEMAPINDEX = "sitemapindex"


class XMLNS(Enum):
    DEFAULT = "xmlns"
    NEWS = "xmlns:news"
    IMAGE = "xmlns:image"
    VIDEO = "xmlns:video"
    XHTML = "xmlns:xhtml"
    ATOM = "xmlns:atom"
    DC = "xmlns:dc"
    MEDIA = "xmlns:media"
    CONTENT = "xmlns:content"


class SCHEMA(Enum):
    ROOT = "http://www.sitemaps.org/schemas/sitemap/0.9"
    NEWS = "http://www.google.com/schemas/sitemap-news/0.9"
    IMAGE = "http://www.google.com/schemas/sitemap-image/1.1"
    VIDEO = "http://www.google.com/schemas/sitemap-video/1.1"
    XHTML = "http://www.w3.org/1999/xhtml"
    ATOM = "http://www.w3.org/2005/Atom"
    DC = "http://purl.org/dc/elements/1.1/"
    MEDIA = "http://search.yahoo.com/mrss/"
    CONTENT = "http://purl.org/rss/1.0/modules/content/"
