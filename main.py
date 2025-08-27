#!/usr/bin/env python3

import os
import dotenv
import traceback
from playwright.sync_api import sync_playwright
from util import send_slack_msg
from daewon import go_daewon
from sofrano import go_sofrano
from playshop import go_playshop

def main():
    dotenv.load_dotenv()
    msg_for_slack = "- - 출석체크 시작 - -\n"
    print("- - 출석체크 시작 - -", flush=True)

    succeed_daewon = False
    succeed_sofrano = False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # 대원샵 출석체크
            daewon_id = os.getenv("DAEWON_ID")
            daewon_pw = os.getenv("DAEWON_PW")
            daewon_result = go_daewon(page, daewon_id, daewon_pw)
            msg_for_slack += daewon_result["msg_for_return"]
            succeed_daewon = daewon_result["succeed"]

            # 소프라노몰 출석체크
            sofrano_id = os.getenv("SOFRANO_ID")
            sofrano_pw = os.getenv("SOFRANO_PW")
            sofrano_result = go_sofrano(page, sofrano_id, sofrano_pw)
            msg_for_slack += sofrano_result["msg_for_return"]
            succeed_sofrano = sofrano_result["succeed"]

            # 플레이샵 출석체크
            playshop_id = os.getenv("PLAYSHOP_ID")
            playshop_pw = os.getenv("PLAYSHOP_PW")
            playshop_result = go_playshop(page, playshop_id, playshop_pw)
            msg_for_slack += playshop_result["msg_for_return"]
            succeed_playshop = playshop_result["succeed"]

            browser.close()

        msg_for_slack += "- - 출석체크 완료 - -\n"
        print(msg_for_slack, flush=True)

        # 결과 요약
        summary = f"대원샵: {'성공' if succeed_daewon else '실패'}, 소프라노몰: {'성공' if succeed_sofrano else '실패'}, 플레이샵: {'성공' if succeed_playshop else '실패'}\n"
        print(summary, flush=True)
        msg_for_slack += summary

        # Slack 전송
        send_slack_msg(msg_for_slack)

    except Exception as e:
        print(f"예외 발생: {e}", flush=True)
        trace_str = traceback.format_exc()
        log_msg = f"예외 발생: {e}\n진행 상황:\n{msg_for_slack}\nTraceback:\n{trace_str}"
        print(log_msg, flush=True)
        send_slack_msg(log_msg)

if __name__ == "__main__":
    main()
