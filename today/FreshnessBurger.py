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


class FreshnessBurger:
    baseurl = "https://search.freshnessburger.co.jp/fb/spot/list?page={}&address={:02}&search=address"
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
                           index=FreshnessBurger._result_df.columns)
        FreshnessBurger._result_df = FreshnessBurger._result_df.append(
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
        area_nums = 47
        for area_num in range(1, area_nums + 1):

            page_num = 1
            while True:

                page = FreshnessBurger._OpenURLWithBeautifulSoup(
                    FreshnessBurger.baseurl.format(page_num, area_num))

                stores = page.find("ul", {"class": "list-unstyled"}).find_all(
                    "li", {"class": "row w_1_searchresult_2_1-shop"})

                if len(stores) <= 0:
                    break

                for store in stores:
                    storeName = store.find(
                        "a", {"class": "w_1_searchresult_2_1-spot-name"}).text.strip()
                    storeAddress = store.find(
                        "dd", {
                            "class": "w_1_searchresult_2_1-td-value table-style-cell"}
                    ).text.strip()

                    storeName = "フレッシュネスバーガー "
                    FreshnessBurger._AppendItemToDataFrame(
                        storeName, storeAddress)

                page_num += 1

        return FreshnessBurger._result_df


if __name__ == "__main__":
    df = FreshnessBurger.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
