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


class TullysCoffee:
    baseurl = "https://map.tullys.co.jp/tullys/articleList?account=tullys"
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
                           index=TullysCoffee._result_df.columns)
        TullysCoffee._result_df = TullysCoffee._result_df.append(
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
        page = TullysCoffee._OpenURLWithSelenium(TullysCoffee.baseurl)

        storeNum = int(page.find_element_by_xpath(
            "/html/body/div[3]/section/p/span[1]").get_attribute("textContent"))
        pageNum = storeNum // 20 + (1 if storeNum % 20 > 0 else 0)

        for i in range(pageNum):
            WebDriverWait(page, 15).until(
                EC.presence_of_all_elements_located)
            time.sleep(0.2)

            stores = page.find_element_by_css_selector(
                "#search_result > table").find_elements_by_tag_name("tr")
            for store in stores:
                storeName = store.find_elements_by_tag_name(
                    "td")[0].get_attribute("textContent")
                storeAddress = store.find_elements_by_tag_name(
                    "td")[1].get_attribute("textContent")
                TullysCoffee._AppendItemToDataFrame(storeName, storeAddress)

            try:
                nextButton = page.find_element_by_css_selector(
                    "#search_result > ul").find_element_by_link_text("次へ")
                nextButton.click()
            except Exception:
                break

        return TullysCoffee._result_df


if __name__ == "__main__":
    df = TullysCoffee.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
