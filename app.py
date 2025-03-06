from chalicelib.generator import ArticleFeedGenerator
from chalicelib.generator.sitemap.processor import generate_article_sitemap, generate_wine_sitemap

from chalice import Chalice, Rate

app = Chalice(app_name='wineandnews-sitemap-api')

LANGUAGE = ["en", "ko", "ja"]
@app.schedule(Rate(1, unit=Rate.DAYS))
def daily_update_sitemaps_article(event):
    generate_article_sitemap()
    return {"status": "success"}

@app.schedule(Rate(1, unit=Rate.DAYS))
def daily_update_sitemaps(event):
    generate_wine_sitemap(["en", "ko", "ja"])
    return {"status": "success"}


# Feed Udpate
@app.schedule(Rate(1, unit=Rate.DAYS))
def daily_upate_total_feed(event):
    ArticleFeedGenerator().process()
    return {"status": "success"}

@app.schedule(Rate(1, unit=Rate.DAYS))
def daily_upate_news_feed(event):
    ArticleFeedGenerator().process("news")
    return {"status": "success"}

@app.schedule(Rate(1, unit=Rate.DAYS))
def daily_upate_ranking_feed(event):
    ArticleFeedGenerator().process("ranking")
    return {"status": "success"}

@app.schedule(Rate(1, unit=Rate.DAYS))
def daily_upate_culture_feed(event):
    ArticleFeedGenerator().process("culture")
    return {"status": "success"}

@app.schedule(Rate(1, unit=Rate.DAYS))
def daily_upate_knowledge_feed(event):
    ArticleFeedGenerator().process("culture")
    return {"status": "success"}