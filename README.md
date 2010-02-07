rivr is a microweb framework inspired by djng, the reason for rivr is djng without the django dependency. It is a lightweight framework which can be included along side another python application. rivr does not include a template engine or a database layer. You can pick your own and use them.

What rivr includes:
- Domain router (Like django's URL router, but you can have a regex search over the whole domain, useful for subdomains).
- A debugging middleware
- Basic HTTP authentication
