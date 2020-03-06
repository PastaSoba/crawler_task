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
import pathlib
import threading
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class Benitora:
    baseurl = "https://kiwa-group.co.jp/benitora_brand/"
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
                           index=Benitora._result_df.columns)
        Benitora._result_df = Benitora._result_df.append(
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

        page = Benitora._OpenURLWithBeautifulSoup(url)

        address = page.find("th", text="住所").find_next().text
        result[storeName] = address

    @staticmethod
    def getStoreInfo():
        page = Benitora._OpenURLWithBeautifulSoup(Benitora.baseurl)

        workers = []
        result = {}
        semaphore = threading.Semaphore(47)

        prefs = page.find("ul", {"class": "lcp_catlist"}).find_all("li")
        for pref in prefs:
            workers.append(threading.Thread(
                target=Benitora.miniworker, args=(semaphore, pref.a.get("href"), result, pref.a.get("title"))))

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        for k, v in result.items():
            Benitora._AppendItemToDataFrame(k, v)

        # # 実行確認用
        # print(Benitora._result_df)
        # Benitora._result_df.to_csv('./Benitora.csv')
        return Benitora._result_df


if __name__ == "__main__":
    df = Benitora.getStoreInfo()
    brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    df['brand_id'] = brand_id
    new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    conn_pg = DBUtil.getConnect()
    UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
