from playwright.sync_api import Page
from util import retry

@retry(times=2)
def go_daewon(page: Page, id: str, pw: str) -> dict:
    """
    대원샵 로그인 + 출석 체크
    page: Playwright Page 객체
    id, pw: 계정 정보
    return: {"succeed": bool, "msg_for_return": str}
    """
    succeed = False
    msg_for_return = ""

    try:
        # 1. 메인 페이지 접속
        page.goto("https://www.daewonshop.com")
        msg_for_return += "- 대원샵 메인 진입 -\n"
        print("- 대원샵 메인 진입 -", flush=True)

        # 2. 메인 팝업 처리
        try:
            main_popup = page.locator("#main-layer-popup")
            popup_class = main_popup.get_attribute("class")
            if "active" in popup_class:
                main_popup.locator("a.close").first.click()
                msg_for_return += "대원샵 팝업 닫음\n"
                print("대원샵 팝업 닫음", flush=True)
        except:
            pass  # 팝업 없으면 무시

        # 3. 로그인 버튼 클릭
        login_btn = page.locator("ul.member-wrap #btn-login")
        if login_btn.count() > 0:
            # 새 창 열림 감지
            with page.expect_popup() as popup_info:
                login_btn.click()
            login_page = popup_info.value  # 새 창 Page 객체
            msg_for_return += "대원샵 로그인창 오픈\n"
            print("대원샵 로그인창 오픈", flush=True)

            # 3-1. 새 창에서 로그인
            login_page.locator("input#logId").wait_for(state="visible", timeout=15000)
            login_page.locator("input#logId").fill(id)

            login_page.locator("input.pw").wait_for(state="visible", timeout=15000)
            login_page.locator("input.pw").fill(pw)

            login_page.locator("#m-login").click()
            msg_for_return += "대원샵 로그인 완료\n"
            print("대원샵 로그인 완료", flush=True)

            # 3-2. 새 창 닫고 원래 페이지로 복귀
            login_page.close()
            page.bring_to_front()

        # 4. 출석체크 페이지 이동
        page.goto("https://www.daewonshop.com/cs/attend")
        msg_for_return += "대원샵 출석체크 페이지 진입\n"
        print("대원샵 출석체크 페이지 진입", flush=True)

        # 5. 출석 체크 버튼 클릭
        try:
            dw_check_btn = page.locator(".attendance-check-btn")
            dw_check_btn.wait_for(state="visible", timeout=20000)
            dw_check_btn.click()
            msg_for_return += "대원샵 출석체크 버튼 클릭\n"
            print("대원샵 출석체크 버튼 클릭", flush=True)
        except:
            msg_for_return += "대원샵 출석체크 버튼 찾기 실패\n"
            print("대원샵 출석체크 버튼 찾기 실패", flush=True)
            return {"succeed": False, "msg_for_return": msg_for_return}

        # 6. 모달 처리
        try:
            modal_content = page.locator("section.dpromotion-modal-content")
            modal_content.wait_for(state="visible", timeout=10000)

            # 6-1. 동의 체크 및 확인 버튼 클릭
            try:
                if modal_content.locator("form").count() > 0:
                    modal_content.locator(".dpromotion-agreement__item-title").click()
                    modal_content.locator(".dpromotion-modal__button.confirm").click()
            except:
                pass

            # 6-2. 결과 메시지 확인
            try:
                result_msg = modal_content.locator(".dpromotion-alert__message").inner_text()
            except:
                result_msg = modal_content.inner_text()
            msg_for_return += f"대원샵 출석체크 결과 : {result_msg}\n"
            print(f"대원샵 출석체크 결과 : {result_msg}", flush=True)

            succeed = True

            # 6-3. 모달 닫기
            try:
                modal_content.locator("button.dpromotion-modal-close").click()
            except:
                pass
        except:
            msg_for_return += "대원샵 모달 처리 실패\n"
            print("대원샵 모달 처리 실패", flush=True)

        msg_for_return += "- 대원샵 완료 -\n"
        print("- 대원샵 완료 -", flush=True)
    except Exception as e:
        msg_for_return += f"예외 발생: {e}\n"
        print(f"예외 발생: {e}", flush=True)

    return {"succeed": succeed, "msg_for_return": msg_for_return}
