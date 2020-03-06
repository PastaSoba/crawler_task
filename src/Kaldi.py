# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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


class Kaldi:
    baseurl = "https://map.kaldi.co.jp/kaldi/articleList?account=kaldi&accmd=0&ftop=1&adr={:02}"
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
                           index=Kaldi._result_df.columns)
        Kaldi._result_df = Kaldi._result_df.append(
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
        browser = webdriver.Chrome())
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
        res=req.urlopen(url)
        soup=BeautifulSoup(res, "html.parser")
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
        soup=BeautifulSoup(page_source, "html.parser")
        return soup

    @staticmethod
    def miniworker(semaphore, url, result_dic):
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
        """
        with semaphore:
            # 操作可能なブラウザを取得
            browser=Kaldi._OpenURLWithSelenium(url)

            while True:
                time.sleep(1)

                try:
                    page=Kaldi._OpenPagesourceWithBeautifulSoup(
                        browser.page_source)

                    stores=page.find("div", id = "DispListArticle").find(
                        "dl", {"class": "spshoplist cz_display-pc-none"}).find_all("a")

                    for store in stores:
                        storeName=store.find("span", class_ = "shopname").text
                        storeAddress=store.find(
                            "span", class_ = "shopadd").text

                        result_dic[storeName]=storeAddress

                    browser.find_element_by_link_text("次へ").click()

                except Exception as err:
                    break

    @staticmethod
    def getStoreInfo():
        page_num=47

        workers=[]
        result={}
        semaphore=threading.Semaphore(15)

        for pref_value in range(1, page_num + 1):
            # for pref_value in range(13, 14):
            workers.append(threading.Thread(
                target=Kaldi.miniworker, args=(semaphore, Kaldi.baseurl.format(pref_value), result)))

        # ワーカーを順次起動させる
        for worker in workers:
            worker.start()

        # ワーカーの動作結果をまとめる
        for worker in workers:
            worker.join()

        for k, v in result.items():
            k="KALDI COFFEE FARM " + re.sub("(（.*）|【.*】)", "", k)
            Kaldi._AppendItemToDataFrame(k, v)

        return Kaldi._result_df


if __name__ == "__main__":
    df=Kaldi.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
