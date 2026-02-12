from google_play_scraper import app
from datetime import datetime
from pprint import pprint


def fetch_app_info(package_name: str) -> dict:
    """Google Play Store에서 앱 정보 크롤링"""
    result = app(package_name, lang="ko", country="kr")

    # 타임스탬프를 ISO 형식 날짜로 변환
    timestamp = result.get("updated", 0)
    updated_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

    return {
        "package_name": package_name,
        "title": result.get("title", ""),
        "version": result.get("version", ""),
        "updated": updated_date,
    }
