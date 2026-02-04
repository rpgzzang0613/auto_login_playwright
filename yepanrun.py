from playwright.sync_api import Page
from util import retry, convert_image
from PIL import Image
import pytesseract
import platform
import io
import re

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

        # 4. 출석체크 + 캡챠 처리
        for i in range(15):
            msg_for_return += f"{i+1}번째 시도\n"
            print(f"{i+1}번째 시도", flush=True)

            try:
                check_btn = page.locator("#attendWriteForm p.ec-base-button a.btnSubmitFix")
                if not check_btn.is_visible():
                    msg_for_return += "이미 출석 완료 상태라 버튼 없음\n"
                    print("이미 출석 완료 상태라 버튼 없음", flush=True)
                    succeed = True
                    break

                check_btn.click()

                page.locator(".attendSecurityLayer").wait_for(state="visible", timeout=10000)

                msg_for_return += "Captcha 모달 오픈\n"
                print("Captcha 모달 오픈", flush=True)

                captcha_img = page.locator(".attendSecurityLayer fieldset img").first
                captcha_img.wait_for(state="visible", timeout=10000)

                img_bytes = captcha_img.screenshot()
                original_img = Image.open(io.BytesIO(img_bytes))
                new_img = convert_image(original_img)

                if platform.system() == "Darwin":
                    pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
                elif platform.system() == "Windows":
                    pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract"
                else:
                    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

                captcha_text = pytesseract.image_to_string(
                    new_img,
                    lang="eng",
                    config="--psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789"
                ).replace("\n", "")

                captcha_text = re.sub(r"[^a-z0-9]", "", captcha_text)

                msg_for_return += f"Captcha 추출: {captcha_text}\n"
                print(f"Captcha 추출: {captcha_text}", flush=True)

                secure_input = page.locator("#secure_text").first
                secure_input.fill(captcha_text)

                submit_btn = page.locator(".attendSecurityLayer fieldset a.btnSubmit").first
                with page.expect_event("dialog", timeout=10000) as dialog_info:
                    submit_btn.click()
                    msg_for_return += "출석체크 버튼 클릭\n"
                    print("출석체크 버튼 클릭", flush=True)

                dialog = dialog_info.value

                msg_for_return += f"예판런 출석체크 결과 : *{dialog.message}*\n"
                print(f"예판런 출석체크 결과 : {dialog.message}", flush=True)

                with page.expect_navigation(wait_until="load", timeout=10000):
                    dialog.accept()

                # 출석 완료 버튼 존재 여부 확인
                if not page.locator("#attendWriteForm p.ec-base-button a.btnSubmitFix").first.is_visible():
                    succeed = True
                    break

            except Exception as e:
                msg_for_return += f"시도 중 예외 발생: {e}\n"
                print(f"시도 중 예외 발생: {e}", flush=True)
                continue
    except Exception as e:
        msg_for_return += f"예외 발생: {e}\n"
        print(f"예외 발생: {e}", flush=True)

    msg_for_return += "- 예판런 완료 -\n"
    print("- 예판런 완료 -", flush=True)

    return {"succeed": succeed, "msg_for_return": msg_for_return}
