# ライブラリの取得

import pandas as pd
import datetime as dt
import jsm
import requests
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert


################################ 自動売買のプログラム ###################################

def buy(code, buy_price, num_stock):
    macds, macd = MACD(code)
    signal1 = signal(9, macds)

    # macdがsignalを超えないうちは買わずに様子見
    # while macd <= signal1:
    #     pass

    driver = webdriver.Chrome()
    driver.set_page_load_timeout(300)
    driver.get("https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html")

    # 次の二行にはそれぞれ自分のアカウントのidとパスワードを入力してください
    login = "ABCD"
    password = "ABCD"


    driver.find_element_by_name("loginid").send_keys(login)
    driver.find_element_by_name("passwd").send_keys(password)
    driver.find_element_by_id("login-btn").click()
    print("login has been finished.")
    sleep(5)
    driver.find_element_by_id("gmenu_domestic_stock").click()
    print("entered menu of domestic stock")
    sleep(5)
    driver.find_element_by_id("jp-stk-top-btn-buy").click()
    sleep(5)

    # 選んだ銘柄を検索する
    driver.find_element_by_id("ss-02").send_keys(code)
    driver.find_element_by_xpath(
        "//*[@id='str-main-inner']/table/tbody/tr/td/form/div[4]/fieldset/p/input[4]").click()
    sleep(5)

    # 買い注文に必要な情報を入力
    driver.find_element_by_id("orderValue").send_keys(num_stock)
    driver.find_element_by_id("marketOrderPrice").send_keys(buy_price)
    # その他買いの条件を変更したい場合は適宜コードを追加してください。

    # 0.5パーセント増で売り注文を同時に入れる
    driver.find_element_by_id('doSetOrder').click()
    driver.find_element_by_id('setOrderPrice').send_keys(int(buy_price * 1.005))

    # 次の行には自分の取引パスワードを入力してください
    buy_password = "1234"

    driver.find_element_by_name("password").send_keys(buy_password)
    driver.find_element_by_xpath(
        "//*[@id='auto_update_field_stock_price']/tbody/tr/td[1]/table[6]/tbody/tr/td/table[1]/tbody/tr/td/table/tbody/tr[1]/td[5]/input").click()
    sleep(1)
    driver.find_element_by_id("sbm").click()
    sleep(5)

    # ブラウザごと終了する
    driver.quit()


# 板から注文価格を取得する関数
def order_book_search(code):

    driver = webdriver.Chrome()
    driver.set_page_load_timeout(300)
    driver.get("https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html")
    login = "ABCD"
    password = "ABCD"
    driver.find_element_by_name("loginid").send_keys(login)
    driver.find_element_by_name("passwd").send_keys(password)
    driver.find_element_by_id("login-btn").click()
    print("login has been finished.")
    sleep(5)
    driver.find_element_by_id("gmenu_domestic_stock").click()
    print("entered menu of domestic stock")
    sleep(5)
    driver.find_element_by_id("dscrCdNm2").send_keys(code)
    driver.find_element_by_xpath('//*[@id="str-main-inner"]/table/tbody/tr/td/form/div[3]/div[1]/table/tbody/tr[1]/td[2]/a/img').click()
    sleep(5)

    html = driver.page_source

    # 取得したページをスクレイピング
    soup = BeautifulSoup(html, "lxml")

    lowest_sell_price_data = soup.select_one("#yori_table_update_ask_1 > span")
    highest_buy_price_data = soup.select_one("#yori_table_update_bid_1 > span")

    # 板から最安売り注文を取得
    lowest_sell_price_tmp1 = str(lowest_sell_price_data).split("<")
    lowest_sell_price_tmp2 = lowest_sell_price_tmp1[1].split(">")
    lowest_sell_price_tmp3 = lowest_sell_price_tmp2[1]
    lowest_sell_price_tmp3.replace("\n\t\t\t\t\t", "")
    lowest_sell_price_tmp3.replace("\n\t\t\t\t", "")
    lowest_sell_price_tmp4 = lowest_sell_price_tmp3.strip()
    lowest_sell_price_tmp5 = lowest_sell_price_tmp4.split(",")
    lowest_sell_price = int("".join(lowest_sell_price_tmp5))



    # 最高買い注文を取得
    highest_buy_price_tmp1 = str(highest_buy_price_data).split("<")
    highest_buy_price_tmp2 = highest_buy_price_tmp1[1].split(">")
    highest_buy_price_tmp3 = highest_buy_price_tmp2[1]
    highest_buy_price_tmp3.replace("\n\t\t\t\t\t", "")
    highest_buy_price_tmp3.replace("\n\t\t\t\t", "")
    highest_buy_price_tmp4 = highest_buy_price_tmp3.strip()
    highest_buy_price_tmp5 = highest_buy_price_tmp4.split(",")

    highest_buy_price = int("".join(highest_buy_price_tmp5))


    # 前日終値との差額を取得
    close_price_yesterday_data = soup.select_one("#update_table2 > table > tbody > tr:nth-child(1) > td:nth-child(4)")
    close_price_yesterday_tmp1 = str(close_price_yesterday_data).split(">")
    close_price_yesterday_tmp2 = close_price_yesterday_tmp1[3].split("（")
    close_price_yesterday_tmp3 = close_price_yesterday_tmp2[0]
    close_price_yesterday_tmp4 = close_price_yesterday_tmp3[1:]
    close_price_yesterday_tmp5 = close_price_yesterday_tmp4.split(",")

    close_price_yesterday = int("".join(close_price_yesterday_tmp5))

    print("売り注文の最安値は" + str(lowest_sell_price) + "です")
    print("買い注文の最高値は" + str(highest_buy_price) + "です")
    print("前日終値は"+ str(close_price_yesterday) +"です")


    sleep(300)
    driver.quit()

    return highest_buy_price, close_price_yesterday
