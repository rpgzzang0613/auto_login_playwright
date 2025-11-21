# auto_login_playwright (대원샵, 소프라노몰, 플레이샵, 예판런 출석체크)
   
1. 파이썬 설치 (현재 패키지는 3.13.7에 맞춰져 있음)
2. 가상환경 세팅
    ```
    # MacOS 기준

    # 터미널에서 프로젝트 디렉토리로 이동
    cd 경로/auto_login_playwright

    # venv 가상환경 생성
    python -m venv .venv

    # 생성한 가상환경 활성화
    source .venv/bin/activate

    # 필요 라이브러리 설치
    pip install -r requirements.txt
    ```
    ```
    # Windows CMD 기준 (파워쉘 아님)

    # 터미널에서 프로젝트 디렉토리로 이동
    cd 경로\auto_login_playwright

    # venv 가상환경 생성
    python -m venv .venv

    # 생성한 가상환경 활성화
    .venv\Scripts\activate
    
    # 필요 라이브러리 설치
    pip install -r requirements.txt
    ```
3. auto_login 디렉토리에 ".env" 파일 만들고   
    ```
    SLACK_BOT_OAUTH_TOKEN="슬랙OAUTH키"   
    SLACK_CHANNEL="#푸쉬받을슬랙채널명"   
    DAEWON_ID="아이디"   
    DAEWON_PW="비번"   
    SOFRANO_ID="아이디"   
    SOFRANO_PW="비번"   
    PLAYSHOP_ID="아이디"   
    PLAYSHOP_PW="비번"   
    YEPANRUN_ID="아이디"   
    YEPANRUN_PW="비번"   
    ```
    써놓고 저장. SLACK 관련사항은 선택사항이므로 없으면 ""로 써놓거나 아예 항목을 없애면 됨   
   
4. 이미지에서 문자열 추출을 위한 테서렉트 설치
    ```
    # MacOS
    brew install tesseract
    ```
    윈도우는 홈페이지에서 인스톨러 받아 설치 (경로는 기본경로로 설치)
   
5. 터미널에서 main.py 실행
    ```
    python main.py
    ```
