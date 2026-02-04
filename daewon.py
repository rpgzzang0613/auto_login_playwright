from playwright.sync_api import Page
from util import retry
from datetime import datetime
import re

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

        # 4. 출석체크 페이지 찾기
        page.goto("https://www.daewonshop.com/cs/event")
        msg_for_return += "대원샵 이벤트 목록 페이지 진입\n"
        print("대원샵 이벤트 목록 페이지 진입", flush=True)

        event_found = False
        pagenate_list = page.locator('#pagging-wrap .page-area ul.list li a')
        event_page_count = pagenate_list.count()
        
        for page_idx in range(event_page_count):
            if page_idx > 0:
                pagenate_list.nth(page_idx).click()
                page.wait_for_timeout(2000)
                msg_for_return += f"대원샵 이벤트 목록 페이지 {page_idx + 1} 진입\n"
                print(f"대원샵 이벤트 목록 페이지 {page_idx + 1} 진입", flush=True)

            li_list = page.locator('ul#cs-event-template-render > li')

            for i in range(li_list.count()):
                li_item = li_list.nth(i)
                li_title = li_item.locator("p.tit").text_content().strip()

                if "출석체크" not in li_title and "출석 체크" not in li_title:
                    continue


                li_date_range = li_item.locator("p.date").text_content().strip()
                if li_date_range == "상시":
                    msg_for_return += f"상시 출석체크 이벤트 발견: {li_title}\n"
                    print(f"상시 출석체크 이벤트 발견: {li_title}", flush=True)
                    continue
            
                try:
                    start_str, end_str = [x.strip() for x in li_date_range.split("~")]
                    start_date = datetime.strptime(start_str, "%Y.%m.%d").date()
                    end_date = datetime.strptime(end_str, "%Y.%m.%d").date()
                except Exception as e:
                    msg_for_return += f"날짜 파싱 실패: {e}\n"
                    print(f"날짜 파싱 실패: {e}", flush=True)
                    continue

                today = datetime.now().date()

                if not (start_date <= today <= end_date):
                    msg_for_return += f"지나간 달의 출석체크는 패스: {li_title}\n"
                    print(f"지나간 달의 출석체크는 패스: {li_title}", flush=True)
                    continue

                li_item.locator("a").click()
                msg_for_return += f"대원샵 출석체크 페이지 진입: {li_title}\n"
                print(f"대원샵 출석체크 페이지 진입: {li_title}", flush=True)
                event_found = True
                break

            if event_found:
                break

        # 5. 출석 체크 버튼 클릭

        try:
            page.wait_for_timeout(10000)

            iframe = page.frame(
                url=re.compile(r"eventkiki\.com/widget/widget/ekiki-calendar_db\.php")
            )

            iframe.wait_for_selector("#eventkiki-calendar-press", timeout=20000)
            iframe.locator("#eventkiki-calendar-press").click()

            msg_for_return += "대원샵 출석체크 버튼 클릭\n"
            print("대원샵 출석체크 버튼 클릭", flush=True)
        except Exception as e:
            msg_for_return += f"대원샵 출석체크 버튼 찾기 실패: {e}\n"
            print(f"대원샵 출석체크 버튼 찾기 실패: {e}", flush=True)
            return {"succeed": False, "msg_for_return": msg_for_return}

        # 6. 모달 처리
        try:
            modal_win = iframe.locator("#eventkikiWin .new_eventkiki_win")
            error_layer = iframe.locator("#reward_error_layer")

            is_win = modal_win.evaluate("el => window.getComputedStyle(el).display") != "none"
            is_err = error_layer.evaluate("el => window.getComputedStyle(el).display") != "none"

            if is_win and not is_err:
                msg_for_return += "대원샵 출석체크 완료\n"
                print("대원샵 출석체크 완료", flush=True)

                modal_win.locator("#btnRwdClose").click()
                succeed = True
            else:
                msg_for_return += "대원샵 출석체크 이미 참여함\n"
                print("대원샵 출석체크 이미 참여함", flush=True)
                succeed = True
        except:
            msg_for_return += "대원샵 모달 처리 실패\n"
            print("대원샵 모달 처리 실패", flush=True)

        msg_for_return += "- 대원샵 완료 -\n"
        print("- 대원샵 완료 -", flush=True)
    except Exception as e:
        msg_for_return += f"예외 발생: {e}\n"
        print(f"예외 발생: {e}", flush=True)

    return {"succeed": succeed, "msg_for_return": msg_for_return}
