<h1>GaumutraBot v2</h1>  
Dev: <a href="https://www.reddit.com/u/meribetisunnyleone">Meribetisunnyleone</a>

Thanks to dataplayer12 for hosting the bot.  

<h2>Usage instructions:</h2> 
1. Register a script app on reddit <br>  
2. Install the requirements

```
$ pip install -r requirements.txt
```

3. Edit `bot.py` with the app details
4. Start bot with 

````
python bot.py subreddit
```` 


<b>Notes:</b> 
1. Incase you want to monitor more than 1 subreddit, use `+`. For example, to monitor bakchodi and indiaspeaks together, do

```
$ python bot.py bakchodi+indiaspeaks
```

2. You can edit skeleton.txt to change how the reply looks. Just make sure `GETTER`, `GIVER`, `NNNNN` and `AUTHOR` are at the right places.

