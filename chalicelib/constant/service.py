from enum import Enum


class COLLECTION(Enum):
    ARTICLE = "articles"
    WINE = "wines"


class CATEGORY(Enum):
    NEWS = "news"
    RANKING = "ranking"
    CULTURE = "culture"
    FEATURE = "feature"
    KNOWLEDGE = "knowledge"


class WINE(Enum):
    RED = "red"
    ROSE = "rose"
    WHITE = "white"
    DESSERT = "dessert"
    SPARKLING = "sparkling"