# 先物の価格を取得する関数

def sakimono_search():
    driver = webdriver.Chrome()

    driver.get("https://www.trkd-asia.com/rakutensecj/indx.jsp?ind=2&ric=0")
    sleep(3)

    html = driver.page_source  # ソースコードを取得
    soup = BeautifulSoup(html, "lxml")  # htmlの読み込み

    # 現在価格の取得
    sakimono_price_data = soup.select_one("#cFut > table:nth-child(6) > tbody > tr:nth-child(1) > td.cell-02 > em")
    # 価格の前日比の取得
    diff_with_yesterday_data = soup.select_one("#cFut > table:nth-child(6) > tbody > tr:nth-child(2) > td.cell-02 > span")

    # 取得したデータの整形
    sakimono_price_tmp1 = str(sakimono_price_data).split("<")
    sakimono_price_tmp2 = sakimono_price_tmp1[1].split(">")
    sakimono_price_tmp3 = sakimono_price_tmp2[1].split(",")
    sakimono_price = int("".join(sakimono_price_tmp3))

    diff_with_yesterday_tmp1 = str(diff_with_yesterday_data).split("<")
    diff_with_yesterday_tmp2 = diff_with_yesterday_tmp1[1].split(">")
    diff_with_yesterday = int("".join(diff_with_yesterday_tmp2[1])) # ここjoinいらないかも

    print(sakimono_price, diff_with_yesterday)
    driver.quit()

    return sakimono_price, diff_with_yesterday

# 先物の前日比で買うか判定するプログラム
def sakimono_judge(trigger_ratio):

    trigger = 0
    sakimono_price, diff_with_yesterday = sakimono_search()
    ratio = sakimono_price/(sakimono_price - diff_with_yesterday) - 1

    if ratio >= trigger_ratio:
        trigger = 1

    return trigger


def main(code):

    if sakimono_judge(0.005):
        buy_max, close_price_yesterday = order_book_search(code)
        if buy_max >= close_price_yesterday:
            buy(code, buy_max*0.995, 100)



################################実行プログラム###################################
import sched
import time
from datetime import datetime
if __name__ == '__main__':
    print("判定、売買したい銘柄のコードを入力してください")
    code = int(input())
    scheduler = sched.scheduler(time.time, time.sleep)
    # 取引開始の5分前に起動
    run_at = datetime.strptime('2019-02-25 09:00:00', '%Y-%m-%d %H:%M:%S')
    run_at = int(time.mktime(run_at.utctimetuple()))
    scheduler.enterabs(run_at, 1, main)
    scheduler.run()







