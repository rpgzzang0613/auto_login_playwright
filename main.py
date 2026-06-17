#!/usr/bin/env python3

import os
import sys
import dotenv
import traceback
from playwright.sync_api import sync_playwright
from util import send_slack_msg
from daewon import go_daewon
from sofrano import go_sofrano
from playshop import go_playshop
from yepanrun import go_yepanrun

ALL_SITES = ["daewon", "sofrano", "playshop", "yepanrun"]

def get_selected_sites():
    selected_sites = sys.argv[1:]

    if not selected_sites or "all" in selected_sites:
        return ALL_SITES

    invalid_sites = [site for site in selected_sites if site not in ALL_SITES]
    if invalid_sites:
        valid_sites = ", ".join(ALL_SITES + ["all"])
        raise ValueError(f"알 수 없는 사이트: {', '.join(invalid_sites)}. 사용 가능: {valid_sites}")

    return selected_sites

def main():
    dotenv.load_dotenv()
    selected_sites = get_selected_sites()
    msg_for_slack = "- - 출석체크 시작 - -\n"
    print("- - 출석체크 시작 - -", flush=True)
    msg_for_slack += f"실행 대상: {', '.join(selected_sites)}\n"
    print(f"실행 대상: {', '.join(selected_sites)}", flush=True)

    succeed_daewon = False
    succeed_sofrano = False
    succeed_playshop = False
    succeed_yepanrun = False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                # 대원샵 출석체크
                if "daewon" in selected_sites:
                    context = browser.new_context()
                    page = context.new_page()
                    try:
                        daewon_id = os.getenv("DAEWON_ID")
                        daewon_pw = os.getenv("DAEWON_PW")
                        daewon_result = go_daewon(page, daewon_id, daewon_pw)
                        msg_for_slack += daewon_result["msg_for_return"]
                        succeed_daewon = daewon_result["succeed"]
                    finally:
                        page.close()
                        context.close()

                # 소프라노몰 출석체크
                if "sofrano" in selected_sites:
                    context = browser.new_context()
                    page = context.new_page()
                    try:
                        sofrano_id = os.getenv("SOFRANO_ID")
                        sofrano_pw = os.getenv("SOFRANO_PW")
                        sofrano_result = go_sofrano(page, sofrano_id, sofrano_pw)
                        msg_for_slack += sofrano_result["msg_for_return"]
                        succeed_sofrano = sofrano_result["succeed"]
                    finally:
                        page.close()
                        context.close()

                # 플레이샵 출석체크
                if "playshop" in selected_sites:
                    context = browser.new_context()
                    page = context.new_page()
                    try:
                        playshop_id = os.getenv("PLAYSHOP_ID")
                        playshop_pw = os.getenv("PLAYSHOP_PW")
                        playshop_result = go_playshop(page, playshop_id, playshop_pw)
                        msg_for_slack += playshop_result["msg_for_return"]
                        succeed_playshop = playshop_result["succeed"]
                    finally:
                        page.close()
                        context.close()

                # 예판런 출석체크
                if "yepanrun" in selected_sites:
                    context = browser.new_context()
                    page = context.new_page()
                    try:
                        yepanrun_id = os.getenv("YEPANRUN_ID")
                        yepanrun_pw = os.getenv("YEPANRUN_PW")
                        yepanrun_result = go_yepanrun(page, yepanrun_id, yepanrun_pw)
                        msg_for_slack += yepanrun_result["msg_for_return"]
                        succeed_yepanrun = yepanrun_result["succeed"]
                    finally:
                        page.close()
                        context.close()
            finally:
                browser.close()

        msg_for_slack += "- - 출석체크 완료 - -\n"
        print(msg_for_slack, flush=True)

        # 결과 요약
        site_results = {
            "daewon": ("대원샵", succeed_daewon),
            "sofrano": ("소프라노몰", succeed_sofrano),
            "playshop": ("플레이샵", succeed_playshop),
            "yepanrun": ("예판런", succeed_yepanrun),
        }
        summary_parts = []
        for site in selected_sites:
            site_name, succeed = site_results[site]
            summary_parts.append(f"{site_name}: {':white_check_mark: *성공*' if succeed else ':x: *실패*'}")
        summary = ", ".join(summary_parts) + "\n"
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
