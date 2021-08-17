import addpath

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import FirefoxOptions

import time
import string
import random

import numpy as np
import scipy.interpolate as si

import requests

import speech_recognition as sr
from os import path
from pydub import AudioSegment
import subprocess
import re

from net_manager import reset_circuit
from human_spoofer import *
from captcha_solvers import *

from accounts import *
from settings import *
from kill import kill_all


def log(S, end='\n'):
	with open(ACCOUNT_LOG_PATH, 'a') as f:
		f.write("{} : {}{}".format(datetime.now().strftime("%b-%d-%Y %H:%M:%S"), S, end))
	if verbose: print(S, end=end)

if not verbose:
	print = log

def modify_name(username):

	if random.uniform(0,1) < .5:
		username = username.lower()

	if random.uniform(0,1) < 0.5:
		username = username.replace("-", "").replace("_", "")

	return username


get_element = lambda xpath : WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH , xpath)))
get_element_t = lambda xpath, t :  WebDriverWait(driver, t).until(EC.element_to_be_clickable((By.XPATH , xpath)))
port = 9072


while True:

    log("")      
    log("") 			
    log("")    
    log("CREATE ACCOUNT SCRIPT HAS STARTED")

	account_created = False
	failed_counter = -1
    while account_created == False:
		failed_counter = failed_counter + 1

		if (failed_counter and DEPLOYED):
			log("Change Tor circuit....")
			reset_circuit(port)
			log("Done.")
		
		with open(HOME_PATH + "user_agents.csv", "r") as fp:
			useragent = random.choice(fp.readlines()).strip()

		log("User agent: " + str(useragent))


		profile = webdriver.FirefoxProfile()
		# Socks5 Host SetUp:-
		if DEPLOYED:
			profile.set_preference('network.proxy.type', 1)
			profile.set_preference('network.proxy.socks', '127.0.0.1')
			profile.set_preference('network.proxy.socks_port', int(port))
		profile.set_preference("general.useragent.override", useragent)

		driver = webdriver.Firefox(firefox_profile=profile)

		try:

			log("Getting webpage...")
			driver.get("https://www.reddit.com/register/?dest=https%3A%2F%2Fwww.reddit.com%2F")

			# log("Exiting... Good luck.")
			# exit(0)

			log("Proceeding to register page")
			continue_btn = get_element("//button[@type='submit']")
			human_like_mouse_move(driver, continue_btn)
			continue_btn.click()

			wait()

			log("Generating username and password...")
			username = get_element("//a[@class='Onboarding__usernameSuggestion']").text
			password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(12))

			username = modify_name(username)

			log("Username: " + username)


			wait()
			type_like_a_human(get_element("//input[@id='regUsername']"), username)
			wait()
			type_like_a_human(get_element("//input[@id='regPassword']"), password)


			long_wait()

			captcha_frame = get_element("//iframe[@title='reCAPTCHA']")
			driver.switch_to.frame(captcha_frame)

			wait()

			log("Solving CAPTCHA")
			chk_box = get_element_t("//span[@id='recaptcha-anchor']", 60)
			human_like_mouse_move(driver, chk_box)
			chk_box.click()

			wait()

			driver.switch_to.parent_frame()
			challenge_frame = get_element("//iframe[@title='recaptcha challenge']")
			driver.switch_to.frame(challenge_frame)

			wait()


		except Exception as e:
			
			print(str(e))

			log("FAILED: Something went wrong. Trying again.")
			driver.close()
			continue


		if image_challenge(driver):
			break




	log("Success! Account created with username: " + username)

	wait()

	log("Creating new keys...")

	while True:

		try:

			driver.get("https://ssl.reddit.com/prefs/apps/")

			long_wait()

			btn = get_element("//button[@id='create-app-button']")
			btn.click()
			break

		except Exception as e:
			
			log(str(e))

	log("Filling out information...")
	wait()
	type_like_a_human( get_element("//input[@name='name']"), ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6)) )
	wait()
	get_element("//input[@id='app_type_script']").click()
	wait()
	type_like_a_human( get_element("//input[@name='about_url']"), "http://localhost:")
	wait()
	type_like_a_human( get_element("//input[@name='redirect_uri']"), "http://localhost:")
	wait()
	get_element("//button[@type='submit']").click()

	log("Retrieving id and secret...")

	get_element("//div[@class='app-details']/h3").click()
	client_id = driver.find_elements_by_xpath("//div[@class='app-details']/h3")[1].text
	client_secret = driver.find_elements_by_xpath("//tbody/tr/td[@class='prefright']")[0].text

	bpaccounts = Account.load(ACCOUNTS_PATH)


	account = Account(user_agent = useragent,
						client_id = client_id,
						client_secret = client_secret,
						username = username,
						password = password,
						email = "",
						post_karma = 1,
						comment_karma = 0,
						state = "aging",
						active_hours = "",
						last_comment = 0,
						last_post = 0,
						age = 0,
						port = port)

	accounts.append(account)

	log("Saving new account...")
	driver.close()

	Account.save(accounts, ACCOUNTS_PATH)
	log("Success! Done.")


	failed_counter = 0
