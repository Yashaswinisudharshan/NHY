import requests

WORLD_BANK_URL = (
    "https://api.worldbank.org/v2/country/IN/indicator/"
    "FP.CPI.TOTL.ZG?format=json&mrv=1"
)

FALLBACK_INFLATION_RATE = 5.0  
# Used if API is down — 5% is India's approximate average

def get_india_inflation_rate() -> float:
    """
    Fetches India's latest CPI inflation rate from World Bank API.
    
    Why World Bank?
    - Free, no API key needed
    - Official data — same source RBI references
    - Returns yearly CPI inflation for India
    
    CPI = Consumer Price Index
    Measures how much prices of everyday goods have risen.
    If CPI inflation is 6%, ₹100 last year = ₹106 worth of goods this year.
    This directly impacts how much budget departments actually need.
    
    Returns: float (e.g. 5.65 for 5.65% inflation)
    """
    try:
        response = requests.get(WORLD_BANK_URL, timeout=5)
        # timeout=5 means if World Bank doesn't respond in 5 seconds, give up
        
        data = response.json()
        # data is a list of 2 items:
        # data[0] = metadata (page info)
        # data[1] = actual records list
        
        records = data[1]
        
        if records and records[0]["value"] is not None:
            rate = round(float(records[0]["value"]), 2)
            print(f"[Inflation API] Fetched rate: {rate}% ({records[0]['date']})")
            return rate
        else:
            print("[Inflation API] No data returned, using fallback")
            return FALLBACK_INFLATION_RATE
            
    except Exception as e:
        # If anything goes wrong (no internet, API down etc)
        # we fall back to a safe default instead of crashing
        print(f"[Inflation API] Error: {e}, using fallback {FALLBACK_INFLATION_RATE}%")
        return FALLBACK_INFLATION_RATE