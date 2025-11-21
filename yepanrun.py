from playwright.sync_api import Page
from util import retry

@retry(times=2)
def go_yepanrun(page: Page, id: str, pw: str) -> dict:
    """
    예판런 로그인 + 출석 체크
    page: Playwright Page 객체
    id, pw: 계정 정보
    return: {"succeed": bool, "msg_for_return": str}
    """
    succeed = False
    msg_for_return = "- 예판런 출석체크 시작 -\n"
    print("- 예판런 출석체크 시작 -", flush=True)

    try:
        # 1. 페이지 진입 시 뜨는 초기 alert 한 번만 자동 수락하는 이벤트 리스너 등록
        page.once("dialog", lambda d: d.accept())
        
        # 2. 출석체크 페이지 접속
        page.goto("https://yepan.run/attend/stamp.html")
        page.wait_for_load_state("domcontentloaded")
        msg_for_return += "예판런 출석체크 페이지 진입\n"
        print("예판런 출석체크 페이지 진입", flush=True)

        # 3. 로그인
        page.locator("#member_id").wait_for(state="visible", timeout=15000)
        page.locator("#member_id").fill(id)
        page.locator("#member_passwd").fill(pw)

        with page.expect_navigation(wait_until="load", timeout=15000):
            page.locator(".login__button a.btnBasic").click()

        msg_for_return += "예판런 로그인 완료\n"
        print("예판런 로그인 완료", flush=True)

        # 4. 출석체크
        check_btn = page.locator("#attendWriteForm p.ec-base-button a.btnSubmitFix")
        if not check_btn.is_visible():
            msg_for_return += "이미 출석 완료 상태라 버튼 없음\n"
            print("이미 출석 완료 상태라 버튼 없음", flush=True)
            succeed = True
        else:
            with page.expect_event("dialog") as dialog_info:
                check_btn.click()
                msg_for_return += "출석체크 버튼 클릭\n"
                print("출석체크 버튼 클릭", flush=True)

        dialog = dialog_info.value

        msg_for_return += f"예판런 출석체크 결과: {dialog.message}\n"
        print(f"예판런 출석체크 결과: {dialog.message}", flush=True)
        dialog.accept()

        # 출석 완료 버튼 존재 여부 확인
        if not page.locator("#attendWriteForm p.ec-base-button a.btnSubmitFix").first.is_visible():
            succeed = True
    except Exception as e:
        msg_for_return += f"예외 발생: {e}\n"
        print(f"예외 발생: {e}", flush=True)

    msg_for_return += "- 예판런 완료 -\n"
    print("- 예판런 완료 -", flush=True)

    return {"succeed": succeed, "msg_for_return": msg_for_return}
