# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
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
import urllib
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class Tabio:
    baseurl = "https://tabio.com/jp/corporate/store/?action=search&page={}"
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
                           index=Tabio._result_df.columns)
        Tabio._result_df = Tabio._result_df.append(
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
            browser = Tabio._OpenURLWithSelenium(url)
            element = WebDriverWait(browser, 15).until(
                EC.presence_of_all_elements_located)
            page = Tabio._OpenPagesourceWithBeautifulSoup(
                browser.page_source)

            stores = page.find("section", class_="result").find_all(
                "div", class_="box")

            for store in stores:
                storeName = store.find("h4").text
                storeAddress = store.find("p").text

                # storeName = "Tabio " + \
                #     re.sub(
                #         "(TODAY's DIAMONDS Tabio|[ \n\t\r\f])", "", storeName)
                # storeAddress = re.sub(
                #     "(TODAY's DIAMONDS Tabio|●|[ \n\t\r\f]|[0-9]{1,2}:[0-9]{2}.*|【.*)", "", storeAddress)
                result_dic[storeName] = storeAddress

    @staticmethod
    def getStoreInfo():
        page_num = 27

        workers = []
        result = {}
        semaphore = threading.Semaphore(5)

        for index in range(1, page_num + 1):
            workers.append(threading.Thread(
                target=Tabio.miniworker, args=(semaphore, Tabio.baseurl.format(index), result)))

        # ワーカーを順次起動させる
        for worker in workers:
            worker.start()

        # ワーカーの動作結果をまとめる
        for worker in workers:
            worker.join()

        for k, v in result.items():
            Tabio._AppendItemToDataFrame(k, v)

        # # 実行確認用
        # print(Tabio._result_df)
        # Tabio._result_df.to_csv('./csv/Tabio.csv')
        return Tabio._result_df


if __name__ == "__main__":
    df = Tabio.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
