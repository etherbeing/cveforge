# CVE Architecture
Each CVE project must include a .cve file at the root when running cveforge in a working directory where exist .cve then the forge will register
this folder path as a CVE and you'd be able to use the CVE from that point onward no matter where you're located.
But note that each time you run the forge and it fails to load a CVE it will increase the failure counter, when the max umbral for the failures
is reached then the user will be prompted at startup for whether or not to remove the project path from the DB.

|- yourproject
|--- .cve
|--- parsers/ # Here it goes the argument parsers for the commands
|--- code/ # Here it goes the execution code of the CVEs
|--- payloads/ # Here it goes the malware or reverse shell etc
|--- fuzzers/ # Here goes payload generators
|--- models/ # Here goes your DB models so you can persist your project
|--- api/ # Here goes your API in case you wanna make your project to be accessible from anywhere else
|--- serializers/ # Here goes the serializers for your models and API
|--- README.md # and other metadata can go wherever you want it

Please note that even if the .cveforge.toml allows you to register projects path is not intended for users but rather is for internal use only (for now)

But wait!!! you can use the admin interface to register manually new exploits path.
