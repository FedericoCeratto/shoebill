<!DOCTYPE HTML>
<html>
    <head>
        <title>Pelican editor</title>
        <style>
            html {
                color: #555;
                font-size: 90%;
                background-color: #fafafa;
            }
            body {
                margin: .8em;
            }
            div#outputbox {
                background: #fefefe;
                -moz-border-radius: 5px;
                border-radius: 5px;
                border: 1px solid #dadada;
                height: 100%;
                overflow:hidden;
                padding: .5em;
            }
            #errmsg {
                border: 1px dashed #ff6060;
                margin: 1em;
                padding: 1em;
                width: 20em;
            }
            a {
                color: black;
                margin: .3em;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            span.errorline {
                color: #900;
            }
        </style>
    </head>
    <body>
        % if output:
        <div id="outputbox">
            % for line in output:
                % if line.startswith(('ERROR:', 'CRITICAL:')):
                <span class="errorline"> {{line}}</span>
                % else:
                <span> {{line}}</span>
                % end
                <br/>
            % end
        </div>
        % end
        % if errmsg:
        <div id="errmsg">{{errmsg}}</div>
        % end
        <a href="/edit">go back</a>
    </body>
</html>

