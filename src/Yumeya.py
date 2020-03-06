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


class Yumeya:
    baseurl = ["https://yu-me-ya.co.jp/242153330324773225771230421271280233694712539264812127112305.html",
               "https://yu-me-ya.co.jp/2421533303247732257712304383062648112305.html",
               "https://yu-me-ya.co.jp/2421533303247732257712304212713852012539200133709612305.html",
               "https://yu-me-ya.co.jp/2421533303247732257712304368173007912305.html",
               "https://yu-me-ya.co.jp/2421533303247732257712304200132226912539222352226912305.html",
               "https://yu-me-ya.co.jp/2421533303247732257712304200612403012539277983226012305.html"]

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
                           index=Yumeya._result_df.columns)
        Yumeya._result_df = Yumeya._result_df.append(
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
        for url in Yumeya.baseurl:
            page = Yumeya._OpenURLWithBeautifulSoup(url)
            prefs = page.find(
                "div", {"class": "main-wrap"}).find("div", {"class": "wsite-section-wrap"}).find_next_siblings()

            for pref in prefs:
                storeNames_box = pref.find(
                    "td", {"class": "wsite-multicol-col"})
                storeAddresses_box = storeNames_box.find_next_sibling()

                storeNames = storeNames_box.find(
                    "div", {"class": "paragraph"}).text.split("▶")[1:]
                striped_storeNames = [
                    re.sub("[\u200b\xa0]", "", storeName) for storeName in storeNames]

                storeAddresses = storeAddresses_box.find(
                    "div", {"class": "paragraph"}).text
                splited_storeAddresses = re.split(
                    "0[0-9]{1,3}-[0-9]{2,4}-[0-9]{2,4}", storeAddresses)
                striped_storeAddresses = [
                    re.sub("[\u200b\xa0\u3000]", "", storeAddress) for storeAddress in splited_storeAddresses][:-1]

                for storeName, storeAddress in zip(striped_storeNames, striped_storeAddresses):
                    Yumeya._AppendItemToDataFrame(
                        "だがし夢や " + storeName, storeAddress)

        return Yumeya._result_df


if __name__ == "__main__":
    df = Yumeya.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
