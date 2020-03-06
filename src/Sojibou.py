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
import pathlib
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class Sojibou:
    baseurl = "https://www.gourmet-kineya.co.jp/search/"
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
                           index=Sojibou._result_df.columns)
        Sojibou._result_df = Sojibou._result_df.append(
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
        """ 検索ページ """
        driver = Sojibou._OpenURLWithSelenium(Sojibou.baseurl)
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located)  # 待機

        checkbutton = driver.find_element_by_xpath(
            "/html/body/div/div/div/section/div/aside/div[1]/form/div[2]/ul/li[1]/label/input")
        checkbutton.click()
        submitbutton = driver.find_element_by_xpath(
            "/html/body/div/div/div/section/div/aside/div[1]/form/div[6]/div/button")
        submitbutton.click()

        """ 検索結果ページ """
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located)  # 待機

        stores = driver.find_element_by_xpath(
            "/html/body/div/div/div/form/div[2]/table/tbody").find_elements_by_tag_name("tr")

        for store in stores:
            image = store.find_element_by_tag_name("img").get_attribute("src")
            if '8.jpg' in image:
                storeName = "そじ坊 " + store.find_element_by_tag_name(
                    "a").get_attribute("text").strip()
                storeAddress = store.find_elements_by_tag_name(
                    "td")[1].get_attribute("innerHTML").replace("<br>", " ")
                Sojibou._AppendItemToDataFrame(storeName, storeAddress)

        return Sojibou._result_df


if __name__ == "__main__":
    df = Sojibou.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
