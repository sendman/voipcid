Client for VOIP CID push service available at AppStore

* Installation of socket server

1. Install and configure for Asterisk:

    1.1. Download and install required libs to agi socket server, 
    python-httplib2 and python SocketServer. Normally this should be already
    installed.

    1.2. Install the push_fastagi.py in /usr/local/bin 
    and the certificate in /usr/local/bin/ssl/push.crt

    1.3. Configure settings.yaml as you need
    
    1.4. Run the socket server:
    $ /usr/local/bin/push_fastagi.py

    The socket will listen at localhost on 8000.

    1.5. Configure asterisk

    1.5.1. create a macro in your extensions.conf, like this:

    [macro-push-agi]
    exten => s,1,Set(email=${DB(push/${CALLERID(dnid)})})
    exten => s,n,GotoIf($["${email}" != ""]?push)
    exten => s,n,MacroExit
    exten => s,n(push),AGI(agi://127.0.0.1:8000,${email})

    Next add at your extensions, to call the macro above just before
    to ring your phone.

    exten => EXTENSION_NUMBER,n,Macro(push-agi)

    1.5.2. Add the appstore account for each extension you want to receive
    push notifications from asterisk server, for that, use the asterisk cli:

    *CLI> database put push EXTENSION APPSTORE_EMAIL_ADDRESS
