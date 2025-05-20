# SlappySpatchy Networking Protocol
The protocol used for SlappySpatchy is one I designed myself, with no real thought for security... It sits in the application level, over TCP and IPv4. 
## Packet Format
It uses C-style struct formatting to pack data into a packet (byte buffer). The general structure the average exchange would look like this: <pre>
```
CLIENT	---------- SERVER
requestType ->
username ->
[request data] ->
          <- response data
```
</pre>
## Request types
All request types are three bytes. The ones generally recognised by the multiplayer-avocado server are:

`JON` : Join the game

`GET` : request data about a player

`SET` : set the status/data about a player

`LSP` : list players, sending each one as a seperate packet for some reason.

`EVT` : specify an event occurred. Currently the server does not respond to this as it is not presently implemented.
