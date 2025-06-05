

## CWEE Modules

### CWEE/Whitebox_Attacks/race_condition.py

**Module:** Whitebox Attacks  
**Topic:** Race Conditions and Session Handling  
**Description:**  
This script targets a web application vulnerable to a race condition in the `buy` endpoint of a gift card system. The vulnerability stems from PHP’s default file-locking behavior when handling session files. To bypass this, multiple unique `PHPSESSID` values are generated via concurrent logins and used to issue parallel requests that trigger the race.

**Technique Highlights:**
- Circumventing PHP session locks by rotating session IDs.
- Exploiting a race condition on the backend's gift card `buy` endpoint.
- Threaded attack execution using `ThreadPoolExecutor`.
- Loop-based control to continue exploiting until a target balance is reached and the flag is purchased.

**Usage:**

```bash
python3 race_condition.py --target http://<host>:<port> \
  --username <user> \
  --password '<password>' \
  --num-logins 30
```