# Injeneer

## In some distant future this should be to metasploit what helix is to neovim. The dream is one obvious short command to RCE on a vulnerable target with zero config or interactivity.
## Right now it's a low-brow mix of sqlmap and metasploit, in the sense that this tool looks for RCE-vulnerable fields and potentially injects a payload, while at the same time hosting a listener/controller.
## Another aim is to be easily scriptable.


```
TODO:
stager logic
meta-shell (easy file passthrough, port forwarding, persistence) (those things should be stager stages written in concise dependency-less C)
csrf tokens/cookies/impersonation
directly call the kernel through linux64, /lib64/ld-linux-x86-64.so.2, or use alternative shells to get around noexec /tmp
-h to print something helpful
```

## How to use:

### The tool has two types of arguments: arg (LPORT 8000) and command (inject)
### They can be combined in any order 

### Supported commands:
    inject - what it sounds like
    generate - print a plaintext or binary payload (by default reverse shell)
    scrape - check if a URL has any obvious entry points
    listen - host a listener for a reverse shell. Can be used standalone instead of nc -l
    control - host a listener for a stager payload. Pretty useless on its own

### Supported arguments (if not provided, the tool will fall back to defaults):
    LHOST
    LPORT - both combine the address for the listener to listen on

    CHOST
    CPORT - same thing but for stager controller

    PTYPE - payload type. On some setups some payloads may fail, use to exhaust possibilites. One of [shell, binshell, stager, custom]

    CUSTOM_PAYLOAD - for custom payloads (like ones from https://www.revshells.com)

    URL - target web page. Only web page.

    TARGET - target any address that is not a web page. Supports a custom ffuf-style inject point (http://1.1.1.1:80/INJECT)

    CUSTOM_LISTENER - boolean 1/0, tells the program not to start the listener automatically

    CUSTOM_STAGES - comma-separated (stage1,stage2) list of payloads. Filepath when injecting a binary, command when injecting plaintext
    CUSTOM_STAGE_TYPES - comma-separated list of payload types. One of [bin,cmd]. Length has to be equal to length of CUSTOM_STAGES

### Example: automatically find vulnerable fields and get a shell
```bash
    ./cli.py URL http://<TARGETIP>:<TARGETPORT>/home inject
```

