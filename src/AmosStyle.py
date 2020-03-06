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
import time
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class AmosStyle:
    baseurl = "http://www.amos-style.com/shoplist/"
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
                           index=AmosStyle._result_df.columns)
        AmosStyle._result_df = AmosStyle._result_df.append(
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
        browser = AmosStyle._OpenURLWithSelenium(AmosStyle.baseurl)
        time.sleep(10)
        page = AmosStyle._OpenPagesourceWithBeautifulSoup(
            browser.page_source)

        prefs = page.find_all("ul", class_="shop_up")
        for pref in prefs:
            pref_name = pref.get("id")

            if pref_name == "北海道":
                pass
            elif pref_name == "大阪" or pref_name == "京都":
                pref_name += "府"
            elif pref_name == "東京":
                pref_name += "都"
            else:
                pref_name += "県"

            stores = pref.find_all("li", class_=[(pref_name + " amo")])
            # shops = pref.find_all("li", class_=[(pref_name + " amo"), (pref_name + " tr")])
            for store in stores:
                storeName = store.find("h4", class_="shopname").text
                storeAddress = store.find("p", class_="address").text
                AmosStyle._AppendItemToDataFrame(storeName, storeAddress)

        # # 実行確認用
        # print(AmosStyle._result_df)
        AmosStyle._result_df.to_csv('./csv/AmosStyle.csv')
        return AmosStyle._result_df


if __name__ == "__main__":
    df = AmosStyle.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
