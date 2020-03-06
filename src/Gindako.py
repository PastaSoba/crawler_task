# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
# from modules.db_util import *
# from modules.update_db import *
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request as req
import sys
import re
import time
import pathlib
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class Gindako:
    baseurl = "http://www.hotland.co.jp/store/?page={}&company_id=1&submit=1#search"
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
                           index=Gindako._result_df.columns)
        Gindako._result_df = Gindako._result_df.append(
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
        MAX_PAGE_INDEX = 49
        for index in range(1, MAX_PAGE_INDEX + 1):
            page = Gindako._OpenURLWithBeautifulSoup(
                Gindako.baseurl.format(index))
            stores = page.find_all("div", {"class": "shopDetail"})
            for store in stores:
                storeAddress = store.find(
                    "dt", text="住所").find_next().text

                # 郵便番号が含まれていない==日本国外の場合は処理を終了する
                if not re.match("[0-9]{3}-[0-9]{4}", storeAddress):
                    return

                storeName = store.find(
                    "h4", {"class": "shopTitle gyotai_1"}).text.strip()
                storeAddress = re.sub(
                    "([0-9]{3}-[0-9]{4}|[ \xaa\n\t\r\f\v]*)", "", storeAddress).replace("\n", "").strip().encode("utf-8").decode("utf-8")

                Gindako._AppendItemToDataFrame(storeName, storeAddress)

        # # 実行確認用
        # print(Gindako._result_df)
        Gindako._result_df.to_csv('./Gindako.csv')
        return Gindako._result_df


if __name__ == "__main__":
    df = Gindako.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
