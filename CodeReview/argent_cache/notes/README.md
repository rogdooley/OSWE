# argent_cache

**Language:** Python (Flask)  
**Focus Area:** Web Cache Poisoning  
**Notes:**  
- Simulates a basic Flask app behind a caching reverse proxy.  
- Consider how headers like `X-User` and cache directives could affect behavior.  
- The flaw may not be obvious from the app alone.

## Hints
- Consider how proxy caching behavior might cache personalized content.
- Look at the response headers in detail.
