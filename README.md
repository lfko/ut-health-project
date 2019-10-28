# ut-health-project
Projekt für das Modul "Urbane Technologien", WS19/20

## Machen Städte krank? / Do cities make you sick?
## Disease / outbreak detection based on natural language processing

- Idea: * (in preparation of the thesis) Could you detect, based on e.g. social media, that there is an suspiciuous amount of sick notes to be expected?
        * Can it be pinned to a certain region?
        * Where is the connection to actual existing data, e.g. from the CDC
        * Outbreak detection even before it has been reported by the officials?
- Model: * ???
- Software: * Python (NLTK?, SpaCy?)
- Data: * https://www.cdc.gov/ (USA)
        * https://daten.berlin.de/datensaetze/gesundheitsberichterstattung-berlin-kontext-gesundheitsmonitoring-2018 (Berlin)
        * Twitter
        * https://www.nhsinform.scot/illnesses-and-condition
- Approach: * historical tweets, location of tweets (per API?), symptoms by disease
            * Scrape Twitter (how to filter?)
            * but first look for text corpora and try to figure out how to describe certain diseases and their symptoms

- Twitter-API: * https://www.tweepy.org/ (already existing python implementation for accessing the Twitter-API) (pip install tweepy)
- Python: * http://www.laurentluce.com/posts/twitter-sentiment-analysis-using-python-and-nltk/