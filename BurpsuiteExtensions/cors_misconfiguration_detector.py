from burp import IBurpExtender, IHttpListener
from java.io import PrintWriter
import re

class BurpExtender(IBurpExtender, IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        callbacks.setExtensionName("CORS Misconfig Detector")

        self.stdout = PrintWriter(callbacks.getStdout(), True)
        self.stderr = PrintWriter(callbacks.getStderr(), True)

        callbacks.registerHttpListener(self)
        self.stdout.println("CORS Misconfig Detector loaded.")

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        # Only analyze responses
        if messageIsRequest:
            return

        response = messageInfo.getResponse()
        analyzedResponse = self.helpers.analyzeResponse(response)
        headers = analyzedResponse.getHeaders()
        body = response[analyzedResponse.getBodyOffset():].tostring()

        cors_headers = {}
        for header in headers:
            if header.lower().startswith("access-control-"):
                k, v = header.split(":", 1)
                cors_headers[k.strip().lower()] = v.strip()

        if cors_headers:
            issues = self.detect_issues(cors_headers)
            if issues:
                url = self.helpers.analyzeRequest(messageInfo).getUrl()
                self.stdout.println("Possible CORS misconfiguration at: " + str(url))
                for issue in issues:
                    self.stdout.println("  - " + issue)

    def detect_issues(self, headers):
        issues = []
        origin = headers.get("access-control-allow-origin")
        credentials = headers.get("access-control-allow-credentials", "").lower()

        if origin == "*":
            if credentials == "true":
                issues.append("Wildcard ACAO combined with credentials (invalid per spec, dangerous if leaked)")
            else:
                issues.append("Wildcard ACAO allows any origin")
        elif origin and re.match(r"https?://[^/]+", origin):
            issues.append("Reflective ACAO: potential for misconfiguration if not validated properly")
        if origin == "null":
            issues.append("Null ACAO: might allow sandboxed or file:// origins")
        return issues

