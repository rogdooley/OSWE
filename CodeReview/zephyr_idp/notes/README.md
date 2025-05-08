# zephyr_idp

**Language:** C# ASP.NET MVC  
**Focus Area:** SAML Assertion Parsing  
**Notes:**  
- This file processes SAML assertions posted to the Assertion Consumer Service (ACS) endpoint.  
- Parsing and identity logic are implemented in a single location.  
- There's a subtle flaw in how the identity is accepted or validated.

## Hints
- Pay close attention to trust boundaries and what is or isn’t validated.
- Consider how tampered input might affect behavior.
