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
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class CommeCaIsm:
    baseurl = "https://online.fivefoxes.co.jp/stores?bslg=003"
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
                           index=CommeCaIsm._result_df.columns)
        CommeCaIsm._result_df = CommeCaIsm._result_df.append(
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
    def getStoreInfo():
        page = CommeCaIsm._OpenURLWithBeautifulSoup(CommeCaIsm.baseurl)
        stores = page.find_all(
            "li", {"class": "d-lg-flex p-store-list__store"})

        for store in stores:
            storeName = store.find("div", {"class": "c-store-name coontainer"}).find(
                "div", {"class": "col-12 c-store-name__col c-store-name__label"}).text.strip()
            storeAddress = store.find("div", {"class": "c-store-information container px-0"}).find(
                "div", {"class": "c-store-information__value"}).text.strip()
            CommeCaIsm._AppendItemToDataFrame(storeName, storeAddress)

        # # 実行確認用
        # print(CommeCaIsm._result_df)
        CommeCaIsm._result_df.to_csv('./csv/CommeCaIsm.csv')
        return CommeCaIsm._result_df


if __name__ == "__main__":
    df = CommeCaIsm.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
