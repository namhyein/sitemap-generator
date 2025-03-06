import logging

from chalicelib.utils.aws import BUCKET
from chalicelib.utils.database import MONGODB

from chalicelib.generator.feed import FeedGenerator
from chalicelib.utils.string import utc_now
from chalicelib.settings import SERVICE_URL


class ArticleFeedGenerator(FeedGenerator):
    def load_existing_feed(self, category):
        raw = BUCKET.get_object(f"/{category}/feed")
        self.from_existing_feed(raw)

    def get_or_create_feed(self, category):
        if BUCKET.head_object():
            return self.load_existing_feed()

        meta = MONGODB.get_document(
            "metas",
            query={"_id": f"/{category}" if category else "/"}
        )
        self._initalize(
            meta["title"], meta["description"], f"https://{SERVICE_URL}", f"https://{SERVICE_URL}/{category}" 
        )

    def update_feed_with_new_articles(self, category, articles):
        """
        기존 피드를 가져와 새로운 아티클을 추가하고, 업데이트된 피드를 S3에 업로드합니다.
        """
        try:
            self.get_or_create_feed(category)
            for article in articles:
                self.append_feed(
                    article["name"],
                    article["meta"]["description"],
                    f"https://{SERVICE_URL}/{category}/{article['_id']}",
                    article['published_at'].strftime("%a, %d %b %Y %H:%M:%S GMT"),
                    article['image']['thumbnail']['url']
                )

            MONGODB.update_documents(
                "articles",
                {"_id": {"$in": [article['_id'] for article in articles]}},
                {"$set": {"feed_updated": utc_now("%a, %d %b %Y %H:%M:%S GMT")}}
            )
    
        except Exception as e:
            logging.error(f"Failed to update feed '{category}': {e}")

    def process(self, category=None):
        try:
            if not category:
                query = {"status": {"$gte": 1}, "feed_updated": {"$exists": False}}
            else:
                query = {"status": {"$gte": 1}, "category._id": category, "subfeed_updated": {"$exists": False}}
    
            new_articles = MONGODB.get_documents(
                "articles",
                query=query,
                projection={
                    "_id": 1,
                    "name": 1,
                    "category._id": 1,
                    "updated_at": 1,
                    "published_at": 1,
                    "image.thumbnail.url": 1,
                    "image.thumbnail.is_generated": 1,
                    "meta.description": 1,
                    "meta.title": 1,
                    "images": {"$filter": {"input": "$blocks.image", "as": "blocks", "cond": {"$not": [None]}}}}
            )

            if not new_articles:
                raise Exception()
            
            self.update_feed_with_new_articles(category, new_articles)

        except Exception as e:
            logging.error(f"Error processing category '{category}': {e}")
