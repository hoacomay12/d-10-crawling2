import pandas as pd  # 데이터 처리 및 CSV 파일 저장을 위한 라이브러리
from bs4 import BeautifulSoup  # HTML 파싱을 위한 라이브러리
from requests import get  # HTTP 요청을 보내기 위한 라이브러리


def get_jobkorea_data(corp_name_list, page_no=1):
    """
    JobKorea 웹사이트에서 기업 정보를 크롤링하여 데이터프레임으로 반환하는 함수.
    Args:
        corp_name_list (List[str]): 검색할 기업명 리스트.
        page_no (int): 검색 결과 페이지 번호 (기본값: 1).
    Returns:
        pd.DataFrame: 크롤링된 기업 정보를 포함하는 데이터프레임.
    """
    jobkorea_data = []  # 크롤링된 데이터를 저장할 리스트
    headers = {
        # HTTP 요청에 사용할 User-Agent 헤더 설정 (브라우저처럼 보이게 함)
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    for corp_name in corp_name_list:
        # 검색 URL 생성 (기업명과 페이지 번호를 포함)
        url = f"https://www.jobkorea.co.kr/Search/?stext={corp_name}&tabType=corp&Page_No={page_no}"
        response = get(url, headers=headers)  # HTTP GET 요청을 보내고 응답 받기
        soup = BeautifulSoup(response.text, "html.parser")  # HTML 응답을 파싱

        # Flex 컴포넌트 구조에서 기업 정보를 포함하는 부분 찾기
        flex_containers = soup.find_all(
            "div",
            class_="Flex_display_flex__i0l0hl2 Flex_direction_row__i0l0hl3 Flex_justify_space-between__i0l0hlf",
        )

        # Flex 컨테이너 개수를 출력 (디버깅용)
        print(f"Found {len(flex_containers)} flex containers for {corp_name}")

        for container in flex_containers:
            # 내부 Flex 컨테이너 찾기
            inner_flex = container.find(
                "div",
                class_="Flex_display_flex__i0l0hl2 Flex_gap_space12__i0l0hls Flex_direction_row__i0l0hl3",
            )
            if not inner_flex:  # 내부 Flex 컨테이너가 없으면 건너뜀
                continue

            # span 태그에서 정보 추출
            spans = inner_flex.find_all(
                "span", class_="Typography_variant_size14__344nw27"
            )

            if len(spans) >= 3:  # 필요한 정보가 포함된 span 태그가 3개 이상인 경우
                corp_type = (
                    spans[0].get_text(strip=True) if spans[0] else None
                )  # 기업형태
                corp_location = (
                    spans[1].get_text(strip=True) if spans[1] else None
                )  # 지역
                corp_industry = (
                    spans[2].get_text(strip=True) if spans[2] else None
                )  # 업종

                # 추출된 데이터를 딕셔너리로 저장
                jobkorea_data.append(
                    {
                        "기업형태": corp_type,
                        "지역": corp_location,
                        "업종": corp_industry,
                    }
                )

                # 추출된 데이터를 출력 (디버깅용)
                print(f"추출된 데이터: {corp_type}, {corp_location}, {corp_industry}")
            else:
                # span 태그가 부족한 경우 경고 메시지 출력
                print(f"정보가 충분하지 않음: {len(spans)} 개의 span 태그 발견")

    # 크롤링된 데이터를 데이터프레임으로 변환하여 반환
    return pd.DataFrame(jobkorea_data)


if __name__ == "__main__":
    """
    메인 실행 코드: 테스트용으로 기업명을 '벡스인텔리전스'로 설정하여 크롤링 수행.
    """
    # 테스트용 기업명 리스트
    corp_name_list = ["벡스인텔리전스"]

    # 실제 사용 시: CSV 파일에서 기업명 리스트를 불러올 수 있음
    # corp_name_list = pd.read_csv("../../enterprise_df_10k.csv")["기업명"].unique().tolist()

    # 데이터 수집
    test_data = get_jobkorea_data(corp_name_list)

    # 결과를 CSV 파일로 저장
    test_data.to_csv("jobkorea_test_data.csv", index=False, encoding="utf-8-sig")

    # 결과 출력
    print(test_data.head())
