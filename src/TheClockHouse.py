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


class TheClockHouse:
    baseurl = "https://www.theclockhouse.jp/shoplist"
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
                           index=TheClockHouse._result_df.columns)
        TheClockHouse._result_df = TheClockHouse._result_df.append(
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
        page = TheClockHouse._OpenURLWithBeautifulSoup(TheClockHouse.baseurl)
        contents = page.find(
            "section", {"class": "content-element content-1"}).next_siblings

        for content in contents:
            pref_name = content.find(
                "div", {"class": "col col-1"}).find("div").text
            stores = content.find_all(
                "div", {"class": re.compile("component component-[1-3] richtext")})

            for store in stores:
                if "トップへ戻る" in store.p.text:
                    continue

                storeInfo = store.p.text.split("\n")
                storeName = storeInfo[0]
                storeAddress = pref_name + \
                    re.sub("〒[0-9]{3}[-‐]*[0-9]{4}[ \xa0\n(&nbsp;)]?",
                           "", storeInfo[1])

                TheClockHouse._AppendItemToDataFrame(storeName, storeAddress)

        # # 実行確認用
        # print(TheClockHouse._result_df)
        # TheClockHouse._result_df.to_csv('./TheClockHouse.csv')
        return TheClockHouse._result_df


if __name__ == "__main__":
    df = TheClockHouse.getStoreInfo()
    brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    df['brand_id'] = brand_id
    new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    conn_pg = DBUtil.getConnect()
    UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)