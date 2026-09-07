from playwright.sync_api import Page

def go_playshop(page: Page, id: str, pw: str) -> dict:
    """
    플레이샵 로그인 + 출석 체크
    page: Playwright Page 객체
    id, pw: 계정 정보
    return: {"succeed": bool, "msg_for_return": str}
    """
    succeed = False
    msg_for_return = "- 플레이샵 출석체크 시작 -\n"
    print("- 플레이샵 출석체크 시작 -", flush=True)

    try:
        # 1. 페이지 진입 시 뜨는 초기 alert 한 번만 자동 수락
        page.once("dialog", lambda d: d.accept())

        # 2. 출석체크 페이지 접속
        page.goto("https://playshop.co.kr/attend/stamp.html")
        page.wait_for_load_state("domcontentloaded")
        msg_for_return += "플레이샵 출석체크 페이지 진입\n"
        print("플레이샵 출석체크 페이지 진입", flush=True)

        # 3. 로그인
        # 새 로그인 위젯은 기존 ID가 있는 폼을 숨기고, ID 없이 같은 name을 사용한다.
        # :visible로 실제 사용자에게 표시되는 입력란만 선택한다.
        page.locator('input[name="member_id"]:visible').fill(id)
        page.locator('input[name="member_passwd"]:visible').fill(pw)

        login_btn = page.locator(
            "#normalLogin_id button.loginBtn:visible, .login .login__button a:visible"
        ).filter(has_text="기존 회원 로그인")

        with page.expect_navigation(wait_until="load", timeout=15000):
            login_btn.click()

        page.wait_for_load_state("domcontentloaded")

        msg_for_return += "플레이샵 로그인 완료\n"
        print("플레이샵 로그인 완료", flush=True)

        if "change_passwd.html" in page.url:
            msg_for_return += "출석체크 페이지가 아니라 비밀번호 변경 페이지에 진입\n"
            print("출석체크 페이지가 아니라 비밀번호 변경 페이지에 진입")

            form = page.locator("#changePasswdForm")
            form.locator("a:has-text('다음에 변경')").click()

            page.goto("https://playshop.co.kr/attend/stamp.html")
            page.wait_for_load_state("domcontentloaded")
            msg_for_return += "플레이샵 출석체크 페이지 다시 진입\n"
            print("플레이샵 출석체크 페이지 다시 진입", flush=True)

        # 4. 출석체크
        check_btn = page.locator("#attendWriteForm a.btnSubmitFix").first

        try:
            check_btn.wait_for(state="visible", timeout=5000)
            button_exists = True
        except:
            button_exists = False

        if not button_exists:
            msg_for_return += "이미 출석 완료 상태라 버튼 없음\n"
            print("이미 출석 완료 상태라 버튼 없음", flush=True)
            succeed = True
        else:
            with page.expect_event("dialog", timeout=10000) as dialog_info:
                check_btn.click()
                msg_for_return += "출석체크 버튼 클릭\n"
                print("출석체크 버튼 클릭", flush=True)

            dialog = dialog_info.value

            msg_for_return += f"플레이샵 출석체크 결과 : *{dialog.message}*\n"
            print(f"플레이샵 출석체크 결과 : {dialog.message}", flush=True)
            dialog.accept()

            # 출석 완료 버튼 존재 여부 확인
            if not page.locator("#attendWriteForm a.btnSubmitFix").first.is_visible():
                succeed = True
    except Exception as e:
        msg_for_return += f"예외 발생: {e}\n"
        print(f"플레이샵 예외 발생: {e}", flush=True)

    msg_for_return += "- 플레이샵 완료 -\n"
    print("- 플레이샵 완료 -", flush=True)

    return {"succeed": succeed, "msg_for_return": msg_for_return}
