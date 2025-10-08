# Server-Side Template Injection (SSTI)

## What is SSTI?
SSTI occurs when user-controlled input is embedded into a server-side template and evaluated as code, allowing arbitrary expression execution.

## Vulnerable Template Engines

| Language | Engines             |
|----------|---------------------|
| Python   | Jinja2, Mako        |
| PHP      | Smarty, Twig        |
| Java     | FreeMarker, Velocity |
| Node.js  | EJS, Handlebars     |

## Exploit Example (Jinja2)

```
{{ config.items() }}
{{ self._TemplateReference__context.cycler.__init__.__globals__.os.system('id') }}
```

## Risk Impact

| Risk             | Impact                        |
|------------------|-------------------------------|
| RCE              | Code execution on the server  |
| File disclosure  | Read local files              |
| Command injection| Spawn shell commands          |

## Detection

- Input reflected inside template rendering
- Special syntax like `{{`, `${`, `[%`, `<%` processed in responses

## Mitigation

- Never pass user input directly into templates
- Escape dynamic content or use safe APIs
- Disable expression evaluation if not needed
- Run templating in sandboxed environments
