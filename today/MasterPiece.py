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
# import chromedriver_binary
import pathlib
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class MasterPiece:
    baseurl = ["http://masterpiece-shop.jp/shop",
               "http://masterpiece-shop.jp/shop2"]
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
                           index=MasterPiece._result_df.columns)
        MasterPiece._result_df = MasterPiece._result_df.append(
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
        for url in MasterPiece.baseurl:
            page = MasterPiece._OpenURLWithBeautifulSoup(url)

            stores = page.find(
                "section", {"class": "post-inner"}).find_all("div", {"class": "rightbox-a"})

            for store in stores:
                storeName = store.find("h3", {"class": "ttl-b"}).text
                storeAddress = store.find(
                    "dl", {"class": "store"}).find("dd").text

                storeName = "マスターピース " + \
                    re.sub("[ \n\r\t\f]", "", storeName)
                storeAddress = re.sub(
                    "(〒[0-9]{3}-[0-9]{4}|[ \r\n\t\f])", "", storeAddress)

                MasterPiece._AppendItemToDataFrame(storeName, storeAddress)

        return MasterPiece._result_df


if __name__ == "__main__":
    df = MasterPiece.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
