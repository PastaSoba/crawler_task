# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from modules.db_util import *
from modules.update_db import *
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request as req
import sys
import re
import threading
import pathlib
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class Lush:
    baseurl = "https://www.iqon.jp/store_locator/brand/LUSH/5231/"
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
                           index=Lush._result_df.columns)
        Lush._result_df = Lush._result_df.append(
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
        """
        urlとresult辞書を読み込み、urlから得られた情報をresultに書き込んでいく
        param
        -----
        *args[1] (url:str)
            読み込みたいページのURL
        *args[2] (result:dic([storeName] = storeAddress))
            結果を書き込むべき辞書
        *args[3] (storeName:str)
            店舗名（結果を書き込むべき辞書のキーとなる）
        """
        url = args[1]
        result = args[2]
        storeName = args[3]

        page = Lush._OpenURLWithBeautifulSoup(url)

        address = page.find("span", {"class": "st-address"}).text
        # 店舗ビルがないような店舗の場合、空文字にする
        try:
            building = page.find("span", {"class": "building"}).text
        except AttributeError:
            building = ""

        result[storeName] = address + building

    @staticmethod
    def prefworker(*args):
        """
        urlとresult辞書を読み込み、urlから得られた情報をresultに書き込んでいく
        param
        -----
        *args[1] (url:str)
            読み込みたいページのURL
        *args[2] (result:dic([storeName] = storeAddress))
            結果を書き込むべき辞書
        """
        semaphore = args[0]
        url = args[1]
        result = args[2]
        workers = []

        page = Lush._OpenURLWithBeautifulSoup(url)
        stores = page.find_all("li", {"class": "store"})
        for store in stores:
            storeName = store.find("span", {"class": "name"}).text
            result[storeName] = ""
            workers.append(threading.Thread(
                target=Lush.miniworker, args=(semaphore, "https://www.iqon.jp" + store.a.get("href"), result, storeName)))

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

    @staticmethod
    def getStoreInfo():
        page = Lush._OpenURLWithBeautifulSoup(Lush.baseurl)
        workers = []
        result = {}
        semaphore = threading.Semaphore(47)

        prefs = page.find(
            "section", {"class": "store-list"}).find_all("li", {"class": "pref_stores clearfix"})
        for pref in prefs:
            workers.append(threading.Thread(
                target=Lush.prefworker, args=(semaphore, "https://www.iqon.jp" + pref.a.get("href"), result)))

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        for k, v in result.items():
            Lush._AppendItemToDataFrame(k, v)

        # # 実行確認用
        # print(Lush._result_df)
        # Lush._result_df.to_csv('./Lush.csv')
        return Lush._result_df


if __name__ == "__main__":
    df = Lush.getStoreInfo()
    brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    df['brand_id'] = brand_id
    new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    conn_pg = DBUtil.getConnect()
    UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
