from bs4 import BeautifulSoup
from app.database import get_async_db
from app.models import Article
from app.insights.schemas import NewsItem
from pydantic import ValidationError
from loguru import logger
from datetime import datetime
from app.main import settings
from sqlalchemy import delete
import requests
import re


def send_request(url: str, retry_times: int = 5) -> str:
    payload = {
        'api_key': settings.SCRAPER_API_KEY,
        'url': url
    }

    for _ in range(retry_times):
        try:
            resp = requests.get(settings.SCRAPER_API_URL, params=payload, timeout=15)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            logger.debug(f"Could not send request: {str(e)}")
            continue
    return ""


def to_full_image_url(url: str) -> str:
    dash = url.rfind("-")
    dot = url.rfind(".")
    
    return url[:dash+1] + "scaled" + url[dot:]


def extract_article_content_EN(url: str) -> str:
    html = send_request(url)
    soup = BeautifulSoup(html, "html.parser")

    content_div = soup.find("div", class_="td-post-content")
    if not content_div:
        return ""

    featured = content_div.find(class_="td-post-featured-image")
    if featured:
        featured.decompose()

    for el in content_div.find_all(id=lambda i: i and i.startswith("cp_popup")):
        el.decompose()

    return str(content_div).replace("\xa0", " ")


def get_daily_news_EN():
    html = send_request(f"https://fintech.global/{str(datetime.utcnow().year)}")
    soup = BeautifulSoup(html, "html.parser")

    modules = soup.find_all("div", class_=re.compile(r"td_module"), limit=10)
    results = []

    for mod in modules:
        thumb_div = mod.find("div", class_="td-module-thumb")
        details_div = mod.find("div", class_="item-details")
        time_tag = mod.find("time")
        excerpt_tag = mod.find("div", class_="td-excerpt")
        if not thumb_div or not details_div or not time_tag or not excerpt_tag:
            continue

        a_tag = thumb_div.find("a")
        img_tag = thumb_div.find("img")

        article_url = a_tag["href"] if a_tag and a_tag.has_attr("href") else None
        thumbnail = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

        title_tag = details_div.find("a")
        title = title_tag.get_text(strip=True) if title_tag else None

        content = extract_article_content_EN(article_url) if article_url else None

        date = time_tag.get_text(strip=True)
        excerpt = excerpt_tag.get_text(strip=True)

        results.append({
            "url": article_url,
            "thumbnail": thumbnail,
            "image": to_full_image_url(thumbnail),
            "title": title,
            "content": content,
            "date": date,
            "excerpt": excerpt,
            "lang": "EN"
        })

    return results


def extract_article_content_UA(url: str) -> str:
    html = send_request(url)
    soup = BeautifulSoup(html, "html.parser")

    content = soup.find("div", class_="content-spacious")
    if not content:
        return ""

    for div in content.find_all("div", class_="wp-block-image"):
        div.decompose()

    for a in content.find_all("a", class_="adc"):
        a.decompose()

    return str(content).replace("\xa0", " ").replace("\n", "")


def get_daily_news_UA():
    html = send_request("https://fintechinsider.com.ua/category/vsi-novyny/")
    soup = BeautifulSoup(html, "html.parser")

    articles = soup.find_all("article", class_="grid-base-post", limit=10)

    results = []

    for art in articles:
        item = {}

        media_div = art.find("div", class_="media")
        content_div = art.find("div", class_="content")

        if not media_div or not content_div:
            continue

        a_tag = media_div.find("a")
        if not a_tag:
            continue

        item["url"] = a_tag.get("href")
        item["title"] = a_tag.get("title")

        span_tag = a_tag.find("span")
        item["thumbnail"] = span_tag.get("data-bgsrc") if span_tag else None

        excerpt_div = content_div.find("div", class_="excerpt")
        item["excerpt"] = excerpt_div.get_text(strip=True) if excerpt_div else None

        time_tag = content_div.find("time", class_="post-date")
        item["date"] = time_tag.get_text(strip=True) if time_tag else None

        item["image"] = to_full_image_url(item["thumbnail"]) if item.get("thumbnail") else None
        item["content"] = extract_article_content_UA(item["url"]) if item.get("url") else None
        item["lang"] = "UA"

        results.append(item)

    return results


async def delete_all_articles():
    async for db in get_async_db():
        try:
            await db.execute(delete(Article))
            await db.commit()
        finally:
            await db.close()
        break


async def save_news_items(news_items: list):
    async for db in get_async_db():
        try:
            for item in news_items:
                db_item = Article(**item)
                db.add(db_item)
            await db.commit()
        finally:
            await db.close()
        break


def validate_items(raw_items: list[dict]) -> list[NewsItem]:
    validated = []
    for item in raw_items:
        try:
            news_item = NewsItem(**item)
            validated.append(item)
        except ValidationError:
            continue
    return validated


async def collect_news():
    logger.debug(f"Trying to collect news at {datetime.utcnow()}")

    await delete_all_articles()

    validated_EN = validate_items(get_daily_news_EN())
    validated_UA = validate_items(get_daily_news_UA())

    await save_news_items(validated_EN + validated_UA)

    


