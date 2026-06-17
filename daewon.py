from playwright.sync_api import Page

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
        # 1. 출석체크 페이지 접속
        page.goto("https://www.popcondplay.com/event/attend")
        msg_for_return += "- 대원샵 출석체크 진입 -\n"
        print("- 대원샵 출석체크 진입 -", flush=True)

        # 2. 출석체크 버튼 클릭
        login_btn = page.locator(".attendance_calendar .btn-login")
        if login_btn.count() > 0:
            # 새 창 열림 감지
            with page.expect_popup() as popup_info:
                login_btn.click()

            login_page = popup_info.value  # 새 창 Page 객체
            msg_for_return += "대원샵 로그인창 오픈\n"
            print("대원샵 로그인창 오픈", flush=True)

            # 3-1. 새 창에서 로그인
            login_page.locator("#loginForm input#logId").wait_for(state="visible", timeout=15000)
            login_page.locator("#loginForm input#logId").fill(id)

            login_page.locator("#loginForm input.pw").wait_for(state="visible", timeout=15000)
            login_page.locator("#loginForm input.pw").fill(pw)

            login_page.locator("#loginForm .membership_btn").click()

            # 로그인 처리 및 쿠키 반영 전에 팝업을 닫는 문제 방지
            try:
                login_page.wait_for_event("close", timeout=15000)
            except:
                # 자동으로 안 닫히는 경우도 있을 수 있으므로 무시
                pass

            msg_for_return += "대원샵 로그인 완료\n"
            print("대원샵 로그인 완료", flush=True)

            # 3-2. 새 창 닫고 원래 페이지로 복귀
            login_page.close()
            page.bring_to_front()

            # 3-3. 출석체크 상태 확인
            page.wait_for_timeout(7000)
            complete_btn = page.locator(".attendance_calendar .att-button a.is-complete")

            if complete_btn.count() > 0:
                # 이미 출석체크가 완료된 경우 버튼 클릭/alert 대기 없이 종료
                msg_for_return += "대원샵 출석체크 결과 : *이미 출석체크 완료*\n"
                print("대원샵 출석체크 결과 : 이미 출석체크 완료", flush=True)
            else:
                # 출석체크가 아직 완료되지 않은 경우 기존 출석체크 버튼 클릭
                attend_btn = page.locator(".attendance_calendar #btn-attend")
                attend_btn.wait_for(state="visible", timeout=15000)

                with page.expect_event("dialog", timeout=10000) as dialog_info:
                    attend_btn.click()
                    msg_for_return += "대원샵 출석체크 버튼 클릭\n"
                    print("대원샵 출석체크 버튼 클릭", flush=True)

                dialog = dialog_info.value

                msg_for_return += f"대원샵 출석체크 결과 : *{dialog.message}*\n"
                print(f"대원샵 출석체크 결과 : {dialog.message}", flush=True)

                # dialog.accept()로 navigation이 항상 발생한다고 보장할 수 없으므로 분리
                dialog.accept()

            succeed = True

            msg_for_return += "- 대원샵 완료 -\n"
            print("- 대원샵 완료 -", flush=True)
        else:
            msg_for_return += "대원샵 출석체크 버튼 못찾음. 페이지 확인 필요\n"
            print("대원샵 출석체크 버튼 못찾음. 페이지 확인 필요", flush=True)
    except Exception as e:
        msg_for_return += f"예외 발생: {e}\n"
        print(f"예외 발생: {e}", flush=True)

    return {"succeed": succeed, "msg_for_return": msg_for_return}
