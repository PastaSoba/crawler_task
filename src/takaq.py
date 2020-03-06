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
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class takaq:
    baseurl = "https://online.taka-q.jp/shop/store/search.aspx?brand=TAKA-Q&search=%E3%81%93%E3%81%AE%E6%9D%A1%E4%BB%B6%E3%81%A7%E6%A4%9C%E7%B4%A2%E3%81%99%E3%82%8B"
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
                           index=takaq._result_df.columns)
        takaq._result_df = takaq._result_df.append(
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
    def getStoreInfo():
        page = takaq._OpenURLWithBeautifulSoup(takaq.baseurl)
        prefs = page.find_all("ul", class_="shop_list_")
        stores = [store for pref in prefs for store in pref.find_all("li")]
        for store in stores:
            storeName = store.find("div", class_="headline_").find("a").text
            storeAddress = store.find("div", class_="address_").text
            takaq._AppendItemToDataFrame(storeName, storeAddress)

        # # 実行確認用
        # print(takaq._result_df)
        # takaq._result_df.to_csv('./takaq.csv')
        return takaq._result_df


if __name__ == "__main__":
    df = takaq.getStoreInfo()
    brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    df['brand_id'] = brand_id
    new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    conn_pg = DBUtil.getConnect()
    UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
