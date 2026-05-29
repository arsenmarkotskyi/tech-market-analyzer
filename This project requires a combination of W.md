This project requires a combination of Web Scraping & Data Analysis skills.

The idea of it is to help you to understand the most demanded technologies on the tech market right now. Of course, to become a Python Developer you need to know Django/Flask, Web, PostgreSQL. But even these technologies may not be so popular in the recent moment you search the job.

So, in order for you to be more prepared for interviews and understand which technologies you should learn, we propose you to create the most demanded technologies statistics, based on a job search website.

Note: You can choose any other jobs resource to make your project more unique, or even more complicated. Resources list:

https://work.ua
https://rabota.ua
https://dou.ua
https://linkedin.com (complicated)
https://djinni.co does not allow scrapping anymore
Long story short - you can scrape vacancies for Python and analyze technologies, written in description (in how many vacancies this specific techonology was mentioned), or even use search by technology-keyword. With this kind of strategy, you can get the most recent state of market needs (in technologies prospective). The result chart may look smth like this:


As you already understand - your task is to implement such service :) Attach the link to the Github repo with implemented project. Also fulfill README.md file with some image examples & instructions on how to launch project.

Notes:
Split as much as possible 2 parts of project (Scraping & Data Analysis), make them independent and follow SRP.
Use config.py or different config file to store possible technologies (and some other configuration also).
Try to make as little as possible requests to a website.
Store results (diagrams), so you can see the demanded technologies history and understand, which of them becoming less popular, and which of them only growing popularity.
Use different experience years choices, to understand junior/middle/senior requirements.
Disclaimer: Scrape only public information. Do not authorize to system using your account. The information you're scraping must be 100% public. You always should remember, that scraping must be legal (so do not scrape here any private info, or info, which requires login first).

Additional Tasks (Optional):
Make your code async:
Use asyncio module to significanlty increase the speed of your program. Understand, how to split operations better (by page, by experience years, etc..).

Get rid of technologies config (complex task):
In first part of the task you probably prepared a list of technologies in config file, and checked if this technology is present in description (or maybe you've just searched by this technology). In this optional part - try not to do so. Possibly, some new technology will arrive on the market, which is still not in your config file, and you won't know about it without updating the code. But if this new technology will be really very popular, you can get this info from vacancies description. So you can count occurrences of each word in every description of vacancy, and get the most used words from there. Of course, you will get smth like these top words: is, are, developer, work and so on. But there are some technologies/libraries, which may help you to remove stop-words & preprocess the text (nltk, TextBlob) or show word occurrence frequency as a beautiful image (wordcloud).

Analyze count of views and applications:


Some vacancies are really popular, some of them not. If you understand, how to analyze the data of views and applications - you may be more successful in your own applications. Try to find the correlation between years of experience for positions, technologies required in it, salary (if exist) with these views and applications parameters. You may find some positions, which are fascinating for you and fit your estimations, but somehow they are not popular with applications. It may help you :)
