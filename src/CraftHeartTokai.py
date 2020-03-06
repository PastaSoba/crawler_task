# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
# from modules.db_util import *
# from modules.update_db import *
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request as req
import sys
import re
import chromedriver_binary
import pathlib
import threading
import time
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class CraftHeartTokai:
    baseurl = "https://www.crafttown.jp/info/contact/realShop.php"
    _result_df = pd.DataFrame(columns=['store_name', 'address'])

    @staticmethod
    def _AppendItemToDataFrame(storeName: str, storeAddress: str):
        """
        店舗名と住所を受け取り、クラス変数のDataFrameに追加する

        Parameters
        -----
        storeName : str
            店舗名
        storeAddress : str
            住所
        """
        tmp_se = pd.Series([storeName, storeAddress],
                           index=CraftHeartTokai._result_df.columns)
        CraftHeartTokai._result_df = CraftHeartTokai._result_df.append(
            tmp_se, ignore_index=True)

    @staticmethod
    def _OpenURLWithSelenium(url: str):
        """
        URLをSeleniumで開く

        Parameter
        -----
        url : str
            開きたいページのURL

        Return
        -----
        browser : WebDriver
            ページを開いた後のWebDriverオブジェクト
        """
        browser = webdriver.Chrome()
        browser.get(url)
        return browser

    @staticmethod
    def _OpenURLWithBeautifulSoup(url: str):
        """
        URLをBeautifulSoup(パーサーはhtml.parser)で開く

        Parameter
        -----
        url : str
            開きたいページのURL

        Return
        -----
        soup : BeautifulSoup
            ページを開いた後のBeautifulSoupオブジェクト
        """
        res = req.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        return soup

    @staticmethod
    def _OpenPagesourceWithBeautifulSoup(page_source):
        """
        WebDriver.pagesourceをBeautifulSoup(パーサーはhtml.parser)で開く

        Parameter
        -----
        page_source
            開きたいページのページソース

        Return
        -----
        soup : BeautifulSoup
            ページを開いた後のBeautifulSoupオブジェクト
        """
        soup = BeautifulSoup(page_source, "html.parser")
        return soup

    def miniworker(semaphore, url, result_dic, value):
        """
        urlとresult辞書を読み込み、urlから得られた情報をresultに書き込んでいく
        param
        -----
        semaphore:threading.Semaphore
            子スレッドのためのセマフォ（過剰な多重起動を防ぐ）
        url:str
            読み込みたいページのURL
        result_dic([storeName] = storeAddress))
            結果を書き込むべき辞書
        value:int
            都道府県コード
        """
        with semaphore:
            # 操作可能なブラウザを取得
            browser = CraftHeartTokai._OpenURLWithSelenium(url)
            WebDriverWait(browser, 15).until(
                EC.visibility_of_all_elements_located)

            # 都道府県を選択
            pref_element = browser.find_element_by_css_selector(
                "#searchByArea > dl.required.error > dd > label > select")
            pref_selector_element = Select(pref_element)
            pref_selector_element.select_by_value(str(value))

            # 検索ボタンをクリック
            search_button = browser.find_element_by_css_selector(
                "#searchByArea > div > div.btn2 > a")
            search_button.click()

            # 検索結果を待機
            WebDriverWait(browser, 15).until(
                EC.visibility_of_all_elements_located)

            # 店舗情報の格納
            page = CraftHeartTokai._OpenPagesourceWithBeautifulSoup(
                browser.page_source)
            stores = page.find_all("article", {"class": "listArticle4"})

            for store in stores:
                storeName = store.find("div", {"class": "head"}).find(
                    "h3", {"class": "title"}).text
                storeAddress = store.find(
                    "div", {"class": "info"}).find("dd").text

                if "クラフトハートトーカイ" in storeName:
                    result_dic[storeName] = storeAddress

    @staticmethod
    def getStoreInfo():
        page_num = 47

        workers = []
        result = {}
        semaphore = threading.Semaphore(5)

        for pref_value in range(1, page_num + 1):
            workers.append(threading.Thread(
                target=CraftHeartTokai.miniworker, args=(semaphore, CraftHeartTokai.baseurl, result, pref_value)))

        # ワーカーを順次起動させる
        for worker in workers:
            time.sleep(0.5)
            worker.start()

        # ワーカーの動作結果をまとめる
        for worker in workers:
            worker.join()

        for k, v in result.items():
            CraftHeartTokai._AppendItemToDataFrame(k, v)

        return CraftHeartTokai._result_df


if __name__ == "__main__":
    df = CraftHeartTokai.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
