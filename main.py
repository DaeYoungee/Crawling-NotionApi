from notion.NotionClient import get_notion_client, get_database, upsert_app_data
from crawling.VersionCheck import fetch_app_info

def main():
    # Notion 클라이언트 초기화
    notion = get_notion_client()

    # 데이터베이스 조회 또는 생성
    database_id = get_database()
    # 크롤링할 패키지 목록
    package_names = [
        "com.anydesk.anydeskandroid",
        "com.teamviewer.quicksupport.market",
    ]
    for pkg in package_names:
        app = fetch_app_info(pkg)
        upsert_app_data(notion, database_id, app)
        # add_new_row(database_id, "test.co.kr", "테스트 앱", "1.0", "2025-01-01")
'''
    

    # 각 패키지 정보 크롤링 및 Notion에 저장
    for pkg in package_names:
        print(f"\n패키지 처리 중: {pkg}")
        try:
            app_data = fetch_app_info(pkg)
            print(f"  앱 이름: {app_data['title']}")
            print(f"  버전: {app_data['version']}")
            print(f"  업데이트 날짜: {app_data['updated']}")

            upsert_app_data(notion, database_id, app_data)
        except Exception as e:
            print(f"  오류 발생: {e}")
'''

if __name__ == "__main__":
    main()
