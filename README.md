# Acesse-iRewards-Automation-Tools
Some tools for automating the boring and useless task of the Acesse iRewards Program

I had a co-worker a few years ago, that had the unforatunate task of dealing with
the Acesse iRewards Program. That unfortunate individial had to go through
several accounts every single day, easily taking a whole afternoon. It was just so
painful to watch that I felt I had to do something. So I created two automated
tools that cut down the time to just an hour or less.

(Note: The said individual no longer deals with this, so I don't know if all the
tools still work. I'm sure they could be easily modified to fit any changes made on the website.)

### AutoSearchTool
This tool logs in to an Acesse account and then goes through the otherwise
painstaking task of doing a web search on their Acesse search engine. The
tool is command line based.
(Note: The Acesse search engine seems to have been removed, although I might
be wrong. So this tool probbaly isn't working anymore.)

### AdViewAutoTool
This tool will open a web browser and then start going through the task of
rating websites. While this tool is supposed to be automated, it's almost
that. I never got around to deal with the captchas. Besides manually
entering captchas every 5 ratings, everything else is automated.
(Note: As far as I am aware, this task is still available at Acesse.)

### Requirements
- Python 2.x - Some of the tools used below won't work with python 3.x
- [PIL Library](http://pythonware.com/products/pil/) - for reading captchas in AutoSearchTool
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) Engine - to read the captcha result
- [Selenium WebDriver](http://docs.seleniumhq.org/projects/webdriver/) - for AdViewAutoTool to open a web browser
