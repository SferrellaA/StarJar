# StarJar

Meant to be a reverse-engineering challenge for my coworkers. Ostensibly an art installation, it advertises `secret` information that can be investigated.


All parts of the challenge can be solved with a mobile phone and without advanced tools. 

## Walkthrough:
### Phase One
<details><summary>The jar flashes in morse-code...</summary>
    <details><summary>An SSID that does not exist...</summary>
        <details><summary>That the player should...</summary>
            <details><summary>Themselves host with a password...</summary>
                That is the same as the SSID
            </details>
            <details><summary>HOWTO</summary>
                Create a phone hotspot with the name of the SSID
            </details>
        </details>
    </details>
</details>
<details><summary>Alternatively look at...</summary>
    <details><summary>Connection attempts via...</summary>
        The Aircrack-ng suite
    </details>
</details>

### Phase Two
<details><summary>spoiler warning</summary>
    - The user connects to the device as a web server
    - The web server presents a page warning the player off
    - The player looks at page source
    - The available endpoints are limited, but a get-thing endpoint can be used to look at things
    - the web server uses the endpoint to provide images, but it is not sandboxed
    - the player uses the get-thing endpoint to see how server.py works
    - server.py at runtime generates a random endpoint the plalyer is supposed to find
    - the jar flashes a code to be entered into the random endpoint
        - this code is also available through a debug endpoint the player might find
    - the player inputs the code into the random endpoint
</details>