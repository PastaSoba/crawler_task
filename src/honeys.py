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
import pathlib
import threading
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class honeys:
    baseurl = "https://www.honeys.co.jp/shop-result/"
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
                           index=honeys._result_df.columns)
        honeys._result_df = honeys._result_df.append(
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
        browser = webdriver.PhantomJS()
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
    def miniworker(*args):
        url = args[1]
        result = args[2]
        # 要素が読み込まれるまで待機する
        browser = honeys._OpenURLWithSelenium(url)
        wait = WebDriverWait(browser, 200, poll_frequency=0.1)
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "hny-shop-results")))

        page = honeys._OpenPagesourceWithBeautifulSoup(browser.page_source)

        stores = page.find_all("div", class_="hny-shop-results-item__info")
        for store in stores:
            storeName = store.find(
                "div", class_="hny-shop-results-item__name").text
            storeAddress = store.find(
                "div", class_="hny-shop-results-item__address").text
            result[storeName] = storeAddress

    @staticmethod
    def getStoreInfo():
        pagenum = 47
        workers = []
        result = {}
        semaphore = threading.Semaphore(47)

        for pageid in range(1, pagenum + 1):
            url = honeys.baseurl + str(format(pageid, '02'))
            workers.append(threading.Thread(
                target=honeys.miniworker, args=(semaphore, url, result)))

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        for k, v in result.items():
            honeys._AppendItemToDataFrame(k, v)

        # print(result)

        # # 実行確認用
        # print(honeys._result_df)
        honeys._result_df.to_csv('./honeys.csv')
        return honeys._result_df


if __name__ == "__main__":
    df = honeys.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
