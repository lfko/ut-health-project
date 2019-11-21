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
        * https://www.bigcitieshealth.org/
        * https://www.ruralhealthinfo.org (Data Explorer on rural data)
        * https://bioportal.bioontology.org/ontologies/DOID/?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FDOID_12549 (for diseases and symptoms)
- Approach: * historical tweets, location of tweets (per API?), symptoms by disease
            * Scrape Twitter (how to filter?)
            * but first look for text corpora and try to figure out how to describe certain diseases and their symptoms
            * the NLP part itself is only of supportive character, since there are no gold labels
            * so therefore use the existing reported data (weekly aggregated) to predict an outbreak (labels?)
            * define thresholds on when to decide what disease we are detecting and if there is a possible outbreak

- Twitter-API: * https://www.tweepy.org/ (already existing python implementation for accessing the Twitter-API) (pip install tweepy)
- Python: * http://www.laurentluce.com/posts/twitter-sentiment-analysis-using-python-and-nltk/


## New project approach (11/21/19)
### Project 1: Do cities make you sick?
- Find datasets which could provide insights in the health environment of cities and rural areas
- Define, what a city area is and what a rureal area is (USA)
    - urbanized area: > 50000 inhabitants, > 1000 density 
    - rural: < 2500 inhabitants, < 999 density
    - apply the same for GER to make life easier
- Find columns, indicators which are worth inspecting/comparing
- Load data, extract all necessary columns/information

### Project 2: Tweet, if you feel sick (or: location-aware tweeting)
- Look if one is able - using geo-position of a tweet - to find out, whether living in a urban area makes you more prone to get ill or not
- different types of disease are expressed through various kinds of symptons, which are again