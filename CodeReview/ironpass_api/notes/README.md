# ironpass_api

**Language:** C# ASP.NET Core  
**Focus Area:** Race Condition / Timing Attack  
**Notes:**  
- Implements password reset flow using token lookup.  
- Uses shared memory structure for token tracking.

## Hints
- What happens under concurrent requests?
- What assumptions are made in `submit` token handling?
