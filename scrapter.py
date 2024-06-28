import os
import re

from selenium.common import NoSuchFrameException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, urljoin
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

def switch_to_frame(driver, frame_id):
    try:
        driver.switch_to.frame(frame_id)
    except NoSuchFrameException:
        pass

def save_blog_post(url):
    try:
        # Selenium을 사용하여 브라우저를 열고 페이지를 로드
        driver = webdriver.Chrome()  # 또는 다른 웹 드라이버 사용
        driver.get(url)

        # 페이지가 완전히 로드될 때까지 기다림 (20초 제한)
        wait = WebDriverWait(driver, 60)

        switch_to_frame(driver, 'mainFrame')
        print("프레임 전환완료")
        # 요소가 로드될 때까지 기다림
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'se-main-container')))
        print("요소 로드 완료")
        # 현재 페이지의 HTML 가져오기
        html = driver.page_source

        # BeautifulSoup을 사용하여 HTML 파싱
        soup = BeautifulSoup(html, 'html.parser')

        # 페이지 제목 가져오기
        title = soup.find('title').text.strip()
        print("제목 가져오기 완료")
        # 폴더 이름에서 특수 문자 및 공백 제거하여 유효한 이름으로 변환
        folder_name = re.sub(r'[^\w\s]', '', title)  # 특수 문자 제거
        folder_name = folder_name.replace(' ', '_')  # 공백을 언더스코어로 대체

        # 폴더 경로 생성
        folder_path = os.path.join(os.getcwd(), folder_name)

        # 폴더 생성
        os.makedirs(folder_path, exist_ok=True)

        # 작성일 가져오기
        publish_date_element1 = soup.find('span', class_='se_publishDate pcol2')
        publish_date_element2 = soup.find('span', class_='date')

        if publish_date_element1:
            publish_date = publish_date_element1.text.strip()
            print("작성일 가져오기 완료")
        elif publish_date_element2:
            publish_date = publish_date_element2.text.strip()
            print("작성일 가져오기 완료")
        else:
            publish_date = "작성일 가져오기 실패"
            print("작성일 실패")


        # 글 내용 저장
        content = soup.find('div', class_='se-main-container').get_text(separator='\n', strip=True)
        with open(os.path.join(folder_path, '본문.txt'), 'w', encoding='utf-8') as f:
            f.write(publish_date + "\n\n")
            f.write(content)



        # 이미지 저장
        image_elements = soup.find_all('img', class_=re.compile(r'se-image.*'))
        for img in image_elements:
            img_url = img.get('data-lazy-src') or img.get('src')
            if img_url:
                original_url = get_original_image_url(url, img_url)
                if original_url:
                    download_image(original_url, folder_path)

        # 브라우저 종료
        driver.quit()

        print("올바르게 처리되었습니다\n")

    except Exception as e:
        print(f"오류발생 : {e}")

def get_original_image_url(base_url, image_url):
    if not image_url.startswith(('http://', 'https://')):
        base_url_parts = urlparse(base_url)
        image_url = urljoin(base_url_parts.scheme + '://' + base_url_parts.netloc, image_url)
    return image_url

# 이미지 다운로드 함수
def download_image(img_url, folder_path):
    response = requests.get(img_url)
    if response.status_code == 200:
        # 이미지 파일 이름 추출
        image_name = os.path.basename(urlparse(img_url).path)
        # 이미지 저장
        with open(os.path.join(folder_path, image_name), 'wb') as f:
            f.write(response.content)


if __name__ == "__main__":
    while True:
        # 네이버 블로그 게시물 URL 입력
        blog_post_url = input("블로그 메인 URL을 입력하세요."+ "(그만 입력 하시려면 0을 입력해주세요) : ")

        if(blog_post_url == '0'):
            break

        # 블로그 게시물 저장
        save_blog_post(blog_post_url)
