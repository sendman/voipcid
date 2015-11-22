Client for VOIP CID push service available at AppStore

* Installation of socket server

1. Install and configure for Asterisk:

    1.1. Download and install required libs to agi socket server, 
    python-httplib2 and python SocketServer. Normally this should be already
    installed.

    1.2. Install the push_fastagi.py in /usr/local/bin 
    and the certificate in /usr/local/bin/ssl/push.crt

    1.3. Configure settings.yaml as you need
        ip
        port
        prefix of your phone numbers
    
    1.4. Run the socket server:
    $ /usr/local/bin/push_fastagi.py

    The socket will listen at localhost on 8000.

    1.5. Configure asterisk

    1.5.1. create a macro in your extensions.conf, like this:

    [macro-push]
    exten => s,1,AGI(agi://127.0.0.1:8000)

    Next add at your extensions, according your dialplan, to call the macro above just before
    to ring your phone.

    Examples:

        exten => EXTENSION_NUMBER,n,Macro(push)

        or

        exten => _X.,n,Macro(push)

    After this configs, all incomming calls, the asterisk server notify the voipcid servers to
    push devices according voip number.

    Don't forget to setup all your phone numbers in app.
