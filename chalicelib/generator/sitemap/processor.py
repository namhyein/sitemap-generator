import logging

from chalicelib.utils.aws import BUCKET
from chalicelib.utils.database import MONGODB


from chalicelib.generator.sitemap._sitemap import SitemapGenerator
from chalicelib.utils.string import convert_timestamp_to_string, n_days_before, utc_now

from chalicelib.constant.xml import XML_ROOT
from chalicelib.settings import SERVICE_URL

def _generate_article_sitemap(articles, language=None):
    sitemap = SitemapGenerator()
    for _, article in enumerate(articles):
        images = [image["external"]["url"] for image in article["images"] if image["is_generated"]]
        if article['image'].get("thumbnail", {}).get("is_generated"):
            images.append(article['image']["thumbnail"]["url"])

        if article['published_at'].strftime("%Y-%m-%d") >= n_days_before(2):
            sitemap.append_news_node(
                f"{SERVICE_URL}/{article['category']['_id']}/{article['_id']}",
                article['published_at'].strftime("%a, %d %b %Y %H:%M:%S GMT"),
                article['name'],
                images=images,
            )
        else:
            if not article["updated_at"]:
                print(article)
            sitemap.append_url_node(
                f"{SERVICE_URL}/{article['category']['_id']}/{article['_id']}",
                convert_timestamp_to_string(article['updated_at']),
                images=images,
                language=language
            )
    sitemap.complete()
    return sitemap.to_xml()

def _generate_wine_sitemap(items, language=None):
    sitemap = SitemapGenerator()
    for item in items:
        sitemap.append_url_node(
            f"{SERVICE_URL}/wine/{item['_id']}",
            convert_timestamp_to_string(item['updated_at']),
                language=language
        )
    sitemap.complete()
    return sitemap.to_xml()

def _generate_sitemap_index(outputs):
    sitemap = SitemapGenerator(XML_ROOT.SITEMAPINDEX.value)
    for output in outputs:
        sitemap.append_sitemap_node(
            f"{SERVICE_URL}/{output}",
            utc_now()
        )

    sitemap.complete()
    return sitemap.to_xml()

def generate_article_sitemap(language=None):
    sub_categories = ["news", "ranking", "culture", "feature", "knowledge"]
    output = []
    for category in sub_categories:
        idx = 0
        skip = 0
        while True:
            articles = MONGODB.get_documents(
                "articles",
                query={"category._id": category, "status": {"$gte": 1}},
                projection={
                    "_id": 1, "name": 1, "category._id": 1, "updated_at": 1, "published_at": 1,
                    "image.thumbnail.url": 1, "image.thumbnail.is_generated": 1,
                    "images": {"$filter": {"input": "$blocks.image", "as": "blocks", "cond": {"$not": [None]}}}},
                limit=5000,
                skip=skip
            )
            logging.info(f"Fetched {len(articles)} articles for category '{category}' at skip {skip}")
            if len(articles) == 0:
                break

            sitemap = _generate_article_sitemap(articles, language)
            path = f"sitemaps/articles/{category}-{idx}.xml"
            output.append(path)

            BUCKET.put_object(path, sitemap,
                                extra_args={
                                    "ContentType": "application/xml",
                                    "ContentDisposition": f"inline; filename=articles.xml"
                                })
            logging.info(f"Uploaded sitemap for category '{category}' index {idx} to S3 at {path}")
            idx = idx + 1
            skip = skip + 5000
    
    sitemap_index = _generate_sitemap_index(output)
    BUCKET.put_object(f"sitemaps/articles.xml",
                        sitemap_index,
                        extra_args={
                            "ContentType": "application/xml",
                            "ContentDisposition": f"inline; filename=articles.xml"
                        })
    logging.info(f"Uploaded sitemap index for 'articles' to S3")

def generate_wine_sitemap(language=None):
    sub_categories = ["red", "white", "rose", "sparkling", "dessert"]
    output = []
    for category in sub_categories:
        idx = 1
        skip = 0
        while True:
            wines = MONGODB.aggregate_documents(
                "wines",
                [
                    {
                        "$match": {
                            "$and": [{"$or": [{"status": 100}, {"article_connected": True}]}, {"types._id": category}]
                        }
                    },
                    {
                        '$group': {
                            '_id': '$slug',
                            'count': {
                                '$sum': 1
                            },
                            'updated_at': {
                                '$max': '$updated_at'
                            }
                        }
                    }
                ]
            )
            logging.info(f"Fetched {len(wines)} wines for category '{category}' at skip {skip}")
            if len(wines) == 0:
                break

            sitemap = _generate_wine_sitemap(wines, language)
            path = f"sitemaps/wines/{category}-{idx}.xml"
            output.append(path)
            #save_xml_string(sitemap, f"wines_{category}_{idx}.xml")
            BUCKET.put_object(path, sitemap,
                                extra_args={
                                    "ContentType": "application/xml",
                                    "ContentDisposition": f"inline; filename=wines.xml"
                                })
            logging.info(f"Uploaded sitemap for category '{category}' index {idx} to S3 at {path}")
            idx = idx + 1
            skip = skip + 5000
            break
    sitemap_index = _generate_sitemap_index(output)
    #save_xml_string(sitemap_index, f"wines_index.xml")
    BUCKET.put_object(f"sitemaps/wines.xml", sitemap_index, extra_args={
        "ContentType": "application/xml",
        "ContentDisposition": f"inline; filename=wines.xml"
    })
    logging.info(f"Uploaded sitemap index for 'wines' to S3")
