# sieloader-repository-client
Sieloader (SIERRA tool addons loader) repository client tool made for communicating with Sieloader Repository Service and downloading addons.

# How to use

```sierepo update/info/install -r addon name (used with command install only) -s server url (used only with info command for getting server info)```
# Examples
```sierepo update```
Updating local metadata from all servers 

```sierepo info -s https://sierra.vladhog.ru/```
Getting information about https://sierra.vladhog.ru/ server

```sierepo install -r invoker-starter-pack```
Will install invoker started pack from sierra.vladhog.ru server

# Adding servers 
To add new servers just added their url like https://sierra.vladhog.ru/ to repo.txt next to sierepo, after it use sierepo update for getting server public key and getting list of addons from server.

# License
Sieloader Repository Client © 2024 by Vladhog Security is licensed under Attribution-NonCommercial-ShareAlike 4.0 International.