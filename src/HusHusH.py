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
import pathlib
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class HusHusH:
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
                           index=HusHusH._result_df.columns)
        HusHusH._result_df = HusHusH._result_df.append(
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
        BASE_URL = 'https://store.world.co.jp/real-store-search?pref=&br=BR511&pcf=1&so=1%2C3&page='
        PAGE_RANGE = 4  # page=1からpage=4まである

        for page_index in range(1, PAGE_RANGE + 1):
            URL = BASE_URL + str(page_index)
            page = HusHusH._OpenURLWithBeautifulSoup(URL)
            storelist_lis = page.find_all('li', class_="point")
            for store in storelist_lis:
                storeName = store.find('a').text.replace(
                    '\n', '').strip().replace("HusHusH", "HusHusH ")
                storeAddress = store.find(
                    'div', class_="txt_address").text.split('\n')[1].strip()
                HusHusH._AppendItemToDataFrame(storeName, storeAddress)

        # # 実行確認用
        # print(HusHusH._result_df)
        # HusHusH._result_df.to_csv('./HusHusH.csv')
        return HusHusH._result_df


if __name__ == "__main__":
    df = HusHusH.getStoreInfo()
    brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    df['brand_id'] = brand_id
    new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    conn_pg = DBUtil.getConnect()
    UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
