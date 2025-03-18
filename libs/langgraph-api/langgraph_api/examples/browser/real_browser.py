import os
import sys
from pathlib import Path

from browser_use.agent.views import ActionResult

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio

from langchain_openai import ChatOpenAI

from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext

browser = Browser(
	config=BrowserConfig(
		# NOTE: you need to close your chrome browser - so that this can open your browser in debug mode
		# chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
		chrome_instance_path='C:\Program Files\Google\Chrome\Application\chrome.exe',
	)
)


async def main():
	agent = Agent(
		task='Go to Reddit, search for ”browser-use“, click on the first post and return the first comment.',
		llm=ChatOpenAI(model='DeepSeek-R1-Distill-Qwen-32B',
					   base_url="http://ai-api.e-tudou.com:9000/v1/",
					   api_key='sk-uG93vRV5V2Dog95J15FfCdE5DaAe438fBb17C642F2E1Ae57'),
		browser=browser,
	)

	await agent.run()
	await browser.close()

	input('Press Enter to close...')


if __name__ == '__main__':
	asyncio.run(main())
