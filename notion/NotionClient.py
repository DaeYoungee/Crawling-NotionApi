import os
from dotenv import load_dotenv
import requests
from notion_client import Client

# .env 파일에서 환경변수 로드
load_dotenv()

# Notion 설정
NOTION_TOKEN = os.getenv("NOTION_KEY")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")  # DB를 생성할 상위 페이지 ID
DATABASE_TITLE = "앱 버전 관리"

def get_notion_client():
    """Notion 클라이언트 생성"""
    if not NOTION_TOKEN:
        raise ValueError("NOTION_TOKEN 환경변수가 설정되지 않았습니다.")
    return Client(auth=NOTION_TOKEN)

def find_database(notion: Client, page_id: str, DB_title: str) -> str | None:
    # notion.pages.create
    print(f"find Database")
    url = "https://api.notion.com/v1/blocks/" + page_id + "/children"

    headers = {
        "Notion-Version": "2025-09-03",
        "Authorization": "Bearer " + notion
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    # 블록들 중 'child_database' 타입만 추출
    databases = [
        {
            "db_id": block["id"],
            "title": block["child_database"]["title"]
        }
        for block in data.get("results", [])
        if block["type"] == "child_database"
    ]

    for db in databases:
        if db["title"] == DB_title:
            print(f"DB 찾음, title: {db['title']}, ID: {db['db_id']}")
            return db["db_id"]
    return None


def create_database(notion: Client, page_id: str, DBTitle: str) -> str:
    print(f"create Database, PageId: {page_id}")
    url = "https://api.notion.com/v1/databases"

    payload = {
        "parent": {
            "type": "page_id",
            "page_id": "2fd00eea388f8029878ee2c4abc3a7fc"
        },
        "title": [
            {
                "text": {
                    "content": DBTitle,
                    # "link": { "url": "<string>" }
                },
                "annotations": {
                    "bold": True,
                    "italic": True,
                    "strikethrough": True,
                    "underline": True,
                    "code": True,
                    "color": "default"
                },
                # "type": "<string>"
            }
        ],
        "description": [
            {
                "text": {
                    "content": "설명",
                    # "link": { "url": "<string>" }
                },
                "annotations": {
                    "bold": True,
                    "italic": True,
                    "strikethrough": True,
                    "underline": True,
                    "code": True,
                    "color": "default"
                },
                # "type": "<string>"
            }
        ],
        "is_inline": True,
        "initial_data_source": {
            "properties": {
                "package": {
                    "title": {}  # 첫 번째 컬럼 (반드시 title 타입 필요)
                },
                "AppName": {
                    "rich_text": {} # 텍스트 컬럼
                },
                "version": {
                    "rich_text": {} # 텍스트 컬럼
                },
                "update": {
                    "rich_text": {} # 텍스트 컬럼
                }
            }
        },
        # "icon": {
        #     "file_upload": { "id": "<string>" },
        #     "type": "<string>"
        # },
        # "cover": {
        #     "file_upload": { "id": "<string>" },
        #     "type": "<string>"
        # }
    }
    headers = {
        "Notion-Version": "2025-09-03",
        "Authorization": "Bearer " + notion,
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
    return response.json()["id"]


def add_new_row(db_id: str, package_val: str, app_name: str, version_val: str, update_val: str):
    url = "https://api.notion.com/v1/pages"
    
    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json"
    }

    payload = {
        "parent": { "database_id": db_id },
        "properties": {
            # 1. title 타입 (package 컬럼)
            "package": {
                "title": [
                    { "text": { "content": package_val } }
                ]
            },
            # 2. rich_text 타입 (AppName 컬럼)
            "AppName": {
                "rich_text": [
                    { "text": { "content": app_name } }
                ]
            },
            # 3. rich_text 타입 (version 컬럼)
            "version": {
                "rich_text": [
                    { "text": { "content": version_val } }
                ]
            },
            # 4. rich_text 타입 (update 컬럼)
            "update": {
                "rich_text": [
                    { "text": { "content": update_val } }
                ]
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ 데이터 추가 성공: {app_name}")
        return response.json()["id"]
    else:
        print(f"❌ 데이터 추가 실패: {response.text}")
        return None


def get_database() -> str:
    """데이터베이스 조회 또는 생성"""
    if not NOTION_PAGE_ID:
        raise ValueError("NOTION_PAGE_ID 환경변수가 설정되지 않았습니다.")
    
    db_id = find_database(NOTION_TOKEN, NOTION_PAGE_ID, DATABASE_TITLE)
    if db_id is None:
        db_id = create_database(NOTION_TOKEN, NOTION_PAGE_ID, DATABASE_TITLE)
        
    return db_id

def find_page_by_package_name(notion: Client, database_id: str, package_name: str) -> str | None:
    """패키지명으로 기존 페이지 찾기"""
    results = notion.data_sources.query(
        data_source_id=database_id,
        filter={"property": "package", "title": {"equals": package_name}},
    )
    print(f"find_page_by_package_name: {results}")
    if results["results"]:
        return results["results"][0]["id"]
    return None

def upsert_app_data(notion: Client, database_id: str, app_data: dict) -> None:
    """DB 튜플 삽입 또는 업데이트"""
    package_name = app_data["package_name"]
    existing_page_id = find_page_by_package_name(notion, database_id, package_name)

    properties = {
        "package": {"title": [{"text": {"content": package_name}}]},
        "AppName": {"rich_text": [{"text": {"content": app_data["title"]}}]},
        "version": {"rich_text": [{"text": {"content": app_data["version"]}}]},
        "update": {"rich_text": [{"text": {"content": app_data["updated"]}}]},
    }

    if existing_page_id:
        # 기존 페이지 업데이트
        notion.pages.update(page_id=existing_page_id, properties=properties)
        print(f"[업데이트] {package_name}")
    else:
        # 신규 페이지 생성
        notion.pages.create(parent={"database_id": database_id}, properties=properties)
        print(f"[신규 추가] {package_name}")